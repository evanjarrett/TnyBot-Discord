from discord.ext import commands


class Greetings:

    _default_greeting = "Welcome {member}!"

    def __init__(self, bot, *, config_file=None, database_url=None):
        self.bot = bot

    async def on_ready(self):
        print("listening in another class " + __name__)

    async def on_message(self, message):
        pass

    async def on_member_join(self, member):
        self.bot.say(self._default_greeting.format(member=member.mention))

    @commands.command(pass_context=True)
    @commands.has_permissions(manage_messages=True)
    async def greeting(self, ctx, *, greeting):
        """Sets the greeting message for this server
        """
        pass
