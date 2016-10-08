import re
import sqlite3
from enum import Enum
from urllib.parse import urlparse

import psycopg2


class SQLType(Enum):
    postgres = 1
    sqlite = 2


class Database:
    def __init__(self, db_file=None, db_url=None):
        url = urlparse(db_url)
        if db_url is None and db_file is not None:
            self.connection = sqlite3.connect(db_file)
            self.sql_type = SQLType.sqlite
        else:
            self.connection = psycopg2.connect(
                database=url.path[1:],
                user=url.username,
                password=url.password,
                host=url.hostname,
                port=url.port
            )
            self.sql_type = SQLType.postgres

        self.cursor = self.connection.cursor()

    def __del__(self):
        if self.connection is not None:
            print("closing the connection")
            self.connection.close()

    def query(self, query: str) -> str:
        if self.sql_type is SQLType.sqlite:
            query = self._convert(query)
        return query

    @staticmethod
    def _convert(query: str) -> str:
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
