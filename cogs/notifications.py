import re

import discord
from discord.ext import commands

from utils.config import Config


class Notifications:
    notification_file = "res/notifications.txt"  # txt because Windows is dumb
    notification_section = "Notifications"
    undo_list = {}

    # TODO: make config
    ignore_list = ["131723417060638721"]

    def __init__(self, bot):
        self.bot = bot
        self.config = Config(self.notification_file, self.notification_section)

    async def on_ready(self):
        print("listening in another class " + __name__)
        await self.bot.change_status(game=discord.Game(name="Notification Bot"))

    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        if message.author.id in self.ignore_list:
            return

        if self.bot.is_prefixed(message, message.content):
            return

        content = message.content
        server = message.server
        # foreach notification
        for n in self.config.get_all():
            search = re.search(n, content, re.IGNORECASE)
            if search is not None:
                search = search.group(0)
                # notification matched
                # foreach user listening to that notification
                for user_id in self.config.get_as_list(n):
                    user = server.get_member(user_id)
                    await self._send_message(user, message, search)

    async def on_message_pinned(self, message):
        server = message.server
        for user_id in self.config.get_as_list("pinnedMessages"):
            user = server.get_member(user_id)
            await self._send_message(user, message, is_pinned=True)

    async def on_pin_removed(self, message):
        pass

    @commands.command(aliases=["notification"], pass_context=True)
    async def notify(self, ctx, notification=None):
        """Adds a new notification. You will get a PM when this keyword is mentioned.
            Also supports some basic regex.
        """
        self.config.append(notification, ctx.message.author.id)
        await self.bot.say("Ok, I will notify you when `{}` is mentioned".format(notification))

    @commands.command(aliases=["notifyPinned"], pass_context=True)
    async def notify_pinned(self, ctx):
        """Adds a notification for when a message is pinned
        """
        self.config.append("pinnedMessages", ctx.message.author.id)
        await self.bot.say("Ok, I will notify you when a message is pinned")

    @commands.command(aliases=["deletenotification"], pass_context=True)
    async def delnotify(self, ctx, notification=None):
        """Deletes a notification. This can be used in conjunction with the notifications command"""
        self.config.truncate(notification, ctx.message.author.id)
        await self.bot.say("Ok, I will no longer notify you when `{}` is mentioned".format(notification))

    @commands.command(pass_context=True)
    async def notifications(self, ctx):
        """Sends you a PM with a list of notifications"""
        notify_list = []
        user = ctx.message.author
        for i, n in enumerate(self.config.get_all()):
            if self.config.contains(n, user.id):
                notify_list.append("{0}. {1}".format(i, n))
        message = "\n".join(notify_list)
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
            await self.bot.send_message(user,
                '`{0.timestamp} - {0.author.name} mentioned {1} in {0.server.name} | #{0.channel.name}:` {0.content}'
                    .format(message, search))
