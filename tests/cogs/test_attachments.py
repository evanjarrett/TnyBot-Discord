from src import utils
from src.cogs import Attachments
from tests import AsyncTestCase, MockBot, MockContext


class TestAttachments(AsyncTestCase):
    def setUp(self):
        self.bot = MockBot()
        self.cog = Attachments(self.bot, utils.full_path("sample_config"))
        self.ctx = MockContext()

    async def asyncTearDown(self):
        await self.bot.logout()

    async def test_get_embeds(self):
        pass

    async def test_get_attachments(self):
        pass

    async def test_upload_images(self):
        pass

    async def test_download_image(self):
        pass

    async def test_url_request(self):
        pass
