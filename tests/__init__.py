from discord import Role
from discord import Server
from discord import User

from .async_testcase import AsyncTestCase


class MockServer(Server):
    def __init__(self, *, id="12345"):
        super().__init__(id=id)


class MockUser(User):
    def __init__(self, *, id="12345"):
        super().__init__(id=id)


class MockRole(Role):
    def __init__(self, *, id="12345", name="MockRole", server=MockServer()):
        super().__init__(id=id, name=name, server=server)
