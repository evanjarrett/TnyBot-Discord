import sqlite3

from src.database import RolesDB
from tests import AsyncTestCase, MockServer, MockRole


class TestRolesDB(AsyncTestCase):
    def setUp(self):
        self.server = MockServer()

        # Make our own connection to test things.
        # noinspection PyArgumentList
        self.connection = sqlite3.connect("file::memory:?cache=shared", uri=True)
        self.cursor = self.connection.cursor()
        self.cursor.execute("DROP TABLE IF EXISTS roles")
        self.connection.commit()

        self.roles_db = RolesDB("file::memory:?cache=shared", uri=True)

    async def asyncSetUp(self):
        await self.roles_db.create_table()
        await self.roles_db.insert(MockRole(), "testing")

        self.cursor.execute("SELECT role, alias, server_id, is_primary FROM roles")
        result = self.cursor.fetchone()
        self.assertTupleEqual(("12345", "testing", "12345", 0), result)

    def tearDown(self):
        self.connection.close()

    async def test_create_table(self):
        await self.roles_db.create_table()
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='roles'")
        result = self.cursor.fetchone()
        self.assertIsNotNone(result)

    async def test_insert(self):
        await self.roles_db.insert(MockRole())

        self.cursor.execute("SELECT role, alias, server_id, is_primary FROM roles WHERE alias='MockRole'")
        result = self.cursor.fetchone()
        self.assertTupleEqual(("12345", "MockRole", "12345", 0), result)

    async def test_bulk_insert(self):
        await self.roles_db.bulk_insert([
            (MockRole(id="11111"), "another", 0),
            (MockRole(id="22222"), "my role", 0),
            (MockRole(id="33333"), "타이니 봇", 0)])

        self.cursor.execute("SELECT role, alias, server_id, is_primary FROM roles")
        result = self.cursor.fetchall()
        self.assertIn(("11111", "another", "12345", 0), result)
        self.assertIn(("22222", "my role", "12345", 0), result)
        self.assertIn(("33333", "타이니 봇", "12345", 0), result)

    async def test_update(self):
        role = MockRole()
        await self.roles_db.update(role, "Role Alias")

        self.cursor.execute("SELECT role, alias, server_id, is_primary FROM roles")
        result = self.cursor.fetchone()
        self.assertTupleEqual((role.id, "Role Alias", "12345", 0), result)

        await self.roles_db.update(role)

        self.cursor.execute("SELECT role, alias, server_id, is_primary FROM roles WHERE alias='MockRole'")
        result = self.cursor.fetchone()
        self.assertTupleEqual((role.id, "MockRole", "12345", 0), result)

    async def test_delete(self):
        await self.roles_db.delete(MockRole())

        self.cursor.execute("SELECT role, alias, server_id, is_primary FROM roles")
        result = self.cursor.fetchone()
        self.assertIsNone(result)

    async def test_delete_by_id(self):
        await self.roles_db.delete_by_id(self.server, MockRole().id)

        self.cursor.execute("SELECT role, alias, server_id, is_primary FROM roles")
        result = self.cursor.fetchone()
        self.assertIsNone(result)

    async def test_bulk_delete(self):
        role1 = MockRole(id="11111")
        role2 = MockRole(id="22222")
        role3 = MockRole(id="33333")
        role4 = MockRole()

        await self.roles_db.bulk_insert([
            (role1, "another", 0),
            (role2, "my role", 0),
            (role3, "타이니 봇", 0)])
        await self.roles_db.bulk_delete([(role1,), (role2,), (None,), (role3,), (role4,)])

        self.cursor.execute("SELECT role, alias, server_id, is_primary FROM roles")
        result = self.cursor.fetchone()
        self.assertIsNone(result)

    async def test_get(self):
        result = await self.roles_db.get(self.server, "testing")
        self.assertEqual(MockRole().id, result)
        result = await self.roles_db.get(self.server, "does_not_exist")
        self.assertIsNone(result)

    async def test_get_all(self):
        role1 = MockRole(id="11111")
        role2 = MockRole(id="22222")
        role3 = MockRole(id="33333")
        role4 = MockRole()

        await self.roles_db.bulk_insert([
            (role1, "another", 1),
            (role2, "my role", 1),
            (role3, "타이니 봇", 0)])
        result = await self.roles_db.get_all(self.server)
        self.assertIn((role1.id, "another"), result)
        self.assertIn((role2.id, "my role"), result)
        self.assertIn((role3.id, "타이니 봇"), result)
        self.assertIn((role4.id, "testing"), result)

    async def test_get_all_main(self):
        role1 = MockRole(id="11111")
        role2 = MockRole(id="22222")
        role3 = MockRole(id="33333")
        role4 = MockRole()

        await self.roles_db.bulk_insert([
            (role1, "another", 1),
            (role2, "my role", 1),
            (role3, "타이니 봇", 0)])
        result = await self.roles_db.get_all_main(self.server)
        self.assertIn((role1.id, "another"), result)
        self.assertIn((role2.id, "my role"), result)
        self.assertNotIn((role3.id, "타이니 봇"), result)
        self.assertNotIn((role4.id, "testing"), result)

    async def test_get_all_regular(self):
        role1 = MockRole(id="11111")
        role2 = MockRole(id="22222")
        role3 = MockRole(id="33333")
        role4 = MockRole()

        await self.roles_db.bulk_insert([
            (role1, "another", 1),
            (role2, "my role", 1),
            (role3, "타이니 봇", 0)])
        result = await self.roles_db.get_all_regular(self.server)
        self.assertIn((role3.id, "타이니 봇"), result)
        self.assertIn((role4.id, "testing"), result)
        self.assertNotIn((role1.id, "another"), result)
        self.assertNotIn((role2.id, "my role"), result)
