from .base_command import BaseCommand
from ..hotmart_handler import HotmartAPI
from ..embed_handler import Embed
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
        self.tree = None  # Será definido no register_commands
    
    def register_commands(self, tree: app_commands.CommandTree):
        self.tree = tree  # Armazena referência do tree
        tree.command(description="Sincronizar comandos e verificar latência")(self.sync_and_ping)
        tree.command(description="Checar funcionalidades disponíveis")(self.feature_check)
        tree.command(description="Consultar assinaturas atrasadas no Hotmart")(self.assinaturas_atrasadas)
    
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
