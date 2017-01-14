import sqlite3

from src.database import ConfigDB
from tests import AsyncTestCase, MockServer


class TestConfigDB(AsyncTestCase):
    def setUp(self):
        # Make our own connection to test things.
        # noinspection PyArgumentList
        self.connection = sqlite3.connect("file::memory:?cache=shared", uri=True)
        self.cursor = self.connection.cursor()
        self.cursor.execute("DROP TABLE IF EXISTS config")
        self.connection.commit()

        self.config_db = ConfigDB("file::memory:?cache=shared", uri=True)

    async def asyncSetUp(self):
        await self.config_db.create_table()
        await self.config_db.insert(MockServer(), "mykey", "mytestvalue")

        self.cursor.execute("SELECT key,value,server_id from config")
        result = self.cursor.fetchone()
        self.assertTupleEqual(("mykey", "mytestvalue", "12345"), result)

    def tearDown(self):
        self.connection.close()

    async def test_create_table(self):
        await self.config_db.create_table()
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='config'")
        result = self.cursor.fetchone()
        self.assertIsNotNone(result)

    async def test_insert(self):
        await self.config_db.insert(MockServer(), "mykey", "mytestvalue")

        self.cursor.execute("SELECT key,value,server_id from config")
        result = self.cursor.fetchone()
        self.assertTupleEqual(("mykey", "mytestvalue", "12345"), result)

    async def test_update(self):
        await self.config_db.update(MockServer(), "mykey", "my new test value")

        self.cursor.execute("SELECT key,value,server_id from config")
        result = self.cursor.fetchone()
        self.assertTupleEqual(("mykey", "my new test value", "12345"), result)

    async def test_delete(self):
        await self.config_db.delete(MockServer(), "mykey")

        self.cursor.execute("SELECT key,value,server_id from config")
        result = self.cursor.fetchone()
        self.assertIsNone(result)

    async def test_get(self):
        result = await self.config_db.get(MockServer(), "mykey")
        self.assertEqual("mytestvalue", result)
        result = await self.config_db.get(MockServer(), "does_not_exist")
        self.assertIsNone(result)

    async def test_get_all(self):
        await self.config_db.insert(MockServer(), "key2", "anothervalue")
        await self.config_db.insert(MockServer(), "awesome", "wow this is cool")

        result = await self.config_db.get_all(MockServer())
        self.assertIn(("mykey", "mytestvalue"), result)
        self.assertIn(("key2", "anothervalue"), result)
        self.assertIn(("awesome", "wow this is cool"), result)
