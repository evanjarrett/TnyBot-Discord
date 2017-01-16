from src.cogs import CustomCommands
from tests import AsyncTestCase, MockBot, MockContext


class TestCustomCommands(AsyncTestCase):
    def setUp(self):
        self.bot = MockBot()
        self.cog = CustomCommands(self.bot, db_file=":memory:")
        self.ctx = MockContext()

    async def asyncTearDown(self):
        await self.bot.logout()

    async def test_add(self):
        self.cog.add.instance = self.cog
        ret = await self.ctx.invoke(self.cog.add, name="cmdName")
        self.assertEqual("Please match the format `!add [command] [link]`", ret)

    async def test_delete(self):
        pass

    async def test_undo(self):
        pass

    async def test_on_message(self):
        pass

    async def test_on_command_error(self):
        pass
