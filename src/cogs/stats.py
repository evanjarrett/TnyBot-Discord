import sqlite3

from discord import Member
from discord.ext import commands

from src.cogs import BaseCog


class Stats(BaseCog):
    _db_file = "res/stats.db"

    def __init__(self, bot):
        super().__init__(bot)
        self.connection = sqlite3.connect(self._db_file)
        self.connection.execute(
            '''CREATE TABLE IF NOT EXISTS stats
            (user_id INT PRIMARY KEY NOT NULL,
            server_id       INT      NOT NULL,
            message_count   INT      NOT NULL DEFAULT 0,
            command_count   INT      NOT NULL DEFAULT 0)''')

    async def on_message(self, message):
        if message.server is None:
            # Ignore PMs
            return
        user_id = message.author.id
        server_id = message.server.id
        sub_query = "COALESCE(((SELECT message_count FROM stats WHERE user_id = {} and server_id = {}) + 1),1)".format(
            user_id,
            server_id
        )
        query = "INSERT OR REPLACE INTO stats (user_id,server_id,message_count) VALUES ({}, '{}', {})".format(
            user_id,
            server_id,
            sub_query
        )
        self.connection.execute(query)
        self.connection.commit()

    @commands.command(pass_context=True)
    async def stats(self, ctx, member: Member):
        user_id = member.id
        server_id = ctx.message.server.id

        query = "SELECT message_count FROM stats WHERE user_id = {} and server_id = {}".format(
            user_id,
            server_id
        )
        cursor = self.connection.execute(query)
        for count in cursor:
            await self.bot.say("{}: {} messages".format(member.mention, count[0]))

