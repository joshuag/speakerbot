import datetime
import json
from os import listdir, getcwd
from os.path import isfile, join


from random import choice


import requests

from config import config
from Speakerbot import SoundEffect
from words import parse_and_fill_mad_lib
from speaker_db import SpeakerDB

def get_mashape_api(url):
    api_key = config["mashape_api_key"]
    headers={
        "X-Mashape-Authorization": api_key
    }

    return requests.get(url, headers=headers)

def price_is_right():

    win_sounds = ["price-come-on-down-1.mp3", "price-come-on-down-2.mp3", "price-is-right.mp3", "price-big-wheel-win.mp3"]
    lose_sounds = ["you-lose.mp3", "good-grief.mp3","priceisright-horns.mp3", "pacman-die.mp3", "sad-trombone.mp3", "wet-fart.mp3"]

    if choice(range(1,20)) == 15:
        winner = True
    else:
        winner = False

    se = SoundEffect()

    se.play("price-big-wheel.mp3")

    if winner:
        se.play(choice(win_sounds))
        return "You win a new car!"
    else:
        se.play(choice(lose_sounds))




def jon():
    db = SpeakerDB()
    results = db.execute("SELECT * FROM snippets where votes > 1 order by rowid desc limit 10")

    speech_list = [result["speech_text"] for result in results]

    if len(speech_list) > 1:
        speech_text = choice(speech_list)
        return speech_text
    else:
        return "I haven't heard enough funny things to commit a jon"

def dada():
    return parse_and_fill_mad_lib("The !adjective !noun !adverb !verb the !noun.")

def ross():

    return "Oh shit! I gotta get out of here!"

def yoda(sentence):

    url = "https://yoda.p.mashape.com/yoda?sentence=%s" % sentence

    r = get_mashape_api(url)
    
    return u"" + r.text

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

    r = requests.get("https://api.forecast.io/forecast/38a9c91bca816b2e960c14c1ecdcf8c6/41.4311,-81.3886")

    weather = json.loads(r.text)

    weather_text = "The current temperature is %s, the weather forecast is %s" % (weather["currently"]["apparentTemperature"], weather["hourly"]["summary"])

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