import configparser
import os

from src.basicbot import BasicBot
from src.cogs import Reminders
config = configparser.RawConfigParser()
config_file = os.path.dirname(os.path.realpath(__file__)) + "/../tnybot_config"
config.read(config_file)

tnybot = BasicBot(name="ReminderBot",
    command_prefix="##########",
    description="Runs reminder notifications"
)
tnybot.add_cog(Reminders(tnybot, config["TimeZone"]["tz"]))
tnybot.run(config["User"]["user"], config["User"]["pass"])
