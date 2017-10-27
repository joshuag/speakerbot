# -*- coding: utf-8 -*-
import time

from slackclient import SlackClient
import requests

from config import config
from speaker_db import SpeakerDB


db = SpeakerDB()
slack_token = config['slackerbot_token']
base_url = config['base_url']

sc = SlackClient(slack_token)

things_to_listen_for = {}


def parse_channel_message(msg):

    try:
        if len(msg) == 0 or msg[0]['type'] != 'message':
            output = {'type': 'noop'}
        else:
            msg = msg[0]
            if msg['type'] == 'message':
                output = parse_message(msg)

    except KeyError:

        output = {'type': 'noop'}

        print msg

    return output


def sb_play_sound(sound_name):

    requests.get("%s/play_sound/%s" % (base_url, sound_name))


def sb_say(speech_text):

    requests.post('%s/say/' % base_url,
        data={'speech-text': speech_text[:100]}
    )


def parse_listener_argument_string(argument):
    try:  # this is defensive coding, right?

        arg = argument.replace(u'“', '"').replace(u'”', '"')

        if '"' in arg:

            first_quote_pos = arg.find('"')

            substring = arg[first_quote_pos + 1:]

            second_quote_pos = substring.find('"')

            thing_to_listen_for = substring[:second_quote_pos].lower()

            command = parse_command(substring[second_quote_pos + 2:])

            return thing_to_listen_for, command

    except:
        pass


def hydrate_listeners():

    listeners = db.execute("SELECT * from slacker_listeners")

    for listener in listeners:

        things_to_listen_for[listener["phrase"]] = (listener["command"], listener["argument"])


def install_listener(thing, command):

    things_to_listen_for[thing] = command

    save_listener(thing, command[0], command[1])


def get_listener(thing):

    listener = None

    try:
        listener = db.execute("select * from slacker_listeners where phrase=?", thing).next()
        return listener["phrase"], listener["command"], listener["argument"]
    except:
        pass

    return listener


def save_listener(thing, command, argument):

    if get_listener(thing):
        db.execute("UPDATE slacker_listeners SET command=?, argument=? WHERE phrase=?", (command, argument, thing))
    else:
        db.execute("INSERT into slacker_listeners (phrase, command, argument) VALUES (?,?,?)", (thing, command, argument))


def route_message(msg_text):

    for key in things_to_listen_for:

            if key in msg_text.lower():

                command_tuple = things_to_listen_for[key]

                route_command(command_tuple[0], command_tuple[1])


def route_command(command, argument):

    if command == 'play':
        sb_play_sound(argument)

    if command == 'say':
        sb_say(argument)

    if command == 'listen':
        install_listener(*parse_listener_argument_string(argument))


def route(msg):

    if msg['type'] == 'message':

        route_message(msg['text'])

    if msg['type'] == 'command':

        route_command(msg['command'], msg['argument'])


def parse_message(msg):

    output = {}

    output['text'] = msg['text']
    output['user'] = msg['user']

    if msg['text'][:3] == '!sb':

        command_tuple = parse_command(msg['text'])

        output['type'] = 'command'
        output['command'] = command_tuple[0]
        output['argument'] = command_tuple[1]

    else:
        output['type'] = 'message'

    return output


def parse_command(text):

    text = text.replace('!sb ', '')

    try:
        first_space_position = text.index(' ')

        command = text[:first_space_position]

        argument = text[first_space_position + 1:]

    except ValueError:

        command = text

        argument = None

    return (command, argument)


# Main Routine

hydrate_listeners()

if sc.rtm_connect():

    while True:

        route(parse_channel_message(sc.rtm_read()))
        time.sleep(1)
else:

    print "Connection Failed"
