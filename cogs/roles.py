from typing import List, Tuple

from discord import Forbidden, Message, Member
from discord.ext import commands
from discord.ext.commands import Context
from discord.ext.commands.converter import RoleConverter

from db.roles import RolesDB


class Roles:
    def __init__(self, bot):
        self.bot = bot
        self.roles_db = RolesDB()

    async def on_ready(self):
        print("listening in another class " + __name__)
        servers = self.bot.servers
        for s in servers:
            await self.roles_db.create_table(s)

    @commands.command(pass_context=True, aliases=["setbias"])
    async def setroles(self, ctx, *, roles):
        rows = await self._parse_roles(ctx, roles)
        await self.roles_db.bulkinsert(ctx.message.server, rows)
        await self.bot.say("Done! Use listroles to check what you added")

    @commands.command(pass_context=True, aliases=["listbias"])
    async def listroles(self, ctx):
        server = ctx.message.server
        all_roles = await self.roles_db.getallregular(server)
        role_names = await self._format_roles(ctx, all_roles)
        await self.bot.say(role_names)

    @commands.command(pass_context=True, aliases=["setmainbias", "addmainbias"])
    async def setmainroles(self, ctx, *, roles):
        rows = await self._parse_roles(ctx, roles, is_primary=1)
        await self.roles_db.bulkinsert(ctx.message.server, rows)
        await self.bot.say("Done! Use listmainroles to check what you added")

    @commands.command(pass_context=True, aliases=["listmainbias"])
    async def listmainroles(self, ctx):
        server = ctx.message.server
        all_roles = await self.roles_db.getallmain(server)
        role_names = await self._format_roles(ctx, all_roles)
        await self.bot.say(role_names)

    @commands.command(pass_context=True, aliases=["mainbias", "primary", "toprole", "main", "mainrole"])
    async def primaryrole(self, ctx, alias):
        """Add a primary role. Only one of these roles can be added to a member
        """
        message = ctx.message
        server = message.server

        role_id = await self.roles_db.get(server, alias, is_primary=1)
        if role_id is None:
            await self.bot.say("That role isn't something I can add")
            return

        role = "<@&{}>".format(role_id)
        role_conv = RoleConverter(ctx, role).convert()

        main_roles = await self.roles_db.getallmain(server)

        members = await self._get_members_from_message(message)
        for m in members:
            if role_conv in m.roles:
                await self.bot.say("{0.mention} already has {1.name} as their main role".format(m, role_conv))

            for r in m.roles:
                if r.id in main_roles:
                    await self.bot.say(
                        "{0.mention} already has a main role, would you like to change it to `{1.name}`? Y/N".format(
                            m, role_conv))
                    reply = await self.bot.wait_for_message(timeout=5.0, author=message.author)
                    if reply.content.lower() in ["yes", "y"]:
                        await self.bot.remove_roles(m, r)
                    else:
                        continue
            try:
                await self.bot.add_roles(m, role_conv)
                await self.bot.say("Adding {0.mention} to `{1.name}`".format(m, role_conv))
            except Forbidden:
                await self.bot.say("Oops, something happened, I don't have permission to give that role.")

    @commands.command(pass_context=True, aliases=["iam", "bias", "setrole", "addrole"])
    async def role(self, ctx, *, all_alias):
        """Add a role. A member can have any number of these roles
        """
        server = ctx.message.server
        alias_arr = all_alias.split(",")
        for a in alias_arr:
            alias = a.strip(" \t\n\r\"'")

            role_id = await self.roles_db.get(server, alias)
            if role_id is None:
                await self.bot.say("That role isn't something I can add")
                return

            role = "<@&{}>".format(role_id)
            role_conv = RoleConverter(ctx, role).convert()

            members = await self._get_members_from_message(ctx.message)
            for m in members:
                try:
                    await self.bot.add_roles(m, role_conv)
                    await self.bot.say("Adding {0.mention} to `{1.name}`".format(m, role_conv))
                except Forbidden:
                    await self.bot.say("Oops, something happened, I don't have permission to give that role.")

    async def _format_roles(self, ctx: Context, all_roles: List) -> List[str]:
        role_names = []
        for role_id in all_roles:
            role = "<@&{}>".format(role_id)
            role_conv = RoleConverter(ctx, role).convert()
            role_names.append(role_conv.name)
        return role_names

    async def _parse_roles(self, ctx: Context, roles: str, is_primary: int = 0) -> List[Tuple]:
        roles_arr = roles.split(",")
        alias = None
        rows = []
        for r in roles_arr:
            if "=" in r:
                role, alias = r.split("=")
                role = role.strip(" \t\n\r\"'")
                alias = alias.strip(" \t\n\r\"'")
            else:
                role = r.strip(" \t\n\r\"'")

            role_conv = RoleConverter(ctx, role).convert()
            if not role_conv:
                await self.bot.say("Couldn't find `{}` on this server".format(role))
            rows.append((role_conv, alias, is_primary))
        return rows

    async def _get_members_from_message(self, msg: Message) -> List[Member]:
        members = msg.mentions
        if not members:
            members = [msg.author]
        return members
