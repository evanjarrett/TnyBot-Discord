import sqlite3

from discord import Member
from discord.ext import commands


class Stats:
    _db_file = "res/stats.db"

    def __init__(self, bot, tz="UTC"):
        self.bot = bot
        self.tz = tz
        self.connection = sqlite3.connect(self._db_file)
        self.connection.execute(
            '''CREATE TABLE IF NOT EXISTS stats
            (user_id INT PRIMARY KEY NOT NULL,
            server_id       INT      NOT NULL,
            message_count   TEXT     NOT NULL DEFAULT 0,
            command_count   INT      NOT NULL DEFAULT 0)''')

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.connection is not None:
            print("closing the connection")
            self.connection.close()

    async def on_ready(self):
        print("listening in another class " + __name__)

    async def on_message(self, message):
        user_id = message.author.id
        server_id = message.server.id
        if server_id != "169697176149164032":
            return
        sub_query = "COALESCE(((SELECT message_count FROM stats WHERE user_id = {} and server_id = {}) + 1),1)".format(
            user_id,
            server_id
        )
        query = "INSERT OR REPLACE INTO stats (user_id,server_id,message_count) VALUES ({}, '{}', {})".format(
            user_id,
            server_id,
            sub_query
        )
        print(query)
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

