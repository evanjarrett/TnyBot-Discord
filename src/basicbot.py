import os
import signal
from pprint import pprint
from time import time

from discord import Message
from discord.ext import commands
from discord.ext.commands import Bot, CheckFailure, CommandNotFound


class BasicBot(Bot):
    def __init__(self, command_prefix=commands.when_mentioned_or("#!"),
            formatter=None,
            name="BasicBot",
            description="""Tnybot is a basic bot that includes custom commands and notifications""",
            pm_help=False, **options):
        super().__init__(command_prefix, formatter, description, pm_help, **options)

        self.name = name
        self.loop.add_signal_handler(getattr(signal, "SIGTERM"), self.exit)

    async def on_ready(self):
        print("------------------------------------------------------------------------------------------------------")
        print("Logged in as")
        print(self.user.name)
        print(self.user.id)
        print(time())
        print("------------------------------------------------------------------------------------------------------")

    async def on_message_edit(self, before, after):
        if before.pinned is False and after.pinned is True:
            self.dispatch("pin_add", after)
        if before.pinned is True and after.pinned is False:
            self.dispatch("pin_remove", after)

    async def on_command_error(self, exception, ctx):
        if isinstance(exception, CheckFailure):
            print("{0} does not have permission to run `{1}`".format(ctx.message.author, ctx.command.name))
        elif isinstance(exception, CommandNotFound):
            # This is handled in CustomCommands
            pass
        else:
            pprint(exception)
            await self.on_error("on_command_error", exception, ctx)

    async def close(self):
        if os.environ["UNIT_TESTS"] != "1":
            print("Closing client...")
            print(time())

        await super().close()

    def exit(self):
        if os.environ["UNIT_TESTS"] != "1":
            print("SIGTERM Closing client... ")
        # This gets handled in the run() method
        raise KeyboardInterrupt

    async def is_prefixed(self, message):
        part = message.content
        prefixes = await self._get_prefix(message)
        if isinstance(prefixes, str):
            if part.startswith(prefixes):
                return True
        else:
            for p in prefixes:
                if part.startswith(p):
                    return True

    async def trim_prefix(self, message: Message, part=None):
        if part is None:
            part = message.content
        prefixes = await self._get_prefix(message)
        for p in prefixes:
            if part.startswith(p):
                part = part[len(p):]
        return part

    def get_prefix(self, ctx):
        return ctx.prefix.replace(self.user.mention, '@' + self.user.name)
