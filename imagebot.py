import configparser

from basicbot import BasicBot
from cogs import Attachments

config = configparser.RawConfigParser()
config_file = "../tnybot_config"
config.read(config_file)

imagebot = BasicBot(command_prefix="#!", description="""Fetches any attachments uploaded to discord""")
imagebot.add_cog(Attachments(imagebot, config_file))

imagebot.run(config["User"]["user"], config["User"]["pass"])
