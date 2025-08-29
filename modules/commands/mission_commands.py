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
        rank="Dificuldade da missão",
        titulo_missao="O nome da sua aventura",
        resumo="Uma sinopse da missão",
        data_hora="Quando a aventura será narrada (ex: 24/08 17:00)",
    )
    async def mission_create(
        self,
        interaction: discord.Interaction,
        mestre: discord.Member,
        rank: Literal[
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

    @app_commands.describe(rank="Dificuldade da missão")
    async def mission_success(
        self,
        interaction: discord.Interaction,
        rank: Literal[
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

    @app_commands.describe(rank="Dificuldade da missão")
    async def mission_failed(
        self,
        interaction: discord.Interaction,
        rank: Literal[
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
