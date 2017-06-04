import importlib
import signal
import sys
from pprint import pprint
from time import time
from typing import List

import discord
from discord import Message
from discord.ext import commands
from discord.ext.commands import Bot, CheckFailure, CommandNotFound


class BasicBot(Bot):
    def __init__(self, command_prefix=commands.when_mentioned_or("#!"),
            formatter=None,
            name="BasicBot",
            description="""Tnybot is a basic bot that includes custom commands and notifications""",
            pm_help=False, **options):
        self.unit_tests = options.pop('unit_tests', False)
        super().__init__(command_prefix, formatter, description, pm_help, **options)

        self.name = name
        if not self.unit_tests and not sys.platform.startswith('win'):  # pragma: no cover
            # This is needed for safe shutdown on Heroku.
            self.loop.add_signal_handler(getattr(signal, "SIGTERM"), self.exit)

    async def on_ready(self):
        print("-" * 48)
        print("Logged in as")
        print(self.user.name)
        print(self.user.id)
        print(time())
        print("-" * 48)

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
        if not self.unit_tests:  # pragma: no cover
            print("Closing client...")
            print(time())

        await super().close()

    def exit(self):
        if not self.unit_tests:  # pragma: no cover
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

    def load_cogs(self, cogs: List):
        for cog, kwargs in cogs:
            try:
                # This is taken from self.load_extensions but allows kwargs to be passed
                if cog in self.extensions:
                    return

                lib = importlib.import_module("src." + cog)
                if not hasattr(lib, 'setup'):
                    del lib
                    del sys.modules[cog]
                    raise discord.ClientException("extension does not have a setup function")

                lib.setup(self, kwargs)
                self.extensions[cog] = lib
            except Exception as e:
                print('Failed to load extension {}\n{}: {}'.format(cog, type(e).__name__, e))
