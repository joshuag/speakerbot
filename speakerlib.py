from os import listdir, getcwd
from os.path import isfile, join
from random import choice

import datetime

from multiprocessing import Lock

from speaker_db import SpeakerDB
from speakerbot_plugins import *

threadLock = Lock()

def economy_is_active():
    if datetime.datetime.today().weekday() in [5,6]:
        return False
        
    current_hour = datetime.datetime.now().hour
    if current_hour >= 8 and current_hour < 18:
        return True

    return False

def create_deferred(function, *args, **kwargs):

    def _exec():
        function(*args, **kwargs)

    return _exec

def parse_and_route_speech(speakerbot, text):
    
    actions = {
        'random':random_utterance,
        'dada':dada,
        'slinging':slinging_burgers,
        'weather':weather,
        'lunch': lunch,
        'datefact':datefact,
        'horoscope':horoscope,
        'yoda':yoda,
        'ross':ross,
        'jon':jon,
        'spin':price_is_right,
        'suspense':random_drumroll,
        'urban': urban
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
                    text_output = method(speakerbot, argument.strip())
                else:
                    text_output = method(speakerbot)

                text = text_output

            except TypeError:
                text = "I need an argument for that function, dummy."


    if text:
        play_speech(speakerbot.say_classy, run_filters(text))

def niceify_number(i):
    #swiped from http://codegolf.stackexchange.com/questions/4707/outputting-ordinal-numbers-1st-2nd-3rd
    k=i%10
    return "%d%s" % (i,"tsnrhtdd"[(i/10%10!=1)*(k<4)*k::4])

def queue_speech_for_tweet(*args, **kwargs):

    text = kwargs["speech_text"]

    if text[0] == "!" or text[0:2] == "..":
        return

    if not text:
        return

    db = SpeakerDB()
    text = text[:139]
    db.execute("INSERT INTO publish_queue (tweet_text) VALUES (?)", [text])

def queue_sound_for_tweet(name, event_result):

    db = SpeakerDB()
    matched_sound = db.execute("SELECT votes FROM sounds where name=?", [name]).fetchone()

    if matched_sound:
        text = "I just played %s for the %s time" % (name, niceify_number(matched_sound["votes"]))
        db.execute("INSERT INTO publish_queue (tweet_text) VALUES (?)", [text])

def play_speech(speech_func, text):
        
    run_with_lock(speech_func, speech_text=text)

def run_with_lock(func, *args, **kwargs):
    try:
        threadLock.acquire(True)
        func(*args, **kwargs)
    except:
        pass
    finally:
        threadLock.release()

def get_image(checker_func=lambda x: True, depth=5):

    path = getcwd() + "/static/r_gifs/"
    
    files = [ f for f in listdir(path) if isfile(join(path,f)) ]

    file_path = choice(files)

    if "?" in file_path:
        file_path = get_image()

    if not checker_func(file_path) and depth != 0:
        print "trying to get passable image"
        depth -= 1
        file_path = get_image(checker_func, depth)

    return file_path