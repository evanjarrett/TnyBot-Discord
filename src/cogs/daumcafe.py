from urllib import request as urllib_request

from discord.ext import commands

from src.cogs import BaseCog


class Daum(BaseCog):
    url = "http://cafe.daum.net"

    # https://apis.daum.net/cafe/v1/articles/MNH-Chungha/g3oh?appkey=
    # https://apis.daum.net/cafe/v1/boards/MNH-Chungha.json?appkey=
    def __init__(self, bot):
        super().__init__(bot)
        opener = urllib_request.build_opener()
        opener.addheaders = [
            ("User-Agent", "Mozilla/5.0 (X11; Linux x86_64) Tnybot/1.0 Chrome/55.0")]
        urllib_request.install_opener(opener)

    @commands.command(aliases=["cafe"], pass_context=True)
    async def daum(self, ctx, *, query):
        pass
