from base_db import base_db

class SpeakerDB(base_db):

    def __init__(self, db_path="speakerbot.db"):
        super(SpeakerDB, self).__init__(db_path=db_path)

    def _migrate_0(self):

        try:
            self.execute("CREATE table db_version (version int);")
            self.execute('CREATE TABLE "snippets" ("speech_text" text, "votes" INTEGER NOT NULL  DEFAULT 0, "name" text, "sha256" text);')
            self.execute('CREATE TABLE sounds (name text, path text, "votes" INTEGER NOT NULL  DEFAULT 0);')
            self.execute('CREATE UNIQUE INDEX UniqueSound ON sounds (name);')
            self.execute('CREATE UNIQUE INDEX UniqueSpeech ON snippets (speech_text);') 
        except sqlite3.OperationalError:
            pass

        self.execute("insert into db_version (version) VALUES (1);")

    def _migrate_1(self):

        self.execute("create table publish_queue (tweet_text text)")

    def _migrate_2(self):

        self.execute("create table users (user_name text, password text)")


if __name__ == "__main__":
    db = SpeakerDB(db_path="../speakerbot.db")
