import sqlite3

from src.database import CommandsDB
from tests import AsyncTestCase, MockServer


class TestCommandsDB(AsyncTestCase):
    def setUp(self):
        # Make our own connection to test things.
        # noinspection PyArgumentList
        self.connection = sqlite3.connect("file::memory:?cache=shared", uri=True)
        self.cursor = self.connection.cursor()
        self.cursor.execute("DROP TABLE IF EXISTS commands")
        self.connection.commit()

        self.commands_db = CommandsDB("file::memory:?cache=shared", uri=True)

    def tearDown(self):
        self.connection.close()

    async def test_create_table(self):
        await self.commands_db.create_table()
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='commands'")
        result = self.cursor.fetchone()
        self.assertIsNotNone(result)

    async def test_insert(self):
        await self._setup()

    async def test_delete(self):
        await self._setup()
        await self.commands_db.delete("testing")

        self.cursor.execute("SELECT name, command from commands")
        result = self.cursor.fetchone()
        self.assertIsNone(result)

    async def test_delete_all(self):
        await self._setup()
        server = MockServer()
        await self.commands_db.insert("another", "another command", server)
        await self.commands_db.insert("test", "asdasdasd", server)
        await self.commands_db.insert("타이니 봇", "안녕", server)
        await self.commands_db.delete_all(server)

        self.cursor.execute("SELECT name, command from commands")
        result = self.cursor.fetchone()
        self.assertIsNone(result)

    async def test_get(self):
        await self._setup()
        result = await self.commands_db.get("testing")
        self.assertIn("this is a test", result)

    async def test_get_all(self):
        await self._setup()
        server = MockServer()
        await self.commands_db.insert("one", "testing", server)
        await self.commands_db.insert("two", "testing", server)
        await self.commands_db.insert("three", "another", server)
        await self.commands_db.insert("four", "testing", server)
        await self.commands_db.insert("five", "another", server)

        result = await self.commands_db.get_all()
        keys = result.keys()
        self.assertIn("one", keys)
        self.assertIn("two", keys)
        self.assertIn("three", keys)
        self.assertIn("four", keys)
        self.assertIn("five", keys)
        self.assertEqual(result["one"], "testing")
        self.assertEqual(result["two"], "testing")
        self.assertEqual(result["three"], "another")
        self.assertEqual(result["four"], "testing")
        self.assertEqual(result["five"], "another")

    async def test_has(self):
        await self._setup()
        result = await self.commands_db.has("testing")
        self.assertTrue(result)
        result = await self.commands_db.has("nothing")
        self.assertFalse(result)

    async def _setup(self):
        await self.commands_db.create_table()
        await self.commands_db.insert("testing", "this is a test", MockServer())

        self.cursor.execute("SELECT name, command, server_id from commands")
        result = self.cursor.fetchone()
        self.assertTupleEqual(("testing", "this is a test", "12345"), result)
