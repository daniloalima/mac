from typing import Literal
import discord,os
from discord import app_commands
from .embed_handler import mission_embed
from .button_handler import JoinButton


class Commands():
    def __init__(self, tree: app_commands.CommandTree, client: discord.Client) -> None:
        self.tree = tree
        self.client = client

        self.client.event(self.on_ready)
        self.tree.command()(self.reload)
        self.tree.command(description="Criar uma missão no quadro")(self.mission_create)

    async def on_ready(self):
        await self.tree.sync()
        print("commands synced and ready")

    async def reload(self, interaction: discord.Interaction):
        await interaction.response.send_message("reloaded!")

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
    
        await interaction.response.send_message(embed=mission_embed(mestre, rank, titulo_missao, resumo, data_hora), view=JoinButton())
    
