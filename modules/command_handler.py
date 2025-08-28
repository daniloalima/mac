import logging
from typing import List, Literal
import discord,os
from discord.ext.commands import Greedy
from dotenv import load_dotenv
from discord import app_commands
from .embed_handler import Embed
from .button_handler import Buttons
from .utils import Utils
from .hotmart_handler import HotmartAPI
import json
import datetime
from dateutil import parser

logger = logging.getLogger(__name__)

class Commands():
    def __init__(self, tree: app_commands.CommandTree, client: discord.Client) -> None:
        load_dotenv()
        self.tree = tree
        self.client = client
        self.log_channel_id = int(os.environ.get('LOG_CHANNEL_ID'))
        self.mission_log_channel_id= int(os.environ.get('MISSION_LOG_CHANNEL_ID'))
        self.admin_roles = os.environ.get('ADMIN_ROLES')
        self.guild_server_id = int(os.environ.get('GUILD_SERVER_ID'))
        self.embed = Embed()
        self.utils = Utils()
        self.admin_roles = self.utils.convert_to_int_list(self.admin_roles)
        self.client.event(self.on_ready)
        self.hotmart_api = HotmartAPI()

        self.tree.command()(self.sync_and_ping)
        self.tree.command(description="Criar uma missão no quadro")(self.mission_create)
        self.tree.command(description="Rolar dados")(self.roll_parabellum)
        self.tree.command(description="Checar funcionalidades disponíveis")(self.feature_check)
        self.tree.command(description="Registrar sucesso de missão")(self.mission_success)
        self.tree.command(description="Registrar falha de missão")(self.mission_failed)
        self.tree.command(description="Registrar uma nova mesa")(self.registrar_mesa)
        self.tree.command(description="Registrar um novo assinante")(self.registrar_assinante)
        self.tree.command(description="Consultar informações de um assinante")(self.consultar_assinante)
        self.tree.command(description="Consultar assinaturas atrasadas no Hotmart")(self.assinaturas_atrasadas)
        self.tree.command(description="Verificar assinantes locais em atraso")(self.assinantes_locais_atrasados)

    async def on_ready(self):
        logger.info("bot up and running")

    async def sync_and_ping(self, interaction: discord.Interaction):
        if not self.utils.check_admin(interaction.user, self.admin_roles):
            await interaction.response.send_message("Você não tem permissão para recarregar os comandos", ephemeral=True)
            return
        synced = await self.tree.sync()
        latency = self.client.latency * 1000
        logger.info(f"reloaded {len(synced)} commands! {latency:.2f}ms")
        await interaction.response.send_message(embed=self.embed.ping_embed(latency, len(synced)))

    async def feature_check(self, interaction: discord.Interaction):
        is_admin = self.utils.check_admin(interaction.user, self.admin_roles)
        is_guild_server = interaction.guild.id == self.guild_server_id
        await interaction.response.send_message(embed=self.embed.feature_check_embed(is_admin, is_guild_server))

    @app_commands.describe(
        mestre = "Narrador da mesa",
        rank="Dificuldade da missão",
        titulo_missao="O nome da sua aventura",
        resumo="Uma sinopse da missão",
        data_hora="Quando a aventura será narrada (ex: 24/08 17:00)",
        )
    async def mission_create(
        self,
        interaction: discord.Interaction,
        mestre: discord.Member,
        rank: Literal [
            "Cobre (XP 15-20)",
            "Bronze (XP 20-35)",
            "Prata (XP 35-60)",
            "Ouro (XP 60-100)",
            "Platina (XP 100-160)",
            "Lenda (XP 160+)"
        ],
        titulo_missao: str,
        resumo: str,
        data_hora: str,
        ):

        if interaction.guild.id != self.guild_server_id:
            await interaction.response.send_message("Esse comando só pode ser utilizado no servidor de guilda", ephemeral=True)
            return

        await interaction.response.send_message(
            embed=self.embed.mission_embed(mestre, rank, titulo_missao, resumo, data_hora),
            view=Buttons(mestre=mestre,
                         log_channel_id=self.log_channel_id,
                         titulo_missao=titulo_missao,
                         admin_roles=self.admin_roles,
                         mission_log_channel_id=self.mission_log_channel_id
                         )
        )

        if self.mission_log_channel_id:
            try:
                mission_log_channel = interaction.guild.get_channel(self.mission_log_channel_id)
                await mission_log_channel.send(f'O mestre {mestre.mention} **ABRIU** uma nova mesa **{titulo_missao}**')
            except:
                logger.warning("falha ao mandar log para o canal")


    @app_commands.describe(
        qtd_dados="Quantidade de dados a serem rolados",
        dificuldade="Dificuldade do teste (quantos dados você vai perder)",
        target="Alvo da rolagem para sucesso (padrão 8)",
        explosao="Valor que será rerolado (padrão 10, coloque 0 para não ter explosão de dados)"
    )
    async def roll_parabellum(self, interaction: discord.Interaction, qtd_dados: int, dificuldade: int = None, target: int = None, explosao: int = None):
        rolled_dice = self.utils.roll(qtd_dados, dificuldade, target, explosao)

        await interaction.response.send_message(
            embed=self.embed.rolls_embed(
                interaction.user,
                rolled_dice[0],
                rolled_dice[1],
                rolled_dice[2],
                rolled_dice[3]
            )
        )

    @app_commands.describe(
        rank="Dificuldade da missão",
    )
    async def mission_success(
            self,
            interaction: discord.Interaction,
            rank: Literal [
                "Cobre (XP 15-20)",
                "Bronze (XP 20-35)",
                "Prata (XP 35-60)",
                "Ouro (XP 60-100)",
                "Platina (XP 100-160)",
                "Lenda (XP 160+)"
            ],
            jogador_1: discord.Member,
            jogador_2: discord.Member,
            jogador_3: discord.Member,
            jogador_4: discord.Member = None,
            jogador_5: discord.Member = None,
        ):
        if interaction.guild.id != self.guild_server_id:
            await interaction.response.send_message("Esse comando só pode ser utilizado no servidor de guilda", ephemeral=True)
            return

        jogadores = [jogador_1, jogador_2, jogador_3, jogador_4, jogador_5]

        await interaction.response.send_message(
            embed=self.embed.mission_success_embed(rank, jogadores)
        )

    @app_commands.describe(
        rank="Dificuldade da missão",
    )
    async def mission_failed(
            self,
            interaction: discord.Interaction,
            rank: Literal [
                "Cobre (XP 15-20)",
                "Bronze (XP 20-35)",
                "Prata (XP 35-60)",
                "Ouro (XP 60-100)",
                "Platina (XP 100-160)",
                "Lenda (XP 160+)"
            ],
            jogador_1: discord.Member,
            jogador_2: discord.Member,
            jogador_3: discord.Member,
            jogador_4: discord.Member = None,
            jogador_5: discord.Member = None,
        ):
        if interaction.guild.id != self.guild_server_id:
            await interaction.response.send_message("Esse comando só pode ser utilizado no servidor de guilda", ephemeral=True)

        jogadores = [jogador_1, jogador_2, jogador_3, jogador_4, jogador_5]

        await interaction.response.send_message(
            embed=self.embed.mission_failed_embed(rank, jogadores)
        )

    @app_commands.describe(
        mestre="Narrador da mesa",
        nome="Nome da mesa",
        sistema="Sistema de RPG utilizado",
        dia_semana="Dia da semana da mesa",
        frequencia="Frequência da mesa (ex: semanal, quinzenal, mensal)"
    )
    async def registrar_mesa(
        self,
        interaction: discord.Interaction,
        mestre: discord.Member,
        nome: str,
        sistema: str,
        dia_semana: str,
        frequencia: str
    ):
        if not self.utils.check_admin(interaction.user, self.admin_roles):
            await interaction.response.send_message("Você não tem permissão para recarregar os comandos", ephemeral=True)
            return

        mesas_path = "mesas.json"
        try:
            with open(mesas_path, "r", encoding="utf-8") as f:
                mesas = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            mesas = []

        novo_id = 1 if not mesas else mesas[-1]["id"] + 1
        nova_mesa = {
            "id": novo_id,
            "mestre": mestre.display_name,
            "nome": nome,
            "mestre_id": mestre.id,
            "sistema": sistema,
            "dia_semana": dia_semana,
            "frequencia": frequencia
        }
        mesas.append(nova_mesa)
        with open(mesas_path, "w", encoding="utf-8") as f:
            json.dump(mesas, f, ensure_ascii=False, indent=2)

        await interaction.response.send_message(
            f"Mesa registrada com sucesso! ID: {novo_id}\n"
            f"Mestre: {mestre.mention}\n"
            f"Nome: {nome}\n"
            f"Sistema: {sistema}\n"
            f"Dia da semana: {dia_semana}\n"
            f"Frequência: {frequencia}"
        )

    @app_commands.describe(
        nome="Nome do assinante",
        email="Email do assinante",
        celular="Celular do assinante",
        mesas="IDs das mesas que o assinante participa (separados por vírgula)",
        ultimo_mes_pago="Último mês pago (ex: 2025-06)",
        forma_pagamento="Forma de pagamento (ex: cartão, pix, boleto)"
    )
    async def registrar_assinante(
        self,
        interaction: discord.Interaction,
        nome: str,
        email: str,
        celular: str,
        mesas: str,
        ultimo_mes_pago: str,
        forma_pagamento: str
    ):
        if not self.utils.check_admin(interaction.user, self.admin_roles):
            await interaction.response.send_message("Você não tem permissão para registrar assinantes", ephemeral=True)
            return

        assinantes_path = "assinantes.json"
        try:
            with open(assinantes_path, "r", encoding="utf-8") as f:
                assinantes = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            assinantes = []

        # Converte a string de mesas para lista de inteiros
        mesas_ids = [int(m.strip()) for m in mesas.split(",") if m.strip().isdigit()]

        novo_id = 1 if not assinantes else assinantes[-1]["id"] + 1
        novo_assinante = {
            "id": novo_id,
            "nome": nome,
            "email": email,
            "celular": celular,
            "mesas": mesas_ids,
            "ultimo_mes_pago": ultimo_mes_pago,
            "forma_pagamento": forma_pagamento
        }
        assinantes.append(novo_assinante)
        with open(assinantes_path, "w", encoding="utf-8") as f:
            json.dump(assinantes, f, ensure_ascii=False, indent=2)

        await interaction.response.send_message(
            f"Assinante registrado com sucesso! ID: {novo_id}\n"
            f"Nome: {nome}\n"
            f"Email: {email}\n"
            f"Celular: {celular}\n"
            f"Mesas: {', '.join(map(str, mesas_ids))}\n"
            f"Último mês pago: {ultimo_mes_pago}\n"
            f"Forma de pagamento: {forma_pagamento}"
        )

    @app_commands.describe(
        assinante_id="ID do assinante para consulta"
    )
    async def consultar_assinante(
        self,
        interaction: discord.Interaction,
        assinante_id: int
    ):
        if not self.utils.check_admin(interaction.user, self.admin_roles):
            await interaction.response.send_message("Você não tem permissão para consultar assinantes", ephemeral=True)
            return

        assinantes_path = "assinantes.json"
        mesas_path = "mesas.json"

        # Busca assinante
        try:
            with open(assinantes_path, "r", encoding="utf-8") as f:
                assinantes = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            await interaction.response.send_message("Nenhum assinante cadastrado.", ephemeral=True)
            return

        assinante = next((a for a in assinantes if a["id"] == assinante_id), None)
        if not assinante:
            await interaction.response.send_message(f"Assinante com ID {assinante_id} não encontrado.", ephemeral=True)
            return

        # Busca mesas
        try:
            with open(mesas_path, "r", encoding="utf-8") as f:
                mesas = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            mesas = []

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
            f"**Forma de pagamento:** {assinante.get('forma_pagamento', '-')}\n\n"
            f"**Mesas** {mesas_info}"
        )

        await interaction.response.send_message(msg)

    @app_commands.describe()
    async def assinaturas_atrasadas(
        self,
        interaction: discord.Interaction
    ):
        if not self.utils.check_admin(interaction.user, self.admin_roles):
            await interaction.response.send_message("Você não tem permissão para consultar assinaturas", ephemeral=True)
            return

        await interaction.response.defer()  # Defer pois pode demorar

        try:
            summary = self.hotmart_api.get_delayed_subscriptions()
            if summary:
                # Discord tem limite de 2000 caracteres por mensagem
                if len(summary) > 2000:
                    # Dividir em múltiplas mensagens
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

    def verificar_atraso_local(self, ultimo_mes_pago):
        """
        Verifica se um assinante está em atraso baseado no ultimo_mes_pago.
        Formato esperado: "DD/MM/YYYY" ou "DD/MM/YYYY" ou variações.
        """
        try:
            # Parse da data do último pagamento
            data_pagamento = parser.parse(ultimo_mes_pago, dayfirst=True)

            # Calcula o próximo vencimento (mesmo dia do mês seguinte)
            if data_pagamento.month == 12:
                proximo_vencimento = data_pagamento.replace(year=data_pagamento.year + 1, month=1)
            else:
                try:
                    proximo_vencimento = data_pagamento.replace(month=data_pagamento.month + 1)
                except ValueError:  # Caso do dia 31 em mês com 30 dias
                    proximo_vencimento = data_pagamento.replace(month=data_pagamento.month + 1, day=30)

            # Verifica se já passou do vencimento
            hoje = datetime.datetime.now()
            return hoje > proximo_vencimento
        except:
            return False  # Se não conseguir parsear, considera não atrasado

    @app_commands.describe()
    async def assinantes_locais_atrasados(
        self,
        interaction: discord.Interaction
    ):
        if not self.utils.check_admin(interaction.user, self.admin_roles):
            await interaction.response.send_message("Você não tem permissão para consultar assinantes", ephemeral=True)
            return

        await interaction.response.defer()

        try:
            # Carrega os dados locais
            with open("mdl_2.json", "r", encoding="utf-8") as f:
                assinantes_locais = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            await interaction.followup.send("Arquivo mdl_2.json não encontrado ou com erro.")
            return

        # Filtra assinantes em atraso
        assinantes_atrasados = []
        for assinante in assinantes_locais:
            ultimo_mes_pago = assinante.get("ultimo_mes_pago", "")
            if self.verificar_atraso_local(ultimo_mes_pago):
                assinantes_atrasados.append(assinante)

        # Monta o resumo
        total_atrasados = len(assinantes_atrasados)

        summary = f"**Resumo de Assinantes Locais em Atraso**\n"
        summary += f"**Total de assinantes atrasados:** {total_atrasados}\n\n"

        if total_atrasados == 0:
            summary += "Nenhum assinante local em atraso encontrado."
        else:
            # Agrupa por valor para facilitar visualização
            valores_summary = {}
            total_value = 0

            for assinante in assinantes_atrasados:
                valor_str = assinante.get("valor", "R$ 0,00")
                # Remove R$ e converte vírgula para ponto
                valor_limpo = valor_str.replace("R$ ", "").replace(".", "").replace(",", ".")
                try:
                    valor = float(valor_limpo)
                except:
                    valor = 0

                total_value += valor

                if valor_str not in valores_summary:
                    valores_summary[valor_str] = {
                        "count": 0,
                        "valor_numerico": valor,
                        "subscribers": []
                    }

                valores_summary[valor_str]["count"] += 1
                valores_summary[valor_str]["subscribers"].append({
                    "name": assinante.get("nome", "N/A"),
                    "celular": assinante.get("celular", "N/A"),
                    "ultimo_pagamento": assinante.get("ultimo_mes_pago", "N/A")
                })

            # Monta o resumo por valores
            summary += "**Por Valores:**\n"
            for valor_str, info in sorted(valores_summary.items(), key=lambda x: x[1]["valor_numerico"], reverse=True):
                plan_total = info["valor_numerico"] * info["count"]
                summary += f"• {valor_str}: {info['count']} assinantes (Total: R$ {plan_total:.2f})\n"

            summary += f"\n**Valor total em atraso:** R$ {total_value:.2f}\n"

            # Lista todos os assinantes atrasados
            summary += "\n**Todos os assinantes em atraso:**\n"
            for assinante in assinantes_atrasados:
                nome = assinante.get("nome", "N/A")
                celular = assinante.get("celular", "N/A")
                valor = assinante.get("valor", "N/A")
                ultimo_pagamento = assinante.get("ultimo_mes_pago", "N/A")
                summary += f"• {nome} ({celular}) - {valor} - Último pagamento: {ultimo_pagamento}\n"

        # Envia a resposta (dividindo se necessário)
        if len(summary) > 2000:
            chunks = [summary[i:i+2000] for i in range(0, len(summary), 2000)]
            await interaction.followup.send(chunks[0])
            for chunk in chunks[1:]:
                await interaction.followup.send(chunk)
        else:
            await interaction.followup.send(summary)
