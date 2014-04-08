import datetime
import json

from os import listdir, getcwd
from os.path import isfile, join
from random import choice

import zc.lockfile
import requests

from words import parse_and_fill_mad_lib
from Speakerbot import SoundEffect
from config import config

def get_mashape_api(url):
    api_key = config["mashape_api_key"]
    headers={
        "X-Mashape-Authorization": api_key
    }

    return requests.get(url, headers=headers)

def dada():
    return parse_and_fill_mad_lib("The !adjective !noun !adverb !verb the !noun.")

def parse_and_route_speech(speech_func, text):
    
    actions = {
        'random':random_utterance,
        'dada':dada,
        'slinging':slinging_burgers,
        'weather':weather,
        'lunch': lunch,
        'datefact':datefact,
        'horoscope':horoscope
    }
    
    token = None
    argument = None
    record_utterance = True

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

                record_utterance = False
                text = text_output

            except TypeError:
                text = "I need an argument for that function, dummy."

    if text:
        play_speech(speech_func, run_filters(text), record_utterance=record_utterance)

def horoscope(sign):
    
    url = "http://widgets.fabulously40.com/horoscope.json?sign=%s" % sign

    r = requests.get(url)

    horoscope = json.loads(r.text)["horoscope"]["horoscope"]


    text = "The horoscope for %s. %s" % (sign, horoscope)

    return text

def datefact():

    day = datetime.datetime.today().day
    month = datetime.datetime.today().month

    url = "https://numbersapi.p.mashape.com/%s/%s/date" % (month, day)

    r = get_mashape_api(url)

    return u"" + r.text


def lunch():
    #TODO: Make this database driven
    places = [
        "parkside", "flipside", "subway", "panera", "zoup", "umami", 
        "dave's", "lemon falls", "giant eagle", "einstein brothers", "fresh start",
        "panini's", "burntwood tavern", "rick's cafe"
    ]

    place = choice(places)

    return "I think you ought to go to %s for lunch" % place

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

def play_speech(speech_func, text, record_utterance):
    
    try:
    
        lock = zc.lockfile.LockFile('play')
        speech_func(speech_text=text, record_utterance=record_utterance)
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