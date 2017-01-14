import sqlite3

from src.database import NotificationsDB
from tests import AsyncTestCase, MockUser


class TestNotificationDB(AsyncTestCase):
    def setUp(self):
        # Make our own connection to test things.
        # noinspection PyArgumentList
        self.connection = sqlite3.connect("file::memory:?cache=shared", uri=True)
        self.cursor = self.connection.cursor()
        self.cursor.execute("DROP TABLE IF EXISTS notifications")
        self.connection.commit()

        self.notif_db = NotificationsDB("file::memory:?cache=shared", uri=True)

    async def asyncSetUp(self):
        await self.notif_db.create_table()
        await self.notif_db.insert(MockUser(), "testing")

        self.cursor.execute("SELECT user_id, notification from notifications")
        result = self.cursor.fetchone()
        self.assertTupleEqual(("12345", "testing"), result)

    def tearDown(self):
        self.connection.close()

    async def test_create_table(self):
        await self.notif_db.create_table()
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='notifications'")
        result = self.cursor.fetchone()
        self.assertIsNotNone(result)

    async def test_insert(self):
        await self.notif_db.insert(MockUser(), "testing")

        self.cursor.execute("SELECT user_id, notification from notifications")
        result = self.cursor.fetchone()
        self.assertTupleEqual(("12345", "testing"), result)

    async def test_bulk_insert(self):
        user = MockUser()
        await self.notif_db.bulk_insert([(user, "another"), (user, "my notif"), (user, "타이니 봇")])

        self.cursor.execute("SELECT user_id, notification from notifications")
        result = self.cursor.fetchall()
        self.assertIn((user.id, "another"), result)
        self.assertIn((user.id, "my notif"), result)
        self.assertIn((user.id, "타이니 봇"), result)

    async def test_delete(self):
        await self.notif_db.delete(MockUser(), "testing")

        self.cursor.execute("SELECT user_id, notification from notifications")
        result = self.cursor.fetchone()
        self.assertIsNone(result)

    async def test_delete_by_id(self):
        await self.notif_db.delete_by_id(MockUser().id, "testing")

        self.cursor.execute("SELECT user_id, notification from notifications")
        result = self.cursor.fetchone()
        self.assertIsNone(result)

    async def test_delete_all(self):
        user = MockUser()
        await self.notif_db.insert(user, "another")
        await self.notif_db.insert(user, "my notif")
        await self.notif_db.insert(user, "타이니 봇")
        await self.notif_db.delete_all(MockUser())

        self.cursor.execute("SELECT user_id, notification from notifications")
        result = self.cursor.fetchone()
        self.assertIsNone(result)

    async def test_get_all_notifications(self):
        await self.notif_db.insert(MockUser(), "testing")
        await self.notif_db.insert(MockUser(id="54321"), "testing")
        await self.notif_db.insert(MockUser(id="11111"), "another")
        await self.notif_db.insert(MockUser(id="22222"), "testing")
        await self.notif_db.insert(MockUser(id="33333"), "another")

        for x in range(0, 2):  # Loop twice to check cache for code coverage
            result = await self.notif_db.get_all_notifications()
            self.assertIn(("another",), result)
            self.assertIn(("testing",), result)

    async def test_get_users(self):
        await self.notif_db.insert(MockUser(), "testing")
        await self.notif_db.insert(MockUser(id="54321"), "testing")
        await self.notif_db.insert(MockUser(id="11111"), "testing")
        await self.notif_db.insert(MockUser(id="22222"), "testing")
        await self.notif_db.insert(MockUser(id="33333"), "testing")

        for x in range(0, 2):  # Loop twice to check cache for code coverage
            result = await self.notif_db.get_users("testing")
            self.assertIn(("54321",), result)
            self.assertIn(("11111",), result)
            self.assertIn(("22222",), result)
            self.assertIn(("33333",), result)
            self.assertIn(("12345",), result)

    async def test_get_notifications(self):
        user = MockUser()
        await self.notif_db.insert(user, "another")
        await self.notif_db.insert(user, "my notif")
        await self.notif_db.insert(user, "타이니 봇")
        result = await self.notif_db.get_notifications(user)

        self.assertIn(("my notif",), result)
        self.assertIn(("another",), result)
        self.assertIn(("타이니 봇",), result)
