import datetime
import json

from os import listdir, getcwd
from os.path import isfile, join
from random import choice

import zc.lockfile

from config import config
from speaker_db import SpeakerDB
from Speakerbot import SoundEffect
from speakerbot_plugins import *

def parse_and_route_speech(speech_func, text):
    
    actions = {
        'random':random_utterance,
        'dada':dada,
        'slinging':slinging_burgers,
        'weather':weather,
        'lunch': lunch,
        'datefact':datefact,
        'horoscope':horoscope,
        'yoda':yoda
    }
    
    token = None
    argument = None

    if text[0] == "!":
        space_pos = text.find(" ")
        if space_pos > 0:
            token = text[1:space_pos]
            argument = text[space_pos:]
        else:
            token = text[1:]

        method = actions.get(token, None)
        
        if method:
            try:
                if argument:
                    text_output = method(argument.strip())
                else:
                    text_output = method()

                text = text_output

            except TypeError:
                text = "I need an argument for that function, dummy."


    if text:
        play_speech(speech_func, run_filters(text))

def queue_speech_for_tweet(*args, **kwargs):
    text = kwargs["speech_text"]

    if not text:
        return

    db = SpeakerDB()
    text = text[:139]
    db.execute("INSERT INTO publish_queue (tweet_text) VALUES (?)", [text])

def queue_sound_for_tweet(name):
    print name

def play_speech(speech_func, text):
    
    try:
    
        lock = zc.lockfile.LockFile('play')
        speech_func(speech_text=text)
        lock.close()

    except zc.lockfile.LockError:
        pass

def run_with_lock(func, *args, **kwargs):
    pass

def get_image():

    path = getcwd() + "/static/r_gifs/"
    
    files = [ f for f in listdir(path) if isfile(join(path,f)) ]

    file_path = choice(files)

    if "?" in file_path:
        file_path = get_image()

    return file_path