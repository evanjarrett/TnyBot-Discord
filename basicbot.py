from pprint import pprint
from time import time

from discord.ext import commands
from discord.ext.commands import Bot, CheckFailure, CommandNotFound


class BasicBot(Bot):
    def __init__(self, command_prefix=commands.when_mentioned_or("#!"),
            formatter=None,
            description="""Tnybot is a basic bot that includes custom commands and notifications""",
            pm_help=False, **options):
        super().__init__(command_prefix, formatter, description, pm_help, **options)

    async def on_ready(self):
        print("------------------------------------------------------------------------------------------------------")
        print("Logged in as")
        print(self.user.name)
        print(self.user.id)
        print(time())
        print("------------------------------------------------------------------------------------------------------")

    async def on_message(self, message):
        splits = message.content.split()
        if splits and splits[0] == self.user.mention:
            await self.process_commands(message)

        elif len(splits) > 0:
            name = self.trim_prefix(message)
            name = name.split()[0]
            if name in self.commands.keys():
                await self.process_commands(message)

    async def on_message_edit(self, before, after):
        if before.pinned is False and after.pinned is True:
            self.dispatch("message_pinned", after)
        if before.pinned is True and after.pinned is False:
            self.dispatch("pin_removed", after)

    async def on_command_error(self, exception, ctx):
        pprint(exception)
        if isinstance(exception, CheckFailure):
            print("{0} does not have permission to run `{1}`".format(ctx.message.author, ctx.command.name))
        elif isinstance(exception, CommandNotFound):
            print(exception.args[0])
        else:
            await self.on_error("on_command_error", exception, ctx)

    async def close(self):
        print("Closing client...")
        print(time())
        return await super().close()

    def is_prefixed(self, message):
        part = message.content
        prefixes = self._get_prefix(message)
        if isinstance(prefixes, str):
            if part.startswith(prefixes):
                return True
        else:
            for p in prefixes:
                if part.startswith(p):
                    return True

    def trim_prefix(self, message, part=None):
        if part is None:
            part = message.content
        prefixes = self._get_prefix(message)
        for p in prefixes:
            part = part.strip(p)
        return part

    def get_prefix(self, ctx):
        return ctx.prefix.replace(self.user.mention, '@' + self.user.name)
