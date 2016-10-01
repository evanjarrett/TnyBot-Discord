import asyncio
import random

import discord
from discord.ext import commands


class Setup:
    def __init__(self, bot):
        self.bot = bot

    async def on_ready(self):
        print("listening in another class " + __name__)
