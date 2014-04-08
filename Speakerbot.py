import time     #for delay
import requests
import subprocess
import os
import sys
from hashlib import md5, sha256
from urllib import quote_plus
from collections import OrderedDict

from speaker_db import SpeakerDB

from IPython import embed

class TextToSpeech(object):

    def __init__(self, speak_path="espeak", wpm=150):
        self.speak_path = speak_path
        self.wpm_string = "-s %s" % wpm 

    def say(self, text): 
        subprocess.call([self.speak_path, text, self.wpm_string])

    def say_classy(self, text):

        if len(text) > 100:
            phrases = text.split(".")
            if len(phrases) == 1:
                text = text[:99]
            else:
                for phrase in phrases:
                    self.say_classy(phrase)
            return

        text = quote_plus(text)

        filename = "speech/%s.mp3" % text

        if not os.path.isfile(filename):
            f = open(filename, "w")
            subprocess.call(
                    ['curl','-A Mozilla',"http://translate.google.com/translate_tts?tl=en_gb&ie=UTF-8&q=%s" % (text)], 
                    stdout=f)

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

        self.db = SpeakerDB()
        self.snippets = OrderedDict()
        self.sounds = OrderedDict()

        self.load_sounds()

        self.se = SoundEffect()
        self.tts = TextToSpeech()

    def load_sounds(self):

        self.sounds = OrderedDict()

        sound_list = self.db.execute("SELECT * from sounds order by votes desc, name asc")

        for sound in sound_list:
            self.sounds[sound["name"]] = (sound["path"], sound["votes"])

        return self.sounds

    def play(self, name):

        self.record_sound_event(name)
        self.se.play(self.sounds[name][0])

    def say(self, name="", speech_text=""):

        if name:
            speech_text = self.snippets[name]

        self.record_utterance(speech_text)

        self.tts.say(speech_text)

    def say_classy(self, name="", speech_text=""):

        if name:    
            speech_text = self.snippets[name]

        self.record_utterance(speech_text)

        self.tts.say_classy(speech_text)        

    def record_utterance(self, speech_text):

        sha = sha256()
        sha.update(speech_text)
        sha_hash = sha.hexdigest()

        matched_snippet = self.db.execute("SELECT votes FROM snippets where sha256=?", [sha_hash]).fetchone()

        if matched_snippet:
            votes = matched_snippet["votes"] + 1

            self.db.execute("UPDATE snippets set votes=? where sha256=?", [votes, sha_hash])
        else:
            self.db.execute("INSERT into snippets (sha256, speech_text, votes) VALUES (?, ?, 0) ", [sha_hash, speech_text])

    def record_sound_event(self, sound_name):

        matched_sound = self.db.execute("SELECT votes FROM sounds where name=?", [sound_name]).fetchone()

        if matched_sound:
            votes = matched_sound["votes"] + 1

            self.db.execute("UPDATE sounds set votes=? where name=?", [votes, sound_name])

    def add_sound_to_db(self, name, path):
        
        self.db.execute("INSERT INTO sounds VALUES (?, ?)", (name, path))

        self.load_sounds()


