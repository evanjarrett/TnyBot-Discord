from discord.ext import commands

from src.database import postgres
from src.database import sqlite


class Greetings:
    _default_greeting = "Welcome {member}!"

    def __init__(self, bot, *, database_url=None):
        if not database_url:
            self.config_db = sqlite.ConfigDB()
        else:
            self.config_db = postgres.ConfigDB(database_url)
        self.bot = bot

    async def on_ready(self):
        print("listening in another class " + __name__)
        await self.config_db.create_table()

    async def on_message(self, message):
        pass

    async def on_member_join(self, member):
        greeting = await self.config_db.get(member.server, "greeting")
        if greeting is None:
            greeting = self._default_greeting
        await self.bot.send_message(member, greeting.format(member=member.mention))

    @commands.command(pass_context=True)
    @commands.has_permissions(manage_server=True)
    async def greeting(self, ctx, *, greeting):
        """
        Sets the greeting message for this server

        Use {member} to substitute in the member name
        """
        await self.config_db.insert(ctx.server, "greeting", greeting)
        pass

    @commands.command(aliases=["testGreeting"], pass_context=True)
    @commands.has_permissions(manage_server=True)
    async def test_greeting(self, ctx):
        """Tests the greeting message for this server
        """
        greeting = await self.config_db.get(ctx.message.server, "greeting")
        if greeting is None:
            greeting = self._default_greeting
        await self.bot.say(greeting.format(member=ctx.message.author.mention))
