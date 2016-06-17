import asyncio
import configparser
import os
import pycurl

from discord.ext import commands

description = """Fetches any attachments uploaded to discord"""
bot = commands.Bot(command_prefix="", description=description)

config = configparser.RawConfigParser()
config.read("../tnybot_config")
base_dir = config["Images"]["dir"]

channels_config = config.items("Channels")
# Channels are in name = id format, but we only need the id
channels = []
for c in channels_config:
    channels.append(c[1])

has_curled = False


@asyncio.coroutine
def get_attachments(message):
    if len(message.attachments):
        chnl = message.channel.id
        if chnl in channels:
            print("attachment found!")
            server_dir = message.channel.server.name
            channel_dir = message.channel.name
            dirs = base_dir + "/" + server_dir + "/" + channel_dir + "/"

            pcurl = pycurl.Curl()
            pcurl.setopt(pcurl.SSL_VERIFYHOST, 2)
            pcurl.setopt(pcurl.SSL_VERIFYPEER, 1)
            pcurl.setopt(pcurl.USERAGENT,
                         "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.63 Safari/537.36")

            for a in message.attachments:
                url = a["url"]
                parts = url.split("/")
                pic_name = parts[-1]
                if "unknown" in pic_name:
                    pic_name = parts[-2] + pic_name
                file_path = dirs + pic_name
                pcurl.setopt(pcurl.URL, url)

                if not os.path.exists(dirs):
                    print("making new directory: " + dirs)
                    os.makedirs(dirs)

                if not os.path.isfile(file_path):
                    f = open(file_path, "wb")
                    pcurl.setopt(pcurl.WRITEDATA, f)
                    print(file_path)
                    pcurl.perform()
                    f.close()
                    global has_curled
                    has_curled = True
                    yield from asyncio.sleep(3)
                else:
                    print("already have that image: " + pic_name)


@bot.listen
@bot.async_event
def on_ready():
    print("Logged in as")
    print(bot.user.name)
    print(bot.user.id)
    print("------")

    for c_id in channels:
        channel = bot.get_channel(c_id)
        if channel is not None:
            print(channel)
            logs = yield from bot.logs_from(channel)
            for message in logs:
                yield from get_attachments(message)
            global has_curled
            if has_curled is True:
                has_curled = False
                print("sleeping for 10")
                yield from asyncio.sleep(10)

    print("Done downloading missed images")


@bot.listen
@bot.async_event
def on_message(message):
    if message.author != bot.user:
        yield from get_attachments(message)

bot.run(config["User"]["user"], config["User"]["pass"])
