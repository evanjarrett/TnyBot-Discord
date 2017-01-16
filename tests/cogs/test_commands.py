from datetime import date

from src.cogs import Commands
from tests import AsyncTestCase, MockBot, MockContext, MockMember


class TestCommands(AsyncTestCase):
    def setUp(self):
        self.bot = MockBot()
        self.cog = Commands(self.bot)
        self.ctx = MockContext()

    async def asyncTearDown(self):
        await self.bot.logout()

    async def test_hello(self):
        self.cog.hello.instance = self.cog
        ret = await self.ctx.invoke(self.cog.hello)
        self.assertIn(ret,
            ["hi",
             "ohai",
             "hello",
             "안녕",
             "안녕하세요",
             "sup",
             ])

    async def test_clear(self):
        pass

    async def test_say(self):
        self.cog.say.instance = self.cog
        ret = await self.ctx.invoke(self.cog.say, message="hello world")
        self.assertEqual("hello world", ret)

        ret = await self.ctx.invoke(self.cog.say)
        self.assertIsNone(ret)

    async def test_joined(self):
        self.cog.joined.instance = self.cog
        member = MockMember(username="00firestar00")
        ret = await self.ctx.invoke(self.cog.joined, member)
        self.assertEqual("00firestar00 joined on {} 00:00:00".format(date.today().isoformat()), ret)

    async def test_emoji(self):
        pass

    async def test_addemoji(self):
        pass

    async def test_invite(self):
        self.cog.invite.instance = self.cog
        ret = await self.ctx.invoke(self.cog.invite)
        self.assertEqual("https://tny.click/invite", ret)

    async def test_cool(self):
        self.ctx.subcommand_passed = "00firestar00"
        self.cog.cool.instance = self.cog

        ret = await self.ctx.invoke(self.cog.cool)
        self.assertEqual("No, 00firestar00 is not cool.", ret)
