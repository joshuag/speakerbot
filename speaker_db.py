from db.base_db import base_db
import sqlite3
import datetime as dt

from dynamic_class import attach_methods, Singleton

from config import config

@attach_methods(
        "speaker_db_plugins.speakerbot_migrations", 
        "speaker_db_plugins.speakerbot_reports", 
        "speaker_db_plugins.speaker_images_comments",
        "speaker_db_plugins.people"
        )
class SpeakerDB(base_db):

    __metaclass__ = Singleton

    def __init__(self, db_path=None):

        db_settings = config.get("database", None)

        if not db_settings and db_path:
            db_settings = db_path

        super(SpeakerDB, self).__init__(settings=db_settings)

if __name__ == "__main__":
    db = SpeakerDB(db_path="speakerbot.db")
