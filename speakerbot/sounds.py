import subprocess
import math
import os

from config import config

class Sound(object):

    def __init__(self, name, file_name, votes, cost, downvotes, sound_player=None):
        self.name = name
        self.file_name = file_name
        self.votes = votes
        self.cost = cost
        self.downvotes = downvotes
        self.sound_player = sound_player
        self.path = os.path.join(config['sound_dir'], file_name)
        if not sound_player:
            self.sound_player = SoundPlayer()

    def get_score(self):
        #Everybody loves pi
        return int(self.votes-self.downvotes*math.pi*3)

    def play(self):
        self.sound_player.play_sound(self.path)

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


