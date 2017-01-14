from src.cogs import Commands
from tests import AsyncTestCase, MockBot, MockContext


class TestCommands(AsyncTestCase):
    def setUp(self):
        self.bot = MockBot()
        self.cog = Commands(self.bot)
        self.ctx = MockContext()

    async def asyncTearDown(self):
        await self.bot.logout()

    async def test_say(self):
        ret = await self.ctx.invoke(self.cog.say, self.cog, message="hello world")
        self.assertEqual("hello world", ret)

        ret = await self.ctx.invoke(self.cog.say, self.cog)
        self.assertIsNone(ret)
