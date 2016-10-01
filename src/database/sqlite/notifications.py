import sqlite3
from typing import List, Tuple

from discord import User


def invalidate_cache(func):
    def decorator(*args):
        args[0].user_cache = []
        args[0].notif_cache = []
        return func(*args)

    return decorator


class NotificationsDB:
    user_cache = []
    notif_cache = []

    _db_file = "res/notifications.db"

    def __init__(self):
        self.connection = sqlite3.connect(self._db_file)

    def __del__(self):
        if self.connection is not None:
            print("closing the connection")
            self.connection.close()

    async def create_table(self):
        """ Creates a new table for notifications if it doesn't exist"""
        q = '''CREATE TABLE IF NOT EXISTS `notifications`
        (user_id        INT    NOT NULL,
         notification   TEXT    NOT NULL,
         UNIQUE(user_id, notification))'''
        self.connection.execute(q)
        self.connection.commit()

    @invalidate_cache
    async def insert(self, user: User, notification: str):
        """ Inserts a new notification into the table.
        """
        if not user or not notification:
            # TODO: raise some exception
            return

        self.connection.execute(
            "INSERT OR IGNORE INTO `notifications` VALUES ('{0.id}', '{1}')".format(user, notification))
        self.connection.commit()

    @invalidate_cache
    async def bulkinsert(self, rows: List[Tuple[User, str]]):
        """ Bulk inserts multiple rows into the table (Really just uses insert...)
            Max rows allowed is 100.
        """
        if len(rows) > 100:
            # TODO: raise some exception
            return

        query = "INSERT OR IGNORE INTO `notifications` VALUES "
        for row in rows:
            user, notification = row
            if not user:
                continue
            query += "('{0.id}', '{1}'),".format(user, notification)

        query = query.strip(",")
        self.connection.execute(query)
        self.connection.commit()

    @invalidate_cache
    async def delete(self, user: User, notification: str):
        """ Delete a notification from the table.
        """
        self.connection.execute(
            "DELETE FROM `notifications` WHERE user_id = '{0.id}' AND notification='{1}'".format(user, notification))
        self.connection.commit()

    @invalidate_cache
    async def deletebyid(self, user_id: str, notification: str):
        """ Delete a notification from the table.
        """
        self.connection.execute(
            "DELETE FROM `notifications` WHERE user_id = '{0}' AND notification='{1}'".format(user_id, notification))
        self.connection.commit()

    @invalidate_cache
    async def deleteall(self, user: User):
        """ Delete all notifications from the table for a particular user
        """
        self.connection.execute(
            "DELETE FROM `notifications` WHERE user_id = '{0.id}'".format(user))
        self.connection.commit()

    async def getallnotifications(self) -> List:
        """ Get all unique notifications
        """
        if not self.notif_cache:
            cursor = self.connection.execute(
                "SELECT notification FROM `notifications` GROUP BY notification")
            self.notif_cache = cursor.fetchall()
        return self.notif_cache

    async def getusers(self, notification: str) -> List:
        """ Gets all users of a notifications
        """
        if not self.user_cache:
            cursor = self.connection.execute(
                "SELECT user_id FROM notifications WHERE notification = '{}'".format(notification))
            self.user_cache = cursor.fetchall()
        return self.user_cache

    async def getnotifications(self, user: User) -> List:
        """ Gets all notifications for a user
        """
        cursor = self.connection.execute(
            "SELECT notification FROM notifications WHERE user_id = '{0.id}'".format(user))
        return cursor.fetchall()
