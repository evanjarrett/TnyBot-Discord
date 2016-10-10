from typing import List, Tuple

from discord import Role, Server

from .database import Database, SQLType


class RolesDB(Database):
    async def create_table(self, server: Server):
        """ Creates a new table for the server if it doesn't exist
        """
        q = '''CREATE TABLE IF NOT EXISTS {0}
        (role       TEXT    NOT NULL PRIMARY KEY,
         alias      TEXT    NOT NULL,
         is_primary INT     NOT NULL DEFAULT 0)'''.format(self._table(server))
        self.cursor.execute(q)
        self.connection.commit()

    async def insert(self, role: Role, alias: str = None, is_primary: int = 0):
        """ Inserts a new role into the table.
            If the alias is not specified, the role name will be used instead
        """
        if self.sql_type is SQLType.sqlite:
            return await self._insert_lite(role, alias, is_primary)

        if not role:
            return

        server = role.server
        if alias is None:
            alias = role.name
        self.cursor.execute(
            self.query(
                '''INSERT INTO {0} VALUES (%(role)s, %(alias)s, %(primary)s)
                    ON CONFLICT(role)
                    DO UPDATE SET alias = %(alias)s''').format(self._table(server)),
            {"role": role.id, "alias": alias, "primary": is_primary})
        self.connection.commit()

    async def bulk_insert(self, rows: List[Tuple[Role, str, int]]):
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
            self.query("UPDATE {0} SET alias =  %(alias)s WHERE role = %(role)s").format(self._table(server)),
            {"role": role.id, "alias": alias})
        self.connection.commit()

    async def delete(self, role: Role):
        """ Delete a role from the table.
        """
        server = role.server
        self.cursor.execute(
            self.query(
                "DELETE FROM {0} WHERE role = %(role)s").format(self._table(server)),
            {"role": role.id})
        self.connection.commit()

    async def delete_by_id(self, server: Server, role_id: str):
        """ Delete a role from the table.
        """
        self.cursor.execute(
            self.query(
                "DELETE FROM {0} WHERE role = %(role)s").format(self._table(server)),
            {"role": role_id})
        self.connection.commit()

    async def bulk_delete(self, rows: List[Tuple[Role]]):
        """ Bulk delete multiple rows from the table
            Max rows allowed is 10.
        """
        if len(rows) > 10:
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
                "SELECT role FROM {0} WHERE alias = %(alias)s AND is_primary = %(primary)s"
            ).format(self._table(server)),
            {"alias": alias, "primary": is_primary})
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
            "SELECT role, alias FROM {0} WHERE is_primary IN {1}".format(self._table(server), primary_in))
        rows = self.cursor.fetchall()
        ret_list = []
        for r in rows:
            role, alias = r
            ret_list.append((str(role), alias))
        return ret_list

    async def _insert_lite(self, role: Role, alias: str = None, is_primary: int = 0):
        """ Inserts a new role into the table.
            If the alias is not specified, the role name will be used instead
        """
        if not role:
            return

        server = role.server
        if alias is None:
            alias = role.name
        self.cursor.execute(
            self.query(
                "INSERT OR REPLACE INTO {0} VALUES (%(role)s, %(alias)s, %(primary)s)").format(self._table(server)),
            {"role": role.id, "alias": alias, "primary": is_primary})
        self.connection.commit()

    def _table(self, server: Server):
        return self.table(server.id)
