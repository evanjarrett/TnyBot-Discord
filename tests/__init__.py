from discord import Channel
from discord import Message
from discord import Role
from discord import Server
from discord import User
from discord.ext.commands import Bot
from discord.ext.commands import Context

from .async_testcase import AsyncTestCase


class MockServer(Server):
    def __init__(self, *, id="12345"):
        super().__init__(id=id)


class MockChannel(Channel):
    def __init__(self, *, id="12345"):
        super().__init__(id=id, server=MockServer())


class MockUser(User):
    def __init__(self, *, id="12345"):
        super().__init__(id=id)


class MockMessage(Message):
    def __init__(self, *, id="12345"):
        super().__init__(id=id, channel=MockChannel(), reactions=[], content="test")


class MockRole(Role):
    def __init__(self, *, id="12345", name="MockRole", server=MockServer()):
        super().__init__(id=id, name=name, server=server)


class MockBot(Bot):
    def __init__(self):
        super().__init__("!")

    async def say(self, msg, *args, **kwargs):
        return msg


class MockContext(Context):
    def __init__(self):
        super().__init__(prefix="!", message=MockMessage())
