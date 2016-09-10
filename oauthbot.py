import configparser

from basicbot import BasicBot
from cogs import Commands, Notifications, Grep, Stats, Roles

config = configparser.RawConfigParser()
config.read("../tnybot_config")

tnybot = BasicBot()

tnybot.add_cog(Commands(tnybot))
tnybot.add_cog(Notifications(tnybot))
tnybot.add_cog(Grep(tnybot))
tnybot.add_cog(Stats(tnybot))
tnybot.add_cog(Roles(tnybot))

tnybot.run(config["OAuth"]["token"])
