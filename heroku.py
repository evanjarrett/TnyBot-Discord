import os

from basicbot import BasicBot
from src.cogs import Commands, Notifications, Grep, Roles

heroku = BasicBot(command_prefix="!", description="""Bot built for discord's oauth bot api""")

heroku.add_cog(Commands(heroku))
heroku.add_cog(Notifications(heroku, database_url=os.environ["DATABASE_URL"]))
heroku.add_cog(Grep(heroku))
heroku.add_cog(Roles(heroku, os.environ["DATABASE_URL"]))

heroku.run(os.environ["TOKEN"])
