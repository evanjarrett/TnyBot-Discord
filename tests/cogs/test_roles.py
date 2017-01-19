from src.cogs import Roles
from tests import AsyncTestCase, MockBot, MockContext


class TestRoles(AsyncTestCase):
    def setUp(self):
        self.bot = MockBot()
        self.cog = Roles(self.bot, db_file=":memery:")
        self.ctx = MockContext()

    async def asyncTearDown(self):
        await self.bot.logout()

    async def test_roleshelp(self):
        pass

    async def test_roleshelp_admin(self):
        pass

    async def test_setrole(self):
        pass

    async def test_listrole(self):
        pass

    async def test_setmainrole(self):
        pass

    async def test_listmainrole(self):
        pass

    async def test_delrole(self):
        pass

    async def test_mainrole(self):
        pass

    async def test_role(self):
        pass

    async def test_clearrole(self):
        pass
