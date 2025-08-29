from .base_command import BaseCommand
from ..hotmart_handler import HotmartAPI
from ..embed_handler import Embed
from ..services.assinante_service import AssinanteService
import discord
from discord import app_commands
import logging

logger = logging.getLogger(__name__)

class AdminCommands(BaseCommand):
    def __init__(self, utils, admin_roles, hotmart_api, embed, guild_server_id, client):
        super().__init__(utils, admin_roles)
        self.hotmart_api = hotmart_api
        self.embed = embed
        self.guild_server_id = guild_server_id
        self.client = client
        self.assinante_service = AssinanteService()
        self.tree = None  # Será definido no register_commands
    
    def register_commands(self, tree: app_commands.CommandTree):
        self.tree = tree  # Armazena referência do tree
        tree.command(description="Sincronizar comandos e verificar latência")(self.sync_and_ping)
        tree.command(description="Checar funcionalidades disponíveis")(self.feature_check)
        tree.command(description="Consultar assinaturas atrasadas no Hotmart")(self.assinaturas_atrasadas)
        tree.command(description="Resumo geral de valores - Hotmart e JSON local")(self.resumo_valores)
    
    async def sync_and_ping(self, interaction: discord.Interaction):
        if not self.check_admin(interaction.user):
            await interaction.response.send_message("Você não tem permissão para recarregar os comandos", ephemeral=True)
            return
        
        synced = await self.tree.sync()
        latency = self.client.latency * 1000
        logger.info(f"reloaded {len(synced)} commands! {latency:.2f}ms")
        await interaction.response.send_message(embed=self.embed.ping_embed(latency, len(synced)))

    async def feature_check(self, interaction: discord.Interaction):
        is_admin = self.check_admin(interaction.user)
        is_guild_server = interaction.guild.id == self.guild_server_id
        await interaction.response.send_message(embed=self.embed.feature_check_embed(is_admin, is_guild_server))
    
    @app_commands.describe()
    async def assinaturas_atrasadas(self, interaction: discord.Interaction):
        if not self.check_admin(interaction.user):
            await interaction.response.send_message("Você não tem permissão para consultar assinaturas", ephemeral=True)
            return

        await interaction.response.defer()

        try:
            summary = self.hotmart_api.get_delayed_subscriptions()
            if summary:
                if len(summary) > 2000:
                    chunks = [summary[i:i+2000] for i in range(0, len(summary), 2000)]
                    await interaction.followup.send(chunks[0])
                    for chunk in chunks[1:]:
                        await interaction.followup.send(chunk)
                else:
                    await interaction.followup.send(summary)
            else:
                await interaction.followup.send("Erro ao consultar assinaturas atrasadas.")
        except Exception as e:
            logger.error(f"Erro ao consultar assinaturas: {e}")
            await interaction.followup.send("Erro interno ao consultar assinaturas.")

    @app_commands.describe()
    async def resumo_valores(self, interaction: discord.Interaction):
        """Comando para gerar resumo de valores das assinaturas ativas e atrasadas"""
        if not self.check_admin(interaction.user):
            await interaction.response.send_message("Você não tem permissão para consultar resumos", ephemeral=True)
            return

        await interaction.response.defer()

        try:
            # Buscar dados da Hotmart
            hotmart_data = self.hotmart_api.get_active_and_delayed_summary()
            if "error" in hotmart_data:
                await interaction.followup.send(f"Erro Hotmart: {hotmart_data['error']}")
                return

            # Buscar dados do JSON local
            assinantes_locais = self.assinante_service.carregar_assinantes()
            assinantes_atrasados_locais = self.assinante_service.listar_atrasados()

            # Processar dados da Hotmart
            hotmart_active = hotmart_data.get("active", {})
            hotmart_delayed = hotmart_data.get("delayed", {})
            
            hotmart_active_items = hotmart_active.get("items", [])
            hotmart_delayed_items = hotmart_delayed.get("items", [])
            
            hotmart_active_total = hotmart_active.get("total", 0)
            hotmart_delayed_total = hotmart_delayed.get("total", 0)

            # Calcular valores Hotmart
            hotmart_active_value = 0
            hotmart_delayed_value = 0
            
            for item in hotmart_active_items:
                price = item.get("price", {})
                hotmart_active_value += price.get("value", 0)
                
            for item in hotmart_delayed_items:
                price = item.get("price", {})
                hotmart_delayed_value += price.get("value", 0)

                        # Calcular valores JSON local
            local_total_value = 0
            local_atrasado_value = 0
            assinantes_mensais = 0
            assinantes_semestrais = 0
            
            for assinante in assinantes_locais:
                valor_str = assinante.get("valor", "R$ 0,00")
                nome = assinante.get("nome", "")
                
                try:
                    valor_num = float(valor_str.replace("R$", "").replace(",", ".").strip())
                    
                    # Verificar se é assinante semestral (tem "(s)" no nome)
                    if "(s)" in nome.lower():
                        valor_mensal = valor_num / 6  # Dividir por 6 para assinantes semestrais
                        assinantes_semestrais += 1
                    else:
                        valor_mensal = valor_num
                        assinantes_mensais += 1
                    
                    local_total_value += valor_mensal
                except:
                    pass
            
            for assinante in assinantes_atrasados_locais:
                valor_str = assinante.get("valor", "R$ 0,00")
                nome = assinante.get("nome", "")
                
                try:
                    valor_num = float(valor_str.replace("R$", "").replace(",", ".").strip())
                    
                    # Verificar se é assinante semestral (tem "(s)" no nome)
                    if "(s)" in nome.lower():
                        valor_mensal = valor_num / 6  # Dividir por 6 para assinantes semestrais
                    else:
                        valor_mensal = valor_num
                    
                    local_atrasado_value += valor_mensal
                except:
                    pass

            # Criar resumo
            summary = "**📊 RESUMO GERAL DE VALORES - ASSINATURAS**\n\n"
            
            summary += "**🌐 HOTMART**\n"
            summary += f"• Assinaturas Ativas: {hotmart_active_total} (R$ {hotmart_active_value:.2f})\n"
            summary += f"• Assinaturas Atrasadas: {hotmart_delayed_total} (R$ {hotmart_delayed_value:.2f})\n"
            summary += f"• **Total Hotmart: R$ {(hotmart_active_value + hotmart_delayed_value):.2f}**\n\n"
            
            summary += "**📋 JSON LOCAL**\n"
            summary += f"• Total de Assinantes: {len(assinantes_locais)} (R$ {local_total_value:.2f})\n"
            summary += f"  - Mensais: {assinantes_mensais} | Semestrais: {assinantes_semestrais}\n"
            summary += f"• Assinantes em Atraso: {len(assinantes_atrasados_locais)} (R$ {local_atrasado_value:.2f})\n"
            summary += f"• **Total JSON Local: R$ {local_total_value:.2f}**\n\n"
            
            summary += "**💰 CONSOLIDADO GERAL**\n"
            total_geral = hotmart_active_value + hotmart_delayed_value + local_total_value
            total_atrasados = hotmart_delayed_value + local_atrasado_value
            summary += f"• **Valor Total Geral: R$ {total_geral:.2f}**\n"
            summary += f"• **Valor Total em Atraso: R$ {total_atrasados:.2f}**\n"
            
            # Adicionar detalhes por planos da Hotmart se houver
            if hotmart_active_items or hotmart_delayed_items:
                summary += "\n**📈 DETALHES HOTMART POR PLANOS:**\n"
                
                # Consolidar planos
                plans_summary = {}
                
                # Processar itens ativos
                for item in hotmart_active_items:
                    plan = item.get("plan", {})
                    price = item.get("price", {})
                    
                    plan_name = plan.get("name", "N/A")
                    value = price.get("value", 0)
                    
                    if plan_name not in plans_summary:
                        plans_summary[plan_name] = {
                            "active_count": 0,
                            "delayed_count": 0,
                            "value": value
                        }
                    
                    plans_summary[plan_name]["active_count"] += 1
                
                # Processar itens atrasados
                for item in hotmart_delayed_items:
                    plan = item.get("plan", {})
                    price = item.get("price", {})
                    
                    plan_name = plan.get("name", "N/A")
                    value = price.get("value", 0)
                    
                    if plan_name not in plans_summary:
                        plans_summary[plan_name] = {
                            "active_count": 0,
                            "delayed_count": 0,
                            "value": value
                        }
                    
                    plans_summary[plan_name]["delayed_count"] += 1
                
                for plan_name, info in plans_summary.items():
                    total_count = info["active_count"] + info["delayed_count"]
                    total_plan_value = info["value"] * total_count
                    summary += f"• {plan_name}: {total_count} assinantes ({info['active_count']} ativas, {info['delayed_count']} atrasadas) - R$ {total_plan_value:.2f}\n"

            # Enviar resposta (quebrar em chunks se necessário)
            if len(summary) > 2000:
                chunks = [summary[i:i+2000] for i in range(0, len(summary), 2000)]
                await interaction.followup.send(chunks[0])
                for chunk in chunks[1:]:
                    await interaction.followup.send(chunk)
            else:
                await interaction.followup.send(summary)

        except Exception as e:
            logger.error(f"Erro ao gerar resumo de valores: {e}")
            await interaction.followup.send("Erro interno ao gerar resumo de valores.")
