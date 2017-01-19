from src.cogs import Logs
from tests import AsyncTestCase, MockBot, MockContext


class TestLogs(AsyncTestCase):
    def setUp(self):
        self.bot = MockBot()
        self.cog = Logs(self.bot)
        self.ctx = MockContext()

    async def asyncTearDown(self):
        await self.bot.logout()

    def test_log(self):
        pass
