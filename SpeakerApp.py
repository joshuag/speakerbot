import datetime
import os, subprocess

from flask import Flask, redirect, url_for,  render_template, request 
from werkzeug.utils import secure_filename

from eventrecorder import EventRecorder
from Speakerbot import Speakerbot
from speaker_db import SpeakerDB
from speakerlib import *
from speakonomy import Speakonomy

print "loading speakerbot"
sb = Speakerbot()
print "loading speakonomy"
speakonomy = Speakonomy(sb)
print "loading speakerdb"
db = SpeakerDB()
print "initializing event recorder"
evr = EventRecorder(db=db)

def stub_interrogator(*args, **kwargs):
    return True

def stub_mangler(*args, **kwargs):
    return args, kwargs


sb.attach_listener("say_classy", queue_speech_for_tweet)
sb.attach_listener("play", queue_sound_for_tweet)
sb.attach_listener("play", speakonomy.sell_sound)
sb.attach_listener("play", evr.record_sound_event)
sb.attach_interrogator("play", stub_interrogator)

#sb.attach_mangler("say_classy", stub_mangler)


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['UPLOAD_FOLDER'] = os.path.relpath('sounds')

print "I'm ready"

@app.context_processor
def inject_speakonomy():
    return dict(speakonomy=speakonomy)

@app.route('/')
@app.route('/home/<image>')
def home(image=None):
    message = request.args.get('message', None)

    if not image:
        image = get_image(db.check_appropriate)

    votes = db.get_image_votes(image)
    comments = db.get_image_comments(image)

    last_withdrawal_time, speakerbucks_per_minute = speakonomy.get_last_withdrawal_time(include_sbpm=True)

    return render_template(
            "home.html", 
            sounds=sb.load_sounds(), 
            image=image, 
            message=message,
            votes=votes,
            comments=comments,
            last_withdrawal_time=last_withdrawal_time,
            speakerbucks_per_minute=speakerbucks_per_minute,
            random_title=parse_and_fill_mad_lib("The !adjective !noun !adverb !verb the !noun.")
            )

@app.route('/upload', methods=["GET", "POST"])
def upload_sound():
    #TODO: Put the sounds into their own class
    message = None
    if request.method == 'POST':
        name = request.form.get('sound_name')
        f = request.files['file']
        filename = secure_filename(f.filename)
        sound_fp = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        f.save(sound_fp)
        sound_seconds = get_mp3_seconds(sound_fp)
        if sound_seconds > 15:
            message = 'This sound is {} seconds! Must be 15 seconds or less.'.format(sound_seconds)
        else:
            base_cost = speakonomy.get_sound_base_cost(sound_fp)
            sb.add_sound_to_db(name, filename, base_cost)
            full_sound_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), sound_fp)
            subprocess.call(['mp3gain','-r', '{}'.format(full_sound_path)])

    return render_template(
            "upload.html", 
            message=message,
            )

@app.route('/theme-songs', methods=["GET", "POST"])
def theme_songs():
    if request.method == 'POST':
        if request.form['user'] and request.form['song']:
            db.execute("update person set theme_song=? where name=?", [request.form['song'], request.form['user']])
        return redirect(url_for("theme_songs"))
    return render_template(
            "themesongs.html", 
            sounds=sorted(sb.load_sounds().keys()), 
            people=db.get_people(),
            )

@app.route('/spadmin', methods=["GET", "POST"])
def admin():
    if request.form.get('person-name'):
        db.add_person(request.form['person-name'])
        return redirect(url_for("admin"))
    elif request.form.get('delete-person'):
        db.remove_person(request.form['delete-person'])
        return redirect(url_for("admin"))

    return render_template(
            "admin.html", 
            people=db.get_people(),
            )

@app.route('/image/<image>/upboat')
def upvote_image(image):
    
    votes = db.get_image_votes(image)

    votes += 1

    db.execute("update images set votes=? where file_name=?", [votes, image])

    speakonomy.deposit_funds(5)

    return redirect(url_for("home", message="Thank you for voting, have 5 speakerbucks"))

