import sqlite3
from urllib.parse import urlparse

import psycopg2


class Database:
    db_file = "res/database.db"

    def __init__(self, database_url=None):
        url = urlparse(database_url)
        if database_url is None:
            self.connection = sqlite3.connect(self.db_file)
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

    async def create_table(self):
        pass

    async def insert(self):
        pass

    async def update(self):
        pass

    async def delete(self):
        pass

    async def get(self):
        pass
