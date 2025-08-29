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
        self.tree.command(description="Consultar todas as mesas cadastradas")(self.consultar_mesas)
        self.tree.command(description="Consultar uma mesa específica por ID")(self.consultar_mesa_id)
        self.tree.command(description="Editar informações de uma mesa")(self.editar_mesa)
        self.tree.command(description="Listar todos os assinantes (resumido)")(self.listar_assinantes)
        self.tree.command(description="Editar informações de um assinante")(self.editar_assinante)

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
        if not self.utils.check_admin(interaction.user, self.admin_roles):
            await interaction.response.send_message("Você não tem permissão para registrar assinantes", ephemeral=True)
            return

        assinantes_path = "mdl_2.json"
        try:
            with open(assinantes_path, "r", encoding="utf-8") as f:
                assinantes = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            assinantes = []

        mesas_ids = [int(m.strip()) for m in mesas.split(",") if m.strip().isdigit()] if mesas.strip() else []

        novo_id = 1 if not assinantes else max(a["id"] for a in assinantes) + 1

        novo_assinante = {
            "id": novo_id,
            "nome": nome,
            "email": email if email.strip() else "",
            "celular": celular,
            "mesas": mesas_ids,
            "ultimo_mes_pago": ultimo_mes_pago,
            "forma_pagamento": forma_pagamento,
            "valor": valor
        }
        assinantes.append(novo_assinante)

        with open(assinantes_path, "w", encoding="utf-8") as f:
            json.dump(assinantes, f, ensure_ascii=False, indent=2)

        await interaction.response.send_message(
            f"Assinante registrado com sucesso! ID: {novo_id}\n"
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
        if not self.utils.check_admin(interaction.user, self.admin_roles):
            await interaction.response.send_message("Você não tem permissão para consultar assinantes", ephemeral=True)
            return

        assinantes_path = "mdl_2.json"
        mesas_path = "mesas.json"

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

    def verificar_atraso_local(self, ultimo_mes_pago):
        """
        Verifica se um assinante está em atraso baseado no ultimo_mes_pago.
        Formato esperado: "DD/MM/YYYY" ou "DD/MM/YYYY" ou variações.
        """
        try:
            data_pagamento = parser.parse(ultimo_mes_pago, dayfirst=True)

            if data_pagamento.month == 12:
                proximo_vencimento = data_pagamento.replace(year=data_pagamento.year + 1, month=1)
            else:
                try:
                    proximo_vencimento = data_pagamento.replace(month=data_pagamento.month + 1)
                except ValueError:
                    proximo_vencimento = data_pagamento.replace(month=data_pagamento.month + 1, day=30)

            hoje = datetime.datetime.now()
            return hoje > proximo_vencimento
        except:
            return False

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
            with open("mdl_2.json", "r", encoding="utf-8") as f:
                assinantes_locais = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            await interaction.followup.send("Arquivo mdl_2.json não encontrado ou com erro.")
            return

        assinantes_atrasados = []
        for assinante in assinantes_locais:
            ultimo_mes_pago = assinante.get("ultimo_mes_pago", "")
            if self.verificar_atraso_local(ultimo_mes_pago):
                assinantes_atrasados.append(assinante)

        total_atrasados = len(assinantes_atrasados)

        summary = f"**Resumo de Assinantes Locais em Atraso**\n"
        summary += f"**Total de assinantes atrasados:** {total_atrasados}\n\n"

        if total_atrasados == 0:
            summary += "Nenhum assinante local em atraso encontrado."
        else:
            valores_summary = {}
            total_value = 0

            for assinante in assinantes_atrasados:
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
                        "valor_numerico": valor,
                        "subscribers": []
                    }

                valores_summary[valor_str]["count"] += 1
                valores_summary[valor_str]["subscribers"].append({
                    "name": assinante.get("nome", "N/A"),
                    "celular": assinante.get("celular", "N/A"),
                    "ultimo_pagamento": assinante.get("ultimo_mes_pago", "N/A")
                })

            summary += "**Por Valores:**\n"
            for valor_str, info in sorted(valores_summary.items(), key=lambda x: x[1]["valor_numerico"], reverse=True):
                plan_total = info["valor_numerico"] * info["count"]
                summary += f"• {valor_str}: {info['count']} assinantes (Total: R$ {plan_total:.2f})\n"

            summary += f"\n**Valor total em atraso:** R$ {total_value:.2f}\n"

            summary += "\n**Todos os assinantes em atraso:**\n"
            for assinante in assinantes_atrasados:
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

    @app_commands.describe()
    async def consultar_mesas(
        self,
        interaction: discord.Interaction
    ):
        if not self.utils.check_admin(interaction.user, self.admin_roles):
            await interaction.response.send_message("Você não tem permissão para consultar mesas", ephemeral=True)
            return

        await interaction.response.defer()

        try:
            with open("mesas.json", "r", encoding="utf-8") as f:
                mesas = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            await interaction.followup.send("Arquivo mesas.json não encontrado ou com erro.")
            return

        if not mesas:
            await interaction.followup.send("Nenhuma mesa cadastrada.")
            return

        total_mesas = len(mesas)
        summary = f"**Lista de Todas as Mesas**\n"
        summary += f"**Total de mesas:** {total_mesas}\n\n"

        for mesa in mesas:
            mestre_id = mesa.get("mestre_id", "")
            mestre_mention = f"<@{mestre_id}>" if mestre_id else mesa.get("mestre", "N/A")

            summary += (
                f"**Mesa ID:** {mesa.get('id', 'N/A')}\n"
                f"**Nome:** {mesa.get('nome', 'N/A')}\n"
                f"**Mestre:** {mestre_mention}\n"
                f"**Sistema:** {mesa.get('sistema', 'N/A')}\n"
                f"**Dia da semana:** {mesa.get('dia_semana', 'N/A')}\n"
                f"**Frequência:** {mesa.get('frequencia', 'N/A')}\n"
                f"**━━━━━━━━━━━━━━━━━━━━━━**\n"
            )

        if len(summary) > 2000:
            chunks = [summary[i:i+2000] for i in range(0, len(summary), 2000)]
            await interaction.followup.send(chunks[0])
            for chunk in chunks[1:]:
                await interaction.followup.send(chunk)
        else:
            await interaction.followup.send(summary)

    @app_commands.describe(
        mesa_id="ID da mesa para consulta"
    )
    async def consultar_mesa_id(
        self,
        interaction: discord.Interaction,
        mesa_id: int
    ):
        if not self.utils.check_admin(interaction.user, self.admin_roles):
            await interaction.response.send_message("Você não tem permissão para consultar mesas", ephemeral=True)
            return

        try:
            with open("mesas.json", "r", encoding="utf-8") as f:
                mesas = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            await interaction.response.send_message("Arquivo mesas.json não encontrado ou com erro.", ephemeral=True)
            return

        mesa = next((m for m in mesas if m["id"] == mesa_id), None)
        if not mesa:
            await interaction.response.send_message(f"Mesa com ID {mesa_id} não encontrada.", ephemeral=True)
            return

        mestre_id = mesa.get("mestre_id", "")
        mestre_mention = f"<@{mestre_id}>" if mestre_id else mesa.get("mestre", "N/A")

        msg = (
            f"**Mesa ID:** {mesa.get('id', 'N/A')}\n"
            f"**Nome:** {mesa.get('nome', 'N/A')}\n"
            f"**Mestre:** {mestre_mention}\n"
            f"**Sistema:** {mesa.get('sistema', 'N/A')}\n"
            f"**Dia da semana:** {mesa.get('dia_semana', 'N/A')}\n"
            f"**Frequência:** {mesa.get('frequencia', 'N/A')}"
        )

        await interaction.response.send_message(msg)

    @app_commands.describe(
        mesa_id="ID da mesa a ser editada",
        mestre="Novo mestre da mesa (opcional)",
        nome="Novo nome da mesa (opcional)",
        sistema="Novo sistema da mesa (opcional)",
        dia_semana="Novo dia da semana (opcional)",
        frequencia="Nova frequência (opcional)"
    )
    async def editar_mesa(
        self,
        interaction: discord.Interaction,
        mesa_id: int,
        mestre: discord.Member = None,
        nome: str = None,
        sistema: str = None,
        dia_semana: str = None,
        frequencia: str = None
    ):
        if not self.utils.check_admin(interaction.user, self.admin_roles):
            await interaction.response.send_message("Você não tem permissão para editar mesas", ephemeral=True)
            return

        try:
            with open("mesas.json", "r", encoding="utf-8") as f:
                mesas = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            await interaction.response.send_message("Arquivo mesas.json não encontrado ou com erro.", ephemeral=True)
            return

        mesa_index = None
        for i, mesa in enumerate(mesas):
            if mesa["id"] == mesa_id:
                mesa_index = i
                break

        if mesa_index is None:
            await interaction.response.send_message(f"Mesa com ID {mesa_id} não encontrada.", ephemeral=True)
            return

        mesa_atual = mesas[mesa_index]
        alteracoes = []

        if mestre is not None:
            mesa_atual["mestre"] = mestre.display_name
            mesa_atual["mestre_id"] = mestre.id
            alteracoes.append(f"Mestre: {mestre.mention}")

        if nome is not None:
            mesa_atual["nome"] = nome
            alteracoes.append(f"Nome: {nome}")

        if sistema is not None:
            mesa_atual["sistema"] = sistema
            alteracoes.append(f"Sistema: {sistema}")

        if dia_semana is not None:
            mesa_atual["dia_semana"] = dia_semana
            alteracoes.append(f"Dia da semana: {dia_semana}")

        if frequencia is not None:
            mesa_atual["frequencia"] = frequencia
            alteracoes.append(f"Frequência: {frequencia}")

        if not alteracoes:
            await interaction.response.send_message("Nenhuma alteração foi especificada.", ephemeral=True)
            return

        with open("mesas.json", "w", encoding="utf-8") as f:
            json.dump(mesas, f, ensure_ascii=False, indent=2)

        alteracoes_str = "\n".join(alteracoes)
        await interaction.response.send_message(
            f"Mesa ID {mesa_id} editada com sucesso!\n\n"
            f"**Alterações realizadas:**\n{alteracoes_str}"
        )

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
        if not self.utils.check_admin(interaction.user, self.admin_roles):
            await interaction.response.send_message("Você não tem permissão para editar assinantes", ephemeral=True)
            return

        try:
            with open("mdl_2.json", "r", encoding="utf-8") as f:
                assinantes = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            await interaction.response.send_message("Arquivo mdl_2.json não encontrado ou com erro.", ephemeral=True)
            return

        assinante_index = None
        for i, assinante in enumerate(assinantes):
            if assinante["id"] == assinante_id:
                assinante_index = i
                break

        if assinante_index is None:
            await interaction.response.send_message(f"Assinante com ID {assinante_id} não encontrado.", ephemeral=True)
            return

        assinante_atual = assinantes[assinante_index]
        alteracoes = []

        if nome is not None:
            assinante_atual["nome"] = nome
            alteracoes.append(f"Nome: {nome}")

        if email is not None:
            assinante_atual["email"] = email if email.strip() else ""
            alteracoes.append(f"Email: {email if email.strip() else 'Removido'}")

        if celular is not None:
            assinante_atual["celular"] = celular
            alteracoes.append(f"Celular: {celular}")

        if mesas is not None:
            mesas_ids = [int(m.strip()) for m in mesas.split(",") if m.strip().isdigit()] if mesas.strip() else []
            assinante_atual["mesas"] = mesas_ids
            alteracoes.append(f"Mesas: {', '.join(map(str, mesas_ids)) if mesas_ids else 'Nenhuma'}")

        if ultimo_mes_pago is not None:
            assinante_atual["ultimo_mes_pago"] = ultimo_mes_pago
            alteracoes.append(f"Último mês pago: {ultimo_mes_pago}")

        if forma_pagamento is not None:
            assinante_atual["forma_pagamento"] = forma_pagamento
            alteracoes.append(f"Forma de pagamento: {forma_pagamento}")

        if valor is not None:
            assinante_atual["valor"] = valor
            alteracoes.append(f"Valor: {valor}")

        if not alteracoes:
            await interaction.response.send_message("Nenhuma alteração foi especificada.", ephemeral=True)
            return

        with open("mdl_2.json", "w", encoding="utf-8") as f:
            json.dump(assinantes, f, ensure_ascii=False, indent=2)

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
        if not self.utils.check_admin(interaction.user, self.admin_roles):
            await interaction.response.send_message("Você não tem permissão para consultar assinantes", ephemeral=True)
            return

        await interaction.response.defer()

        try:
            with open("mdl_2.json", "r", encoding="utf-8") as f:
                assinantes = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            await interaction.followup.send("Arquivo mdl_2.json não encontrado ou com erro.")
            return

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
