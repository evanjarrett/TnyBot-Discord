from src.cogs import Reaction
from tests import AsyncTestCase, MockBot, MockContext


class TestReaction(AsyncTestCase):
    def setUp(self):
        self.bot = MockBot()
        self.cog = Reaction(self.bot)
        self.ctx = MockContext()

    async def asyncTearDown(self):
        await self.bot.logout()

    async def test_secret(self):
        pass

    async def test_vote(self):
        pass

    async def test_endvote(self):
        pass
