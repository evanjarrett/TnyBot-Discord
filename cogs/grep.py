from discord.ext import commands


class Grep:
    def __init__(self, bot):
        self.bot = bot

    async def on_ready(self):
        print("listening in another class " + __name__)

    @commands.group(pass_context=True)
    async def grep(self, ctx):
        if ctx.invoked_subcommand is None:
            pass

    @grep.command(name="-i")
    async def _ignore(self):
        """Ignore case distinctions in both the PATTERN and the input files."""
        await self.bot.say("ignoring case")

    @grep.command(name="-c")
    async def _count(self):
        """Suppress normal output; instead print a count of matching lines for each input file. """
        await self.bot.say("getting count")

    async def _messages(self):
        pass

    async def _members(self):
        pass

    async def _channels(self):
        pass

