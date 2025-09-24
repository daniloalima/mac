from .base_command import BaseCommand
from ..embed_handler import Embed
from ..button_handler import Buttons
import discord
from discord import app_commands
from typing import Literal
import logging

logger = logging.getLogger(__name__)

class MissionCommands(BaseCommand):
    def __init__(self, utils, admin_roles, embed, guild_server_id, log_channel_id, mission_log_channel_id):
        super().__init__(utils, admin_roles)
        self.embed = embed
        self.guild_server_id = guild_server_id
        self.log_channel_id = log_channel_id
        self.mission_log_channel_id = mission_log_channel_id

    def register_commands(self, tree: app_commands.CommandTree):
        tree.command(description="Criar uma missão no quadro")(self.mission_create)
        tree.command(description="Registrar sucesso de missão")(self.mission_success)
        tree.command(description="Registrar falha de missão")(self.mission_failed)

    @app_commands.describe(
        mestre="Narrador da mesa",
        nivel="Nível da missão (1-20)",
        titulo_missao="O nome da sua aventura",
        resumo="Uma sinopse da missão",
        data_hora="Quando a aventura será narrada (ex: 24/08 17:00)",
    )
    async def mission_create(
        self,
        interaction: discord.Interaction,
        mestre: discord.Member,
        nivel: int,
        titulo_missao: str,
        resumo: str,
        data_hora: str,
    ):
        if interaction.guild.id != self.guild_server_id:
            await interaction.response.send_message("Esse comando só pode ser utilizado no servidor de guilda", ephemeral=True)
            return

        # Validar se o nível está entre 1 e 20
        if nivel < 1 or nivel > 20:
            await interaction.response.send_message("O nível da missão deve estar entre 1 e 20", ephemeral=True)
            return

        await interaction.response.send_message(
            embed=self.embed.mission_embed(mestre, nivel, titulo_missao, resumo, data_hora),
            view=Buttons(
                mestre=mestre,
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

    @app_commands.describe(nivel="Nível da missão (1-20)")
    async def mission_success(
        self,
        interaction: discord.Interaction,
        nivel: Literal[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
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
            embed=self.embed.mission_success_embed(nivel, jogadores)
        )

    @app_commands.describe(nivel="Nível da missão (1-20)")
    async def mission_failed(
        self,
        interaction: discord.Interaction,
        nivel: Literal[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
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
            embed=self.embed.mission_failed_embed(nivel, jogadores)
        )
