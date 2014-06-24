from os import listdir, getcwd
from os.path import isfile, join
from random import choice
import re
import subprocess

import datetime

from speaker_db import SpeakerDB
from speakerbot_plugins import *

from instrumentation import time_instrument

try:   
    from uwsgidecorators import lock

except ImportError:
    def lock(f):
        return f

def get_mp3_seconds(path):
    out = subprocess.check_output('mpg321 -t "{}"'.format(path), shell=True, stderr=subprocess.STDOUT)

    mins, secs = re.search(r'\[(\d+):(\d+)\] Decoding', out).groups()
    return int(mins) * 60 + int(secs)

@lock
def parse_and_route_speech(speakerbot, text):
    
    actions = {
        'random':random,
        'dada':dada,
        'slinging':slinging,
        'weather':weather,
        'lunch': lunch,
        'datefact':datefact,
        'horoscope':horoscope,
        'yoda':yoda,
        'ross':ross,
        'jon':jon,
        'josh':josh,
        'dave':dave,
        'spin':spin,
        'suspense':suspense,
        'urban': urban,
        'comment': comment,
        'wiki':wiki
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
        speakerbot.say_classy(speech_text=run_filters(text))

def niceify_number(i):
    #swiped from http://codegolf.stackexchange.com/questions/4707/outputting-ordinal-numbers-1st-2nd-3rd
    k=i%10
    return "%d%s" % (i,"tsnrhtdd"[(i/10%10!=1)*(k<4)*k::4])

def minimize_string(s):
    if isinstance(s, (str, unicode)):
        return ''.join(c.lower() for c in s if not c.isspace())
    return s

def play_speech(speech_func, text):
        
    run_with_lock(speech_func, speech_text=text)

@lock
def run_with_lock(func, *args, **kwargs):
    func(*args, **kwargs)

@time_instrument
def get_image(checker_func=lambda x: True, depth=5):

    path = getcwd() + "/static/r_gifs/"
    
    files = [ f for f in listdir(path) if isfile(join(path,f)) ]

    file_path = choice(files)

    if "?" in file_path:
        file_path = get_image()

    if "-static.gif" in file_path:
        #don't want the static images
        file_path = get_image()

    if not checker_func(file_path) and depth != 0:
        print "trying to get passable image"
        depth -= 1
        file_path = get_image(checker_func, depth)

    return file_path