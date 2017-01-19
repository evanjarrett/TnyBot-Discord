from src.cogs import Notifications

from tests import AsyncTestCase, MockBot, MockContext


class TestNotifications(AsyncTestCase):
    def setUp(self):
        self.bot = MockBot()
        self.cog = Notifications(self.bot, db_file=":memory:")
        self.ctx = MockContext()

    async def asyncTearDown(self):
        await self.bot.logout()

    async def test_notify(self):
        pass

    async def test_notify_pinned(self):
        pass

    async def test_delnotify(self):
        pass

    async def test_notifications(self):
        pass
