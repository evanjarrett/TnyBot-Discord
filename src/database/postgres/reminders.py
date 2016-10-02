from typing import List
from urllib.parse import urlparse

from pgdb import connect


class RemindersDB:
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

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.connection is not None:
            print("closing the connection")
            self.connection.close()

    async def create_table(self):
        """ Creates a new table for the server if it doesn't exist"""
        q = '''CREATE TABLE IF NOT EXISTS reminders
            (user_id    TEXT    NOT NULL,
            message     TEXT    NOT NULL,
            remind_date INT     NOT NULL)'''
        self.connection.execute(q)
        self.connection.commit()

    async def insert(self, user_id: str, message: str = None, date: int = 0):
        """ Inserts a new reminder into the table.
        """
        self.connection.execute(
            "INSERT INTO reminders VALUES ({0}, '{1}', {2})".format(user_id, message, date))
        self.connection.commit()

    async def delete(self, dt: float):
        """ Delete expired reminders from the table.
        """
        self.connection.execute(
            "DELETE FROM reminders WHERE remind_date <= {}".format(dt + 60))
        self.connection.commit()

    async def get(self, dt: float) -> List:
        """ Gets the role info by its alias
        """
        self.connection.execute(
            "SELECT user_id, message, remind_date FROM reminders WHERE remind_date <= {}".format(dt + 60))
        return self.cursor.fetchall()
