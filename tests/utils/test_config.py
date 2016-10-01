import os
import unittest

from src.utils import Config


class TestConfig(unittest.TestCase):
    def setUp(self):
        fullpath = os.path.join(os.path.abspath(os.path.dirname(__file__)), "test_config")

        data = []
        data.append("[Ignore]")
        data.append("list = user1,user2,user3,user4,user5,user6")
        data.append("")
        data.append("[Channels]")
        data.append("general = 000000000000000000001")
        data.append("test = 000000000000000000002")
        data.append("awesome = 000000000000000000003")
        data.append("asdf = 000000000000000000004")
        data.append("cool = 000000000000000000005")
        data.append("voice = 000000000000000000006")

        with open(fullpath, 'w') as f:
            f.write("\n".join(data))

        self.channel_config = Config(fullpath, "Channels")
        self.ignore_config = Config(fullpath, "Ignore")

    def test_get(self):
        id = self.channel_config.get("test")
        self.assertEqual(id, "000000000000000000002")

    def test_get_as_list(self):
        users = self.ignore_config.get_as_list("list")
        list = ["user1", "user2", "user3", "user4", "user5", "user6"]
        self.assertListEqual(users, list)

    def test_get_all(self):
        channels = self.channel_config.get_all()
        list = ["general", "test", "awesome", "asdf", "cool", "voice"]
        self.assertListEqual(channels, list)

    def test_save(self):
        self.channel_config.save("newchannel", "111111111111111111")
        id = self.channel_config.get("newchannel")
        self.assertEqual(id, "111111111111111111")

    def test_append(self):
        self.ignore_config.append("list", "user9001")
        users = self.ignore_config.get("list")
        self.assertIn(",user9001", users)

    def test_truncate(self):
        self.ignore_config.truncate("list", "user3")
        users = self.ignore_config.get("list")
        self.assertNotIn("user3", users)

    def test_delete(self):
        self.channel_config.delete("asdf")
        channels = self.channel_config.get_all()
        self.assertNotIn("asdf", channels)

    def test_has(self):
        does_contain = self.channel_config.has("awesome")
        self.assertTrue(does_contain)

    def test_contains(self):
        does_contain = self.ignore_config.contains("list", "user5")
        self.assertTrue(does_contain)
