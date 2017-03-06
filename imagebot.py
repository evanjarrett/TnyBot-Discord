import configparser
import os

from src.basicbot import BasicBot

config = configparser.RawConfigParser()
config_file = os.path.dirname(os.path.realpath(__file__)) + "/../tnybot_config"
config.read(config_file)

imagebot = BasicBot(name="ImageBot",
    command_prefix="##########",
    description="Fetches any attachments uploaded to discord"
)

# Tuple of the path to the cog file, and the extra args it takes
cogs = [
    ("cogs.attachments", {"config_file": config_file}),
]

imagebot.load_cogs(cogs)

imagebot.run(config["User2"]["user"], config["User2"]["pass"])
