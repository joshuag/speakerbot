""" This is default config file. Fill in and rename to config.py """
config = {
    'debug': False,
    'mashape_api_key': "",
    'database':{
    	'driver':'mysql|sqlite3',
    	'host':'',
    	'user':'',
    	'pass':'',
    	'database':'',
        'db_path':'' #sqlite database file name
    },
    'sound_dir': 'sounds/',
    'sound_player': 'mpg321',
    'wav_player': 'aplay|afplay',
    'att_speech': {
        'client_id': '',
        'client_secret': '',
        'scope': (
            'TTS',
        )
    }
}