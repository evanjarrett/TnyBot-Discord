import asyncio
import re
import time

import discord
from discord.ext import commands
from parsedatetime import parsedatetime
from pytz import timezone

from database import postgres, sqlite


class Reminders:
    def __init__(self, bot, tz="UTC", database_url=None):
        self.bot = bot
        self.tz = tz
        if not database_url:
            self.reminder_db = sqlite.RemindersDB()
        else:
            self.reminder_db = postgres.RemindersDB(database_url)
        self.bot.loop.create_task(self.background())

    async def background(self):
        await self.bot.wait_until_ready()
        # We want to run this in a separate process, since on_ready could be called multiple times
        while not self.bot.is_closed:
            await self.check_db()
            await asyncio.sleep(60)

    async def on_ready(self):
        print("listening in another class " + __name__)
        await self.reminder_db.create_table()

    async def on_message(self, message):
        pass

    @commands.command(aliases=["reminder", "remind"], pass_context=True)
    async def remindme(self, ctx, *, date):
        """Creates a reminder. You will receive a PM when the reminder is done."""
        message = self.get_quoted_message(ctx)
        date = date.split("\"")[0]

        cal = parsedatetime.Calendar()
        dt = cal.parseDT(datetimeString=date, tzinfo=timezone(self.tz))[0]
        date = dt.astimezone(timezone('UTC')).timestamp()
        await self.bot.say("Ok I will message you about '{}' on {}".format(message, date))
        await self.reminder_db.insert(ctx.message.author.id, date, message)

    async def check_db(self):
        dt = time.time()
        for user_id, message, date in await self.reminder_db.get(dt):
            user = None
            for server in self.bot.servers:
                user = server.get_member(str(user_id))
                if isinstance(user, discord.User):
                    break
            await self.bot.send_message(user, "Hey you told me to remind you about `{}` at this time.".format(message))
        await self.reminder_db.delete(dt)

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
