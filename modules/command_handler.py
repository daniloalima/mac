import logging
from typing import List
import discord, os
from dotenv import load_dotenv
from discord import app_commands
from .embed_handler import Embed
from .utils import Utils
from .hotmart_handler import HotmartAPI

# Importar comandos
from .commands.mission_commands import MissionCommands
from .commands.dice_commands import DiceCommands
from .commands.mesa_commands import MesaCommands
from .commands.assinante_commands import AssinanteCommands
from .commands.admin_commands import AdminCommands

logger = logging.getLogger(__name__)

class Commands():
    def __init__(self, tree: app_commands.CommandTree, client: discord.Client) -> None:
        load_dotenv()
        self.tree = tree
        self.client = client

        # Inicializar dependências primeiro
        self.embed = Embed()
        self.utils = Utils()
        self.hotmart_api = HotmartAPI()

        # Depois carregar configurações
        self._load_config()

        self._init_command_categories()

        self.client.event(self.on_ready)

    def _load_config(self):
        """Carrega configurações do ambiente"""
        self.log_channel_id = int(os.environ.get('LOG_CHANNEL_ID'))
        self.mission_log_channel_id = int(os.environ.get('MISSION_LOG_CHANNEL_ID'))
        self.admin_roles = self.utils.convert_to_int_list(os.environ.get('ADMIN_ROLES'))
        self.guild_server_id = int(os.environ.get('GUILD_SERVER_ID'))

    def _init_command_categories(self):
        """Inicializa e registra todas as categorias de comandos"""
        self.mission_commands = MissionCommands(
            self.utils, self.admin_roles, self.embed,
            self.guild_server_id, self.log_channel_id, self.mission_log_channel_id
        )
        self.dice_commands = DiceCommands(self.utils, self.admin_roles, self.embed)
        self.mesa_commands = MesaCommands(self.utils, self.admin_roles)
        self.assinante_commands = AssinanteCommands(self.utils, self.admin_roles)
        self.admin_commands = AdminCommands(
            self.utils, self.admin_roles, self.hotmart_api,
            self.embed, self.guild_server_id, self.client
        )

        # Registrar comandos
        self.mission_commands.register_commands(self.tree)
        self.dice_commands.register_commands(self.tree)
        self.mesa_commands.register_commands(self.tree)
        self.assinante_commands.register_commands(self.tree)
        self.admin_commands.register_commands(self.tree)

    async def on_ready(self):
        logger.info("bot up and running")
