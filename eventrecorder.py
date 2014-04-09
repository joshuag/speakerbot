from hashlib import sha256

class EventRecorder(object):

    def __init__(self, db):

        self.db = db

    def record_utterance(self, speech_text):

        sha = sha256()
        sha.update(speech_text)
        sha_hash = sha.hexdigest()

        matched_snippet = self.db.execute("SELECT votes FROM snippets where sha256=?", [sha_hash]).fetchone()

        if matched_snippet:
            votes = matched_snippet["votes"] + 1
            self.db.execute("UPDATE snippets set votes=? where sha256=?", [votes, sha_hash])
        else:
            self.db.execute("INSERT into snippets (sha256, speech_text, votes) VALUES (?, ?, 0) ", [sha_hash, speech_text])

    def record_sound_event(self, sound_name, event_result=None):

        matched_sound = self.db.execute("SELECT votes FROM sounds where name=?", [sound_name]).fetchone()

        if matched_sound:
            votes = matched_sound["votes"] + 1

            self.db.execute("UPDATE sounds set votes=? where name=?", [votes, sound_name])