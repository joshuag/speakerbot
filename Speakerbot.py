import time     #for delay
import requests
import subprocess
import os
import sys
import sqlite3
from hashlib import md5
from urllib import quote_plus

from IPython import embed

class TextToSpeech(object):

    def __init__(self, speak_path="espeak", wpm=150):
        self.speak_path = speak_path
        self.wpm_string = "-s %s" % wpm 

    def say(self, text): 
        subprocess.call([self.speak_path, text, self.wpm_string])

    def say_classy(self, text):
        text = quote_plus(text)

        filename = "speech/%s.mp3" % text

        if not os.path.isfile(filename):
            f = open(filename, "w")
            subprocess.call(['curl','-A Mozilla',"http://translate.google.com/translate_tts?tl=en_gb&ie=UTF-8&q=%s" % (text)], stdout=f)

        s = SoundEffect()
        s.play_sound(filename)

class SoundEffect(object):

    def __init__(self, sound_player="mpg321", sound_dir="sounds"):
        self.sound_player = sound_player
        self.path = "%s/" % sound_dir

    def play(self, sound_file):

        file_path = self.path + sound_file

        self.play_sound(file_path)

    def play_sound(self, file_path):

        subprocess.call([self.sound_player, file_path])

class Speakerbot(object):

    def __init__(self):

        self.conn = sqlite3.connect("speakerbot.db")
        self.snippets = {}
        self.sounds = {}

        self.load_sounds()
        self.load_snippets()

        self.se = SoundEffect()
        self.tts = TextToSpeech()

    def load_sounds(self):

        self.sounds = {}
        sound_list = self.conn.execute("SELECT * from sounds order by name")

        for sound in sound_list:
            self.sounds[sound[0]] = sound[1]

    def load_snippets(self):

        self.snippets = {}
        snippet_list = self.conn.execute("SELECT * FROM snippets")

        for snippet in snippet_list:
            self.snippets[snippet[0]] = snippet[1]

    def play(self, name):

        self.se.play(self.sounds[name])

    def say(self, name="", speech_text=""):

        if name:
            speech_text = self.snippets[name]

        self.tts.say(speech_text)

    def say_classy(self, name="", speech_text=""):

        if name:    
            speech_text = self.snippets[name]

        self.tts.say_classy(speech_text)        

    def _create_tables(self):

        self.conn.execute("CREATE TABLE sounds (name text, path text)")
        self.conn.execute("CREATE TABLE snippets (name text, speech_text text)")

        self.conn.commit()

    def _create_indexes(self):

        self.conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS UniqueSound ON sounds (name)")
        self.conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS UniqueSnippet ON snippets (name)")

    def add_sound_to_db(self, name, path):
        
        
        self.conn.execute("INSERT INTO sounds VALUES (?, ?)", (name, path))

        self.conn.commit()

        self.load_sounds()

    def add_snippet_to_db(self, name, speech_text):

        self.conn.execute("INSERT INTO snippets VALUES (?, ?)", (name, speech_text))

        self.conn.commit()

        self.load_snippets()


