from .base_command import BaseCommand
from ..services.mesa_service import MesaService
import discord
from discord import app_commands

class MesaCommands(BaseCommand):
    def __init__(self, utils, admin_roles):
        super().__init__(utils, admin_roles)
        self.mesa_service = MesaService()

    def register_commands(self, tree: app_commands.CommandTree):
        tree.command(description="Registrar uma nova mesa")(self.registrar_mesa)
        tree.command(description="Consultar todas as mesas cadastradas")(self.consultar_mesas)
        tree.command(description="Consultar uma mesa específica por ID")(self.consultar_mesa_id)
        tree.command(description="Editar informações de uma mesa")(self.editar_mesa)

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
        if not self.check_admin(interaction.user):
            await interaction.response.send_message("Você não tem permissão para registrar mesas", ephemeral=True)
            return

        nova_mesa = self.mesa_service.criar_mesa(
            mestre.display_name, mestre.id, nome, sistema, dia_semana, frequencia
        )

        await interaction.response.send_message(
            f"Mesa registrada com sucesso! ID: {nova_mesa['id']}\n"
            f"Mestre: {mestre.mention}\n"
            f"Nome: {nome}\n"
            f"Sistema: {sistema}\n"
            f"Dia da semana: {dia_semana}\n"
            f"Frequência: {frequencia}"
        )

    @app_commands.describe()
    async def consultar_mesas(self, interaction: discord.Interaction):
        if not self.check_admin(interaction.user):
            await interaction.response.send_message("Você não tem permissão para consultar mesas", ephemeral=True)
            return

        await interaction.response.defer()

        mesas = self.mesa_service.carregar_mesas()
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

    @app_commands.describe(mesa_id="ID da mesa para consulta")
    async def consultar_mesa_id(self, interaction: discord.Interaction, mesa_id: int):
        if not self.check_admin(interaction.user):
            await interaction.response.send_message("Você não tem permissão para consultar mesas", ephemeral=True)
            return

        mesa = self.mesa_service.buscar_por_id(mesa_id)
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
        if not self.check_admin(interaction.user):
            await interaction.response.send_message("Você não tem permissão para editar mesas", ephemeral=True)
            return

        updates = {}
        alteracoes = []

        if mestre is not None:
            updates["mestre"] = mestre.display_name
            updates["mestre_id"] = mestre.id
            alteracoes.append(f"Mestre: {mestre.mention}")

        if nome is not None:
            updates["nome"] = nome
            alteracoes.append(f"Nome: {nome}")

        if sistema is not None:
            updates["sistema"] = sistema
            alteracoes.append(f"Sistema: {sistema}")

        if dia_semana is not None:
            updates["dia_semana"] = dia_semana
            alteracoes.append(f"Dia da semana: {dia_semana}")

        if frequencia is not None:
            updates["frequencia"] = frequencia
            alteracoes.append(f"Frequência: {frequencia}")

        if not alteracoes:
            await interaction.response.send_message("Nenhuma alteração foi especificada.", ephemeral=True)
            return

        mesa_atualizada = self.mesa_service.atualizar_mesa(mesa_id, **updates)
        if not mesa_atualizada:
            await interaction.response.send_message(f"Mesa com ID {mesa_id} não encontrada.", ephemeral=True)
            return

        alteracoes_str = "\n".join(alteracoes)
        await interaction.response.send_message(
            f"Mesa ID {mesa_id} editada com sucesso!\n\n"
            f"**Alterações realizadas:**\n{alteracoes_str}"
        )
