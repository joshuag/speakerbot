import json
import os
import subprocess

from config import config
from hashlib import sha256
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
import requests
from urllib import quote_plus

from text_manipulators import split_text
from sounds import SoundPlayer

from speaker_db import SpeakerDB


class IBMTextToSpeech(object):

    PHRASE_LENGTH = 1000

    def __init__(self):
        self._db = SpeakerDB()
        self._voice = config['ibm_speech']['voice']

    def say(self, text):
        phrases = [text]
        filenames = []
        if len(text) > self.PHRASE_LENGTH:
            phrases = split_text(text, self.PHRASE_LENGTH)

        voice = self._voice
        if 'debias' in text.lower() or 'debiac' in text.lower():
            voice = 'it-IT_FrancescaVoice'

        for phrase in phrases:
            hsh = sha256()
            hsh.update(phrase.lower() + voice
            filename = 'speech/%s.wav' % hsh.hexdigest()
            self.create_sound_file(filename, phrase, voice)
            filenames.append(filename)

        for filename in filenames:
            SoundPlayer(config['wav_player']).play_sound(filename)

    def create_sound_file(self, filename, text, voice):
        if os.path.isfile(filename) and os.path.getsize(filename):
            return

        headers = {
            'Content-Type': 'text/plain',
            'Accept': 'audio/wav'
        }

        params = {
            'text': text,
            'voice': voice
        }

        response = requests.get('https://stream.watsonplatform.net/text-to-speech/api/v1/synthesize',
                                headers=headers,
                                auth=(config['ibm_speech']['user'], config['ibm_speech']['pw']),
                                params=params)

        with open(filename, 'wb') as f:
            f.write(response.content)


class ATTTextToSpeech(object):

    CLIENT_ID = config['att_speech']['client_id']
    CLIENT_SECRET = config['att_speech']['client_secret']
    CLIENT_SCOPE = ['TTS']
    TOKEN_FIELD_NAME = 'att_speech_token'
    TOKEN_URL = 'https://api.att.com/oauth/v4/token'
    TTS_URL = 'https://api.att.com/speech/v3/textToSpeech'
    TTS_VOICE = config['att_speech']['voice_name']
    TTS_TEMPO = config['att_speech']['tempo']
    TTS_HEADERS = {
            'Content-Type': 'text/plain',
            'Accept': 'audio/x-wav',
            'X-Arg': 'VoiceName={},Tempo={}'.format(TTS_VOICE, TTS_TEMPO)
    }

    def __init__(self):
        self._db = SpeakerDB()
        self.client = self.get_client()

    def get_client(self):
        token = self._db.get_field_value('att_speech_token')
        if token:
            token = json.loads(token)
        else:
            oauth = OAuth2Session(client=BackendApplicationClient(client_id=self.CLIENT_ID))
            token = oauth.fetch_token(token_url=self.TOKEN_URL,
                                      client_id=self.CLIENT_ID,
                                      client_secret=self.CLIENT_SECRET,
                                      scope=self.CLIENT_SCOPE)
            self.save_token(token)

        return OAuth2Session(self.CLIENT_ID,
                             token=token,
                             auto_refresh_url=self.TOKEN_URL,
                             token_updater=self.save_token)

    def save_token(self, token):
        self._db.set_field_value(self.TOKEN_FIELD_NAME, json.dumps(token))

    def say(self, text):
        phrases = [text]
        filenames = []
        if len(text) > 100:
            phrases = split_text(text, 100)

        for phrase in phrases:
            hsh = sha256()
            hsh.update(phrase.lower() + self.TTS_VOICE + self.TTS_TEMPO)
            filename = 'speech/%s.wav' % hsh.hexdigest()
            self.create_sound_file(filename, phrase)
            filenames.append(filename)

        for filename in filenames:
            SoundPlayer(config['wav_player']).play_sound(filename)

    def create_sound_file(self, filename, text):
        if os.path.isfile(filename) and os.path.getsize(filename):
            return

        response = self.client.post(self.TTS_URL, headers=self.TTS_HEADERS, data=text)
        with open(filename, 'wb') as f:
            f.write(response.content)


class GoogleTextToSpeech(object):

    def __init__(self, url_string=None):

        self.url_string = url_string
        if not url_string:
            self.url_string = u"http://translate.google.com/translate_tts?tl=en_gb&ie=UTF-8&q=%s"

    def say(self, text):

        if len(text) > 100:
            phrases = split_text(text, 100)
            for phrase in phrases:
                self.say(phrase)

            return

        text = quote_plus(text.encode("utf-8"))

        hsh = sha256()
        hsh.update(text.lower())

        filename = "speech/%s.mp3" % hsh.hexdigest()

        self.get_file(filename, self.url_string % (text))

        s = SoundPlayer()
        s.play_sound(filename)

    def get_file(self, filename, url, retries=3):

        if not os.path.isfile(filename) or os.path.getsize(filename) == 0:
            f = open(filename, "w")
            subprocess.call(
                    ['curl','-A Mozilla', url], 
                    stdout=f)
        if os.path.getsize(filename) == 0 and retries > 0:
            self.get_file(filename, url, retries=retries-1)


class EspeakTextToSpeech(object):

    def __init__(self, speak_path="espeak", wpm=150):

        self.speak_path = speak_path
        self.wpm_string = "-s %s" % wpm 

    def say(self, text): 

        subprocess.call([self.speak_path, text, self.wpm_string])