import asyncio
import configparser
import os
import imghdr
import shutil

from urllib import request as urllib_request
from urllib.error import HTTPError


class Attachments:
    has_curled = False

    def __init__(self, bot, config_file):
        self.bot = bot

        opener = urllib_request.build_opener()
        opener.addheaders = [("User-Agent", "Mozilla/5.0 (X11; Linux x86_64) Tnybot/1.0 Chrome/53.0")]
        urllib_request.install_opener(opener)

        config = configparser.RawConfigParser()
        config.read(config_file)

        self.base_dir = config["Images"]["dir"]

        channels_config = config.items("Channels")
        # Channels are in name = id format, but we only need the id
        self.channels = []
        for c in channels_config:
            self.channels.append(c[1])

        merged_channels_config = config.items("MergedChannels")
        # Do the same for the channels that we want merged together
        self.mergedChannels = []
        for c in merged_channels_config:
            self.mergedChannels.append(c[1])

        self.bot.loop.create_task(self.wait())

    async def wait(self):
        print("Running background task")
        await self.bot.wait_until_ready()
        # We want to run this in a separate process, since on_ready could be called multiple times
        for c_id in self.channels:
            channel = self.bot.get_channel(c_id)
            if channel is not None:
                print(channel)
                logs = self.bot.logs_from(channel)
                async for message in logs:
                    if message.author != self.bot.user:
                        await self.get_attachments(message)
                        await self.get_embeds(message)

                if self.has_curled is True:
                    self.has_curled = False
                    print("sleeping for 10")
                    await asyncio.sleep(10)
        print("Done downloading missed images")

    async def on_ready(self):
        print("listening in another class " + __name__)

    async def on_message(self, message):
        if message.author != self.bot.user:
            await self.get_attachments(message)
            await self.get_embeds(message)

    async def get_embeds(self, message):
        if len(message.embeds):
            chnl = message.channel.id
            if chnl in self.channels:
                dirs = self.get_directory(message.channel)
                has_print = False
                for e in message.embeds:
                    if e["type"] == "image":
                        if not has_print:
                            print("embedded image found! Uploaded by {}".format(message.author.name))
                            has_print = True
                        url = e["url"]
                        await self.download_image(url, dirs)

    async def get_attachments(self, message):
        if len(message.attachments):
            chnl = message.channel.id
            if chnl in self.channels:
                dirs = self.get_directory(message.channel)
                print("attachment found! Uploaded by {}".format(message.author.name))
                for a in message.attachments:
                    url = a["url"]
                    await self.download_image(url, dirs)

    async def download_image(self, url, dirs):
        parts = url.split("/")
        pic_name = parts[-1]
        if ".srt" in pic_name or ".html" in pic_name:
            return
        if "unknown" in pic_name:
            pic_name = parts[-2] + pic_name

        file_path = dirs + pic_name
        if not self.has_extension(file_path):
            if os.path.exists(file_path + ".jpeg") \
                    or os.path.exists(file_path + ".gif") \
                    or os.path.exists(file_path + ".png"):
                # Don't bother checking the content-type if have a file saved with an extension already
                return
            try:
                res = urllib_request.urlopen(url)
                img_ext = res.info().get_content_subtype()
                pic_name += ("." + img_ext)
                file_path += ("." + img_ext)
            except HTTPError as e:
                print(e.code)
                return

        if not os.path.exists(dirs):
            print("making new directory: " + dirs)
            os.makedirs(dirs)

        if not os.path.isfile(file_path):
            try:
                urllib_request.urlretrieve(url, file_path)
                print(file_path)
            except HTTPError as e:
                print(e.code)
                return
            except UnicodeEncodeError:
                # Special retry logic for IDN domains
                try:
                    url = "http://" + url.replace("http://", "").encode("idna").decode("utf-8")
                    urllib_request.urlretrieve(url, file_path)
                    print(file_path)
                except HTTPError as e:
                    print(e.code)
                    return
            else:
                self.has_curled = True
                await asyncio.sleep(3)
        else:
            print("already have that image: " + pic_name)
            pass

        ext = imghdr.what(file_path)
        if ext is not None and not file_path.lower().endswith(ext):
            if not (ext == "jpeg" and file_path.lower().endswith("jpg")):
                file, curr_ext = os.path.splitext(file_path)
                new_file = "{}.{}".format(file, ext)
                if not os.path.isfile(new_file):
                    print("!! Making a copy with {} extension".format(ext))
                    shutil.copy(file_path, new_file)

    def get_directory(self, channel):
        server_dir = channel.server.name
        server_dir = server_dir.strip(".")
        channel_dir = channel.name
        dirs = self.base_dir + "/" + server_dir + "/"
        if channel.id not in self.mergedChannels:
            dirs = dirs + channel_dir + "/"
        return dirs

    @staticmethod
    def has_extension(file_path):
        for e in ["jpg", "jpeg", "png", "gif"]:
            # I really only care about these, anything else probably wont download correctly anyways
            if file_path.lower().endswith("." + e):
                return True
        return False
