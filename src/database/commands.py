from typing import Dict

from discord import Server

from .database import Database, SQLType


# TODO: be smarter and only clear server related command cache
def invalidate_cache(func):
    def decorator(*args):
        args[0].cmd_cache = {}
        return func(*args)

    return decorator


class CommandsDB(Database):
    cmd_cache = {}

    async def create_table(self):
        """ Creates a new table for notifications if it doesn't exist
        """
        q = '''CREATE TABLE IF NOT EXISTS commands
        (name       TEXT    NOT NULL PRIMARY KEY,
         command    TEXT    NOT NULL,
         server_id  TEXT    NOT NULL)'''  # Currently not used, all custom commands are global
        self.cursor.execute(q)
        self.connection.commit()
        # Pre-populate cache
        await self.get_all()

    @invalidate_cache
    async def insert(self, name: str, command: str, server: Server):
        """ Inserts a new command into the table.
        """
        if not name or not command:  # pragma: no cover
            # TODO: raise some exception
            return False

        if self.sql_type is SQLType.sqlite:
            return await self._insert_lite(name, command, server)
        else:  # pragma: no cover
            self.cursor.execute(
                self.query("INSERT INTO commands VALUES (%(name)s, %(command)s, %(server)s) ON CONFLICT DO NOTHING"),
                {"name": name, "command": command, "server": server.id})
            self.connection.commit()
            if self.cursor.rowcount > 0:
                return True
            return False

    @invalidate_cache
    async def delete(self, name: str):
        """ Delete a command from the table.
        """
        self.cursor.execute(
            self.query("DELETE FROM commands WHERE name = %(name)s"),
            {"name": name})
        self.connection.commit()
        if self.cursor.rowcount > 0:
            return True
        return False

    @invalidate_cache
    async def delete_all(self, server: Server):
        """ Delete all commands from the table for a particular user
        """
        self.cursor.execute(
            self.query("DELETE FROM commands WHERE server_id = %(server)s"),
            {"server": server.id})
        self.connection.commit()
        if self.cursor.rowcount > 0:
            return True
        return False

    async def get(self, name: str) -> str:
        """ Get all unique commands
        """
        if name not in self.cmd_cache.keys():
            self.cursor.execute(
                self.query("SELECT command FROM commands WHERE name = %(name)s"),
                {"name": name})
            one = self.cursor.fetchone()
            if one is not None:
                self.cmd_cache[name] = one[0]
            else:  # Store the miss so the DB doesn't get hammered
                self.cmd_cache[name] = None
        return self.cmd_cache[name]

    async def get_all(self) -> Dict:
        """ Get all unique commands
        """
        if not self.cmd_cache:
            self.cursor.execute(
                self.query("SELECT name, command FROM commands"))
            rows = self.cursor.fetchall()
            for name, command in rows:
                self.cmd_cache[name] = command
        return self.cmd_cache

    async def has(self, name: str):
        """ Checks the cache for the name
        """
        command = await self.get(name)
        if command is None:
            return False
        return True

    async def _insert_lite(self, name: str, command: str, server: Server):
        """ Inserts a new notification into the table.
        """
        self.cursor.execute(
            self.query("INSERT OR IGNORE INTO commands VALUES (%(name)s, %(command)s, %(server)s)"),
            {"name": name, "command": command, "server": server.id})
        self.connection.commit()
        if self.cursor.rowcount > 0:
            return True
        return False
