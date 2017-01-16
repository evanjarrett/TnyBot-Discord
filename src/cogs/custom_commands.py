from discord.ext import commands
from discord.ext.commands import CommandNotFound

from src.cogs import BaseDBCog
from src.database import CommandsDB


class CustomCommands(BaseDBCog):
    _undo_list = {}

    def __init__(self, bot, *, db_url=None):
        super().__init__(bot, CommandsDB("res/commands.db", db_url))

    async def on_message(self, message):
        if not await self.bot.is_prefixed(message):
            return

        name = await self.bot.trim_prefix(message, message.content)
        if message.author != self.bot.user and name not in self.bot.commands.keys():
            if await self.database.has(name):
                command = await self.database.get(name)
                await self.bot.send_message(message.channel, command)

    async def on_command_error(self, exception, ctx):
        if isinstance(exception, CommandNotFound):
            if await self.database.has(ctx.invoked_with):
                return
            else:
                print(exception.args[0])

    @commands.command(pass_context=True, no_pm=True)
    async def add(self, ctx, name=None, *, command=None):
        """Adds a new custom command"""
        message = ctx.message
        if name is None or command is None:
            return await self.bot.say("Please match the format `{}add [command] [link]`".format(self.bot.get_prefix(ctx)))

        command.replace("\n", "")
        name = await self.bot.trim_prefix(message, name)
        if name in self.bot.commands.keys() or await self.database.has(name):
            return await self.bot.say("Command `{}` is already in the commands list.".format(name))
        else:
            if await self.database.insert(name, command, message.server):
                msg = await self.bot.say(
                    "Added `{0}` to the commands list. `{1}undo` if you made an error".format(name,
                        self.bot.get_prefix(ctx)))
                self._undo_list[message.author] = name
                print("{0} | added by: {1}".format(name, message.author.name))
                return msg

    @commands.command(pass_context=True, no_pm=True)
    async def delete(self, ctx, name=None):
        """Deletes a custom command"""
        message = ctx.message
        if name is None:
            await self.bot.say("Please match the format `{}delete [command]`".format(self.bot.get_prefix(ctx)))
            return

        name = await self.bot.trim_prefix(message, name)
        if await self.database.delete(name):
            await self.bot.say("Deleted `{}`".format(name))
        else:
            await self.bot.say("Couldn't find `{}`".format(name))

    @commands.command(pass_context=True, no_pm=True)
    async def undo(self, ctx):
        """Undo the last command you tried to make"""
        message = ctx.message
        author = message.author

        if author in self._undo_list:
            name = self._undo_list[author]
            if await self.database.delete(name):
                await self.bot.say("Undid `{}`".format(name))
            else:
                await self.bot.say("Couldn't find `{}`".format(name))

            del self._undo_list[author]
        else:
            await self.bot.say("No new command was added recently.")
