from db.base_db import base_db
import sqlite3
import datetime as dt

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

        self.execute("insert into db_version (version) values(0)")

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

    def _migrate_9(self):

        self.execute("create table bank_account (balance INTEGER)")
        self.execute("insert into bank_account (balance) values(0)")

    def _migrate_10(self):

        self.execute("ALTER table bank_account add column free_play_timeout INTEGER NOT NULL DEFAULT 0")

    def _migrate_11(self):

        self.execute("ALTER table bank_account add column last_withdrawal_time INTEGER NOT NULL DEFAULT 0")

    def _migrate_12(self):

        #need to seed these, otherwise the string formatting on the page gets jacked.
        self.execute("update sounds set cost=0 where cost is null")
        self.execute("update sounds set base_cost=0 where base_cost is null")

    def _migrate_13(self):
        self.execute('CREATE TABLE person (name text NOT NULL, theme_song text, last_theme_play_time INTEGER NOT NULL DEFAULT 0);')
        self.execute('CREATE UNIQUE INDEX UniquePerson ON person (name);')

    def _migrate_14(self):
        self.execute('CREATE TABLE wager_history (wager INTEGER NOT NULL, outcome INTEGER NOT NULL, wager_time INTEGER NOT NULL, chosen_number INTEGER NOT NULL, win_multiplier INTEGER NOT NULL, cheated_death INTEGER NOT NULL);')

    def _migrate_15(self):
        self.execute("ALTER table wager_history ADD COLUMN lucky_number INTEGER NOT NULL DEFAULT 0")



    def record_wager(self, lucky_number, wager, outcome, chosen_number, win_multiplier, cheated_death):
        wager_time = dt.datetime.now().strftime("%s")

        self.execute("INSERT INTO wager_history (lucky_number, wager, outcome, wager_time, chosen_number, win_multiplier, cheated_death) VALUES (?, ?, ?, ?, ?, ?, ?)", [lucky_number, wager, outcome, wager_time, chosen_number, win_multiplier, cheated_death])

    def get_wager_history(self, limit=50):

        return self.execute ("select datetime(wager_time, 'unixepoch') as wager_time, lucky_number, wager, outcome, chosen_number, win_multiplier, cheated_death from wager_history order by wager_time desc LIMIT ?", [limit])

    def get_lucky_numbers(self):
        pass


    def get_number_occurence(self):
        return self.execute("select chosen_number, count(chosen_number) as occurences, sum(case when outcome < 1 then 1 else 0 end) as negative_outcomes, sum(case when outcome > 1 then 1 else 0 end)  as successful_outcomes from wager_history group by chosen_number")

    def get_multiplier_occurence(self):
        return self.execute("select win_multiplier, count(win_multiplier) as occurences, sum(case when outcome < 1 then 1 else 0 end) as negative_outcomes, sum(case when outcome > 1 then 1 else 0 end)  as successful_outcomes from wager_history group by win_multiplier")

    def get_wagers_and_outcomes_by_day(self, limit=30):

        return self.execute("select date(wager_time, 'unixepoch') as wager_date, sum(wager) as amount_wagered, sum(outcome) as outcome from wager_history group by date(wager_time, 'unixepoch') limit ?", [limit])

    def get_wagers_by_outcome(self, limit=10):

        return self.execute("select wager, sum(case when outcome > 1 then 1 else 0 end)  as successful_outcomes, sum(case when outcome < 1 then 1 else 0 end) as negative_outcomes from wager_history group by wager limit ?", [limit])


    def get_aggregate_wager_stats(self, start=0, end=4000000000):

        results = self.execute("""
                SELECT 
                    AVG(wager) as average_wager, 
                    AVG(outcome) as average_outcome, 
                    MAX(wager) as max_wager, 
                    SUM(wager) as total_wagered, 
                    SUM(outcome) as net_winnings, 
                    AVG(win_multiplier) as average_multiplier,
                    SUM(cheated_death) as cheated_death
                FROM 
                wager_history
                where wager_time > ? and wager_time < ?
                """, [start, end])
        try:
            results = results.next()
            results["average_outcome"] = int(round(results["average_outcome"]))
            results["average_wager"] = int(round(results["average_wager"]))
            results["average_multiplier"] = int(round(results["average_multiplier"]))
            results["roi"] = str(int(round(results["average_outcome"] / results["average_wager"], 2) * 100)) + "%"
        except:
            results = None
            pass

        return results

    def add_comment(self, image, comment):

        self.execute("insert into image_comments (file_name, comment) values (?, ?)", [image, comment])

    def get_image_comments(self, image):

        return self.execute("select comment from image_comments where file_name=?", [image])

    def get_nsfw_images(self):

        return self.execute("select * from images where nsfw=1")

    def get_top_images(self, num_images=20):

        return self.execute("select * from images order by votes desc limit ?", [num_images])

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

    def get_random_comment(self):
        #if this gets slow, it's because it selects the whole table first
        cursor = self.execute("SELECT distinct comment FROM image_comments ORDER BY Random() LIMIT 1")

        result = cursor.next()

        return result["comment"]

    def get_random_utterance(self):
        #if this gets slow, it's because it selects the whole table first
        cursor = self.execute("SELECT speech_text FROM snippets ORDER BY Random() LIMIT 1")

        result = cursor.next()

        return result["speech_text"]


    def get_people(self):

        return self.execute("select * from person order by name")
        
    def add_person(self, name):

        self.execute("insert into person (name) values (?)", [name,])

    def remove_person(self, name):

        self.execute("DELETE FROM person WHERE name = ?", [name,])

    def check_appropriate(self, image):
        appropriate = True
        try:
            cursor = self.execute("select nsfw, votes from images where file_name=?", [image])
            result = cursor.next()
            if result["nsfw"]:
                nsfw = int(result["nsfw"])
            else:
                nsfw = 0

            if result["votes"]:
                votes = int(result["votes"])
            else:
                votes = 0

            if nsfw == 1 or votes < 0:
                appropriate = False

        except sqlite3.OperationalError:
            appropriate = True
        except TypeError:
            appropriate = True
        except StopIteration:
            appropriate = True

        return appropriate


if __name__ == "__main__":
    db = SpeakerDB(db_path="speakerbot.db")
