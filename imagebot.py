import asyncio
import configparser
import os
import pycurl

from discord.ext.commands import Bot


class ImageBot(Bot):
    has_curled = False

    mergedChannels = [
        '185164155592900608',
        '133389185988952064',
        '195732639724994560'
    ]

    def __init__(self, channels, command_prefix, formatter=None, description=None, pm_help=False, **options):
        super().__init__(command_prefix, formatter, description, pm_help, **options)
        self.channels = channels

    async def on_ready(self):
        print("Logged in as")
        print(self.user.name)
        print(self.user.id)
        print("------")

        for c_id in self.channels:
            channel = bot.get_channel(c_id)
            if channel is not None:
                print(channel)
                logs = bot.logs_from(channel)
                async for message in logs:
                    await self.get_attachments(message)
                if self.has_curled is True:
                    self.has_curled = False
                    print("sleeping for 10")
                    await asyncio.sleep(10)

        print("Done downloading missed images")

    async def on_message(self, message):
        if message.author != bot.user:
            await self.get_attachments(message)

    async def get_attachments(self, message):
        if len(message.attachments):
            chnl = message.channel.id
            if chnl in self.channels:
                print("attachment found!")
                server_dir = message.channel.server.name
                channel_dir = message.channel.name

                dirs = base_dir + "/" + server_dir + "/"
                if chnl not in self.mergedChannels:
                    dirs = dirs + channel_dir + "/"

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
                        self.has_curled = True
                        await asyncio.sleep(3)
                    else:
                        print("already have that image: " + pic_name)


config = configparser.RawConfigParser()
config.read("../tnybot_config")

base_dir = config["Images"]["dir"]

channels_config = config.items("Channels")
# Channels are in name = id format, but we only need the id
channels = []
for c in channels_config:
    channels.append(c[1])

bot = ImageBot(channels, command_prefix="#!", description="""Fetches any attachments uploaded to discord""")

bot.run(config["User"]["user"], config["User"]["pass"])
