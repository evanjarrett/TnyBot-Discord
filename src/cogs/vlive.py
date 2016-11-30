from urllib import request as urllib_request
from urllib.parse import quote

from bs4 import BeautifulSoup, FeatureNotFound
from discord.ext import commands

from src.cogs import BaseCog


class Vlive(BaseCog):
    vlive_url = "http://www.vlive.tv"

    def __init__(self, bot):
        super().__init__(bot)

        opener = urllib_request.build_opener()
        opener.addheaders = [
            ("User-Agent", "Mozilla/5.0 (X11; Linux x86_64) Tnybot/1.0 Chrome/55.0")]
        urllib_request.install_opener(opener)

    @commands.command(aliases=["vapp"], pass_context=True)
    async def vlive(self, ctx, *, query):
        if ctx.invoked_subcommand is not None:
            return
        query = query.lower()

        soup = await self.get_url_contents("{0}/search/all?query={1}".format(self.vlive_url, quote(query)))

        channels = soup.find_all("a", "ct_box")
        if channels:
            channel = channels[0]
            for c in channels:
                if c["data-name"].lower() == query:
                    channel = c
                    break
            await self.bot.say(
                "Found channel `{0}`. Searching for videos..".format(channel["data-name"])
            )
            channel_url = self.vlive_url + channel["href"]
            channel_html = await self.get_url_contents(channel_url)
            channel_vid, live = await self.get_vid(channel_html)
            await self.print_vid(channel_vid, live)
        else:
            await self.bot.say(
                "No channels found for `{0}`. Getting first video result...".format(query)
            )
            vid, live = await self.get_vid(soup)
            await self.print_vid(vid, live)

    async def print_vid(self, vid, live):
        if vid:
            header = ""
            if live is not None:
                header = "```http\nLIVE:\n```\n"
            await self.bot.say("{0}{1}".format(header, vid))
        else:
            await self.bot.say("No videos found :(")

    async def get_url_contents(self, url: str) -> BeautifulSoup:
        search_page = urllib_request.urlopen(url)
        try:
            return BeautifulSoup(search_page.read(), "lxml")
        except FeatureNotFound:
            return BeautifulSoup(search_page.read(), "html.parser")

    async def get_vid(self, html: BeautifulSoup):
        first_vid = html.find("a", "thumb_area")
        if first_vid is not None:
            live = first_vid.find("span", "ico_live")
            if live is not None:
                live = live.string
            return self.vlive_url + first_vid["href"], live
        return None
