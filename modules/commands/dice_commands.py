from .base_command import BaseCommand
from ..embed_handler import Embed
import discord
from discord import app_commands

class DiceCommands(BaseCommand):
    def __init__(self, utils, admin_roles, embed):
        super().__init__(utils, admin_roles)
        self.embed = embed
    
    def register_commands(self, tree: app_commands.CommandTree):
        tree.command(description="Rolar dados")(self.roll_parabellum)
    
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
