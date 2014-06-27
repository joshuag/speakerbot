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

def niceify_number(i):
    #swiped from http://codegolf.stackexchange.com/questions/4707/outputting-ordinal-numbers-1st-2nd-3rd
    k=i%10
    return "%d%s" % (i,"tsnrhtdd"[(i/10%10!=1)*(k<4)*k::4])