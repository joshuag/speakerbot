import os
import math
import subprocess
from collections import OrderedDict

from listenable import listenable, event
from speaker_db import SpeakerDB
from dynamic_class import attach_methods, PluggableObject, MissingPluginException
from sounds import Sound, SoundPlayer
from util.speech_providers import GoogleTextToSpeech
from util.words import parse_and_fill_mad_lib

from config import config

try:   
    import uwsgi
    def lock(f):
        def locked(*args, **kwargs):
            if uwsgi.i_am_the_spooler():
                return
            uwsgi.lock()
            try:
                return f(*args, **kwargs)
            finally:
                uwsgi.unlock()
        return locked

except ImportError:
    def lock(f):
        return f

@listenable
@attach_methods("speakerbot_plugins")
class Speakerbot(PluggableObject):

    def __init__(self, db=SpeakerDB, speech_provider=GoogleTextToSpeech):

        self.db = db()
        self.sound_player = SoundPlayer(config['sound_dir'], config['sound_player'])
        
        self.sounds = OrderedDict()

        self.listeners = {}

        self.load_sounds()

        self.tts = speech_provider()

        

    def run_filters(self, text):
    
        text = parse_and_fill_mad_lib(text)

        return text

    def load_sounds(self, score_cutoff=None):

        self.sounds = OrderedDict()

        sound_list = self.db.execute("SELECT * from sounds order by votes desc, name asc")

        for dbsound in sound_list:
            sound = Sound(
                name=dbsound["name"],
                file_name=dbsound["path"],
                votes=dbsound["votes"],
                cost=dbsound["cost"],
                downvotes=dbsound["downvotes"],
                sound_player=self.sound_player
            )
            if score_cutoff and sound.get_score() < score_cutoff:
                continue
            self.sounds[sound.name] = sound

        return self.sounds

    def _play(self, name):
        self.sounds[name].play()

    @lock
    @event
    def play(self, name):
        self._play(name)

    @event #we may want to record the output of the filtered speech
    def speech_provider_say(self, speech_text, record_utterance):
        self.tts.say(speech_text)

    @lock
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

