import os
import unittest

from src.utils import Config


class TestConfig(unittest.TestCase):
    def setUp(self):
        self.current_path = os.path.abspath(os.path.dirname(__file__))
        fullpath = os.path.join(self.current_path, "test_config")

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

    def tearDown(self):
        new_file = os.path.join(self.current_path, "new_file")
        if os.path.isfile(new_file):
            os.remove(new_file)

    def test_create_file(self):
        new_file = os.path.join(self.current_path, "new_file")
        self.assertFalse(os.path.isfile(new_file))
        Config(new_file, "MySection")
        self.assertTrue(os.path.isfile(new_file))
        os.remove(new_file)

    def test_get(self):
        channel_id = self.channel_config.get("test")
        self.assertEqual(channel_id, "000000000000000000002")

    def test_get_as_list(self):
        users = self.ignore_config.get_as_list("list")
        user_list = ["user1", "user2", "user3", "user4", "user5", "user6"]
        self.assertListEqual(users, user_list)

    def test_get_all(self):
        channels = self.channel_config.get_all()
        channel_list = ["general", "test", "awesome", "asdf", "cool", "voice"]
        self.assertListEqual(channels, channel_list)

    def test_save(self):
        self.channel_config.save("newchannel", "111111111111111111")
        channel_id = self.channel_config.get("newchannel")
        self.assertEqual(channel_id, "111111111111111111")

    def test_append(self):
        self.ignore_config.append("list", "user9001")
        users = self.ignore_config.get("list")
        self.assertIn(",user9001", users)
        # Try adding again for code coverage
        self.ignore_config.append("list", "user9001")
        users = self.ignore_config.get("list")
        self.assertIn(",user9001", users)
        # Try adding it to a new option to assert option is created
        self.ignore_config.append("list2", "user9001")
        users = self.ignore_config.get("list2")
        self.assertIn("user9001", users)

    def test_truncate(self):
        self.ignore_config.truncate("list", "user3")
        users = self.ignore_config.get("list")
        self.assertNotIn("user3", users)
        self.ignore_config.truncate("list2", "user3")
        does_have = self.ignore_config.has("list2")
        self.assertFalse(does_have)

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
        does_contain = self.ignore_config.contains("list2", "user5")
        self.assertFalse(does_contain)
