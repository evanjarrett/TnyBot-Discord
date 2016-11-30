
import configparser

from src.cogs import Reminders
from src.basicbot import BasicBot

config = configparser.RawConfigParser()
config_file = "../tnybot_config"
config.read(config_file)

tnybot = BasicBot(name="ReminderBot", command_prefix="####################", description="Runs reminder notifications")
tnybot.add_cog(Reminders(tnybot, config["TimeZone"]["tz"]))
tnybot.run(config["User"]["user"], config["User"]["pass"])
