import os
import math
import subprocess

from collections import OrderedDict

from listenable import listenable, event
from speaker_db import SpeakerDB
from dynamic_class import attach_methods, PluggableObject, MissingPluginException
from sounds import SoundEffect
from util.speech_providers import GoogleTextToSpeech
from util.words import parse_and_fill_mad_lib

try:   
    from uwsgidecorators import lock

except ImportError:
    def lock(f):
        return f

@listenable
@attach_methods("speakerbot_plugins")
class Speakerbot(PluggableObject):

    def __init__(self, db=SpeakerDB, speech_provider=GoogleTextToSpeech):

        self.db = db()
        self.sounds = OrderedDict()

        self.listeners = {}

        self.load_sounds()

        self.se = SoundEffect()
        self.tts = speech_provider()

    def run_filters(self, text):
    
        text = parse_and_fill_mad_lib(text)

        return text

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

    @event #we may want to record the output of the filtered speech
    def speech_provider_say(self, speech_text, record_utterance):
        self.tts.say(speech_text)

    @event
    def say(self, speech_text="", record_utterance=False):

        token = None
        argument = None

        if speech_text[0] == "!":
            space_pos = speech_text.find(" ")
            if space_pos > 0:
                token = speech_text[1:space_pos]
                argument = speech_text[space_pos:]
            else:
                token = speech_text[1:]

            try:
                if argument:
                    speech_text = self.dispatch_plugin(token, argument.strip())
                else:
                    speech_text = self.dispatch_plugin(token)

            except TypeError:
                
                speech_text = "I need an argument for that function, dummy."

            except MissingPluginException:

                speech_text = "I don't have a plugin called %s" % token

        if speech_text:
            self.speech_provider_say(self.run_filters(speech_text), record_utterance)


    def add_sound_to_db(self, name, path, base_cost=0):

        self.db.execute("INSERT INTO sounds (name, path, votes, cost, base_cost) VALUES (?, ?, ?, ?, ?)", (name, path, 0, base_cost, base_cost))

        self.load_sounds()

