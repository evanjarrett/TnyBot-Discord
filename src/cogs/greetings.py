from discord import Server
from discord.ext import commands
from discord.ext.commands import MissingRequiredArgument

from src.cogs.base_cog import BaseDBCog
from src.database import ConfigDB


class Greetings(BaseDBCog):
    _default_greeting = "Welcome {member}!"
    _server_greetings = {}

    def __init__(self, bot, *, db_url=None):
        super().__init__(bot, ConfigDB("res/config.db", db_url))

    async def on_member_join(self, member):
        server = member.server
        chnl_id = await self.get_greeting_channel(server)
        if chnl_id not in ("0", None):
            greeting = await self.database.get(server, "greeting")
            greeting_channel = server.get_channel(chnl_id)
            if greeting is None:
                greeting = self._default_greeting
            if greeting_channel is not None:
                await self.bot.send_message(greeting_channel, greeting.format(member=member.mention))

    @commands.command(pass_context=True)
    @commands.has_permissions(manage_server=True)
    async def greeting(self, ctx, *, greeting):
        """
        Sets the greeting message for this server

        Use {member} to substitute in the member name
        """
        server = ctx.message.server
        chnl = await self.get_greeting_channel(server)
        if chnl in ("0", None):
            bot_message = await self.bot.say("Greetings are not enabled. Would you like me to turn them on? Y/N")
            reply = await self.bot.wait_for_message(timeout=5.0, author=ctx.message.author)
            if reply and reply.content.lower() in ["yes", "y"]:
                await self.database.insert(server, "greeting", greeting)
                await self.do_toggle_greeting(ctx, "on")
            else:
                await self.bot.delete_message(bot_message)

    @commands.command(aliases=["toggleGreeting"], pass_context=True)
    @commands.has_permissions(manage_server=True)
    async def toggle_greeting(self, ctx, toggle):
        """
        Toggles the greeting message for this server
        """
        self.do_toggle_greeting(ctx, toggle)

    async def do_toggle_greeting(self, ctx, toggle):
        server = ctx.message.server
        channel = ctx.message.channel
        on_toggle = ["on", "yes", "y", "1", "true"]
        off_toggle = ["off", "no", "n", "0", "false"]
        if toggle in on_toggle:
            await self.database.insert(server, "greeting_channel", channel.id)
            self._server_greetings[server.id] = channel.id
            await self.bot.say("Turning on greetings")
        elif toggle in off_toggle:
            await self.database.insert(server, "greeting_channel", "0")
            self._server_greetings[server.id] = "0"
            await self.bot.say("Turning off greetings")
        else:
            await self.bot.say("I'm not sure what you mean. Try using `on` or `off`.")

    @toggle_greeting.error
    async def on_greeting_error(self, exception, ctx):
        if isinstance(exception, MissingRequiredArgument):
            await self.bot.send_message(ctx.message.channel, "Oops, you need to specify `on` or `off`")

    @commands.command(aliases=["testGreeting"], pass_context=True)
    @commands.has_permissions(manage_server=True)
    async def test_greeting(self, ctx):
        """Tests the greeting message for this server
        """
        server = ctx.message.server
        chnl = await self.get_greeting_channel(server)
        if chnl in ("0", None):
            await self.bot.say("Greetings aren't turned on for this server. Try using toggleGreeting.")
        await self.on_member_join(ctx.message.author)

    async def get_greeting_channel(self, server: Server):
        if server.id not in self._server_greetings or self._server_greetings[server.id] is None:
            self._server_greetings[server.id] = await self.database.get(server, "greeting_channel")
        return self._server_greetings[server.id]
