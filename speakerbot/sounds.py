import datetime as dt
import math
import os
import subprocess

from config import config

class Sound(object):

    def __init__(self, name, file_name, votes, cost, base_cost, downvotes, date_added, sound_player=None):
        self.name = name
        self.file_name = file_name
        self.votes = votes
        self.cost = cost
        self.base_cost = base_cost
        self.downvotes = downvotes
        self.sound_player = sound_player
        self.date_added = date_added
        self.path = os.path.join(config['sound_dir'], file_name)
        if not sound_player:
            self.sound_player = SoundPlayer()

    def get_score(self):
        #Everybody loves pi
        return int(self.votes-self.downvotes*math.pi*3)

    def play(self):
        self.sound_player.play_sound(self.path)

    def was_recently_added(self):
        if (dt.datetime.now() - self.date_added).total_seconds() / 60 / 60 / 24 < 7:
            return True
        return False

class SoundPlayer(object):

    def __init__(self, executable=None):
        self.executable = executable
        if not executable:
            self.executable = config['sound_player']

    def play_sound(self, file_path):
        if not os.path.exists(file_path):
            raise Exception("File not found: {}".format(file_path))
        with open(os.devnull, "w") as fnull:
            subprocess.call([self.executable, file_path], stdout=fnull, stderr=fnull)


