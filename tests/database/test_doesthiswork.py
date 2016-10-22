import sqlite3

import unittest

from tests import AsyncTestCase


class TestConfigDB(AsyncTestCase):
    def setUp(self):
        # Make our own connection to test things.
        # noinspection PyArgumentList
        self.connection = sqlite3.connect("file::memory:?cache=shared", uri=True)
        self.cursor = self.connection.cursor()
        self.connection.commit()

    def tearDown(self):
        self.connection.close()

    async def test_this_database(self):
        q = '''CREATE TABLE IF NOT EXISTS reminders
            (user_id    TEXT    NOT NULL,
            message     TEXT    NOT NULL,
            remind_date INT     NOT NULL)'''
        self.cursor.execute(q)
        self.connection.commit()
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='reminders'")
        result = self.cursor.fetchone()
        self.assertTupleEqual(result, ("reminders",))
