from flask import Flask, redirect, url_for,  render_template, request 
from Speakerbot import Speakerbot, SoundEffect
import json, string
import zc.lockfile

from os import listdir, getcwd
from os.path import isfile, join

from random import choice
from words import parse_and_fill_mad_lib

sb = Speakerbot()
app = Flask(__name__)
app.config['DEBUG'] = True

def dada():
    return parse_and_fill_mad_lib("The !adjective !noun !adverb !verb the !noun.")

def parse_and_route_speech(text):
    
    actions = {
        'random':random_utterance,
        'dada':dada
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
        play_speech(run_filters(text))

def run_filters(text):
    text = parse_and_fill_mad_lib(text)

    return text

def random_utterance():
    
    path = getcwd() + "/speech/"
    
    files = [ f for f in listdir(path) if isfile(join(path,f)) ]

    file_path = choice(files)

    se = SoundEffect()

    se.play_sound(path + file_path)

def play_speech(text):
    try:
        lock = zc.lockfile.LockFile('play')
        sb.say_classy(speech_text=text)
        lock.close()
    except zc.lockfile.LockError:
        pass

def get_image():

    path = getcwd() + "/static/r_gifs/"
    
    files = [ f for f in listdir(path) if isfile(join(path,f)) ]

    file_path = choice(files)

    return file_path

@app.route('/')
def home():
    sounds = sb.sounds
    o_sounds = sounds.keys()
    o_sounds.sort()

    sound_tuples = [(url_for("play_sound", sound_name=sound), sound) for sound in o_sounds]

    return render_template("home.html", sounds=sound_tuples, image=get_image(), random_title=parse_and_fill_mad_lib("The !adjective !noun !adverb !verb the !noun."))

    out = "<!DOCTYPE html>"
    out += "<head><title>Speakerbot and the love below</title></head><body width='100%'>"
    out += '<input type="text" id="text" /><button onclick="var txt=document.getElementById(\'text\').value;location.href=\'/say/\' + encodeURIComponent(txt);">say</button>'
    out += '<table width="100%"><tr><td width="50%">'
    out += "<ul>"
    for sound in o_sounds:
        out += '<li><a href="%s">%s</a></li>' % (url_for("play_sound", sound_name=sound), sound)
    out += "</ul></td>"
    out += "<td valign='top' align='right' width='50%'><br />" + parse_and_fill_mad_lib("The !adjective !noun !adverb !verb the !noun.") + "</td></tr></table>"
    out += "</body></html>"

    return out

@app.route('/play_sound/<sound_name>')
def play_sound(sound_name):
    try:
        lock = zc.lockfile.LockFile('play')
        #o_sounds = sb.sounds.keys()
        #sound_name = choice((sound_name, sound_name, sound_name, sound_name, choice(o_sounds)))
        sb.play(sound_name)
        lock.close()
    except zc.lockfile.LockError:
        pass

    return redirect(url_for("home"))

@app.route('/say/')
@app.route('/say/<text>')
def say(text=None):
    if not text:
        text = request.args.get('speech-text', None)

    if not text or len(text) > 100:
        return redirect(url_for("home"))

    parse_and_route_speech(text)

    return redirect(url_for("home"))    

if __name__ == '__main__':
    app.run('0.0.0.0',port=8080)
