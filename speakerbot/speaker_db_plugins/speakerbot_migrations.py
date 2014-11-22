from hashlib import sha256

def _migrate_0(self):

    self.execute("CREATE table db_version (version int);")
    self.execute('CREATE TABLE snippets (speech_text text, votes INTEGER NOT NULL  DEFAULT 0, name text, sha256 text);')
    self.execute('CREATE TABLE sounds (name text, path text, votes INTEGER NOT NULL  DEFAULT 0);')
    self.execute('CREATE UNIQUE INDEX UniqueSound ON sounds (name(50));')
    self.execute('CREATE UNIQUE INDEX UniqueSpeech ON snippets (sha256(64));') 
    self.execute("INSERT INTO db_version (version) VALUES (0)")

def _migrate_1(self):
    if self.settings["driver"] == "mysql":
        self.execute("CREATE TABLE publish_queue (tweet_text text)")

    if self.settings["driver"] == "sqlite3":
        self.execute("CREATE TABLE publish_queue (id int PRIMARY KEY, tweet_text text, MD5_HASH text)")        

def _migrate_2(self):

    self.execute("CREATE TABLE users (user_name text, password text)")

def _migrate_3(self):

    self.execute("CREATE TABLE groups (group_id text, group_name text)")
    self.execute("CREATE TABLE group_membership (group_id text, user_name text)")

    group_name = "admin"
    sha = sha256()
    sha.update(group_name)
    group_name_hexdigest = sha.hexdigest()

    self.execute("INSERT INTO groups (group_id, group_name) VALUES (?, ?)", [group_name, group_name_hexdigest])
    self.execute("INSERT INTO group_membership (group_id, user_name) VALUES (?, ?)", [group_name_hexdigest, "*"])

def _migrate_4(self):

    self.execute("DELETE FROM snippets")

def _migrate_5(self):

    self.execute("ALTER TABLE sounds ADD COLUMN cost INTEGER")

def _migrate_6(self):

    self.execute("DELETE FROM publish_queue")
    self.execute("CREATE TABLE images (file_name text, votes integer, nsfw integer)")

def _migrate_7(self):

    self.execute("CREATE TABLE image_comments (comment text, file_name text)")

def _migrate_8(self):

    self.execute("ALTER TABLE sounds ADD COLUMN base_cost INTEGER")

def _migrate_9(self):

    self.execute("CREATE TABLE bank_account (balance INTEGER)")
    self.execute("INSERT INTO bank_account (balance) VALUES (0)")

def _migrate_10(self):

    self.execute("ALTER TABLE bank_account add column free_play_timeout INTEGER NOT NULL DEFAULT 0")

def _migrate_11(self):

    self.execute("ALTER TABLE bank_account add column last_withdrawal_time INTEGER NOT NULL DEFAULT 0")

def _migrate_12(self):

    #need to seed these, otherwise the string formatting on the page gets jacked.
    self.execute("UPDATE sounds SET cost=0 WHERE cost is null")
    self.execute("UPDATE sounds SET base_cost=0 WHERE base_cost is null")

def _migrate_13(self):
    self.execute('CREATE TABLE person (name text NOT NULL, theme_song text, last_theme_play_time INTEGER NOT NULL DEFAULT 0);')
    self.execute('CREATE UNIQUE INDEX UniquePerson ON person (name(50));')

def _migrate_14(self):
    self.execute('CREATE TABLE wager_history (wager INTEGER NOT NULL, outcome INTEGER NOT NULL, wager_time INTEGER NOT NULL, chosen_number INTEGER NOT NULL, win_multiplier INTEGER NOT NULL, cheated_death INTEGER NOT NULL);')

def _migrate_15(self):
    self.execute("ALTER TABLE wager_history ADD COLUMN lucky_number INTEGER NOT NULL DEFAULT 0")

def _migrate_16(self):

    self.execute("ALTER TABLE sounds add column downvotes INTEGER NOT NULL DEFAULT 0")

def _migrate_17(self):

    self.execute("ALTER TABLE images ADD INDEX (file_name(20))")

def _migrate_18(self):
    self.execute("ALTER TABLE image_comments ADD INDEX (file_name(20))")
    self.execute("ALTER TABLE sounds ADD INDEX (name(50)) USING BTREE")
    self.execute("ALTER TABLE sounds ADD INDEX (votes) USING BTREE")

def _migrate_19(self):
    self.execute("ALTER TABLE images ADD INDEX (votes) USING BTREE")
    self.execute("ALTER TABLE images ADD INDEX (nsfw) USING BTREE")

def _migrate_20(self):
    if self.settings["driver"] == 'mysql':
        self.execute("ALTER TABLE publish_queue ADD id INT NOT NULL AUTO_INCREMENT PRIMARY KEY")

def _migrate_21(self):
    if self.settings["driver"] == 'mysql':
        self.execute("ALTER TABLE publish_queue ADD md5_hash varchar(64);")
        self.execute("UPDATE publish_queue set md5_hash=MD5(tweet_text);")
        self.execute("CREATE INDEX md5_hash ON publish_queue (md5_hash(64));")

def _migrate_22(self):
    self.execute("CREATE TABLE field_values (field_name VARCHAR(64) NOT NULL, field_value VARCHAR(256) NOT NULL);")
    self.execute("CREATE INDEX field_name ON field_values (field_name) USING HASH")

def _migrate_23(self):
    self.execute("ALTER TABLE sounds ADD COLUMN date_added INTEGER NOT NULL DEFAULT 0")

def _migrate_24(self):
    self.execute("CREATE TABLE macros (name varchar(50), manifest text)")
