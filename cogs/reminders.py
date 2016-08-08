import asyncio
import sqlite3
import time

from discord.ext import commands


class Reminders:
    _db_file = "res/reminders.db"

    def __init__(self, bot):
        self.bot = bot

        self.connection = sqlite3.connect(self._db_file)
        self.connection.execute(
            '''CREATE TABLE IF NOT EXISTS reminders
            (id         INT PRIMARY KEY NOT NULL,
            user_id     INT             NOT NULL,
            message     TEXT            NOT NULL,
            remind_date INT             NOT NULL
        )''')
        self.connection.close()

    async def on_ready(self):
        print("listening in another class " + __name__)
        while True:
            await self.check_db()
            await asyncio.sleep(60)

    async def on_message(self, message):
        pass

    @commands.command(aliases=["reminder", "remind"], pass_context=True)
    async def remindme(self, ctx, date, message):
        """Creates a reminder. You will receive a PM when the reminder is done."""
        await self.bot.say("Ok I will message you about '{}' on {}".format(message, date))
        await self.save(ctx.message.author.id, date, message)
        pass

    async def save(self, user_id, date, message):
        self.connection.execute(
            "INSERT INTO reminders (user_id,message,remind_date) VALUES ({}, {}, {}".format(
                user_id,
                date,
                message
            )
        )
        self.connection.commit()
        self.connection.close()

    async def check_db(self):
        cursor = self.connection.execute(
            "SELECT id, user_id, message, reminder_date FROM reminders where remind_date <= {}".format(time.time()))
        for row in cursor:
            print("id " + row[0])
            print("user " + row[1])
            print("message " + row[2])
            print("date " + row[3])

        self.connection.commit()
        self.connection.close()
