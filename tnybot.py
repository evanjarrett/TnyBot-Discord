import configparser

from basicbot import BasicBot
from cogs import Commands, CustomCommands, Notifications, Grep, Reminders, Stats

config = configparser.RawConfigParser()
config.read("../tnybot_config")

tnybot = BasicBot()

tnybot.add_cog(Commands(tnybot))
tnybot.add_cog(CustomCommands(tnybot))
tnybot.add_cog(Notifications(tnybot))
tnybot.add_cog(Grep(tnybot))
tnybot.add_cog(Stats(tnybot))
tnybot.add_cog(Reminders(tnybot, config["TimeZone"]))

tnybot.run(config["User"]["user"], config["User"]["pass"])
