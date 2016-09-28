import configparser

from basicbot import BasicBot
from cogs import Commands, Notifications, Grep, Roles

config = configparser.RawConfigParser()
config.read("../tnybot_config")

oauthbot = BasicBot(command_prefix="!", description="""Bot built for discord's oauth bot api""")

oauthbot.add_cog(Commands(oauthbot))
oauthbot.add_cog(Notifications(oauthbot))
oauthbot.add_cog(Grep(oauthbot))
oauthbot.add_cog(Roles(oauthbot, config["Postgres"]["URL"]))

oauthbot.run(config["OAuth"]["token"])
