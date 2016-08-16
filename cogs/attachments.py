import asyncio
import configparser
import os

from urllib import request as urllib_request


class Attachments:
    has_curled = False

    mergedChannels = [
        '185164155592900608',
        '133389185988952064',
        '195732639724994560'
    ]

    def __init__(self, bot, config_file):
        self.bot = bot

        config = configparser.RawConfigParser()
        config.read(config_file)

        self.base_dir = config["Images"]["dir"]

        channels_config = config.items("Channels")
        # Channels are in name = id format, but we only need the id
        self.channels = []
        for c in channels_config:
            self.channels.append(c[1])

    async def on_ready(self):
        for c_id in self.channels:
            channel = self.bot.get_channel(c_id)
            if channel is not None:
                print(channel)
                logs = self.bot.logs_from(channel)
                async for message in logs:
                    await self.fetch(message)

                if self.has_curled is True:
                    self.has_curled = False
                    print("sleeping for 10")
                    await asyncio.sleep(10)

        print("Done downloading missed images")

    async def on_message(self, message):
            await self.fetch(message)

    async def fetch(self, message):
        if message.author != self.bot.user:
            await self.get_attachments(message)
            await self.get_embeds(message)

    async def get_embeds(self, message):
        if len(message.embeds):
            chnl = message.channel.id
            if chnl in self.channels:
                dirs = self.get_directory(message.channel)
                for e in message.embeds:
                    if e["type"] == "image":
                        print("embedded image found! Uploaded by {}".format(message.author.name))
                        url = e["url"]
                        await self.download_image(url, dirs)

    async def get_attachments(self, message):
        if len(message.attachments):
            chnl = message.channel.id
            if chnl in self.channels:
                dirs = self.get_directory(message.channel)
                for a in message.attachments:
                    print("attachment found! Uploaded by {}".format(message.author.name))
                    url = a["url"]
                    await self.download_image(url, dirs)

    async def download_image(self, url, dirs):
        parts = url.split("/")
        pic_name = parts[-1]
        if "unknown" in pic_name:
            pic_name = parts[-2] + pic_name
        file_path = dirs + pic_name

        if not os.path.exists(dirs):
            print("making new directory: " + dirs)
            os.makedirs(dirs)

        if not os.path.isfile(file_path):
            opener = urllib_request.build_opener()
            opener.addheaders = [("User-Agent", "Mozilla/5.0 (X11; Linux x86_64) Tnybot/1.0 Chrome/53.0")]
            urllib_request.install_opener(opener)
            urllib_request.urlretrieve(url, file_path)
            self.has_curled = True
            await asyncio.sleep(3)
        else:
            print("already have that image: " + pic_name)

    def get_directory(self, channel):
        server_dir = channel.server.name
        server_dir = server_dir.strip(".")
        channel_dir = channel.name
        dirs = self.base_dir + "/" + server_dir + "/"
        if channel.id not in self.mergedChannels:
            dirs = dirs + channel_dir + "/"
        return dirs
