import textwrap

import discord
from PIL import Image, ImageDraw
from PIL import ImageFont
from discord.ext import commands

from src.cogs import BaseCog


class Spoiler(BaseCog):
    fontname = "res/NotoSansMonoCJKkr-Regular.otf"

    def __init__(self, bot):
        super().__init__(bot)

    async def on_message(self, message):
        if message.author != self.bot.user:
            if ":spoiler:" in message.content:
                content_split = message.content.split(":spoiler:")
                title = content_split[0]
                content = content_split[1]
                await self.run_spoiler(message, content, title)

    @commands.command(pass_context=True)
    async def spoiler(self, ctx, *, text):
        await self.run_spoiler(ctx.message, text, "")

    async def run_spoiler(self, message, content, title):
        self.set_text(content)
        content = "{0} {1} spoiler".format(message.author.mention, title)
        try:
            await self.bot.delete_message(message)
        except discord.Forbidden:
            print("Can't delete spoiler post. Don't have permissions")

        await self.bot.send_file(message.channel, "res/temp.gif", content=content)

    def set_text(self, text):
        font = ImageFont.truetype(self.fontname, 14)

        formatted_lines = []
        max_width = 400
        max_height = 0
        offset = 5

        for line in text.split("\n"):
            width, height = font.getsize(line)
            if width > max_width:
                max_width = width
            splits = textwrap.wrap(line, width=40)
            max_height += (height * len(splits))
            formatted_lines.extend(splits)

        max_height += 10

        spoiler_im = self.get_spoiler_text(max_width, max_height)

        im = Image.new("RGB", (max_width, max_height), (54, 57, 62))
        draw = ImageDraw.Draw(im)

        for line in formatted_lines:
            width, height = font.getsize(line)
            draw.text((5, offset), line, font=font)
            offset += height

        content_im = im.convert('P', palette=Image.ADAPTIVE, colors=5)
        spoiler_im.save("res/temp.gif", "GIF", save_all=True, append_images=[content_im])

    def get_spoiler_text(self, width=400, height=100):

        im = Image.new("RGB", (width, height), (54, 57, 62))
        d = ImageDraw.Draw(im)

        font = ImageFont.truetype(self.fontname, 14)
        d.text((5, 5), "( Hover to reveal spoiler )", font=font)
        return im.convert('P', palette=Image.ADAPTIVE, colors=5)
