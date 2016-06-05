from discord.ext import commands
import asyncio
import configparser
import pycurl
import os

description = """Fetches any attachments uploaded to discord"""
bot = commands.Bot(command_prefix="", description=description)

config = configparser.RawConfigParser()
config.read("../tnybot_config")
base_dir = config["Images"]["dir"]

channels_config = config.items("Channels")
channels = []
for c in channels_config:
    channels.append(c[1])


@bot.event
@asyncio.coroutine
def on_ready():
    print("Logged in as")
    print(bot.user.name)
    print(bot.user.id)
    print("------")


@bot.event
@asyncio.coroutine
def on_message(message):
    if len(message.attachments):
        chnl = message.channel.id
        if chnl in channels:
            server_dir = message.channel.server.name
            channel_dir = message.channel.name
            c = pycurl.Curl()
            for a in message.attachments:
                url = a["url"]
                pic_name = url.split("/")[-1]
                c.setopt(c.URL, url)
                c.setopt(c.SSL_VERIFYHOST, 2)
                c.setopt(c.SSL_VERIFYPEER, 1)
                c.setopt(c.USERAGENT,
                         "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.63 Safari/537.36")
                dirs = base_dir + "/" + server_dir + "/" + channel_dir + "/"
                if not os.path.exists(dirs):
                    os.makedirs(dirs)
                f = open(dirs + pic_name, "wb")
                c.setopt(c.WRITEDATA, f)
                c.perform()
                f.close()


bot.run(config["User"]["user"], config["User"]["pass"])
