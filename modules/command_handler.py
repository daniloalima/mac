import logging
from typing import List, Literal
import discord,os
from discord.ext.commands import Greedy
from dotenv import load_dotenv
from discord import app_commands
from .embed_handler import Embed
from .button_handler import Buttons
from .utils import Utils
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

        self.tree.command()(self.sync_and_ping)
        self.tree.command(description="Criar uma missão no quadro")(self.mission_create)
        self.tree.command(description="Rolar dados")(self.roll_parabellum)
        self.tree.command(description="Checar funcionalidades disponíveis")(self.feature_check)
        self.tree.command(description="Registrar sucesso de missão")(self.mission_success)
        self.tree.command(description="Registrar falha de missão")(self.mission_failed)

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
