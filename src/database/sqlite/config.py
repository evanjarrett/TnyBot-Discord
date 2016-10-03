import sqlite3
from typing import List

from discord import Server


class ConfigDB:
    _db_file = "res/config.db"

    def __init__(self):
        self.connection = sqlite3.connect(self._db_file)
        self.cursor = self.connection.cursor()

    def __del__(self):
        if self.connection is not None:
            print("closing the connection")
            self.connection.close()

    async def create_table(self):
        """ Creates a new table for if it doesn't exist"""
        q = '''CREATE TABLE IF NOT EXISTS `config`
        (key        TEXT    NOT NULL,
         value      TEXT    NOT NULL,
         server_id  TEXT    NOT NULL
         UNIQUE(key, server_id))'''
        self.cursor.execute(q)
        self.connection.commit()

    async def insert(self, server: Server, key: str, value: str):
        """ Inserts a new config into the table.
        """
        self.cursor.execute(
            '''INSERT OR REPLACE INTO config VALUES ('{0}', '{1}', '{2.id}')'''.format(key, value, server))
        self.connection.commit()

    async def update(self, server: Server, key: str, value: str = None):
        """ Updates the value of a key
        """
        self.cursor.execute(
            "UPDATE config SET  value = '{0}' WHERE key = '{1}' AND server_id = '{2.id}'".format(value, key, server))
        self.connection.commit()

    async def delete(self, server: Server, key: str):
        """ Delete a config from the table.
        """
        self.cursor.execute(
            "DELETE FROM config WHERE key = '{0}' AND server_id = '{1.id}'".format(key, server))
        self.connection.commit()

    async def get(self, server: Server, key: str) -> str:
        """ Gets the value of a config
        """
        self.cursor.execute(
            "SELECT value FROM config WHERE key = '{0}' AND server_id = '{1.id}'".format(key, server))
        one = self.cursor.fetchone()
        if one is not None:
            one = one[0]
        return one

    async def getall(self, server: Server) -> List:
        """ Gets all the configs for a server
        """
        self.cursor.execute(
            "SELECT key, value FROM config WHERE server_id = '{0.id}'".format(server))
        return self.cursor.fetchall()
