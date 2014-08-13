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
        if not sound_player:
            self.sound_player = SoundPlayer(config['sound_dir'], config['sound_player'])

    def get_score(self):
        #Everybody loves pi
        return int(self.votes-self.downvotes*math.pi*3)

    def play(self):
        self.sound_player.play_sound(self.file_name)

class SoundPlayer(object):

    def __init__(self, sound_dir, sound_player):
        self.base_path = sound_dir
        self.sound_player = sound_player


    def play_sound(self, file_name):
        file_path = os.path.join(self.base_path, file_name)

        with open(os.devnull, "w") as fnull:
            subprocess.call([self.sound_player, file_path], stdout=fnull, stderr=fnull)


