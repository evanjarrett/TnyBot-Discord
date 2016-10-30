from discord.ext.commands import Bot

from src.database import Database


class BaseCog:
    def __init__(self, bot: Bot):
        self.bot = bot

    async def on_ready(self):
        print("loading cog: " + self.__class__.__name__)


class BaseDBCog(BaseCog):
    def __init__(self, bot: Bot, database: Database):
        super().__init__(bot)
        self.database = database

    async def on_ready(self):
        await super().on_ready()
        await self.database.create_table()
