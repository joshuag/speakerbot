import datetime
import json
from os import listdir, getcwd
from os.path import isfile, join

from random import choice

import requests
import re

from config import config
from Speakerbot import SoundEffect
from speakonomy import Speakonomy
from words import parse_and_fill_mad_lib, term_map
from speaker_db import SpeakerDB
from pyquery import PyQuery as pq

db = SpeakerDB()

#http://stackoverflow.com/a/250373
def smart_truncate(content, length=100, suffix='...'):
    if len(content) <= length:
        return content
    else:
        return ' '.join(content[:length+1].split(' ')[0:-1]) + suffix

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
    outstr = None
    cheated_death = 0
    added_message = ""

    speakonomy = Speakonomy()
    if wager.upper() == 'MAX':
        wager = speakonomy.get_speakerbuck_balance()
    elif wager.upper() == 'MAX69':
        wager = speakonomy.get_speakerbuck_balance()
        wager = wager - wager % 69
    try:
        wager = int(wager)
    except:
        return "Fuckstick, you can't wager %s" % wager

    if wager <= 0:
        return "Nice try wiseguy"
    if speakonomy.is_active():
        if not speakonomy.check_affordability(cost=wager):
            return "Not enough speakerbucks to spin"
        speakonomy.withdraw_funds(wager)
    win_sounds = ["price-come-on-down-1.mp3", "price-come-on-down-2.mp3", "price-is-right.mp3", "price-big-wheel-win.mp3"]
    lose_sounds = ["you-lose.mp3", "good-grief.mp3","priceisright-horns.mp3", "pacman-die.mp3", "sad-trombone.mp3", "wet-fart.mp3"]

    rng = range(1,20)

    if wager % 69 == 0:

        rng = range(12,20)

        win_multiplier = choice(range(2,20) * 2 + [69, 69, 6900])

        if choice(range(1,20)) == 7:
            lost_it_all = True

    lucky_number = choice(rng)
    chosen_number = choice(rng)

    if chosen_number == lucky_number or wager == lucky_number:
        if wager == lucky_number:
            win_multiplier = choice(range(2,20) + [200, 400, 600, 800, 1000, 10000])
            added_message = "And your wager matched the lucky number, you sly dog."

            if chosen_number == wager and win_multiplier == wager:
                win_multiplier = win_multiplier * 100000
                added_message = "The wager, chosen number, lucky number and win multiplier all matched. It's a megabucks bonanza!"
            elif chosen_number == wager:
                #Triply lucky
                win_multiplier = win_multiplier * 30
                added_message += "And the chosen number matched too! You are thirty times as lucky!"

            chosen_number = wager

        winner = True
    else:
        winner = False

    se = SoundEffect()

    se.play("price-big-wheel.mp3")

    if winner:
        outcome = wager*win_multiplier
        prizes = ["a new car","a european vacation", "a deluxe horse trailer", "new jet skis", "a trip to the moon", "a large fry", "a bucket of golden nuggets", "gender neutral servant robots", "Abe Lincoln's death mask"]
        se.play(choice(win_sounds))
        if speakonomy.is_active():
            speakonomy.deposit_funds(outcome)
        outstr = "You win {prize}. And {outcome} speakerbucks!".format(outcome=outcome,prize=choice(prizes))
        if lost_it_all:
            outstr += "You also cheated death."
            cheated_death = 1

        outstr += added_message
    else:
        outcome = wager * -1
        se.play(choice(lose_sounds))
        if lost_it_all:
            outcome = speakonomy.get_speakerbuck_balance() * -1
            speakonomy.withdraw_funds(speakonomy.get_speakerbuck_balance())
            outstr = "You risked it all for sexy times. And lost."

    db.record_wager(lucky_number, wager, outcome, chosen_number, win_multiplier, cheated_death)

    return outstr


def jon(sb):
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

def dave(sb):
    options = ['shut the fuck up', 'who gives a shit']
    return choice(options)

def josh(sb):
    exclamations = ['Oh nuts on nuts.', 'Heavens to betsy','Jiminy Crickets','Hells bells','Holy hell','Son of a gun','Balls on a hat','Poop in a bucket','God damnit', 'Goodness gracious','Sweet Moses', 'Geez um crow', 'Cheese and Rice',]
    gripe_recipient = ['Django']
    subjects = ['dude','guy','girl','woman','man']
    gripe_recipient.extend(['this {}'.format(s) for s in subjects])
    gripe_recipient.extend(['that {}'.format(s) for s in subjects])
    predicates = ['can go eat a nutsack', 'gets my knickers in a twist', 'is a complete {noun}','is a total {noun}','is an outright {noun}', 'is an absolute {noun}', 'is an udder {noun}', 'can go piss up a rope', 'about as useful as tits on a bull','a son of a gun']
    predicate_nouns = ['fuckstick', 'chucklefuck', 'knucklehead', 'dicknut', 'scallywag', 'shithead', 'waste of skin']

    phrase = '{exclamation}! {gripe_recipient} {predicate}'.format(
        exclamation=choice(exclamations),
        gripe_recipient=choice(gripe_recipient),
        predicate=choice(predicates).format(noun=choice(predicate_nouns))
    )
    return phrase

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
        defn = re.sub('<[^<]+?>(.*?)</[^<]+?>', r'\1', defn_tag.html().split("<br/>")[0])
        defn = smart_truncate("".join(defn.split(".")[:3]), length=200)

    if not defn:
        return "I couldn't find a definition for %s" % text
    else:
        return "The definition for %s: %s" % (text, defn)

def random_comment(sb):
    return db.get_random_comment()

def random_utterance(sb):
    return db.get_random_utterance()
