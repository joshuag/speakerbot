from flask import Flask, redirect, url_for,  render_template, request 
from Speakerbot import Speakerbot
import datetime

import zc.lockfile

from speakerlib import *

sb = Speakerbot()
app = Flask(__name__)
app.config['DEBUG'] = True

@app.route('/')
def home():

    return render_template("home.html", sounds=sb.load_sounds(), image=get_image(), random_title=parse_and_fill_mad_lib("The !adjective !noun !adverb !verb the !noun."))

@app.route('/play_sound/<sound_name>')
def play_sound(sound_name):

    if sound_name == "rebecca-black" and not datetime.datetime.today().weekday() == 4:
        sound_name = choice(sb.sounds.keys())
    
    try:
        lock = zc.lockfile.LockFile('play')
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

    parse_and_route_speech(sb.say_classy, text)

    return redirect(url_for("home"))    

if __name__ == '__main__':
    app.run('0.0.0.0',port=8080)
