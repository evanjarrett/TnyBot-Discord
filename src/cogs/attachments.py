import asyncio
import configparser
import hashlib
import imghdr
import os
import re
import shutil
from pprint import pprint
from typing import Optional
from urllib import request as urllib_request
from urllib.error import HTTPError
from urllib.parse import urlparse, parse_qs

from src.cogs import BaseCog


class Attachments(BaseCog):
    has_curled = False
    channel_checksums = {}
    # Regex pulled from https://github.com/Seklfreak/discord-image-downloader-go
    regexps = [
        "^https?:\/\/pbs\.twimg\.com\/media\/[^\./]+\.(jpg|png)((\:[a-z]+)?)$",
        "^https?:\/\/[a-z0-9]+\.uf\.tistory\.com\/(image|original)\/[A-Z0-9]+$",
        "^https?:\/\/[0-9a-z]+.daumcdn.net\/[a-z]+\/[a-zA-Z0-9\.]+\/\?scode=mtistory&fname=https?%3A%2F%2F[a-z0-9]+\.uf\.tistory\.com%2F(image|original)%2F[A-Z0-9]+$",
        "^https?:\/\/gfycat\.com\/([A-Za-z]+)$",
        "^https?:\/\/(i\.)?imgur\.com\/[A-Za-z0-9]+(\.gifv)?$",
        "^https?:\/\/imgur\.com\/a\/[A-Za-z0-9]+$",
        # "^https?:\/\/(www\.)?instagram\.com\/p\/[^/]+\/(\?[^/]+)?$",
        # "^https?:\/\/drive\.google\.com\/file\/d\/[^/]+\/view$",
        # "^https?:\/\/[0-9a-zA-Z\.-]+\/(m\/)?(photo\/)?[0-9]+$",
        # "^https?:\/\/(www\.)?flickr\.com\/photos\/([0-9]+)@([A-Z0-9]+)\/([0-9]+)(\/)?(\/in\/album-([0-9]+)(\/)?)?$",
        # "^https?:\/\/(www\.)?flickr\.com\/photos\/([0-9]+)@([A-Z0-9]+)\/albums\/(with\/)?([0-9]+)(\/)?$",
        # "^https?:\/\/(www\.)?streamable\.com\/([0-9a-z]+)$"
    ]

    def __init__(self, bot, config_file):
        super().__init__(bot)

        opener = urllib_request.build_opener()
        opener.addheaders = [("User-Agent", "Mozilla/5.0 (X11; Linux x86_64) Tnybot/1.0 Chrome/55.0")]
        urllib_request.install_opener(opener)

        config = configparser.RawConfigParser()
        config.read(config_file)

        self.base_dir = config["Images"]["dir"]
        self.checksum = config["Images"]["checksum"] == "True" or False
        if self.checksum:
            print(
                """!!!! Warning! Using checksums to detect duplicate images.
                Processing image hashes may take awhile on older CPUs.
                This will save disk space, but will cause an increase in downloads on restart.
                """
            )

        self.channels = self.get_config_values(config, "Channels")
        self.merged_channels = self.get_config_values(config, "MergedChannels") or []
        self.upload_channels = self.get_config_values(config, "Upload")

        if not self.bot.unit_tests:  # pragma: no cover
            self.bot.loop.create_task(self.background())
            # self.bot.loop.create_task(self.upload())

    async def upload(self):
        print("Running background task")
        await self.bot.wait_until_ready()
        for c_id in self.upload_channels:
            channel = self.bot.get_channel(c_id)
            if channel is not None:
                print(channel)
                await self.upload_images(channel)
                await asyncio.sleep(10)

    async def background(self):
        print("Running background task")
        await self.bot.wait_until_ready()
        # We want to run this in a separate process, since on_ready could be called multiple times
        for c_id in self.channels:
            channel = self.bot.get_channel(c_id)
            if channel is not None:
                self.save_checksums(channel)
                print(channel)
                logs = self.bot.logs_from(channel)
                async for message in logs:
                    if message.author != self.bot.user:
                        await self.get_attachments(message)
                        await self.get_embeds(message)
                        await self.get_links(message)

                if self.has_curled is True:
                    self.has_curled = False
                    print("sleeping for 10")
                    await asyncio.sleep(10)
        print("Done downloading missed images")

    async def on_message(self, message):
        if message.author != self.bot.user:
            await self.get_attachments(message)
            await self.get_embeds(message)
            await self.get_links(message)

    async def get_embeds(self, message):
        if len(message.embeds):
            chnl = message.channel.id
            if chnl in self.channels:
                dirs = self.get_directory(message.channel, self.channels)
                has_print = False
                for e in message.embeds:
                    if e["type"] == "image":
                        if not has_print:
                            print("Embedded image found! Linked by {}".format(message.author.name))
                            has_print = True
                        url = e["url"]
                        await self.download_image(url, dirs)

    async def get_attachments(self, message):
        if len(message.attachments):
            chnl = message.channel.id
            if chnl in self.channels:
                dirs = self.get_directory(message.channel, self.channels)
                print("Attachment found! Uploaded by {}".format(message.author.name))
                for a in message.attachments:
                    url = a["url"]
                    proxy_url = a["proxy_url"]
                    await self.download_image(url, dirs, proxy_url)

    async def get_links(self, message):
        chnl = message.channel.id
        if chnl in self.channels:
            dirs = self.get_directory(message.channel, self.channels)
            for exp in self.regexps:
                msg = message.content
                for m in re.finditer(exp, msg):
                    url = m.group(0)
                    proxy_url = url
                    if "gfycat" in url:
                        animal = m.group(1)
                        url = "https://{}.gfycat.com/{}.gif".format("giant", animal)
                        proxy_url = "https://{}.gfycat.com/{}.gif".format("fat", animal)
                    elif "tistory" in url:
                        url = url.replace("/image/", "/original/")
                        parsed = urlparse(url)
                        qs = parse_qs(parsed.query)
                        if "fname" in qs and qs["fname"] is not None:
                            url = ["fname"]
                    elif "instagram" in url:
                        pass
                    elif "imgur" in url:
                        url = url.replace("imgur.com/", "imgur.com/download/")
                        url = url.replace(".gifv", "")
                        if "/a/" in url:
                            print("downloading full albums not supported yet")
                            continue
                    elif "flickr" in url:
                        print("Who still uses flickr?????")
                        continue
                    if url is not None:
                        print("Regex URL matched! Linked by {}".format(message.author.name))
                        await self.download_image(url, dirs, proxy_url)

    async def upload_images(self, channel):
        dirs = self.get_directory(channel, self.upload_channels)
        os.chdir(dirs)
        files = filter(os.path.isfile, os.listdir(dirs))
        files = [os.path.join(dirs, f) for f in files]  # add path to each file
        files.sort(key=lambda x: os.path.getmtime(x))
        pprint(files)
        logs = self.bot.logs_from(channel)
        pic_names = []
        async for message in logs:
            for a in message.attachments:
                url = a["url"]
                pic_name = self.get_name_from_url(url)
                if pic_name is not None:
                    pic_names.append(pic_name)
            for e in message.embeds:
                if e["type"] == "image":
                    url = e["url"]
                    pic_name = self.get_name_from_url(url)
                    if pic_name is not None:
                        pic_names.append(pic_name)

        for f in files:
            name = f.replace(dirs, "")
            if name in pic_names:
                print("already have that")
            else:
                await self.bot.send_file(channel, f)
                await asyncio.sleep(3)

    async def download_image(self, url, dirs, proxy_url=None):
        url = url.replace(u"\u202c", "")
        pic_name = self.get_name_from_url(url)
        if not pic_name:
            return
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
                print("{}\t{}".format(e.code, url))
                return
            except UnicodeEncodeError as e:
                pprint(e)
                return

        if not os.path.exists(dirs):
            print("making new directory: " + dirs)
            os.makedirs(dirs)

        if self.checksum:
            while os.path.isfile(file_path):
                file, extention = file_path.rsplit('.', 1)
                file_path = file + "1" + extention

        if not os.path.isfile(file_path):
            try:
                await self.url_request(url, file_path, proxy_url)
            except Exception as e:
                pprint(e)
                return
            else:
                self.has_curled = True
                await asyncio.sleep(3)
        else:
            print("already have that image: " + pic_name)
            return

        if self.checksum:
            file_checksum = hashlib.sha256(open(file_path, 'rb').read()).digest()
            if file_checksum in self.channel_checksums[dirs]:
                os.remove(file_path)
                print("Removing file, because checksum matched")
                return

        ext = imghdr.what(file_path)
        if ext is not None and not file_path.lower().endswith(ext):
            if not (ext == "jpeg" and file_path.lower().endswith("jpg")):
                file, curr_ext = os.path.splitext(file_path)
                new_file = "{}.{}".format(file, ext)
                if not os.path.isfile(new_file):
                    print("!! Making a copy with {} extension".format(ext))
                    shutil.copy(file_path, new_file)

    def get_directory(self, channel, chnl_dict=None):
        server_dir = channel.server.name
        server_dir = server_dir.strip(".")
        if chnl_dict is None:
            channel_dir = channel.name
        else:
            channel_dir = chnl_dict.get(channel.id, channel.name)
        dirs = self.base_dir + "/" + server_dir + "/"
        if channel.id not in self.merged_channels:
            dirs = dirs + channel_dir + "/"
        return dirs

    async def url_request(self, url, file_path, proxy_url=None):
        try:
            urllib_request.urlretrieve(url, file_path)
            print(file_path)
        except HTTPError as e:
            print(e.code)
            if proxy_url is not None:
                print("Trying proxy URL")
                url = proxy_url
                await self.url_request(url, file_path)
            else:
                raise e
        except UnicodeEncodeError:
            # Special retry logic for IDN domains
            url = "http://" + url.replace("http://", "").encode("idna").decode("utf-8")
            await self.url_request(url, file_path)

    @staticmethod
    def has_extension(file_path: str) -> bool:
        for e in ["jpg", "jpeg", "png", "gif"]:
            # I really only care about these, anything else probably wont download correctly anyways
            if file_path.lower().endswith("." + e):
                return True
        return False

    @staticmethod
    def get_name_from_url(url: str) -> Optional[str]:
        parts = url.split("/")
        pic_name = parts[-1]
        if ".srt" in pic_name or ".html" in pic_name:
            return
        if "unknown" in pic_name:
            pic_name = parts[-2] + pic_name
        return pic_name

    @staticmethod
    def get_config_values(config, section: str) -> dict:
        try:
            merged_channels_config = config.items(section)
        except configparser.NoSectionError:
            return
        # Do the same for the channels that we want merged together
        items = {}
        for c_id, dirs in merged_channels_config:
            items[c_id] = dirs
        return items

    def save_checksums(self, channel):
        dirs = self.get_directory(channel, self.channels)
        if not os.path.exists(dirs):
            print("making new directory: " + dirs)
            os.makedirs(dirs)
        if dirs not in self.channel_checksums:
            files = [os.path.join(dirs, f) for f in os.listdir(dirs)]
            checksums = [hashlib.sha256(open(fname, 'rb').read()).digest() for fname in files]
            self.channel_checksums[dirs] = checksums


def setup(bot, kwargs):
    bot.add_cog(Attachments(bot, **kwargs))
