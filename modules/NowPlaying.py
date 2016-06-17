import asyncio

import discord
import psutil

from .abstract_module import AbstractMethod


class NowPlaying(AbstractMethod):
    _process_list = [
        "PyCharm"
    ]

    def __init__(self, bot):
        super().__init__(bot)

    @asyncio.coroutine
    def on_ready(self):
        print(__name__ + " module loaded")
        status = None
        for proc in psutil.process_iter():
            for name in self._process_list:
                try:
                    if name.lower() in proc.name().lower():
                        status = name
                except psutil.NoSuchProcess:
                    pass

        game = None if status is None else discord.Game(name=status)
        yield from self.bot.change_status(game)

    @asyncio.coroutine
    def on_message(self, message):
        pass
