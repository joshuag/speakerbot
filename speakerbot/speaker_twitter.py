from random import randrange
from time import sleep

from twython import Twython
from twython.exceptions import TwythonError

from config import config
from speaker_db import SpeakerDB
from Speakerbot import Speakerbot
import requests

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

        forbidden_words = ["nohodo", "vk", "vertical knowledge", "d "]

        try:
            tweet_record = self.db.execute("select id, tweet_text from publish_queue limit 1").next()
        except StopIteration:
            tweet_record = False

        if tweet_record:
            tweet_text = unicode(tweet_record["tweet_text"])
            tweet_id = tweet_record["id"]

            requests.post("https://thevk.slack.com/services/hooks/slackbot?token=MSI1tk9s0IZrTRApssF5f1sC&channel=%23random", data=tweet_text)

            tweet_this = True
            for word in forbidden_words:
                if word in tweet_text.lower():
                    tweet_this = False

            if tweet_this:
                try:
                    self.twitter.update_status(status=tweet_text)
                except TwythonError as e:
                    print str(e)
                    print "---------"
                    print tweet_text
                    pass
                
            self.db.execute("delete from publish_queue where id=?", [tweet_id])



if __name__ == "__main__":
    sb = Speakerbot()
    st = SpeakerTwitter(speakerbot=sb)

    while True:
        
        st.publish_from_queue()

        sleep(180)
        

