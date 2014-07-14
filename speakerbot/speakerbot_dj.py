
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
        sb.load_sounds()
        results = self.db.execute("SELECT name, theme_song, last_theme_play_time FROM person").fetchall()
        for result in results:
            play_ok = True
            if result['last_theme_play_time']:
                last_theme_play_time = dt.datetime.fromtimestamp(result['last_theme_play_time'])
                minutes_since_last_theme = (dt.datetime.now() - last_theme_play_time).total_seconds() / 60
                if minutes_since_last_theme < 15:
                    play_ok = False

            self.theme_songs[minimize_string(result['name'])] = (result['name'], result['theme_song'], play_ok)
        self.last_theme_cache_time = dt.datetime.now()

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
            return

        for message_number in messages[0].split(' '):
            (ret, data) = mail.fetch(message_number, '(RFC822)')
            email_body = str(email.message_from_string(data[0][1]))

            user = self.extract_email_field(email_body, 'User')
            door = self.extract_email_field(email_body, 'Door')
            # date = self.extract_email_field(email_body, 'Date')
            # time = self.extract_email_field(email_body, 'Time')
            # entry_time = dt.datetime.strptime(date+' '+time, '%m/%d/%y %I:%M:%S %p EDT')
            if not user:
                print "No user"
                continue
            user = minimize_string(user)
            door = minimize_string(door)
            #lookup theme song based on user
            if not self.theme_songs.get(user):
                print "Unrecognized user:", user
                print self.theme_songs
                continue
            print "USER: [{}] DOOR: [{}]".format(user, door)
            real_name, theme_song, play_ok = self.theme_songs[user]

            if not theme_song or not play_ok:
                print "No theme song or play_ok"
                continue
            if door in ['mezstairdevhall','nstair2labdrb1n1mezz','nhall2labdrb2n2mezz']:
                print 'queue now'
            elif door in ['sstairdrb2n1serv']:
                print 'queue in 45 seconds'
                sleep(45)
            elif door in ['1stflelevbutton']:
                print 'queue in 60 seconds'
                sleep(60)
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
    dj = SpeakerbotDJ(speakerbot=sb)
    while True:
        if (dt.datetime.now()-dj.last_theme_cache_time).total_seconds() >= 60:
            dj.cache_theme_songs()            

        try:
            dj.check_for_entrance()
        except Exception as e:
            print str(e)
        sleep(2)
