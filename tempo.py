import rumps
from pathlib import Path
import sqlite3

DB_PATH = Path.home() / Path(".tempo.db")


LABELS = {
    "epoch": "Unix Epoch",
    "epoch_ms": "Unix Epoch / 1000",
    "cocoa": "Cocoa Core Data",
    "chrome": "Google Chrome",
}

ALGORITHMS = {
    LABELS["epoch"]: """datetime(?, 'unixepoch', ?)""",
    LABELS["epoch_ms"]: """datetime(? / 1000, 'unixepoch', ?)""",
    LABELS["cocoa"]: """datetime(? + 978307200, 'unixepoch', ?)""",
    LABELS["chrome"]: """datetime(? / 1000000 - 11644473600, 'unixepoch', ?)""",
}


class Tempo(object):
    def __init__(self):
        self.app = rumps.App("Tempo", "⏰")

        self.algorithms_button = rumps.MenuItem("⏰ Algorithms")
        self.algorithms = list(map(lambda label: rumps.MenuItem(LABELS[label], callback=self.set_algorithm), LABELS.keys()))

        self.modifier_button = rumps.MenuItem("🌎 Modifier")
        self.modifiers = list(
            map(
                lambda hr: rumps.MenuItem(f"{hr} hours", callback=self.set_modifier),
                range(-12, 13),
            )
        )

        self.enter_timestamp = rumps.MenuItem("👉 Enter timestamp", self.timestamp)

        self.app.menu = [
            [self.algorithms_button, self.algorithms],
            [self.modifier_button, self.modifiers],
            self.enter_timestamp,
        ]

        self.db = Database()
        self.db.tidy_db()

    def set_algorithm(self, algorithm):
        self.db.set_meta("algorithm", algorithm.title)

    def set_modifier(self, modifier):
        self.db.set_meta("modifier", modifier.title)

    def get_input(self):
        timestamp_window = rumps.Window("Enter your value...", "Timestamp").run()
        user_input = timestamp_window.text
        return user_input

    def timestamp(self, _):
        user_input = self.get_input()
        self.db.insert_timestamp(user_input)
        self.show_history()

    def show_history(self):
        result = self.db.get_timestamp()
        rumps.alert(title="Timestamp", message=result)
        self.app.menu.add(result)

    def run(self):
        self.app.run()


class Database:
    def __init__(self):
        self.setup_required = not DB_PATH.is_file()
        self.conn = sqlite3.connect(f"{DB_PATH.absolute()}")
        self.cursor = self.conn.cursor()
        if self.setup_required:
            self.setup()

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
        sql = f"""
            PRAGMA journal_mode = "WAL";

            CREATE TABLE timestamps (
                pk INTEGER PRIMARY KEY AUTOINCREMENT,
                user_input TEXT
            );

            CREATE TABLE meta (
                pk INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT,
                value TEXT
            );

            INSERT INTO meta (
                key, value
            ) values (
                "algorithm", "{LABELS['epoch']}"
            );

            INSERT INTO meta (
                key, value
            ) values (
                "modifier", "0 hours"
            );
        """
        self.executescript(sql)

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

    def insert_timestamp(self, user_input: str):
        algorithm = self.get_meta("algorithm")
        modifier = self.get_meta("modifier")
        sql = f"""
            INSERT INTO timestamps (
                user_input
            ) values (
                {ALGORITHMS[algorithm]}
            )
        """
        print(sql)
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

    def set_meta(self, key: str, value: str):
        sql = """
            UPDATE
                meta
            SET
                value = ?
            WHERE
                key = ?
        """
        self.execute(sql, (value, key))

    def get_meta(self, key):
        sql = """
            SELECT
                value
            FROM
                meta
            WHERE
                key = ?
            LIMIT
                1
        """
        result = self.execute(sql, (key,))
        return result[0][0]

    def __del__(self):
        self.conn.close()


if __name__ == "__main__":
    app = Tempo()
    app.run()
