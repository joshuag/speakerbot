""" This is default config file. Fill in and rename to config.py """
config = {
    'mashape_api_key': "",
    'twitter':{
        'app_key':'',
        'app_secret':'',
        'oauth_token':'',
        'oauth_token_secret':''
    },
    'database':{
    	'driver':'mysql|sqlite3',
    	'host':'',
    	'user':'',
    	'pass':'',
    	'database':'',
        'db_path':'' #sqlite database file name
    }
}