import discord
from discord.ext import commands
import asyncio
import random
import configparser

description = """An example bot to showcase the discord.ext.commands extension
module.
There are a number of utility commands being showcased here."""
bot = commands.Bot(command_prefix=commands.when_mentioned_or(""), description=description)

config = configparser.RawConfigParser()
config.read("../tnybot_config")


@bot.async_event
def on_ready():
    print("Logged in as")
    print(bot.user.name)
    print(bot.user.id)
    print("------")


@bot.async_event
def on_message(message):
    yield from bot.process_commands(message)


@bot.command(aliases=["hi", "sup", "안녕"])
@asyncio.coroutine
def hello():
    """Returns a random hello phrase"""
    choices = ["hi",
               "ohai",
               "hello",
               "안녕",
               "안녕하세요",
               "sup",
               ]
    yield from bot.say(random.choice(choices))


# @bot.command(pass_context=True)
# @asyncio.coroutine
# def clear(ctx, amount=10):
#     """Clears chat"""
#     messages = yield from bot.logs_from(ctx.message.channel, amount)
#     for msg in messages:
#         yield from bot.delete_message(msg)
#         yield from asyncio.sleep(.5)


@bot.command(aliases=["샤샤샤"])
@asyncio.coroutine
def shyshyshy():
    """No Sana No Life."""
    yield from bot.upload("res/shyshyshy.gif", content="샤샤샤")


@bot.command()
@asyncio.coroutine
def joined(member: discord.Member):
    """Says when a member joined."""
    yield from bot.say("{0.name} joined in {0.joined_at}".format(member))


@bot.group(pass_context=True)
@asyncio.coroutine
def cool(ctx):
    """Says if a user is cool.
    In reality this just checks if a subcommand is being invoked.
    """
    if ctx.invoked_subcommand is None:
        yield from bot.say("No, {0.subcommand_passed} is not cool".format(ctx))


@cool.command(name="bot")
@asyncio.coroutine
def _bot():
    """Is the bot cool?"""
    yield from bot.say("Yes, the bot is cool.")


bot.run(config["User2"]["user"], config["User2"]["pass"])
