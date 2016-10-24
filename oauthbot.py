import configparser

from src.basicbot import BasicBot
from src.cogs import Commands, Notifications, Grep, Roles

config = configparser.RawConfigParser()
config_file = "../tnybot_config"
config.read(config_file)

oauthbot = BasicBot(command_prefix="!", description="""Bot built for discord's oauth bot api""")

oauthbot.add_cog(Commands(oauthbot))
oauthbot.add_cog(Notifications(oauthbot, config_file=config_file))
oauthbot.add_cog(Grep(oauthbot))
oauthbot.add_cog(Roles(oauthbot, db_url=config["Postgres"]["URL"]))

oauthbot.run(config["OAuth"]["token"])
