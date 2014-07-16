from util.instrumentation import time_instrument
from random import randrange
import datetime as dt

def record_wager(self, lucky_number, wager, outcome, chosen_number, win_multiplier, cheated_death):
    wager_time = dt.datetime.now().strftime("%s")

    self.execute("INSERT INTO wager_history (lucky_number, wager, outcome, wager_time, chosen_number, win_multiplier, cheated_death) VALUES (?, ?, ?, ?, ?, ?, ?)", [lucky_number, wager, outcome, wager_time, chosen_number, win_multiplier, cheated_death])

def add_comment(self, image, comment):

    self.execute("insert into image_comments (file_name, comment) values (?, ?)", [image, comment])

def get_image_comments(self, image):

    return self.execute("select comment from image_comments where file_name=?", [image])

def get_nsfw_images(self):

    return self.execute("select * from images where nsfw=1")

def get_top_images(self, num_images=20, order="desc"):

    if order == "desc":
        return self.execute("select * from images order by votes desc limit ?", [num_images])
    else:
        return self.execute("select * from images order by votes asc limit ?", [num_images])

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

def get_random_utterance(self, seed=None):
    #if this gets slow, it's because it selects the whole table first

    if seed:
        sql_seed = '%' + seed + '%'
        cursor = self.execute("SELECT speech_text FROM snippets where speech_text like ? ORDER BY Random() LIMIT 1", [sql_seed])
    else:
        cursor = self.execute("SELECT speech_text FROM snippets ORDER BY Random() LIMIT 1")

    try:
        result = cursor.next()
    except StopIteration:
        if seed:
            return "It seems as though nobody has mentioned %s" % seed

    return result["speech_text"]

def check_nsfw(self, image):

        nsfw = 0
        try:
            cursor = self.execute("select nsfw from images where file_name=?", [image])
            result = cursor.next()
            nsfw = int(result["nsfw"])
        except:
            pass

        return nsfw == 1

def add_image(self, file_name):
    image = None

    try:
        image = self.execute("select file_name from images where file_name=?", [file_name]).next()
    except StopIteration:
        image = None
    
    if not image:
        self.execute("INSERT INTO images (file_name, votes, nsfw) values (?, 0, 0)", [file_name])

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

        if nsfw == 1 or votes < -3:
            appropriate = False

    except TypeError:
        appropriate = True
    except StopIteration:
        appropriate = True

    return appropriate

@time_instrument
def get_random_image(self):

    min_votes = self.execute("SELECT min(votes) as min_votes FROM images where votes >= 0 and nsfw <> 1").next()["min_votes"]

    image_count = self.execute("SELECT count(*) as image_count FROM images where votes = ? and nsfw <> 1", [min_votes]).next()["image_count"]

    if image_count == 0:
        return ""

    image_limit = randrange(0, image_count)

    return self.execute("SELECT file_name FROM images where votes between -5 and ? and nsfw <> 1 LIMIT ?, 1", [min_votes, image_limit]).next()["file_name"]
