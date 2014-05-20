import datetime
import json
from os import listdir, getcwd
from os.path import isfile, join


from random import choice


import requests

from config import config
from Speakerbot import SoundEffect
from speakonomy import Speakonomy
from words import parse_and_fill_mad_lib, term_map
from speaker_db import SpeakerDB
from pyquery import PyQuery as pq

def get_mashape_api(url):
    api_key = config["mashape_api_key"]
    headers={
        "X-Mashape-Authorization": api_key
    }

    return requests.get(url, headers=headers)

def random_drumroll(sb):

    sb.play("drumroll")
    
    sound = choice(sb.sounds.keys())

    sb.play(sound)

def price_is_right(sb, wager):

    lost_it_all = False
    win_multiplier = 20

    wager = int(wager)
    if wager <= 0:
        return "Nice try wiseguy"
    speakonomy = Speakonomy()
    if speakonomy.is_active():
        if not speakonomy.check_affordability(cost=wager):
            return "Not enough speakerbucks to spin"
        speakonomy.withdraw_funds(wager)
    win_sounds = ["price-come-on-down-1.mp3", "price-come-on-down-2.mp3", "price-is-right.mp3", "price-big-wheel-win.mp3"]
    lose_sounds = ["you-lose.mp3", "good-grief.mp3","priceisright-horns.mp3", "pacman-die.mp3", "sad-trombone.mp3", "wet-fart.mp3"]

    rng = range(1,20)

    if wager % 69 == 0:

        rng = range(12,20)

        win_multiplier = choice(range(2,20))

        if choice(range(1,20)) == 7:
            lost_it_all = True



    if choice(rng) == 15:
        winner = True
    else:
        winner = False

    se = SoundEffect()

    se.play("price-big-wheel.mp3")

    if winner:
        se.play(choice(win_sounds))
        if speakonomy.is_active():
            speakonomy.deposit_funds(wager*20)
        return "You win a new car. And {} speakerbucks!".format(wager*win_multiplier)
    else:
        se.play(choice(lose_sounds))
        if lost_it_all:
            speakonomy.withdraw_funds(speakonomy.get_speakerbuck_balance())
            return "You risked it all for sexy times. And lost."


def jon(sb):
    db = SpeakerDB()
    results = db.execute("SELECT * FROM snippets where votes > 1 order by rowid desc limit 10")

    speech_list = [result["speech_text"] for result in results]

    if len(speech_list) > 1:
        speech_text = choice(speech_list)
        return speech_text
    else:
        return "I haven't heard enough funny things to commit a jon"

def dada(sb):
    return parse_and_fill_mad_lib("The !adjective !noun !adverb !verb the !noun.")

def ross(sb):

    return "Oh shit! I gotta get out of here!"

def yoda(sb, sentence):

    url = "https://yoda.p.mashape.com/yoda?sentence=%s" % sentence

    r = get_mashape_api(url)
    
    return u"" + r.text

def horoscope(sb, sign):
    
    url = "http://widgets.fabulously40.com/horoscope.json?sign=%s" % sign

    r = requests.get(url)

    horoscope = json.loads(r.text)["horoscope"]["horoscope"]


    text = "The horoscope for %s. %s" % (sign, horoscope)

    return text

def datefact(sb):

    day = datetime.datetime.today().day
    month = datetime.datetime.today().month

    url = "https://numbersapi.p.mashape.com/%s/%s/date" % (month, day)

    r = get_mashape_api(url)

    return u"" + r.text


def lunch(sb):
    #TODO: Make this database driven
    places = [
        "parkside", "flipside", "subway", "panera", "zoup", "umami", 
        "dave's", "lemon falls", "giant eagle", "einstein brothers", "fresh start",
        "panini's", "burntwood tavern", "rick's cafe"
    ]

    place = choice(places)

    return "I think you ought to go to %s for lunch" % place

def weather(sb):

    r = requests.get("https://api.forecast.io/forecast/38a9c91bca816b2e960c14c1ecdcf8c6/41.4311,-81.3886")

    weather = json.loads(r.text)

    weather_text = "The current temperature is %s, the weather forecast is %s" % (weather["currently"]["apparentTemperature"], weather["hourly"]["summary"])

    return weather_text

def slinging_burgers(sb):

    verb = choice(term_map["verb"])
    
    return "Anyone who describes !verb ing as " + verb + " ing !noun should be " + verb + " ing !noun"

def run_filters(text):
    
    text = parse_and_fill_mad_lib(text)

    return text

def urban(sb, text):

    page = requests.get("http://www.urbandictionary.com/define.php?term=%s" % text)

    page = pq(page.text)

    defn_tag = page("div.meaning")
    defn = ""

    if defn_tag:
        print defn_tag.html()
        defn = defn_tag.html().split("<br/>")[0]

    if not defn:
        return "I couldn't find a definition for %s" % text
    else:
        return "The definition for %s: %s" % (text, defn)



def random_utterance(sb):
    
    path = getcwd() + "/speech/"
    
    files = [ f for f in listdir(path) if isfile(join(path,f)) ]

    file_path = choice(files)

    se = SoundEffect()

    se.play_sound(path + file_path)