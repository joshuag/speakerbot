import datetime as dt
import os
import sys
from speaker_db import SpeakerDB

class Speakonomy:
    def __init__(self, speakerbot=None):
        self.db = SpeakerDB()
        self.speakerbot = speakerbot

    def is_active(self):
        if dt.datetime.today().weekday() in [5,6]:
            return False
            
        current_hour = dt.datetime.now().hour
        if current_hour >= 8 and current_hour < 18:
            return True

        return False

    def get_speakerbuck_balance(self):
        balance = self.db.execute("SELECT balance FROM bank_account").fetchone()
        if balance:
            return balance['balance']
        return 0

    def check_affordability(self, sound_name=None, cost=None):
        if not cost:
            cost = self.db.execute("SELECT cost FROM sounds WHERE name=?", [sound_name,]).fetchone()['cost']
        balance = self.get_speakerbuck_balance()
        if cost <= balance:
            return True
        return False

    def sell_sound(self, sound_name, **kwargs):
        if self.is_active():
            cost = self.db.execute("SELECT cost FROM sounds WHERE name=?", [sound_name,]).fetchone()['cost']
            self.db.execute("UPDATE bank_account SET balance=balance-{}".format(cost))
            self.db.execute("UPDATE sounds set cost=cost*2 where name=?", [sound_name,])

    def withdraw_funds(self, amount):
        self.deposit_funds(amount=-1*amount)

    def deposit_funds(self, amount=1):
        assert isinstance(amount,int)
        self.db.execute("UPDATE bank_account set balance=balance+{}".format(amount))

    def regulate_costs(self):
        self.db.execute("UPDATE sounds set cost=CAST(0.95*cost+0.05*base_cost AS INT) WHERE cost > base_cost")
        self.db.execute("UPDATE sounds set cost=base_cost WHERE cost < base_cost")

    def set_sound_base_costs(self, sound_dir="sounds"):
        assert self.speakerbot != None
        if not self.speakerbot.sounds:
            self.speakerbot.load_sounds()

        for sound_name in self.speakerbot.sounds:
            sound_path = '{}/{}'.format(sound_dir, self.speakerbot.sounds[sound_name][0])
            sound_cost = os.stat(sound_path).st_size
            try:
                sound_size = os.stat(sound_path).st_size
                sound_cost = int(sound_size/1024 * 0.0854455 - 0.0953288 + 0.5)
                if sound_cost < 1:
                    sound_cost = 1
            except:
                sound_cost = 0
            self.db.execute("UPDATE sounds SET base_cost={} where name='{}'".format(sound_cost, sound_name))

if __name__ == "__main__":
    try:
        deposit_amount = sys.argv[1]
    except:
        deposit_amount = 1
    speakonomy = Speakonomy()
    speakonomy.deposit_funds(deposit_amount)
    speakonomy.regulate_costs()