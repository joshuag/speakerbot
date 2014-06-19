import os
import math
import subprocess

from collections import OrderedDict
from urllib import quote_plus

from listenable import listenable, event
from speaker_db import SpeakerDB

def split_text(text, length):

    split_list = [".", "!", ";", " and "]

    for split in split_list:

        phrases = split_and_keep(text, split)

        if len(phrases) == 1 and len(phrases[0]) > length:
            continue
        else:
            return phrases

    if len(phrases) == 1 and len(phrases[0]) > length:

        split_phrases = split_and_keep(phrases[0], " ")

        out_phrase = ""
        phrases = []

        for phrase in split_phrases:

            if len(out_phrase) + len(phrase) < length:
                out_phrase = out_phrase + phrase
            else:
                phrases.append(out_phrase)
                out_phrase = phrase

        phrases.append(out_phrase)

    return phrases

def split_and_keep(text, delimiter):

    split_items = text.split(delimiter)

    split_list = [item + delimiter for item in split_items if item != ""]

    split_list[-1] = split_list[-1].replace(delimiter, "")

    return split_list
    

class TextToSpeech(object):

    def __init__(self, speak_path="espeak", wpm=150):

        self.speak_path = speak_path
        self.wpm_string = "-s %s" % wpm 

    def say(self, text): 

        subprocess.call([self.speak_path, text, self.wpm_string])

    def say_api(self, text, url_string):

        if len(text) > 100:
            phrases = split_text(text, 100)
            for phrase in phrases:
                self.say_api(phrase, url_string)

            return

        text = quote_plus(text.encode("utf-8"))

        filename = "speech/%s.mp3" % text

        if not os.path.isfile(filename):
            f = open(filename, "w")
            subprocess.call(
                    ['curl','-A Mozilla', url_string % (text)], 
                    stdout=f)

        s = SoundEffect()
        s.play_sound(filename)

    def say_classy(self, text):
        
        url_string = u"http://translate.google.com/translate_tts?tl=en_gb&ie=UTF-8&q=%s"
        self.say_api(text, url_string)


class SoundEffect(object):

    def __init__(self, sound_player="mpg321", sound_dir="sounds"):
        self.sound_player = sound_player
        self.path = "%s/" % sound_dir

    def play(self, sound_file):

        file_path = self.path + sound_file

        self.play_sound(file_path)

    def play_sound(self, file_path):

        subprocess.call([self.sound_player, file_path])

@listenable
class Speakerbot(object):

    def __init__(self):

        self.db = SpeakerDB()
        self.snippets = OrderedDict()
        self.sounds = OrderedDict()

        self.listeners = {}

        self.load_sounds()

        self.se = SoundEffect()
        self.tts = TextToSpeech()

    def get_sound_score(self, sound):
        return int(sound["votes"]-sound["downvotes"]*math.pi*3)

    def load_sounds(self, score_cutoff=None):

        self.sounds = OrderedDict()

        sound_list = self.db.execute("SELECT * from sounds order by votes desc, name asc")

        for sound in sound_list:
            if score_cutoff and self.get_sound_score(sound) < score_cutoff:
                continue
            self.sounds[sound["name"]] = (sound["path"], sound["votes"], sound["cost"], sound["downvotes"], self.get_sound_score(sound))

        return self.sounds

    @event
    def play(self, name):

        self.se.play(self.sounds[name][0])


    def say(self, name="", speech_text=""):

        if name:
            speech_text = self.snippets[name]

        self.tts.say(speech_text)

    @event
    def say_classy(self, name="", speech_text=""):

        if name:    
            speech_text = self.snippets[name]

        self.tts.say_classy(speech_text)

    def add_sound_to_db(self, name, path, base_cost=0):

        self.db.execute("INSERT INTO sounds (name, path, votes, cost, base_cost) VALUES (?, ?, ?, ?, ?)", (name, path, 0, base_cost, base_cost))

        self.load_sounds()

