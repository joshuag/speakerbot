import subprocess
import os

class SoundEffect(object):

    def __init__(self, sound_player="mpg321", sound_dir="sounds"):
        self.sound_player = sound_player
        self.path = "%s/" % sound_dir

    def play(self, sound_file):

        file_path = self.path + sound_file

        self.play_sound(file_path)

    def play_sound(self, file_path):

        with open(os.devnull, "w") as fnull:
            subprocess.call([self.sound_player, file_path], stdout = fnull, stderr = fnull)