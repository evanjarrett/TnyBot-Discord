import asyncio
import configparser
import os

from discord.ext import commands


class Reminders:

    def __init__(self, bot):
        self.bot = bot
        self.thisfile = os.path.dirname(os.path.abspath(__file__))

    async def on_ready(self):
        print("listening in another class " + __name__)

    async def on_message(self, message):
        pass

    @commands.command(aliases=["reminder", "remind"], pass_context=True)
    async def remindme(self, ctx):
        """Creates a reminder. You will receive a PM when the reminder is done."""
        pass
