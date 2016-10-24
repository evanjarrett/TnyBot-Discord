import configparser

from src.basicbot import BasicBot
from src.cogs import Attachments

config = configparser.RawConfigParser()
config_file = "../tnybot_config"
config.read(config_file)

imagebot = BasicBot(command_prefix="#!", description="""Fetches any attachments uploaded to discord""")
imagebot.add_cog(Attachments(imagebot, config_file))

imagebot.run(config["User2"]["user"], config["User2"]["pass"])
