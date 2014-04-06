from base_db import base_db

class SpeakerDB(base_db):

    def _migrate_0(self):

        try:
            self.execute("CREATE table db_version (version int);")
        except sqlite3.OperationalError:
            pass

        self.execute("insert into db_version (version) VALUES (1);")

    def _migrate_1(self):

        self.execute("create table publish_queue (tweet_text text)")

    def _migrate_2(self):

        self.execute("create table users (user_name text, password text)")


if __name__ == "__main__":
    db = SpeakerDB(db_path="../speakerbot.db")
    #db.run_migrations()