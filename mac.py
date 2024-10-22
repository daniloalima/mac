import logging
from dotenv import load_dotenv
from modules.client_handler import Client
from modules.command_handler import Commands

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO, datefmt='%m/%d/%Y %I:%M:%S')
logger = logging.getLogger(__name__)
load_dotenv()

if __name__ == "__main__":
    client_instance = Client()
    client_data = client_instance.get_client_data()
    client_instance = client_data['client']
    commands = Commands(client_data['tree'], client_data['client'])
    logger.info("instancia de comandos iniciada")
    client_instance.run(client_data['token'])