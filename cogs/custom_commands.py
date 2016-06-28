import configparser
import random

from discord.ext import commands

from utils.config import Config


class CustomCommands:
    commands_file = "res/commands.txt"  # txt because Windows is dumb
    commands_section = "Commands"
    undo_list = {}

    def __init__(self, bot):
        self.bot = bot
        self.config = Config(self.commands_file, self.commands_section)

    async def on_ready(self):
        print("listening in another class " + __name__)

    async def on_message(self, message):
        if not self.bot.is_prefixed(message, message.content):
            return

        name = self.bot.trim_prefix(message, message.content.split()[0])
        if message.author != self.bot.user and name not in self.bot.commands.keys():
            try:
                command = self.config.get(name)
            except configparser.NoOptionError:
                return

            await self.bot.send_message(message.channel, command)

    @commands.command(pass_context=True, no_pm=True)
    async def add(self, ctx, name=None, *, command=None):
        """Adds a new custom command"""
        message = ctx.message
        if name is None or command is None:
            await self.bot.say("Please match the format `{}add [command] [link]`".format(self.bot.get_prefix(message)))

        command.replace("\n", "")
        name = self.bot.trim_prefix(message, name)

        if name in self.bot.commands.keys() or self.config.has(name):
            await self.bot.say("Command `{}` is already in the commands list.".format(name))
        else:
            self.config.save(name, command)
            await self.bot.say(
                "Added `{0}` to the commands list. `{1}undo` if you made an error".format(name,
                    self.bot.get_prefix(message)))
            self.undo_list[message.author] = name
            print("{0} | added by: {1}".format(name, message.author.name))

    @commands.command(pass_context=True, no_pm=True)
    async def delete(self, ctx, name=None):
        """Deletes a custom command"""
        message = ctx.message
        if name is None:
            await self.bot.say("Please match the format `{}delete [command]`".format(self.bot.get_prefix(message)))

        name = self.bot.trim_prefix(message, name)

        if self.config.delete(name):
            await self.bot.say("Deleted `{}`".format(name))
        else:
            await self.bot.say("Couldn't find `{}`".format(name))

    @commands.command(pass_context=True, no_pm=True)
    async def undo(self, ctx):
        """Undo the last command you tried to make"""
        message = ctx.message
        author = message.author

        if author in self.undo_list:
            name = self.undo_list[author]
            if self.config.delete(name):
                await self.bot.say("Undid `{}`".format(name))
            else:
                await self.bot.say("Couldn't find `{}`".format(name))

            del self.undo_list[author]
        else:
            await self.bot.say("No new command was added recently.")

    @commands.command(no_pm=True)
    async def random(self):
        """Returns a random command from the list"""
        random_command = random.choice(self.config.get_all())
        await self.bot.say(self.config.get(random_command))

    @commands.command(aliases=["latest"], no_pm=True)
    async def last(self):
        """Returns the last/latest command in the list"""
        last_command = self.config.get_all()[-1]
        await self.bot.say(self.config.get(last_command))

    # @commands.command(pass_context=True, no_pm=True)
    # @commands.has_role("test")
    # async def temp(self, ctx):
    #     for r in ctx.message.author.roles:
    #         print(r.name)
    #     pass
