from hashlib import md5, sha256

from speakerlib import niceify_number

import requests

from config import config

from fuzzywuzzy import process

class EventRecorder(object):

    def __init__(self, db):

        self.db = db
        #self.censored_words = self.db.execute('')


    def censor(*args, **kwargs):


        self = args[0]
        args = list(args)
        censored_words = self.db.execute("select word from badwords")
        bad_words = [row["word"] for row in censored_words]

        speech_text = kwargs.get("speech_text", None) or args[1]

        try:
            speech_text.decode("ascii")
        except UnicodeEncodeError:
            speech_text = " "

        speech_list = speech_text.split(" ")

        for phrase in bad_words:
            if process.extractOne(phrase, speech_list)[1] >= 90:
                speech_text = " "
                break

        for word in speech_list:
            if word.lower() in bad_words:
                speech_text = " "
                break

        if kwargs.get("speech_text", None):
            kwargs["speech_text"] = speech_text
        else:
            args[1] = speech_text

        return tuple(args)[1:], kwargs


    def post_to_slack(self, speech_text, record_utterance=False, **kwargs):
        #Skip plugins
        if speech_text[0] == "!":
            return

        if config.get("slack_url", None) and record_utterance:
            requests.post(config["slack_url"], data=speech_text)

    def record_utterance(self, speech_text, record_utterance=False, event_result=None):
        if not record_utterance or speech_text[0] == "!":
            return

        speech_text = speech_text.lower()

        sha = sha256()
        sha.update(speech_text)
        sha_hash = sha.hexdigest()

        matched_snippet = self.db.execute("SELECT votes FROM snippets where sha256=?", [sha_hash]).fetchone()

        if matched_snippet:
            votes = matched_snippet["votes"] + 1
            self.db.execute("UPDATE snippets set votes=? where sha256=?", [votes, sha_hash])
        else:
            self.db.execute("INSERT into snippets (sha256, speech_text, votes) VALUES (?, ?, 0) ", [sha_hash, speech_text])

    def record_sound_event(self, sound_name, event_result=None):

        matched_sound = self.db.execute("SELECT votes FROM sounds where name=?", [sound_name]).fetchone()

        if matched_sound:
            votes = matched_sound["votes"] + 1

            self.db.execute("UPDATE sounds set votes=? where name=?", [votes, sound_name])

    def queue_speech_for_tweet(self, speech_text, record_utterance=False, event_result=None):

        print record_utterance
        if not record_utterance:
            return

        if speech_text[0] == "!":
            return

        speech_text = speech_text[:139].replace("@","~")

        md5_hash = md5()
        md5_hash.update(speech_text.lower())
        md5_hash = md5_hash.hexdigest()

        try:
            check_existence = self.db.execute("SELECT * FROM publish_queue where md5_hash=?", [md5_hash]).next()
        except StopIteration:
            check_existence = False

        if not check_existence:

            self.db.execute("INSERT INTO publish_queue (tweet_text, md5_hash) VALUES (?, ?)", [speech_text, md5_hash])

    def queue_sound_for_tweet(self, name, event_result):

        matched_sound = self.db.execute("SELECT votes FROM sounds where name=?", [name]).fetchone()

        if matched_sound:
            text = "I just played %s for the %s time" % (name, niceify_number(matched_sound["votes"]))
            md5_hash = md5()
            md5_hash.update(text)
            md5_hash = md5_hash.hexdigest()

            self.db.execute("INSERT INTO publish_queue (tweet_text, md5_hash) VALUES (?, ?)", [text, md5_hash])




