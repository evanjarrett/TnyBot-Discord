import sqlite3
import time

from src.database import RemindersDB
from tests import AsyncTestCase, MockUser


class TestRemindersDB(AsyncTestCase):
    def setUp(self):
        self.remind_date = time.time()
        # Make our own connection to test things.
        # noinspection PyArgumentList
        self.connection = sqlite3.connect("file::memory:?cache=shared", uri=True)
        self.cursor = self.connection.cursor()
        self.cursor.execute("DROP TABLE IF EXISTS reminders")
        self.connection.commit()

        self.reminders_db = RemindersDB("file::memory:?cache=shared", uri=True)

    def tearDown(self):
        self.connection.close()

    async def test_create_table(self):
        await self.reminders_db.create_table()
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='reminders'")
        result = self.cursor.fetchone()
        self.assertIsNotNone(result)

    async def test_insert(self):
        await self._setup()

    async def test_delete(self):
        await self._setup()
        await self.reminders_db.delete(self.remind_date - 61)

        self.cursor.execute("SELECT user_id, message, remind_date from reminders")
        result = self.cursor.fetchone()
        self.assertIsNotNone(result)  # Assert we didn't delete it

        await self.reminders_db.delete(self.remind_date)

        self.cursor.execute("SELECT user_id, message, remind_date from reminders")
        result = self.cursor.fetchone()
        self.assertIsNone(result)  # Assert we did delete it

    async def test_get(self):
        await self._setup()
        result = await self.reminders_db.get(self.remind_date)
        self.assertListEqual([("12345", "my reminder message", self.remind_date)], result)

    async def _setup(self):
        await self.reminders_db.create_table()
        await self.reminders_db.insert(MockUser(), "my reminder message", self.remind_date)

        self.cursor.execute("SELECT user_id, message, remind_date from reminders")
        result = self.cursor.fetchone()
        self.assertTupleEqual(("12345", "my reminder message", self.remind_date), result)
