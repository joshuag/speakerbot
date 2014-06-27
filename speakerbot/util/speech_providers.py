import os
import subprocess
from urllib import quote_plus

from text_manipulators import split_text
from sounds import SoundEffect

class GoogleTextToSpeech(object):

    def __init__(self, url_string=None):

        self.url_string = url_string
        if not url_string:
            self.url_string = u"http://translate.google.com/translate_tts?tl=en_gb&ie=UTF-8&q=%s"

    def say(self, text):

        if len(text) > 100:
            phrases = split_text(text, 100)
            for phrase in phrases:
                self.say(phrase)

            return

        text = quote_plus(text.encode("utf-8"))

        filename = "speech/%s.mp3" % text

        if not os.path.isfile(filename):
            f = open(filename, "w")
            subprocess.call(
                    ['curl','-A Mozilla', self.url_string % (text)], 
                    stdout=f)

        s = SoundEffect()
        s.play_sound(filename)

class EspeakTextToSpeech(object):

    def __init__(self, speak_path="espeak", wpm=150):

        self.speak_path = speak_path
        self.wpm_string = "-s %s" % wpm 

    def say(self, text): 

        subprocess.call([self.speak_path, text, self.wpm_string])