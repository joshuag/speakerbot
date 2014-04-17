from db.base_db import base_db
import sqlite3

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

    def _migrate_1(self):

        self.execute("create table publish_queue (tweet_text text)")

    def _migrate_2(self):

        self.execute("create table users (user_name text, password text)")

    def _migrate_3(self):

        self.execute("create table groups (group_id text, group_name text)")
        self.execute("create table group_membership (group_id text, user_name text)")

        from hashlib import sha256
        group_name = "admin"
        sha = sha256()
        sha.update(group_name)
        group_name_hexdigest = sha.hexdigest()

        self.execute("insert into groups (group_id, group_name) VALUES (?, ?)", [group_name, group_name_hexdigest])
        self.execute("insert into group_membership (group_id, user_name) VALUES (?, ?)", [group_name_hexdigest, "*"])

    def _migrate_4(self):

        self.execute("delete from snippets")

    def _migrate_5(self):

        self.execute("ALTER TABLE sounds ADD COLUMN cost INTEGER")

    def _migrate_6(self):
        self.execute("delete from publish_queue")
        self.execute("create table images (file_name text, votes integer, nsfw integer)")

    def _migrate_7(self):
        self.execute("create table image_comments (comment text, file_name text)")

    def _migrate_8(self):
        self.execute("ALTER TABLE sounds ADD COLUMN base_cost INTEGER")

    def add_comment(self, image, comment):

        self.execute("insert into image_comments (file_name, comment) values (?, ?)", [image, comment])

    def get_image_comments(self, image):

        return self.execute("select comment from image_comments where file_name=?", [image])

    def get_image_votes(self, image):

        votes = 0

        try:
            cursor = self.execute("select votes from images where file_name=?", [image])
            result = cursor.next()
            votes = int(result["votes"])
        except StopIteration:
            self.execute("insert into images (file_name) values (?)", [image])
            votes = 0
        except:
            votes = 0

        return votes

    def check_sfw(self, image):
        
        try:
            cursor = self.execute("select nsfw from images where file_name=?", [image])
            result = cursor.next()
            nsfw = int(result["nsfw"])
        except sqlite3.OperationalError:
            nsfw = 0
        except TypeError:
            nsfw = 0

        except StopIteration:
            nsfw = 0

        return nsfw != 1


if __name__ == "__main__":
    db = SpeakerDB(db_path="speakerbot.db")
