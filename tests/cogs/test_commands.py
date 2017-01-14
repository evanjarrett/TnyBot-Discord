from src.cogs import Commands
from tests import AsyncTestCase, MockBot, MockContext


class TestCommands(AsyncTestCase):
    def setUp(self):
        self.bot = MockBot()
        self.cog = Commands(self.bot)
        self.ctx = MockContext()

    def tearDown(self):
        pass

    async def test_say(self):
        ret = await self.ctx.invoke(self.cog.say, self.cog, message="hello world")
        self.assertEqual("hello world", ret)
        await self.bot.logout()
