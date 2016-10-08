import re

from discord.ext import commands


class Grep:
    ignore_case = False
    count = False

    def __init__(self, bot):
        self.bot = bot

    async def on_ready(self):
        print("listening in another class " + __name__)

    @commands.group(pass_context=True, no_pm=True)
    async def grep(self, ctx):
        """
        Works similar to GNU grep. Searches for a string in messages,channels or members.
        Examples:
            grep tnybot members
            grep "this works" messages
            grep -i 'This WOrKs' messages
            grep -c "bob" members
        """
        # Reset flags
        self.ignore_case = False
        self.count = False

        if ctx.invoked_subcommand is None:
            await self.issue_command(ctx)

    @grep.error
    async def on_grep_error(self, exception, ctx):
        await self.bot.send_message(ctx.message.channel, "That isn't something I can search")
        await self.bot.send_message(ctx.message.channel, "Try searching messages, channels or members")

    @grep.command(name="-i", pass_context=True, no_pm=True)
    async def _ignore(self, ctx):
        """Ignore case distinctions in both the PATTERN and the input files."""
        self.ignore_case = True
        await self.issue_command(ctx)

    @grep.command(name="-c", pass_context=True, no_pm=True)
    async def _count(self, ctx):
        """Suppress normal output; instead print a count of matching lines for each input file. """
        self.count = True
        await self.issue_command(ctx)

    @grep.command(name="-ci", aliases=["-ic"], pass_context=True, no_pm=True)
    async def _count_ignore(self, ctx):
        """Suppress normal output; instead print a count of matching lines for each input file.
        Ignore case distinctions in both the PATTERN and the input files."""
        self.count = True
        self.ignore_case = True
        await self.issue_command(ctx)

    async def _messages(self, ctx, needle):
        channel = ctx.message.channel
        msg_id = ctx.message.id
        logs = self.bot.logs_from(channel)
        lines = []
        n = needle
        if self.ignore_case:
            n = n.lower()

        async for message in logs:
            if message.author == self.bot.user or msg_id == message.id:
                continue

            c = message.content
            if self.ignore_case:
                c = c.lower()

            if n in c:
                author = message.author.name
                line = message.content.replace(needle, "`{}`".format(needle))
                line = "{0} | {1} ".format(author, line)
                lines.append(line)

        if self.count:
            await self.bot.say("{} matches".format(len(lines)))
            return

        if len(lines) > 0:
            await self.bot.say("\n".join(lines))
        else:
            await self.bot.say("I couldn't find any matches for `{}` in the last 100 messages".format(needle))

    async def _members(self, ctx, needle):
        members = ctx.message.server.members
        lines = []
        n = needle
        if self.ignore_case:
            n = n.lower()

        for user in members:
            name = user.name
            nick = user.nick if user.nick is not None else ""
            if self.ignore_case:
                name = name.lower()
                nick = nick.lower()

            if n in name or n in nick:
                if user.nick is None:
                    line = "{}".format(user.name).replace(needle, "`{}`".format(needle))
                else:
                    line = "{0} | {1}".format(user.nick, user.name).replace(needle, "`{}`".format(needle))
                lines.append(line)

        if self.count:
            await self.bot.say("{} matches".format(len(lines)))
            return

        if len(lines) > 0:
            await self.bot.say("\n".join(lines))
        else:
            await self.bot.say("I couldn't find any matches for `{}` in the user list".format(needle))

    async def _channels(self, ctx, needle):
        channels = ctx.message.server.channels
        lines = []
        n = needle
        if self.ignore_case:
            n = n.lower()

        for channel in channels:
            name = channel.name
            if self.ignore_case:
                name = name.lower()

            if n in name:
                line = "{0}".format(channel.name).replace(needle, "`{}`".format(needle))
                lines.append(line)

        if self.count:
            await self.bot.say("{} matches".format(len(lines)))
            return

        if len(lines) > 0:
            await self.bot.say("\n".join(lines))
        else:
            await self.bot.say("I couldn't find any matches for `{}` in the channel list".format(needle))

    async def issue_command(self, ctx):
        msg = ctx.message.content
        regex = re.compile(r"([\"'])((?:\\\1|.)*?)\1\s+(.*)")
        match = re.search(regex, msg)
        if match is None:
            haystack = msg.split()[-1]
            needle = msg.split()[-2]
        else:
            quote = match.group(1)
            needle = match.group(2)
            needle = needle.replace("\\" + quote, quote)
            haystack = match.group(3)

        command = getattr(self, "_" + haystack)
        await command(ctx, needle)
