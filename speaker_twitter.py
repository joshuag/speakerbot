from random import randrange
from time import sleep

from config import config
from speaker_db import SpeakerDB
from Speakerbot import Speakerbot
from speakerlib import minimize_string

from twython import Twython
from twython.exceptions import TwythonError

class SpeakerTwitter(object):

    def __init__(self, speakerbot=None):
        self.db = SpeakerDB()
        self.theme_songs = {}
        self.speakerbot = speakerbot
        self.config = config["twitter"]
        self.twitter = Twython(
            self.config["app_key"], 
            self.config["app_secret"], 
            self.config["oauth_token"], 
            self.config["oauth_token_secret"])

    def publish_from_queue(self):

        try:
            tweet_record = self.db.execute("select id, tweet_text from publish_queue limit 1").next()
        except StopIteration:
            tweet_record = False

        if tweet_record:
            tweet_text = tweet_record["tweet_text"]
            tweet_id = tweet_record["id"]

            try:

                self.twitter.update_status(status=tweet_text)
                self.db.execute("delete from publish_queue where id=?", [tweet_id])

            except TwythonError:
                pass


if __name__ == "__main__":
    sb = Speakerbot()
    st = SpeakerTwitter(speakerbot=sb)

    while True:
        
        st.publish_from_queue()

        sleep(randrange(60,180))
        

