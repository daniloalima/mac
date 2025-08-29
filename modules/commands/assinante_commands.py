from .base_command import BaseCommand
from ..services.assinante_service import AssinanteService
from ..services.mesa_service import MesaService
import discord
from discord import app_commands

class AssinanteCommands(BaseCommand):
    def __init__(self, utils, admin_roles):
        super().__init__(utils, admin_roles)
        self.assinante_service = AssinanteService()
        self.mesa_service = MesaService()
    
    def register_commands(self, tree: app_commands.CommandTree):
        tree.command(description="Registrar um novo assinante")(self.registrar_assinante)
        tree.command(description="Consultar informações de um assinante")(self.consultar_assinante)
        tree.command(description="Editar informações de um assinante")(self.editar_assinante)
        tree.command(description="Listar todos os assinantes (resumido)")(self.listar_assinantes)
        tree.command(description="Verificar assinantes locais em atraso")(self.assinantes_locais_atrasados)
    
    @app_commands.describe(
        nome="Nome do assinante",
        email="Email do assinante",
        celular="Celular do assinante",
        mesas="IDs das mesas que o assinante participa (separados por vírgula)",
        ultimo_mes_pago="Último mês pago (ex: 30/08/2025)",
        forma_pagamento="Forma de pagamento (ex: PIX, cartão, boleto)",
        valor="Valor da assinatura (ex: R$ 79,80)"
    )
    async def registrar_assinante(
        self,
        interaction: discord.Interaction,
        nome: str,
        email: str,
        celular: str,
        mesas: str,
        ultimo_mes_pago: str,
        forma_pagamento: str,
        valor: str
    ):
        if not self.check_admin(interaction.user):
            await interaction.response.send_message("Você não tem permissão para registrar assinantes", ephemeral=True)
            return

        mesas_ids = [int(m.strip()) for m in mesas.split(",") if m.strip().isdigit()] if mesas.strip() else []

        novo_assinante = self.assinante_service.criar_assinante(
            nome, email, celular, mesas_ids, ultimo_mes_pago, forma_pagamento, valor
        )

        await interaction.response.send_message(
            f"Assinante registrado com sucesso! ID: {novo_assinante['id']}\n"
            f"Nome: {nome}\n"
            f"Email: {email if email.strip() else 'Não informado'}\n"
            f"Celular: {celular}\n"
            f"Mesas: {', '.join(map(str, mesas_ids)) if mesas_ids else 'Nenhuma'}\n"
            f"Último mês pago: {ultimo_mes_pago}\n"
            f"Forma de pagamento: {forma_pagamento}\n"
            f"Valor: {valor}"
        )
    
    @app_commands.describe(
        assinante_id="ID do assinante para consulta"
    )
    async def consultar_assinante(
        self,
        interaction: discord.Interaction,
        assinante_id: int
    ):
        if not self.check_admin(interaction.user):
            await interaction.response.send_message("Você não tem permissão para consultar assinantes", ephemeral=True)
            return

        assinante = self.assinante_service.buscar_por_id(assinante_id)
        if not assinante:
            await interaction.response.send_message(f"Assinante com ID {assinante_id} não encontrado.", ephemeral=True)
            return

        mesas = self.mesa_service.carregar_mesas()
        mesas_do_assinante = [m for m in mesas if m["id"] in assinante.get("mesas", [])]

        mesas_info = ""
        if mesas_do_assinante:
            for mesa in mesas_do_assinante:
                mesas_info += (
                    f"\n**Nome:** {mesa.get('nome', '-')}\n"
                    f"**Mestre:** {mesa.get('mestre', '-')}\n"
                    f"**Sistema:** {mesa.get('sistema', '-')}\n"
                    f"**Dia:** {mesa.get('dia_semana', '-')}\n"
                    f"**Frequência:** {mesa.get('frequencia', '-')}\n"
                )
        else:
            mesas_info = "Nenhuma mesa encontrada para este assinante."

        msg = (
            f"**Assinante ID:** {assinante['id']}\n"
            f"**Nome:** {assinante['nome']}\n"
            f"**Email:** {assinante['email']}\n"
            f"**Celular:** {assinante['celular']}\n"
            f"**Último mês pago:** {assinante['ultimo_mes_pago']}\n"
            f"**Forma de pagamento:** {assinante.get('forma_pagamento', '-')}\n"
            f"**Valor:** {assinante.get('valor', '-')}\n\n"
            f"**Mesas:** {mesas_info}"
        )

        await interaction.response.send_message(msg)

    @app_commands.describe(
        assinante_id="ID do assinante a ser editado",
        nome="Novo nome do assinante (opcional)",
        email="Novo email do assinante (opcional)",
        celular="Novo celular do assinante (opcional)",
        mesas="Novos IDs das mesas (separados por vírgula, opcional)",
        ultimo_mes_pago="Nova data do último pagamento (opcional)",
        forma_pagamento="Nova forma de pagamento (opcional)",
        valor="Novo valor da assinatura (opcional)"
    )
    async def editar_assinante(
        self,
        interaction: discord.Interaction,
        assinante_id: int,
        nome: str = None,
        email: str = None,
        celular: str = None,
        mesas: str = None,
        ultimo_mes_pago: str = None,
        forma_pagamento: str = None,
        valor: str = None
    ):
        if not self.check_admin(interaction.user):
            await interaction.response.send_message("Você não tem permissão para editar assinantes", ephemeral=True)
            return

        updates = {}
        alteracoes = []

        if nome is not None:
            updates["nome"] = nome
            alteracoes.append(f"Nome: {nome}")

        if email is not None:
            updates["email"] = email if email.strip() else ""
            alteracoes.append(f"Email: {email if email.strip() else 'Removido'}")

        if celular is not None:
            updates["celular"] = celular
            alteracoes.append(f"Celular: {celular}")

        if mesas is not None:
            mesas_ids = [int(m.strip()) for m in mesas.split(",") if m.strip().isdigit()] if mesas.strip() else []
            updates["mesas"] = mesas_ids
            alteracoes.append(f"Mesas: {', '.join(map(str, mesas_ids)) if mesas_ids else 'Nenhuma'}")

        if ultimo_mes_pago is not None:
            updates["ultimo_mes_pago"] = ultimo_mes_pago
            alteracoes.append(f"Último mês pago: {ultimo_mes_pago}")

        if forma_pagamento is not None:
            updates["forma_pagamento"] = forma_pagamento
            alteracoes.append(f"Forma de pagamento: {forma_pagamento}")

        if valor is not None:
            updates["valor"] = valor
            alteracoes.append(f"Valor: {valor}")

        if not alteracoes:
            await interaction.response.send_message("Nenhuma alteração foi especificada.", ephemeral=True)
            return

        assinante_atualizado = self.assinante_service.atualizar_assinante(assinante_id, **updates)
        if not assinante_atualizado:
            await interaction.response.send_message(f"Assinante com ID {assinante_id} não encontrado.", ephemeral=True)
            return

        alteracoes_str = "\n".join(alteracoes)
        await interaction.response.send_message(
            f"Assinante ID {assinante_id} editado com sucesso!\n\n"
            f"**Alterações realizadas:**\n{alteracoes_str}"
        )

    @app_commands.describe()
    async def listar_assinantes(
        self,
        interaction: discord.Interaction
    ):
        if not self.check_admin(interaction.user):
            await interaction.response.send_message("Você não tem permissão para consultar assinantes", ephemeral=True)
            return

        await interaction.response.defer()

        assinantes = self.assinante_service.carregar_assinantes()
        if not assinantes:
            await interaction.followup.send("Nenhum assinante cadastrado.")
            return

        total_assinantes = len(assinantes)
        summary = f"**Lista de Todos os Assinantes (Resumo)**\n"
        summary += f"**Total de assinantes:** {total_assinantes}\n\n"

        for assinante in assinantes:
            assinante_id = assinante.get("id", "N/A")
            nome = assinante.get("nome", "N/A")
            summary += f"**ID {assinante_id}:** {nome}\n"

        if len(summary) > 2000:
            chunks = [summary[i:i+2000] for i in range(0, len(summary), 2000)]
            await interaction.followup.send(chunks[0])
            for chunk in chunks[1:]:
                await interaction.followup.send(chunk)
        else:
            await interaction.followup.send(summary)

    @app_commands.describe()
    async def assinantes_locais_atrasados(
        self,
        interaction: discord.Interaction
    ):
        if not self.check_admin(interaction.user):
            await interaction.response.send_message("Você não tem permissão para consultar assinantes", ephemeral=True)
            return

        await interaction.response.defer()

        atrasados = self.assinante_service.listar_atrasados()
        total_atrasados = len(atrasados)

        summary = f"**Resumo de Assinantes Locais em Atraso**\n"
        summary += f"**Total de assinantes atrasados:** {total_atrasados}\n\n"

        if total_atrasados == 0:
            summary += "Nenhum assinante local em atraso encontrado."
        else:
            valores_summary = {}
            total_value = 0

            for assinante in atrasados:
                valor_str = assinante.get("valor", "R$ 0,00")
                valor_limpo = valor_str.replace("R$ ", "").replace(".", "").replace(",", ".")
                try:
                    valor = float(valor_limpo)
                except:
                    valor = 0

                total_value += valor

                if valor_str not in valores_summary:
                    valores_summary[valor_str] = {
                        "count": 0,
                        "valor_numerico": valor
                    }

                valores_summary[valor_str]["count"] += 1

            # Monta o resumo por valores
            summary += "**Por Valores:**\n"
            for valor_str, info in sorted(valores_summary.items(), key=lambda x: x[1]["valor_numerico"], reverse=True):
                plan_total = info["valor_numerico"] * info["count"]
                summary += f"• {valor_str}: {info['count']} assinantes (Total: R$ {plan_total:.2f})\n"

            summary += f"\n**Valor total em atraso:** R$ {total_value:.2f}\n"

            # Lista todos os assinantes atrasados
            summary += "\n**Todos os assinantes em atraso:**\n"
            for assinante in atrasados:
                nome = assinante.get("nome", "N/A")
                celular = assinante.get("celular", "N/A")
                valor = assinante.get("valor", "N/A")
                ultimo_pagamento = assinante.get("ultimo_mes_pago", "N/A")
                summary += f"• {nome} ({celular}) - {valor} - Último pagamento: {ultimo_pagamento}\n"

        if len(summary) > 2000:
            chunks = [summary[i:i+2000] for i in range(0, len(summary), 2000)]
            await interaction.followup.send(chunks[0])
            for chunk in chunks[1:]:
                await interaction.followup.send(chunk)
        else:
            await interaction.followup.send(summary)
