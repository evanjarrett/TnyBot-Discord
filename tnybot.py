import configparser

from discord.ext import commands
from discord.ext.commands import Bot, CheckFailure
from cogs import Commands, CustomCommands, Notifications, Grep


class TnyBot(Bot):
    def __init__(self, command_prefix=commands.when_mentioned_or("!"),
            formatter=None,
            description="""Tnybot is a basic bot that includes custom commands and notifications""",
            pm_help=False, **options):
        super().__init__(command_prefix, formatter, description, pm_help, **options)

    async def on_ready(self):
        print("Logged in as")
        print(self.user.name)
        print(self.user.id)
        print("------")

    async def on_message(self, message):
        splits = message.content.split()
        if len(splits) > 0:
            name = self.trim_prefix(message, splits[0])
            if name in self.commands.keys():
                await self.process_commands(message)

    async def on_command_error(self, exception, ctx):
        if isinstance(exception, CheckFailure):
            print("{0} does not have permission to run `{1}`".format(ctx.message.author, ctx.command.name))
        else:
            await self.on_error("on_command_error", exception, ctx)

    def is_prefixed(self, message, part):
        prefixes = self._get_prefix(message)
        for p in prefixes:
            if part.startswith(p):
                return True

    def trim_prefix(self, message, part):
        prefixes = self._get_prefix(message)
        for p in prefixes:
            part = part.strip(p)
        return part

    def get_prefix(self, message):
        return self._get_prefix(message)


bot = TnyBot()

config = configparser.RawConfigParser()
config.read("../tnybot_config")

bot.add_cog(Commands(bot))
bot.add_cog(CustomCommands(bot))
bot.add_cog(Notifications(bot))
bot.add_cog(Grep(bot))
bot.run(config["User2"]["user"], config["User2"]["pass"])
