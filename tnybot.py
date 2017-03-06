import configparser
import os

from discord.ext import commands as cmds

from src.basicbot import BasicBot

config = configparser.RawConfigParser()
config_file = os.path.dirname(os.path.realpath(__file__)) + "/../tnybot_config"
config.read(config_file)

tnybot = BasicBot(name="TnyBot", command_prefix=cmds.when_mentioned_or("#!"))

# Tuple of the path to the cog file, and the extra args it takes
cogs = [
    ("cogs.commands", {}),
    ("cogs.custom_commands", {}),
    ("cogs.greetings", {}),
    ("cogs.logs", {}),
    ("cogs.music", {}),
    ("cogs.notifications", {"config_file": config_file}),
    ("cogs.reaction", {}),
    ("cogs.reminders", {"tz": config["TimeZone"]["tz"]}),
    ("cogs.vlive", {}),
]

tnybot.load_cogs(cogs)

tnybot.run(config["User"]["user"], config["User"]["pass"])
