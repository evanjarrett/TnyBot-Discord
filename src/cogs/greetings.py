from discord.ext import commands

from src.database import ConfigDB


class Greetings:

    _default_greeting = "Welcome {member}!"
    _server_greetings = {}

    def __init__(self, bot, *, db_url=None):
        self.config_db = ConfigDB("res/config.db", db_url)
        self.bot = bot

    async def on_ready(self):
        print("listening in another class " + __name__)
        await self.config_db.create_table()

    async def on_message(self, message):
        pass

    async def on_member_join(self, member):
        server = member.server
        if server.id not in self._server_greetings or self._server_greetings[server.id] is None:
            self._server_greetings[server.id] = await self.config_db.get(server, "greeting_toggle")

        if self._server_greetings[server.id] == "1":
            greeting = await self.config_db.get(server, "greeting")
            if greeting is None:
                greeting = self._default_greeting
            await self.bot.send_message(member, greeting.format(member=member.mention))

    @commands.command(pass_context=True)
    @commands.has_permissions(manage_server=True)
    async def greeting(self, ctx, *, greeting):
        """
        Sets the greeting message for this server

        Use {member} to substitute in the member name
        """
        await self.config_db.insert(ctx.server, "greeting", greeting)

    @commands.command(aliases=["toggleGreeting"], pass_context=True)
    @commands.has_permissions(manage_server=True)
    async def toggle_greeting(self, ctx, toggle):
        """
        Toggles the greeting message for this server
        """
        server = ctx.message.server
        on_toggle = ["on", "yes", "y", "1", "true"]
        off_toggle = ["off", "no", "n", "0", "false"]
        if toggle in on_toggle:
            await self.config_db.insert(server, "greeting_toggle", "1")
            self._server_greetings[server.id] = "1"
            await self.bot.say("Turning on greetings")
        elif toggle in off_toggle:
            await self.config_db.insert(server, "greeting_toggle", "0")
            self._server_greetings[server.id] = "0"
            await self.bot.say("Turning off greetings")
        else:
            await self.bot.say("I'm not sure what you mean. Try using `on` or `off`.")

    @commands.command(aliases=["testGreeting"], pass_context=True)
    @commands.has_permissions(manage_server=True)
    async def test_greeting(self, ctx):
        """Tests the greeting message for this server
        """
        server = ctx.message.server
        if server.id not in self._server_greetings or self._server_greetings[server.id] is None:
            self._server_greetings[server.id] = await self.config_db.get(server, "greeting_toggle")

        if self._server_greetings[server.id] in ("0", None):
            await self.bot.say("Greetings aren't turned on for this server. Try using toggleGreeting.")
        await self.on_member_join(ctx.message.author)
