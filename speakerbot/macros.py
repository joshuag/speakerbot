import json
import re

class Macro(object):

    def __init__(self, speakerbot, name, manifest=None):
        self.sb = speakerbot
        self.name = name
        self.load_from_manifest(manifest)

    def load_from_manifest(self, manifest):
        commands = json.loads(manifest)

        self.commands = []
        for command in commands:
            command_type, command_text = command.split('|', 1)
            if command_type not in ['sound','speech']:
                raise Exception("Invalid command type")
            self.commands.append((command_type, command_text))
    
    def execute(self):
        for command_type, command_argument in self.commands:
            if command_type == 'sound':
                self.sb.play(command_argument)
            elif command_type == 'speech':
                self.sb.say(command_argument)

    def get_cost(self):
        total_cost = 0
        sound_queue = []

        for command_type, command_argument in self.commands:
            if command_type == 'sound':
                total_cost += self.sb.sounds[command_argument].cost * (sound_queue.count(command_argument) + 1)
                sound_queue.append(command_argument)
            elif command_type == 'speech':
                total_cost += 2 * len(re.sub(r'[^a-z0-9]','', command_argument, flags=re.I))

        return total_cost
