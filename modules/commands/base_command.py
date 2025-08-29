from abc import ABC, abstractmethod
import discord
from discord import app_commands
from typing import List

class BaseCommand(ABC):
    def __init__(self, utils, admin_roles):
        self.utils = utils
        self.admin_roles = admin_roles
    
    def check_admin(self, user: discord.Member) -> bool:
        """Verifica se o usuário é admin"""
        return self.utils.check_admin(user, self.admin_roles)
    
    @abstractmethod
    def register_commands(self, tree: app_commands.CommandTree):
        """Registra os comandos desta categoria"""
        pass
