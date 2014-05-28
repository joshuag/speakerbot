
import datetime as dt
import email
import imaplib
import re
from time import sleep

from config import config
from speaker_db import SpeakerDB
from Speakerbot import Speakerbot
from speakerlib import minimize_string

class SpeakerbotDJ:

    def __init__(self, speakerbot=None):
        self.db = SpeakerDB()
        self.theme_songs = {}
        self.speakerbot = speakerbot
        self.last_theme_cache_time = dt.datetime.min

    def extract_email_field(self, s, field):
        field_match = re.search(r'^\s*{}:\s+(.*?)\s*$'.format(re.escape(field)), s, flags=re.I|re.M)
        if not field_match:
            return None
        return field_match.group(1)

    def cache_theme_songs(self):
        self.last_theme_cache_time = dt.datetime.now()
        results = self.db.execute("SELECT name, theme_song, last_theme_play_time FROM person").fetchall()
        for result in results:
            play_ok = True
            if result['last_theme_play_time']:
                last_theme_play_time = dt.datetime.fromtimestamp(result['last_theme_play_time'])
                minutes_since_last_theme = (dt.datetime.now() - last_theme_play_time).total_seconds() / 60
                if minutes_since_last_theme < 240:
                    play_ok = False

            self.theme_songs[minimize_string(result['name'])] = (result['name'], result['theme_song'], play_ok)

    def check_for_entrance(self):
        # Needs cleanup... 
        mail = imaplib.IMAP4(config['email']['host'])
        mail.login(config['email']['user'], config['email']['pass'])
        mail.select()
        (retcode, messages) = mail.search(None, '(UNSEEN)')
        if retcode != 'OK':
            print 'Unknown error'
            return
        if len(messages[0]) == 0:
            print 'No new mail'
            return

        for message_number in messages[0].split(' '):
            (ret, data) = mail.fetch(message_number, '(RFC822)')
            email_body = str(email.message_from_string(data[0][1]))

            user = self.extract_email_field(email_body, 'User')
            door = self.extract_email_field(email_body, 'Door')
            if not user:
                continue
            user = minimize_string(user)
            door = minimize_string(door)
            #lookup theme song based on user
            if not self.theme_songs.get(user):
                print "Unrecognized user:", user
                continue
            real_name, theme_song, play_ok = self.theme_songs[user]

            if not theme_song or not play_ok:
                continue
            if door in ['mezstairdevhall','nstair2labdrb1n1mezz']:
                print 'queue now'
            elif door in ['sstairdrb2n1serv']:
                print 'queue in a minute'
                sleep(45)
            else:
                print 'Unknown door:', door
                continue

            # Hackaround to avoid economy
            sb.se.play(sb.sounds[theme_song][0])
            theme_play_time = dt.datetime.now().strftime("%s")
            self.db.execute("UPDATE person SET last_theme_play_time=? WHERE name=?", [theme_play_time, real_name])
            self.cache_theme_songs()
        mail.close()

if __name__ == "__main__":
    sb = Speakerbot()
    dj = SpeakerbotDJ()
    while True:
        if (dt.datetime.now()-dj.last_theme_cache_time).total_seconds() >= 60:
            dj.cache_theme_songs()            

        dj.check_for_entrance()
        sleep(2)
