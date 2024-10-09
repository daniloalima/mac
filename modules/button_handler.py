import discord

class JoinButton(discord.ui.View):
    def __init__(self, *, timeout: float | None = 180, max_spots: int = 5):
        self.spots_left = max_spots
        self.clicked_users = set()
        super().__init__(timeout=timeout)

    @discord.ui.button(label="Entrar",style=discord.ButtonStyle.green)
    async def submit_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id in self.clicked_users:
            await interaction.response.send_message("Você já entrou nessa mesa!", ephemeral=True)
            return
        self.clicked_users.add(interaction.user.id)
        self.spots_left -= 1
        
        button.label = f"Vagas restantes: {self.spots_left}"
        if self.spots_left <= 0:
            button.label = "Vagas esgotadas"
            button.disabled = True
            button.style = discord.ButtonStyle.danger
        await interaction.response.edit_message(view=self)