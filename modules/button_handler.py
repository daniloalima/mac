import logging
from typing import List
import discord
logger = logging.getLogger(__name__)

class Buttons(discord.ui.View):
    def __init__(
            self,
            *,
            timeout: float | None = 180,
            max_spots: int = 5,
            mestre: discord.Member,
            log_channel_id: int,
            titulo_missao: str,
            admin_roles: List[int],
            mission_log_channel_id: int
    ):
        self.spots_left = max_spots
        self.clicked_users = set()
        self.mestre = mestre
        self.log_channel_id = log_channel_id
        self.titulo_missao = titulo_missao
        self.admin_roles = admin_roles
        self.mission_log_channel_id = mission_log_channel_id
        super().__init__(timeout=timeout)

    @discord.ui.button(label="Entrar",style=discord.ButtonStyle.green)
    async def submit_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id in self.clicked_users:
            await interaction.response.send_message(f'Você já entrou na mesa **{self.titulo_missao}**!', ephemeral=True)
            return
        elif interaction.user.id == self.mestre.id:
            await interaction.response.send_message(f'Você não pode ser jogador na sua própria mesa **{self.titulo_missao}**!', ephemeral=True)
            return

        self.clicked_users.add(interaction.user.id)
        self.spots_left -= 1

        button.label = f"Vagas restantes: {self.spots_left}"
        if self.spots_left <= 0:
            button.label = "Vagas esgotadas"
            button.disabled = True
            button.style = discord.ButtonStyle.danger

        if self.log_channel_id:
            try:
                log_channel = interaction.guild.get_channel(self.log_channel_id)
                await log_channel.send(f'O jogador {interaction.user.mention} **ENTROU** na mesa **{self.titulo_missao}** do mestre {self.mestre.mention}')
            except:
                logger.warning("falha ao mandar log para o canal")

        await interaction.response.edit_message(view=self)

    @discord.ui.button(label="Sair", style=discord.ButtonStyle.red)
    async def leave_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id not in self.clicked_users:
            await interaction.response.send_message(f'Você não está participando da mesa **{self.titulo_missao}**.', ephemeral=True)
            return

        self.clicked_users.remove(interaction.user.id)
        self.spots_left += 1

        self.children[0].label = f"Vagas restantes: {self.spots_left}"
        self.children[0].disabled = False
        self.children[0].style = discord.ButtonStyle.green

        if self.log_channel_id:
            try:
                log_channel = interaction.guild.get_channel(self.log_channel_id)
                await log_channel.send(f'O jogador {interaction.user.mention} **SAIU** da mesa **{self.titulo_missao}** do mestre {self.mestre.mention}')
            except:
                logger.warning("falha ao mandar log para o canal")

        await interaction.response.edit_message(view=self)

    @discord.ui.button(label="Fechar mesa", style=discord.ButtonStyle.gray)
    async def close_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_is_admin = False

        for role in interaction.user.roles:
            if role.id in self.admin_roles:
                user_is_admin = True

        if interaction.user.id == self.mestre.id or user_is_admin:
            for item in self.children:
                item.disabled = True
                item.label = "Mesa fechada"
            await interaction.response.edit_message(view=self)
            if self.log_channel_id:
                try:
                    log_channel = interaction.guild.get_channel(self.log_channel_id)
                    await log_channel.send(f'A mesa **{self.titulo_missao}** foi fechada por {interaction.user.mention}.')
                except:
                    logger.warning("falha ao mandar log para o canal")
        else:
            await interaction.response.send_message(f'Você não tem permissão para fechar a mesa **{self.titulo_missao}**!', ephemeral=True)
