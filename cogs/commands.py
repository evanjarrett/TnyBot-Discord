import asyncio
import random

import discord
from discord.ext import commands


class Commands:
    def __init__(self, bot):
        self.bot = bot

    async def on_ready(self):
        print("listening in another class " + __name__)

    @commands.command(aliases=["hi", "sup", "안녕"])
    async def hello(self):
        """Returns a random hello phrase"""
        choices = ["hi",
                   "ohai",
                   "hello",
                   "안녕",
                   "안녕하세요",
                   "sup",
                   ]
        await self.bot.say(random.choice(choices))

    @commands.command(pass_context=True)
    async def clear(self, ctx, amount=10):
        """Clears chat"""
        messages = self.bot.logs_from(ctx.message.channel, amount)
        count = 0
        async for msg in messages:
            await self.bot.delete_message(msg)
            if count >= 10:
                count = 0
                await asyncio.sleep(1)

    @commands.command(pass_context=True)
    async def playing(self, ctx):
        """Sets now playing status"""
        await self.bot.set_status(ctx.message)

    @commands.command(aliases=["샤샤샤"])
    async def shyshyshy(self):
        """No Sana No Life."""
        await self.bot.upload("res/shyshyshy.gif", content="샤샤샤")

    @commands.command()
    async def joined(self, member: discord.Member):
        """Says when a member joined."""
        await self.bot.say("{0.name} joined in {0.joined_at}".format(member))

    @commands.group(pass_context=True)
    async def cool(self, ctx):
        """Says if a user is cool.
        In reality this just checks if a subcommand is being invoked.
        """
        if ctx.invoked_subcommand is None:
            await self.bot.say("No, {0.subcommand_passed} is not cool".format(ctx))

    @cool.command(name="bot")
    async def _bot(self):
        """Is the bot cool?"""
        await self.bot.say("Yes, the bot is cool.")
