from discord.ext import commands
from db.roles import RolesDB
from discord.ext.commands.converter import RoleConverter


class Roles:
    def __init__(self, bot):
        self.bot = bot
        self.roles_db = RolesDB()

    async def on_ready(self):
        print("listening in another class " + __name__)

    @commands.group(pass_context=True)
    async def role(self, ctx):
        """Manage user roles"""
        if ctx.invoked_subcommand is None:
            await self.bot.say("Please specify what you want to do with the roles.")
            await self.bot.say("add, remove, primary, secondary, update, delete")

    @role.command(pass_context=True, aliases=["asar", "setroles"])
    async def _self_assign_role(self, ctx, *, roles):
        roles_arr = roles.split(",")
        alias = None
        for r in roles_arr:
            if "=" in r:
                role, alias = r.split("=")
                role = role.strip(" \t\n\r\"'")
                alias = alias.strip(" \t\n\r\"'")
            else:
                role = r.strip(" \t\n\r\"'")

            role_conv = RoleConverter.convert(role)
            if not role_conv:
                await self.bot.say("Couldn't find {} on this server".format(role))
            await self.roles_db.insert(role_conv, alias)

    @role.command(pass_context=True, name="add")
    async def _add(self, ctx, alias):
        """Add a role"""
        role = alias
        server = ctx.message.server
        members = ctx.message.mentions
        if not members:
            m = ctx.message.author
            await self.bot.say("Adding {0} to {1.mention}".format(role, m))
        else:
            for m in members:
                await self.bot.say("Adding {0} to {1.mention}".format(role, m))

    @role.command(name="remove", aliases=["rm", "del", "delete"])
    async def _remove(self):
        """Is the bot cool?"""
        await self.bot.say("Yes, the bot is cool.")


