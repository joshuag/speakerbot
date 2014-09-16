import datetime
import json
from random import choice, randrange

import requests
from pyquery import PyQuery as pq

from config import config
from speakonomy import Speakonomy
from util.words import parse_and_fill_mad_lib, term_map
from speaker_db import SpeakerDB
from dynamic_class import plugin
from mitch import quotes as mitch_quotes

db = SpeakerDB()

def get_mashape_api(url):
    api_key = config["mashape_api_key"]
    headers={
        "X-Mashape-Authorization": api_key
    }

    return requests.get(url, headers=headers)

@plugin
def suspense(sb):
    speakonomy = Speakonomy()
    if speakonomy.is_active():
        if not speakonomy.check_affordability(cost=20):
            return "Not enough speakerbucks for drumroll"
        speakonomy.withdraw_funds(20)

    sb.play("drumroll", free=True)
    
    sound = choice(sb.sounds.keys())

    sb.play(sound, free=True)

@plugin
def spin(sb, wager):

    lost_it_all = False
    win_multiplier = 20
    outstr = None
    silent = False
    cheated_death = 0
    added_message = ""

    wager_list = wager.split(" ")
    wager = wager_list[0]

    if len(wager_list) > 1 and wager_list[1] == "silent" and choice(range(1,15)) != 4:
        silent = True

    speakonomy = Speakonomy()
    if wager.upper() == 'MAX':
        wager = speakonomy.get_speakerbuck_balance()
    elif wager.upper() == 'MAX69':
        wager = speakonomy.get_speakerbuck_balance()
        wager = wager - wager % 69
    try:
        wager = int(wager)
    except:
        return "Fuckstick, you can't wager %s" % " ".join(wager_list)

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
            new_win_multiplier = choice(range(6,20) + [200, 400, 600, 800, 1000, 10000])
            added_message = "And your wager matched the lucky number, you sly dog."

            if chosen_number == wager and win_multiplier == wager:
                new_win_multiplier = new_win_multiplier * 1000000
                added_message = "The wager, chosen number, lucky number and win multiplier all matched. It's a megabucks bonanza!"
            elif chosen_number == wager:
                #Triply lucky
                new_win_multiplier = new_win_multiplier * 300
                added_message += "And the chosen number matched too! You are thirty times as lucky!"

            win_multiplier = new_win_multiplier

        winner = True
    else:
        winner = False

    sp = sb.sound_player

    if winner or not silent: sp.play_sound("sounds/price-big-wheel.mp3")

    if winner:
        outcome = wager*win_multiplier
        prizes = ["a new car","a european vacation", "a deluxe horse trailer", "new jet skis", "a trip to the moon", "a large fry", "a bucket of golden nuggets", "gender neutral servant robots", "Abraham Lincoln's death mask"]
        sp.play_sound("sounds/"+choice(win_sounds))
        if speakonomy.is_active():
            speakonomy.deposit_funds(outcome)
        outstr = "You win {prize}. And {outcome} speakerbucks!".format(outcome=outcome,prize=choice(prizes))
        if lost_it_all:
            outstr += "You also cheated death."
            cheated_death = 1

        outstr += added_message
    else:
        outcome = wager * -1
        if not silent: sp.play_sound("sounds/"+choice(lose_sounds))
        if lost_it_all:
            outcome = speakonomy.get_speakerbuck_balance() * -1
            speakonomy.withdraw_funds(speakonomy.get_speakerbuck_balance())
            outstr = "You risked it all for sexy times. And lost."

    db.record_wager(lucky_number, wager, outcome, chosen_number, win_multiplier, cheated_death)

    return outstr

@plugin
def jon(sb):
    results = db.execute("SELECT * FROM snippets where votes > 1 order by votes desc limit 10")

    speech_list = [result["speech_text"] for result in results]

    if len(speech_list) > 1:
        speech_text = choice(speech_list)
        return speech_text
    else:
        return "I haven't heard enough funny things to commit a jon"

@plugin
def dada(sb):
    return parse_and_fill_mad_lib("The !adjective !noun !adverb !verb the !noun.")

@plugin
def ross(sb):

    return "Oh shit! I gotta get out of here!"

@plugin
def dave(sb):
    options = ['shut the fuck up', 'who gives a shit']
    return choice(options)

@plugin
def josh(sb):
    exclamations = ['Good gravy', 'Fuck beans', 'Shit on a stick', 'Oh nuts on nuts.', 'Heavens to betsy','Jiminy Crickets','Hells bells','Holy hell','Son of a gun','Balls on a hat','Poop in a bucket','God damnit', 'Goodness gracious','Sweet Moses', 'Geez um crow', 'Cheese and Rice',]
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

@plugin
def yoda(sb, sentence):

    url = "https://yoda.p.mashape.com/yoda?sentence=%s" % sentence

    r = get_mashape_api(url)
    
    return u"" + r.text

@plugin
def horoscope(sb, sign):
    
    url = "http://widgets.fabulously40.com/horoscope.json?sign=%s" % sign
    r = requests.get(url)

    horoscope = json.loads(r.text)["horoscope"]["horoscope"]


    text = "The horoscope for %s. %s" % (sign, horoscope)

    return text

@plugin
def datefact(sb):

    day = datetime.datetime.today().day
    month = datetime.datetime.today().month

    url = "https://numbersapi.p.mashape.com/%s/%s/date" % (month, day)

    r = get_mashape_api(url)

    return u"" + r.text

@plugin
def lunch(sb):
    #TODO: Make this database driven
    places = [
        "parkside", "flipside", "subway", "panera", "zoup", "umami", 
        "dave's", "lemon falls", "giant eagle", "einstein brothers", "fresh start",
        "panini's", "burntwood tavern", "rick's cafe"
    ]

    place = choice(places)

    return "I think you ought to go to %s for lunch" % place

@plugin
def weather(sb):

    r = requests.get("https://api.forecast.io/forecast/38a9c91bca816b2e960c14c1ecdcf8c6/41.4311,-81.3886")

    weather = json.loads(r.text)

    weather_text = "The current temperature is %s, the weather forecast is %s" % (weather["currently"]["apparentTemperature"], weather["hourly"]["summary"])

    return weather_text

@plugin
def slinging(sb):

    verb = choice(term_map["verb"])
    
    return "Anyone who describes !verb ing as " + verb + " ing !noun should be " + verb + " ing !noun"

@plugin
def define(sb, text):

    page = requests.get("http://www.dictionary.com/browse/%s" % text)

    page = pq(page.text)

    defn_tag = page(".dndata")

    if defn_tag:
        defn = page(defn_tag[0]).text()

    if not defn:
        return "I couldn't find a definition for %s" % text
    else:
        return "The definition for %s: %s" % (text, defn)

@plugin
def urban(sb, text):

    return define(sb, text)

@plugin
def wiki(sb):

    page = requests.get("http://en.wikipedia.org/wiki/Special:Random")

    page = pq(page.text)

    text = choice(pq(page("#mw-content-text")[0]).text().split("."))

    return text

@plugin
def comment(sb):
    return db.get_random_comment()

@plugin
def random(sb, seed=None):
    return db.get_random_utterance(seed=seed)

@plugin
def scrum(sb):
    sp = sb.sound_player
    if randrange(1,5) != 3:
        sp.play_sound("sounds/price-big-wheel-win.mp3")
        return "There is no scrum today!"
    else:
        sp.play_sound("sounds/tornado-siren.mp3")
        return "There will be a scrum today."

@plugin
def mitch(sb):
    return choice(mitch_quotes)
