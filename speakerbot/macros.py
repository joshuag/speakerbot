import json

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
            if command_type == 'sound':
                self.commands.append((self.sb._play, command_text))
            elif command_type == 'speech':
                self.commands.append((self.sb._say, command_text))
            else:
                raise Exception("Invalid command type")
    
    def execute(self):
        for f, v in self.commands:
            f(v)

    def get_cost(self):
        return 999