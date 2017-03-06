import asyncio
import re
import time

import discord
from discord.ext import commands
from parsedatetime import parsedatetime
from pytz import timezone

from src.cogs import BaseDBCog
from src.database import RemindersDB


class Reminders(BaseDBCog):
    def __init__(self, bot, tz="UTC", db_file="res/reminders.db", db_url=None):
        super().__init__(bot, RemindersDB(db_file, db_url))
        self.tz = tz

    async def on_ready(self):
        await super().on_ready()
        # The checks are done by a cron that runs reminderbot.py
        if self.bot.name == "ReminderBot":
            await self.check_db()
            await asyncio.sleep(10)
            await self.bot.logout()

    @commands.command(aliases=["reminder", "remind"], pass_context=True)
    async def remindme(self, ctx, *, date):
        """ Creates a reminder. You will receive a PM when the reminder is done.
            The message you want to be reminded of should be in "quotes"

            examples: !remindme 5 min "about this thing"
                      !remindme "about this thing" 1 hour
        """
        message = self.get_quoted_message(ctx)
        date = date.split("\"")[0]

        cal = parsedatetime.Calendar()
        dt = cal.parseDT(datetimeString=date, tzinfo=timezone(self.tz))[0]
        dt = dt.astimezone(timezone('UTC'))
        date = dt.timestamp()
        await self.bot.say(
            "Ok I will message you about '{}' on {}".format(message, dt.strftime('%Y-%m-%d %H:%M:%S %Z')))
        await self.database.insert(ctx.message.author, message, date)

    async def check_db(self):
        dt = time.time()
        for user_id, message, date in await self.database.get(dt):
            user = None
            for server in self.bot.servers:
                user = server.get_member(str(user_id))
                if isinstance(user, discord.User):
                    break
            await self.bot.send_message(user,
                "Hey you told me to remind you about `{}` at this time.".format(message))
        await self.database.delete(dt)

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


def setup(bot, kwargs):
    bot.add_cog(Reminders(bot, **kwargs))
