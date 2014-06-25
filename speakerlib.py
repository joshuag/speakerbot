import re
import subprocess

def get_mp3_seconds(path):
    out = subprocess.check_output('mpg321 -t "{}"'.format(path), shell=True, stderr=subprocess.STDOUT)

    mins, secs = re.search(r'\[(\d+):(\d+)\] Decoding', out).groups()
    return int(mins) * 60 + int(secs)

def minimize_string(s):
    if isinstance(s, (str, unicode)):
        return ''.join(c.lower() for c in s if not c.isspace())
    return s