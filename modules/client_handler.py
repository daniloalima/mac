import discord,os
from discord import app_commands


class Client():
    def __init__(self) -> None:
        self.intents = discord.Intents.default()
        self.intents.message_content = True
        self.client = discord.Client(intents=self.intents)
        self.tree = app_commands.CommandTree(self.client)
        self.token = os.environ.get("TOKEN")

    def get_client_data(self):
        return {
            'client': self.client,
            'tree': self.tree,
            'token': self.token
        }