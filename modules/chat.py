import asyncio

from exceptions.expections import SameUserException
from .abstract_module import AbstractMethod


class Chat(AbstractMethod):
    def __init__(self, bot):
        super().__init__(bot)

    @asyncio.coroutine
    def on_ready(self):
        print("listening in another class " + __name__)

    @asyncio.coroutine
    def on_message(self, message):
        try:
            super().on_message(message)
        except SameUserException:
            return

        if "test" in message.content:
            yield from self.bot.send_message(message.channel, "what are you testing?")
