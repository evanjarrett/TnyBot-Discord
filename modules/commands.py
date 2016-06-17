import asyncio

from .abstract_module import AbstractMethod


class Commands(AbstractMethod):
    def __init__(self, bot):
        super().__init__(bot)

    @asyncio.coroutine
    def on_ready(self):
        print("listening in another class " + __name__)

    @asyncio.coroutine
    def on_message(self, message):
        print("found message " + message.content)
