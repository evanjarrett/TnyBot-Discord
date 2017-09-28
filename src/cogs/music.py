import asyncio
from random import shuffle

import discord
from discord import Member
from discord import Message
from discord.ext import commands

from src.cogs import BaseCog

    @commands.command(no_pm=true)
    async def thot(self, channel, member: discord.Member)
        """Tells weather a user is a thot or not"""
        choices = ["{0.name} is a thot".format(member)),
                   "{0.name} is not a thot".format(member)),
                   ]
        return await self.bot.say(random.choice(choices)) 

def setup(bot, kwargs):
    bot.add_cog(Thot(bot))
