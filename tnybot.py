import discord
from discord.ext import commands
import asyncio
import random
import configparser

description = """An example bot to showcase the discord.ext.commands extension
module.
There are a number of utility commands being showcased here."""
bot = commands.Bot(command_prefix="", description=description)

config = configparser.RawConfigParser()
config.read("../tnybot_config")
bot.run(config["User2"]["user"], config["User2"]["pass"])

@bot.event
@asyncio.coroutine
def on_ready():
    print("Logged in as")
    print(bot.user.name)
    print(bot.user.id)
    print("------")


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


# @bot.event
# @asyncio.coroutine
# def on_message(message):
#     if len(message.attachments):
#         server_dir = message.channel.server.name
#         channel_dir = message.channel.name
#         c = pycurl.Curl()
#         for a in message.attachments:
#             url = a["url"]
#             pic_name = url.split("/")[-1]
#             c.setopt(c.URL, url)
#             c.setopt(c.SSL_VERIFYHOST, 2)
#             c.setopt(c.SSL_VERIFYPEER, 1)
#             c.setopt(c.USERAGENT, "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.63 Safari/537.36")
#             dirs = server_dir + "/" + channel_dir + "/"
#             if not os.path.exists(dirs):
#                 os.makedirs(dirs)
#             f = open(dirs + pic_name, "wb")
#             c.setopt(c.WRITEDATA, f)
#             c.perform()
#             f.close()


@bot.command()
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

