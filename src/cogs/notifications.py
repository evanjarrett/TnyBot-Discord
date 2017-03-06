import configparser
import re

import discord
from discord.ext import commands

from src.cogs import BaseDBCog
from src.database import NotificationsDB


class Notifications(BaseDBCog):
    ignore_list = []

    def __init__(self, bot, *, config_file=None, db_file="res/notifications.db", db_url=None):
        super().__init__(bot, NotificationsDB(db_file, db_url))

        if config_file is not None:
            config = configparser.RawConfigParser()
            config.read(config_file)
            ignore_config = config.items("Ignore")
            # Ignore List is in name = id format, but we only need the id
            for c in ignore_config:
                self.ignore_list.append(c[1])

    async def on_ready(self):
        await super().on_ready()
        await self.bot.change_presence(game=discord.Game(name="Notification Bot"))

    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        if message.author.id in self.ignore_list:
            return

        if await self.bot.is_prefixed(message):
            return

        content = message.content
        server = message.server
        # foreach notification
        for (n,) in await self.database.get_all_notifications():
            search = re.search(n, content, re.IGNORECASE)
            if search is not None:
                search = search.group(0)
                # notification matched
                # foreach user listening to that notification
                for (user_id,) in await self.database.get_users(n):
                    user = server.get_member(str(user_id))
                    await self._send_message(user, message, search)

    async def on_pin_add(self, message):
        server = message.server
        for user_id in await self.database.get_users("pinnedMessages"):
            user = server.get_member(user_id)
            await self._send_message(user, message, is_pinned=True)

    async def on_pin_remove(self, message):
        pass

    @commands.command(aliases=["notification"], pass_context=True)
    async def notify(self, ctx, notification=None):
        """Adds a new notification. You will get a PM when this keyword is mentioned.
            Also supports some basic regex.
        """
        await self.database.insert(ctx.message.author, notification)
        await self.bot.say("Ok, I will notify you when `{}` is mentioned".format(notification))

    @commands.command(aliases=["notifyPinned"], pass_context=True)
    async def notify_pinned(self, ctx):
        """Adds a notification for when a message is pinned
        """
        await self.database.insert(ctx.message.author, "pinnedMessages")
        await self.bot.say("Ok, I will notify you when a message is pinned")

    @commands.command(aliases=["deletenotification"], pass_context=True)
    async def delnotify(self, ctx, notification=None):
        """Deletes a notification. This can be used in conjunction with the notifications command"""
        await self.database.delete(ctx.message.author, notification)
        await self.bot.say("Ok, I will no longer notify you when `{}` is mentioned".format(notification))

    @commands.command(pass_context=True)
    async def notifications(self, ctx):
        """Sends you a PM with a list of notifications"""
        notify_list = []
        user = ctx.message.author
        notifs = await self.database.get_notifications(user)
        for i, (n,) in enumerate(notifs):
            notify_list.append("{0}. {1}".format(i, n))
        message = "\n".join(notify_list)
        if not message:
            await self.bot.send_message(user, "You don't currently have any notifications set.")
        else:
            await self.bot.send_message(user, message)

    async def _send_message(self, user, message, search=None, is_pinned=False):
        if user is None or user == message.author:
            return
        if is_pinned:
            # Until we have a way to know who edited/pinned a message, it will say "Someone"
            await self.bot.send_message(user,
                '`Someone pinned a message by {0.author.name} in {0.server.name} | #{0.channel.name}:` {0.content}'
                    .format(message))
        else:
            time = message.timestamp.now().strftime('%H:%M:%S')
            date = message.timestamp.now().strftime('%Y-%m-%d')
            await self.bot.send_message(user,
                '`{1} {2} - {3} was mentioned in <#{0.channel.name}>`\n'
                'Search Query:\n'
                '```during:{2} from:{0.author} in:{0.channel.name} {0.content}```'
                    .format(message, time, date, search))
