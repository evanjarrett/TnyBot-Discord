from unittest import TestCase

from src.database import Database
from src.database import SQLType


class TestDatabase(TestCase):
    def setUp(self):
        self.database = Database(":memory:")

    def test_query(self):
        query = self.database.query("INSERT INTO commands VALUES (%(name)s, %(command)s, %(server)s)")
        self.assertEqual("INSERT INTO commands VALUES (:name, :command, :server)", query)

    def test_table(self):
        table = self.database.table("commands")
        self.assertEqual("`commands`", table)

        self.database.sql_type = SQLType.postgres
        table = self.database.table("commands")
        self.assertEqual("\"commands\"", table)
