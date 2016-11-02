from typing import List, Tuple

from discord import Role, Server

from .database import Database, SQLType


class RolesDB(Database):
    async def create_table(self):
        """ Creates a new table for the server if it doesn't exist
        """
        q = '''CREATE TABLE IF NOT EXISTS roles
        (role       TEXT    NOT NULL,
         alias      TEXT    NOT NULL,
         server_id  TEXT    NOT NULL,
         is_primary INT     NOT NULL DEFAULT 0,
         primary key (role, server_id))'''
        self.cursor.execute(q)
        self.connection.commit()

    async def insert(self, role: Role, alias: str = None, is_primary: int = 0):
        """ Inserts a new role into the table.
            If the alias is not specified, the role name will be used instead
        """
        if not role:  # pragma: no cover
            return
        if alias is None:
            alias = role.name

        server = role.server
        if self.sql_type is SQLType.sqlite:
            return await self._insert_lite(role, server, alias, is_primary)
        else:  # pragma: no cover
            self.cursor.execute(
                self.query(
                    '''INSERT INTO roles VALUES (%(role)s, %(alias)s, %(server)s, %(primary)s)
                        ON CONFLICT(role, server_id)
                        DO UPDATE SET alias = %(alias)s'''),
                {"role": role.id, "alias": alias, "server": server.id, "primary": is_primary})
            self.connection.commit()

    async def bulk_insert(self, rows: List[Tuple[Role, str, int]]):
        """ Bulk inserts multiple rows into the table (Really just uses insert...)
            Max rows allowed is 100.
        """
        if len(rows) > 100:  # pragma: no cover
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
            self.query("UPDATE roles SET alias = %(alias)s WHERE role = %(role)s AND server_id = %(server)s"),
            {"role": role.id, "server": server.id, "alias": alias})
        self.connection.commit()

    async def delete(self, role: Role):
        """ Delete a role from the table.
        """
        server = role.server
        self.cursor.execute(
            self.query(
                "DELETE FROM roles WHERE role = %(role)s AND server_id = %(server)s"),
            {"role": role.id, "server": server.id})
        self.connection.commit()

    async def delete_by_id(self, server: Server, role_id: str):
        """ Delete a role from the table.
        """
        self.cursor.execute(
            self.query(
                "DELETE FROM roles WHERE role = %(role)s AND server_id = %(server)s"),
            {"role": role_id, "server": server.id})
        self.connection.commit()

    async def bulk_delete(self, rows: List[Tuple[Role]]):
        """ Bulk delete multiple rows from the table
            Max rows allowed is 10.
        """
        if len(rows) > 10:  # pragma: no cover
            # TODO: raise some exception
            return

        for row in rows:
            role = row[0]
            if not role:
                continue
            await self.delete(role)

    async def get(self, server: Server, alias: str, is_primary: int = 0) -> str:
        """ Gets the role info by its alias
        """
        self.cursor.execute(
            self.query(
                "SELECT role FROM roles WHERE alias = %(alias)s AND is_primary = %(primary)s AND server_id = %(server)s"
            ),
            {"alias": alias, "primary": is_primary, "server": server.id})
        one = self.cursor.fetchone()
        if one is not None:
            one = one[0]
        return one

    async def get_all(self, server: Server) -> List:
        """ Gets all the roles
        """
        return await self._get_all(server, None)

    async def get_all_main(self, server: Server) -> List:
        """ Gets the primary roles
        """
        return await self._get_all(server, 1)

    async def get_all_regular(self, server: Server) -> List:
        """ Gets all the regular roles
        """
        return await self._get_all(server, 0)

    async def _get_all(self, server: Server, is_primary: int = None) -> List:
        """ Internal helper method to fetch role and alias
        """
        primary_in = "(0,1)"
        if is_primary == 1:
            primary_in = "(1)"

        if is_primary == 0:
            primary_in = "(0)"

        self.cursor.execute(
            self.query(
                "SELECT role, alias FROM roles WHERE is_primary IN {0} AND server_id = %(server)s".format(primary_in)),
            {"server": server.id})
        rows = self.cursor.fetchall()
        ret_list = []
        for r in rows:
            role, alias = r
            ret_list.append((str(role), alias))
        return ret_list

    async def _insert_lite(self, role: Role, server: Server, alias: str = None, is_primary: int = 0):
        """ Inserts a new role into the table.
            If the alias is not specified, the role name will be used instead
        """
        self.cursor.execute(
            self.query(
                "INSERT OR REPLACE INTO roles VALUES (%(role)s, %(alias)s, %(server)s, %(primary)s)"),
            {"role": role.id, "alias": alias, "server": server.id, "primary": is_primary})
        self.connection.commit()
