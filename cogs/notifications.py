import re

import discord
from discord.ext import commands

from utils.config import Config


class Notifications:
    notification_file = "res/notifications.txt"  # txt because Windows is dumb
    notification_section = "Notifications"
    undo_list = {}

    def __init__(self, bot):
        self.bot = bot
        self.config = Config(self.notification_file, self.notification_section)

    async def on_ready(self):
        print("listening in another class " + __name__)
        await self.bot.change_status(game=discord.Game(name="Notification Bot"))

    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        if self.bot.is_prefixed(message, message.content):
            return

        content = message.content
        server = message.server
        # foreach notification
        for n in self.config.get_all():
            search = re.search(n, content)
            if search is not None:
                search = search.group(0)
                # notification matched
                # foreach user listening to that notification
                for user_id in self.config.get_as_list(n):
                    user = server.get_member(user_id)
                    if user is not None and user != message.author:
                        await self.bot.send_message(user,
                            '`{} mentioned {} in {} | #{}:` {}'.format(message.author.name, search, message.server.name,
                                message.channel.name, message.content))

    @commands.command(aliases=["notification"], pass_context=True)
    async def notify(self, ctx, notification=None):
        """Adds a new notification. You will get a PM when this keyword is mentioned.
            Also supports some basic regex.
        """
        self.config.append(notification, ctx.message.author.id)
        await self.bot.say("Ok, I will notify you when `{}` is mentioned".format(notification))

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
