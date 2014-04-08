from words import parse_and_fill_mad_lib
from os import listdir, getcwd
from os.path import isfile, join
import zc.lockfile
from Speakerbot import SoundEffect

from random import choice
import requests
import json


def dada():
    return parse_and_fill_mad_lib("The !adjective !noun !adverb !verb the !noun.")

def parse_and_route_speech(speech_func, text):
    
    actions = {
        'random':random_utterance,
        'dada':dada,
        'slinging':slinging_burgers,
        'weather':weather
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
            if argument:
                text_output = method(argument)
            else:
                text_output = method()
            
            text = text_output

    if text:
        play_speech(speech_func, run_filters(text))

def weather():

    r = requests.get("https://api.forecast.io/forecast/38a9c91bca816b2e960c14c1ecdcf8c6/41.4311,81.3886")

    weather = json.loads(r.text)

    weather_text = "The current temperature is %s, the weather is %s" % (weather["currently"]["apparentTemperature"], weather["hourly"]["summary"])

    return weather_text

def slinging_burgers():
    return "Anyone who describes !verb ing as !verb ing !noun should be !verb ing !noun"

def run_filters(text):
    text = parse_and_fill_mad_lib(text)

    return text

def random_utterance():
    
    path = getcwd() + "/speech/"
    
    files = [ f for f in listdir(path) if isfile(join(path,f)) ]

    file_path = choice(files)

    se = SoundEffect()

    se.play_sound(path + file_path)

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