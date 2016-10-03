from typing import List
from urllib.parse import urlparse

from discord import Server
from psycopg2 import connect


class ConfigDB:
    def __init__(self, database_url):
        url = urlparse(database_url)
        self.connection = connect(
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
        """ Creates a new table for if it doesn't exist"""
        q = '''CREATE TABLE IF NOT EXISTS config
        (key        TEXT    NOT NULL,
         value      TEXT    NOT NULL,
         server_id  TEXT    NOT NULL,
         primary key (key, server_id))'''
        self.cursor.execute(q)
        self.connection.commit()

    async def insert(self, server: Server, key: str, value: str):
        """ Inserts a new config into the table.
        """
        self.cursor.execute(
            "INSERT INTO config VALUES (%(key)s, %(value)s, %(server)s) ON CONFLICT DO UPDATE SET value = %(value)s",
            {"key": key, "value": value, "server": server.id})
        self.connection.commit()

    async def update(self, server: Server, key: str, value: str = None):
        """ Updates the value of a key
        """
        self.cursor.execute(
            "UPDATE config SET  value = %(value)s WHERE key = %(key)s AND server_id = %(server)s",
            {"key": key, "value": value, "server": server.id})
        self.connection.commit()

    async def delete(self, server: Server, key: str):
        """ Delete a config from the table.
        """
        self.cursor.execute(
            "DELETE FROM config WHERE key = %(key)s  AND server_id = %(server)s",
            {"key": key, "server": server.id})
        self.connection.commit()

    async def get(self, server: Server, key: str) -> str:
        """ Gets the value of a config
        """
        self.cursor.execute(
            "SELECT value FROM config WHERE key = %(key)s AND server_id = %(server)s",
            {"key": key, "server": server.id})
        one = self.cursor.fetchone()
        if one is not None:
            one = one[0]
        return one

    async def getall(self, server: Server) -> List:
        """ Gets all the configs for a server
        """
        self.cursor.execute(
            "SELECT key, value FROM config WHERE server_id = %(server)s",
            {"server": server.id})
        return self.cursor.fetchall()
