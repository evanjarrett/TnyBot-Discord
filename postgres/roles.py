from typing import List, Tuple
from urllib.parse import urlparse

from discord import Role, Server
from pgdb import connect


class RolesDB:
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

    async def create_table(self, server: Server):
        """ Creates a new table for the server if it doesn't exist"""
        q = '''CREATE TABLE IF NOT EXISTS "{0.id}"
        (role       TEXT     NOT NULL PRIMARY KEY,
         alias      TEXT    NOT NULL,
         is_primary INT     NOT NULL DEFAULT 0)'''.format(server)
        self.cursor.execute(q)
        self.connection.commit()

    async def insert(self, role: Role, alias: str = None, is_primary: int = 0):
        """ Inserts a new role into the table.
            If the alias is not specified, the role name will be used instead
        """
        if not role:
            return

        server = role.server
        if alias is None:
            alias = role.name
        self.cursor.execute(
            '''INSERT INTO "{0.id}" VALUES ('{1.id}', '{2}', '{3}')
                ON CONFLICT(role)
                DO UPDATE SET alias='{2}'
            '''.format(server, role, alias, is_primary))
        self.connection.commit()

    async def bulkinsert(self, server: Server, rows: List[Tuple[Role, str, int]]):
        """ Bulk inserts multiple rows into the table (Really just uses insert...)
            Max rows allowed is 100.
        """
        if len(rows) > 100:
            # TODO: raise some exception
            return

        for row in rows:
            role, alias, is_primary = row
            await self.insert(role, alias, is_primary)

    async def update(self, role: Role, alias: str = None):
        """ Updates the alias of a role
            If the alias is not specified, the role name will be used instead
        """
        server = role.server
        if alias is None:
            alias = role.name
        self.cursor.execute(
            "UPDATE \"{0.id}\" SET alias = '{1}' WHERE role = '{2.id}'".format(server, alias, role))
        self.connection.commit()

    async def delete(self, role: Role):
        """ Delete a role from the table.
        """
        server = role.server
        self.cursor.execute(
            "DELETE FROM \"{0.id}\" WHERE role = '{1.id}'".format(server, role))
        self.connection.commit()

    async def deletebyid(self, server: Server, role_id: str):
        """ Delete a role from the table.
        """
        self.cursor.execute(
            "DELETE FROM \"{0.id}\" WHERE role = '{1}'".format(server, role_id))
        self.connection.commit()

    async def bulkdelete(self, server: Server, rows: List[Tuple[Role]]):
        """ Bulk delete multiple rows from the table
            Max rows allowed is 10.
        """
        if len(rows) > 10:
            # TODO: raise some exception
            return

        query = "DELETE FROM \"{0.id}\" WHERE role IN (".format(server)
        for row in rows:
            role = row[0]
            if not role:
                continue
            query += "'{0.id}',".format(role)

        query = query.strip(",")
        query += ")"
        self.cursor.execute(query)
        self.connection.commit()

    async def get(self, server: Server, alias: str, is_primary: int = 0) -> str:
        """ Gets the role info by its alias
        """
        self.cursor.execute(
            "SELECT role FROM \"{0.id}\" WHERE alias = '{1}' AND is_primary = '{2}'".format(server, alias,
                is_primary))
        one = self.cursor.fetchone()
        if one is not None:
            one = one[0]
        return one

    async def getall(self, server: Server) -> List:
        """ Gets all the roles
        """
        return await self._getall(server, None)

    async def getallmain(self, server: Server) -> List:
        """ Gets the primary roles
        """
        return await self._getall(server, 1)

    async def getallregular(self, server: Server) -> List:
        """ Gets all the regular roles
        """
        return await self._getall(server, 0)

    async def _getall(self, server: Server, is_primary: int = None) -> List:
        """ Internal helper method to fetch role and alias
        """
        primary_in = "(0,1)"
        if is_primary == 1:
            primary_in = "(1)"

        if is_primary == 0:
            primary_in = "(0)"

        self.cursor.execute(
            "SELECT role, alias FROM \"{0.id}\" WHERE is_primary IN {1}".format(server, primary_in))
        rows = self.cursor.fetchall()
        ret_list = []
        for r in rows:
            role, alias = r
            ret_list.append((str(role), alias))
        return ret_list