@app.route('/image/<image>/downgoat')
def downvote_image(image):
    votes = db.get_image_votes(image)

    votes -= 1

    db.execute("update images set votes=? where file_name=?", [votes, image])

    speakonomy.deposit_funds(5)

    return redirect(url_for("home", message="Thank you for voting, have 5 speakerbucks"))

@app.route('/image/<image>/nsfw')
def flag_image(image):
    
    db.execute("update images set nsfw=1 where file_name=?", [image])

    return redirect(url_for("home", image=image))

@app.route('/comment/<image>', methods=["POST"])
def comment_image(image):

    comment = request.form["image-comment"]
    
    if comment.strip() != '':
        db.add_comment(image, comment)
        speakonomy.deposit_funds(10)

    return redirect(url_for("home", image=image, message="Thank you for commenting, have 10 speakerbucks"))

@app.route('/images/nsfw')
def nsfw_images():

    images = db.get_nsfw_images()
    return render_template("images.html", images=images, speakonomy=speakonomy)

@app.route('/images/top')
def top_images():

    num_images = request.args.get("num", 25)

    images = db.get_top_images(num_images=num_images)
    return render_template("images.html", images=images, speakonomy=speakonomy)

@app.route('/images/worst')
def worst_images():

    num_images = request.args.get("num", 25)

    images = db.get_top_images(num_images=num_images, order="asc")
    return render_template("images.html", images=images, speakonomy=speakonomy)

@app.route('/spinstats')
def spinstats():

    now = datetime.datetime.now()
    midnight = datetime.datetime(now.year, now.month, now.day).strftime("%s") 

    aggregate_stats = db.get_aggregate_wager_stats()
    today_aggregate_stats = db.get_aggregate_wager_stats(start=midnight)
    recent_spins = db.get_wager_history(20)
    number_occurence = db.get_number_occurence()
    multiplier_occurence = db.get_multiplier_occurence()
    wagers_and_outcomes = db.get_wagers_and_outcomes_by_day()
    wagers_by_outcome = db.get_wagers_by_outcome()
    lucky_numbers = db.get_lucky_numbers()
    number_cooccurence = db.get_lucky_and_chosen_cooccurence()

    return render_template("spinstats.html", 
            aggregate_stats=aggregate_stats, 
            today_aggregate_stats=today_aggregate_stats, 
            recent_spins=recent_spins,
            number_occurence=number_occurence,
            multiplier_occurence=multiplier_occurence,
            wagers_and_outcomes=wagers_and_outcomes,
            wagers_by_outcome=wagers_by_outcome,
            lucky_numbers=lucky_numbers,
            number_cooccurrence=number_cooccurence
            )

@app.route('/play_sound/<sound_name>')
def play_sound(sound_name):

    if sound_name == "rebecca-black" and datetime.datetime.today().weekday() != 4:
        sound_name = choice(sb.sounds.keys())


    #Economy - is it affordable to play?
    if not speakonomy.check_affordability(sound_name):
        return redirect(url_for("home", message="Ain't nobody got speakerbucks for that!"))
    
    run_with_lock(sb.play, sound_name)
    if sound_name == "rebecca-black":
        speakonomy.set_free_play_timeout(minutes=5)
        parse_and_route_speech(sb, "It's Friday. Friday. So all sounds are free for the next 5 minutes.")
    return redirect(url_for("home"))

@app.route('/say/')
@app.route('/say/<text>')
def say(text=None):

    if not text:
        text = request.args.get('speech-text', None)

    if request.args.get('record_utterance', "false") == "true" and text[0] != "!":
        evr.record_utterance(text)
    elif text[0] != "!":
        text = ".." + text

    if not text or len(text) > 100:
        return redirect(url_for("home"))

    parse_and_route_speech(sb, text)

    redir = request.referrer or url_for("home")
    return redirect(redir)  

if __name__ == '__main__':
    app.run('0.0.0.0',port=8080)
