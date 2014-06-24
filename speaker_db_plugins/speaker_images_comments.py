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