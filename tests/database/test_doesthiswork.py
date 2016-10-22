import sqlite3

import unittest

from tests import AsyncTestCase


class TestConfigDB(unittest.TestCase):
    def setUp(self):
        # Make our own connection to test things.
        # noinspection PyArgumentList
        self.connection = sqlite3.connect("file::memory:?cache=shared", uri=True)
        self.cursor = self.connection.cursor()
        self.connection.commit()

        # noinspection PyArgumentList
        self.connection2 = sqlite3.connect("file::memory:?cache=shared", uri=True)
        self.cursor2 = self.connection2.cursor()
        self.connection2.commit()

    def tearDown(self):
        self.connection.close()

    def test_this_database(self):
        q = '''CREATE TABLE IF NOT EXISTS reminders
            (user_id    TEXT    NOT NULL,
            message     TEXT    NOT NULL,
            remind_date INT     NOT NULL)'''
        self.cursor2.execute(q)
        self.connection2.commit()

        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='reminders'")
        result = self.cursor.fetchone()
        self.assertTupleEqual(result, ("reminders",))
