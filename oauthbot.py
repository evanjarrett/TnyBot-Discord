import configparser
import os

from discord.ext import commands as cmds

from src.basicbot import BasicBot
from src.cogs import *

config = configparser.RawConfigParser()
config_file = os.path.dirname(os.path.realpath(__file__)) + "/../tnybot_config"
config.read(config_file)


oauthbot = BasicBot(command_prefix=cmds.when_mentioned_or("!"))

oauthbot.add_cog(Reaction(oauthbot))
oauthbot.add_cog(Commands(oauthbot))
oauthbot.add_cog(CustomCommands(oauthbot))
oauthbot.add_cog(Greetings(oauthbot))
oauthbot.add_cog(Grep(oauthbot))
oauthbot.add_cog(Logs(oauthbot))
oauthbot.add_cog(Stats(oauthbot))
oauthbot.add_cog(Notifications(oauthbot, config_file=config_file))
# oauthbot.add_cog(Roles(oauthbot, db_url=config["Postgres"]["URL"]))
oauthbot.add_cog(Reminders(oauthbot, config["TimeZone"]["tz"]))
oauthbot.run(config["OAuth"]["token"])
