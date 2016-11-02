from typing import List, Tuple

from discord import User

from .database import Database, SQLType


def invalidate_cache(func):
    def decorator(*args):
        args[0].user_cache = []
        args[0].notif_cache = []
        return func(*args)

    return decorator


class NotificationsDB(Database):
    user_cache = []
    notif_cache = []

    async def create_table(self):
        """ Creates a new table for notifications if it doesn't exist"""
        q = '''CREATE TABLE IF NOT EXISTS notifications
        (user_id        TEXT    NOT NULL,
         notification   TEXT    NOT NULL,
         primary key (user_id, notification))'''
        self.cursor.execute(q)
        self.connection.commit()

    @invalidate_cache
    async def insert(self, user: User, notification: str):
        """ Inserts a new notification into the table.
        """
        if not user or not notification:  # pragma: no cover
            # TODO: raise some exception
            return

        if self.sql_type is SQLType.sqlite:
            return await self._insert_lite(user, notification)
        else:  # pragma: no cover
            self.cursor.execute(
                self.query("INSERT INTO notifications VALUES (%(user)s, %(notification)s) ON CONFLICT DO NOTHING"),
                {"user": user.id, "notification": notification})
            self.connection.commit()

    @invalidate_cache
    async def bulk_insert(self, rows: List[Tuple[User, str]]):
        """ Bulk inserts multiple rows into the table (Really just uses insert...)
            Max rows allowed is 100.
        """
        if len(rows) > 100:
            # TODO: raise some exception
            return

        for row in rows:
            user, notification = row
            await self.insert(user, notification)

    @invalidate_cache
    async def delete(self, user: User, notification: str):
        """ Delete a notification from the table.
        """
        self.cursor.execute(
            self.query("DELETE FROM notifications WHERE user_id = %(user)s AND notification = %(notification)s"),
            {"user": user.id, "notification": notification})
        self.connection.commit()

    @invalidate_cache
    async def delete_by_id(self, user_id: str, notification: str):
        """ Delete a notification from the table.
        """
        self.cursor.execute(
            self.query("DELETE FROM notifications WHERE user_id = %(user)s AND notification = %(notification)s"),
            {"user": user_id, "notification": notification})
        self.connection.commit()

    @invalidate_cache
    async def delete_all(self, user: User):
        """ Delete all notifications from the table for a particular user
        """
        self.cursor.execute(
            self.query("DELETE FROM notifications WHERE user_id = %(user)s"),
            {"user": user.id})
        self.connection.commit()

    async def get_all_notifications(self) -> List:
        """ Get all unique notifications
        """
        if not self.notif_cache:
            self.cursor.execute(
                self.query("SELECT notification FROM notifications GROUP BY notification"))
            self.notif_cache = self.cursor.fetchall()
        return self.notif_cache

    async def get_users(self, notification: str) -> List:
        """ Gets all users of a notifications
        """
        if not self.user_cache:
            self.cursor.execute(
                self.query("SELECT user_id FROM notifications WHERE notification = %(notification)s"),
                {"notification": notification})
            self.user_cache = self.cursor.fetchall()
        return self.user_cache

    async def get_notifications(self, user: User) -> List:
        """ Gets all notifications for a user
        """
        self.cursor.execute(
            self.query("SELECT notification FROM notifications WHERE user_id = %(user)s"),
            {"user": user.id})
        return self.cursor.fetchall()

    async def _insert_lite(self, user: User, notification: str):
        """ Inserts a new notification into the table.
        """
        self.cursor.execute(
            self.query("INSERT OR IGNORE INTO notifications VALUES (%(user)s, %(notification)s)"),
            {"user": user.id, "notification": notification})
        self.connection.commit()
