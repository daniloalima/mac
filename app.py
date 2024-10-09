import logging
from modules.client_handler import Client
from modules.command_handler import Commands

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    client_instance = Client()
    client_data = client_instance.get_client_data()
    client_instance = client_data['client']
    commands = Commands(client_data['tree'], client_data['client'])
    logger.info("instancia de comandos iniciada")
    client_instance.run(client_data['token'])