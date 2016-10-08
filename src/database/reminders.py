from typing import List

from .database import Database


class RemindersDB(Database):
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
            self.query("INSERT INTO reminders VALUES (%(user)s, %(message)s, %(date)s)"),
            {"user": user_id, "message": message, "date": date})
        self.connection.commit()

    async def delete(self, dt: float):
        """ Delete expired reminders from the table.
        """
        self.connection.execute(
            self.query("DELETE FROM reminders WHERE remind_date <=  %(date)s)"),
            {"date": dt + 60})
        self.connection.commit()

    async def get(self, dt: float) -> List:
        """ Gets the role info by its alias
        """
        self.connection.execute(
            self.query("SELECT user_id, message, remind_date FROM reminders WHERE remind_date <= %(date)s)"),
            {"date": dt + 60})
        return self.cursor.fetchall()
