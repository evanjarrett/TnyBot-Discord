import re
import sqlite3
from enum import Enum
from urllib.parse import urlparse

import psycopg2


class Database:
    _db_file = "res/database.db"

    def __init__(self, database_url=None):
        url = urlparse(database_url)
        if database_url is None:
            self.connection = sqlite3.connect(self._db_file)
        else:
            self.connection = psycopg2.connect(
                database=url.path[1:],
                user=url.username,
                password=url.password,
                host=url.hostname,
                port=url.port
            )
        self.cursor = self.connection.cursor()

    def __del__(self):
        if self.connection is not None:
            print("closing the connection")
            self.connection.close()


class SQLType(Enum):
    postgres = 1
    sqlite = 2


class Query:
    def __init__(self, query: str, sql_type: SQLType = SQLType.postgres):
        self.query = query
        self.sql_type = sql_type

    def __str__(self):
        if self.sql_type is SQLType.sqlite:
            return self._convert(self.query)
        return self.query

    @staticmethod
    def _convert(query):
        """
        Converts a query from pyformat to named format
        """
        pyformat = "%\((\w+)\)s"
        temp_query = query
        regex = re.compile(pyformat)
        for match in re.finditer(regex, query):
            var_name = match.group(1)
            old = "%({0})s".format(var_name)
            new = ":{0}".format(var_name)
            temp_query = temp_query.replace(old, new)
        return temp_query
