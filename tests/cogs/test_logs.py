import os

from src.cogs import Logs
from tests import AsyncTestCase, MockBot, MockMessage, MockChannel


class TestLogs(AsyncTestCase):
    _test_dirs = "res/logs/MockServer/"

    def setUp(self):
        self.bot = MockBot()
        self.cog = Logs(self.bot)

    async def asyncTearDown(self):
        await self.bot.logout()
        os.remove(self._test_dirs + "TestThis.log")
        os.removedirs(self._test_dirs)

    async def test_on_message_delete(self):
        await self.cog.on_message_delete(MockMessage(channel=MockChannel(name="TestThis")))
        self.assertTrue(os.path.exists(self._test_dirs))
        with open(self._test_dirs + "TestThis.log", "r") as f:
            self.assertEqual("deleted: 'test' from: None in #TestThis\n", f.read())

