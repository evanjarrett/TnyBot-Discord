import configparser

from discord.ext import commands

from basicbot import BasicBot
from src.cogs import Commands, CustomCommands, Notifications, Grep, Reminders, Stats, Logs, Roles
from src.cogs import Greetings

config = configparser.RawConfigParser()
config_file = "../tnybot_config"
config.read(config_file)

tnybot = BasicBot(command_prefix=commands.when_mentioned_or("#!"))

tnybot.add_cog(Commands(tnybot))
tnybot.add_cog(CustomCommands(tnybot))
tnybot.add_cog(Notifications(tnybot, config_file=config_file))
tnybot.add_cog(Grep(tnybot))
tnybot.add_cog(Stats(tnybot))
tnybot.add_cog(Logs(tnybot))
#tnybot.add_cog(Greetings(tnybot))
tnybot.add_cog(Roles(tnybot, config["Postgres"]["URL"]))
tnybot.add_cog(Reminders(tnybot, config["TimeZone"]["tz"]))
tnybot.run(config["User"]["user"], config["User"]["pass"])
