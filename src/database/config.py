from typing import List

from discord import Server

from .database import Database, SQLType


# TODO: Might be good to add caching, but these shouldn't be hit often
class ConfigDB(Database):
    async def create_table(self):
        """ Creates a new table for if it doesn't exist
        """
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
        if self.sql_type is SQLType.sqlite:
            return await self._insert_lite(server, key, value)
        else:  # pragma: no cover
            self.cursor.execute(
                self.query(
                    "INSERT INTO config VALUES (%(key)s, %(value)s, %(server)s) "
                    "ON CONFLICT(key, server_id) DO UPDATE SET value = %(value)s"
                ),
                {"key": key, "value": value, "server": server.id})
            self.connection.commit()

    async def update(self, server: Server, key: str, value: str = None):
        """ Updates the value of a key
        """
        self.cursor.execute(
            self.query("UPDATE config SET  value = %(value)s WHERE key = %(key)s AND server_id = %(server)s"),
            {"key": key, "value": value, "server": server.id})
        self.connection.commit()

    async def delete(self, server: Server, key: str):
        """ Delete a config from the table.
        """
        self.cursor.execute(
            self.query("DELETE FROM config WHERE key = %(key)s AND server_id = %(server)s"),
            {"key": key, "server": server.id})
        self.connection.commit()

    async def get(self, server: Server, key: str) -> str:
        """ Gets the value of a config
        """
        self.cursor.execute(
            self.query("SELECT value FROM config WHERE key = %(key)s AND server_id = %(server)s"),
            {"key": key, "server": server.id})
        one = self.cursor.fetchone()
        if one is not None:
            one = one[0]
        return one

    async def get_all(self, server: Server) -> List:
        """ Gets all the configs for a server
        """
        self.cursor.execute(
            self.query("SELECT key, value FROM config WHERE server_id = %(server)s"),
            {"server": server.id})
        return self.cursor.fetchall()

    async def _insert_lite(self, server: Server, key: str, value: str):
        """ Inserts a new config into the table. This has special syntax for sqlite
        """
        self.cursor.execute(
            self.query(
                "INSERT OR REPLACE INTO config VALUES (%(key)s, %(value)s, %(server)s)"
            ),
            {"key": key, "value": value, "server": server.id})
        self.connection.commit()
