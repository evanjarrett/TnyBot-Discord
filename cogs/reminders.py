import asyncio
import re
import sqlite3
import time

import discord
from discord.ext import commands
from parsedatetime import parsedatetime
from pytz import timezone


class Reminders:
    _db_file = "res/reminders.db"

    def __init__(self, bot, tz="UTC"):
        self.bot = bot
        self.tz = tz

        self.connection = sqlite3.connect(self._db_file)
        self.connection.execute(
            '''CREATE TABLE IF NOT EXISTS reminders
            (user_id    INT     NOT NULL,
            message     TEXT    NOT NULL,
            remind_date INT     NOT NULL)''')
        self.bot.loop.create_task(self.background())

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.connection is not None:
            print("closing the connection")
            self.connection.close()

    async def background(self):
        await self.bot.wait_until_ready()
        # We want to run this in a separate process, since on_ready could be called multiple times
        while not self.bot.is_closed:
            await self.check_db()
            await asyncio.sleep(60)

    async def on_ready(self):
        print("listening in another class " + __name__)

    async def on_message(self, message):
        pass

    @commands.command(aliases=["reminder", "remind"], pass_context=True)
    async def remindme(self, ctx, *, date):
        """Creates a reminder. You will receive a PM when the reminder is done."""
        message = self.get_quoted_message(ctx)
        date = date.split("\"")[0]

        cal = parsedatetime.Calendar()
        # I'm not sure if this TZ needs to be set to where the bot is, or where the user is...
        dt = cal.parseDT(datetimeString=date, tzinfo=timezone(self.tz))[0]
        date = dt.astimezone(timezone('UTC')).timestamp()
        await self.bot.say("Ok I will message you about '{}' on {}".format(message, date))
        await self.save(ctx.message.author.id, date, message)

    async def save(self, user_id, date, message):
        query = "INSERT INTO reminders (user_id,message,remind_date) VALUES ({}, '{}', {})".format(
            user_id,
            message,
            date
        )
        print(query)
        self.connection.execute(query)
        self.connection.commit()

    async def check_db(self):
        dt = time.time()
        # print("checking database {}".format(dt))
        cursor = self.connection.execute(
            "SELECT user_id, message, remind_date FROM reminders WHERE remind_date <= {}".format(dt + 60))
        for user_id, message, date in cursor:
            user = None
            for server in self.bot.servers:
                user = server.get_member(str(user_id))
                if isinstance(user, discord.User):
                    break

            await self.bot.send_message(user, "Hey you told me to remind you about `{}` at this time.".format(message))

        self.connection.execute("DELETE FROM reminders WHERE remind_date <= {}".format(dt + 60))
        self.connection.commit()

    @staticmethod
    def get_quoted_message(ctx):
        msg = ctx.message.content
        regex = re.compile(r"([\"'])((?:\\\1|.)*?)\1")
        match = re.search(regex, msg)
        if match is None:
            msg_str = msg.split()[-1]
        else:
            quote = match.group(1)
            needle = match.group(2)
            msg_str = needle.replace("\\" + quote, quote)

        return msg_str
