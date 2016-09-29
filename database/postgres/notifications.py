from typing import List, Tuple
from urllib.parse import urlparse

from discord import User
from pgdb import connect


def invalidate_cache(func):
    def decorator(*args):
        args[0].user_cache = []
        args[0].notif_cache = []
        return func(*args)

    return decorator


class NotificationsDB:
    user_cache = []
    notif_cache = []

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
        """ Creates a new table for notifications if it doesn't exist"""
        q = '''CREATE TABLE IF NOT EXISTS "notifications"
        (user_id        TEXT    NOT NULL,
         notification   TEXT    NOT NULL,
         primary key (user_id, notification))'''
        self.cursor.execute(q)
        self.connection.commit()

    @invalidate_cache
    async def insert(self, user: User, notification: str):
        """ Inserts a new notification into the table.
        """
        if not user or not notification:
            # TODO: raise some exception
            return

        self.cursor.execute(
            "INSERT INTO notifications VALUES ('{0.id}', '{1}') ON CONFLICT DO NOTHING".format(user, notification))
        self.connection.commit()

    @invalidate_cache
    async def bulkinsert(self, rows: List[Tuple[User, str]]):
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
            "DELETE FROM notifications WHERE user_id = '{0.id}' AND notification='{1}'".format(user, notification))
        self.connection.commit()

    @invalidate_cache
    async def deletebyid(self, user_id: str, notification: str):
        """ Delete a notification from the table.
        """
        self.cursor.execute(
            "DELETE FROM notifications WHERE user_id = '{0}' AND notification='{1}'".format(user_id, notification))
        self.connection.commit()

    @invalidate_cache
    async def deleteall(self, user: User):
        """ Delete all notifications from the table for a particular user
        """
        self.cursor.execute(
            "DELETE FROM notifications WHERE user_id = '{0.id}'".format(user))
        self.connection.commit()

    async def getallnotifications(self) -> List:
        """ Get all unique notifications
        """
        if not self.notif_cache:
            self.cursor.execute(
                "SELECT notification FROM notifications GROUP BY notification")
            self.notif_cache = self.cursor.fetchall()
        return self.notif_cache

    async def getusers(self, notification: str) -> List:
        """ Gets all users of a notifications
        """
        if not self.user_cache:
            self.cursor.execute(
                "SELECT user_id FROM notifications WHERE notification = '{}'".format(notification))
            self.user_cache = self.cursor.fetchall()
        return self.user_cache

    async def getnotifications(self, user: User) -> List:
        """ Gets all notifications for a user
        """
        self.cursor.execute(
            "SELECT notification FROM notifications WHERE user_id = '{0.id}'".format(user))
        return self.cursor.fetchall()
