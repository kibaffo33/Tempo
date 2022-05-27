import rumps
from pathlib import Path
import sqlite3

DB_PATH = Path.home() / Path(".tempo.db")


class Tempo(object):
    def __init__(self):
        self.app = rumps.App("Tempo", "⏰")
        self.ts_button = rumps.MenuItem("⏰ Timestamp", callback=self.timestamp)
        self.tsm_button = rumps.MenuItem("⏰ Timestamp / 1000", callback=self.timestamp_ms)
        self.modifier_button = rumps.MenuItem("🌎 Modifier")
        self.modifiers = list(
            map(
                lambda hr: rumps.MenuItem(f"{hr} hours", callback=self.set_modifier),
                range(-12, 13),
            )
        )
        self.app.menu = [
            self.ts_button,
            self.tsm_button,
            [self.modifier_button, self.modifiers],
        ]
        self.db = Database()

    def set_modifier(self, modifier):
        self.db.set_modifier(modifier.title)

    def get_input(self):
        timestamp_window = rumps.Window("Enter your value...", "Timestamp").run()
        user_input = timestamp_window.text
        return user_input

    def timestamp(self, _):
        user_input = self.get_input()
        self.db.insert(user_input, False)
        self.show_history()

    def timestamp_ms(self, _):
        user_input = self.get_input()
        self.db.insert(user_input, True)
        self.show_history()

    def show_history(self):
        result = self.db.get_timestamp()
        rumps.alert(title="Timestamp", message=result)
        self.app.menu.add(result)

    def run(self):
        self.app.run()


class Database:
    def __init__(self):
        self.conn = sqlite3.connect(f"{DB_PATH}")
        self.cursor = self.conn.cursor()
        exists = self.cursor.fetchone()
        self.setup()
        self.tidy_db()

    def execute(self, sql: str, values=None):
        if values:
            self.cursor.execute(sql, values)
        else:
            self.cursor.execute(sql)
        self.conn.commit()
        results = self.cursor.fetchall()
        return results

    def executescript(self, script: str):
        self.cursor.executescript(script)
        self.conn.commit()

    def setup(self):
        sql = """
            PRAGMA journal_mode = "WAL";

            CREATE TABLE if not exists timestamps (
                pk INTEGER PRIMARY KEY AUTOINCREMENT,
                user_input TEXT
            );

            CREATE TABLE IF NOT EXISTS meta (
                pk INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT,
                value TEXT
            );
        """
        self.executescript(sql)
        sql = """SELECT COUNT(*) FROM meta"""
        meta = self.execute(sql)
        if meta[0][0] == 0:
            sql = """
                INSERT INTO meta (
                    key, value
                ) values (
                    "modifier", "0 hours"
                )
            """
            self.execute(sql)
        else:
            self.set_modifier("0 hours")

    def insert(self, user_input: str, milliseconds: bool):
        modifier = self.get_modifier()
        if milliseconds:
            sql = """
                INSERT INTO timestamps (
                    user_input
                ) values (
                    datetime(? / 1000, 'unixepoch', ?)
                )
            """
        else:
            sql = """
                INSERT INTO timestamps (
                    user_input
                ) values (
                    datetime(?, 'unixepoch', ?)
                )
            """
        self.execute(sql, (user_input, modifier))

    def get_timestamp(self):
        sql = """
            SELECT
                user_input
            FROM
                timestamps
            ORDER BY
                pk DESC
            LIMIT
                1
        """
        result = self.execute(sql)
        return result[0][0]

    def tidy_db(self):
        sql = """
            DELETE FROM
                timestamps
            WHERE
                pk NOT IN (
                    SELECT 
                        pk 
                    FROM 
                        timestamps
                    ORDER BY 
                        pk DESC 
                    LIMIT 
                        1000
                )
        """
        self.execute(sql)

    def set_modifier(self, modifier: str):
        sql = """
            UPDATE
                meta
            SET 
                value = ?
            WHERE
                key = "modifier"
        """
        self.execute(sql, (modifier,))

    def get_modifier(self):
        sql = """
            SELECT
                value
            FROM
                meta
            WHERE
                key = "modifier"
            LIMIT
                1
        """
        result = self.execute(sql)
        return result[0][0]

    def __del__(self):
        self.conn.close()


if __name__ == "__main__":
    app = Tempo()
    app.run()
