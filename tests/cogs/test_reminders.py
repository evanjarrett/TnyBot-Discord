from src.cogs import Reminders
from tests import AsyncTestCase, MockBot, MockContext


class TestReminders(AsyncTestCase):
    def setUp(self):
        self.bot = MockBot()
        self.cog = Reminders(self.bot, db_file=":memery:")
        self.ctx = MockContext()

    async def asyncTearDown(self):
        await self.bot.logout()

    async def test_remindme(self):
        pass
