from src.cogs import Greetings
from tests import AsyncTestCase, MockBot, MockContext


class TestGreetings(AsyncTestCase):
    def setUp(self):
        self.bot = MockBot()
        self.cog = Greetings(self.bot, db_file=":memory:")
        self.ctx = MockContext()

    async def asyncTearDown(self):
        await self.bot.logout()

    async def test_greeting(self):
        pass

    async def test_toggle_greeting(self):
        pass
