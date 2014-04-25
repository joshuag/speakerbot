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
        if current_hour < 8 or current_hour > 18:
            return False

        if dt.datetime.now() < self.get_free_play_timeout():
            return False

        return True

    def set_free_play_timeout(self, expiration_datetime=None, hours=0, minutes=0):
        if not expiration_datetime:
            expiration_datetime = dt.datetime.now() + dt.timedelta(hours=hours, minutes=minutes)
        expiration_timestamp = expiration_datetime.strftime("%s")
        self.db.execute("UPDATE bank_account SET free_play_timeout=?", [expiration_timestamp,])

    def get_free_play_timeout(self):
        expiration_timestamp = self.db.execute("SELECT free_play_timeout FROM bank_account").fetchone()['free_play_timeout']
        return dt.datetime.fromtimestamp(expiration_timestamp)

    def get_speakerbuck_balance(self):
        balance = self.db.execute("SELECT balance FROM bank_account").fetchone()
        if balance:
            return balance['balance']
        return 0

    def check_affordability(self, sound_name=None, cost=None):
        if not self.is_active():
            return True
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
        withdrawal_time = dt.datetime.now().strftime("%s")
        self.db.execute("UPDATE bank_account SET last_withdrawal_time={}".format(withdrawal_time))

    def deposit_funds(self, amount=1):
        assert isinstance(amount,int)
        self.db.execute("UPDATE bank_account set balance=balance+{}".format(amount))

    def get_last_withdrawal_time(self):
        last_withdrawal_time = self.db.execute("SELECT last_withdrawal_time FROM bank_account").fetchone()['last_withdrawal_time']
        return dt.datetime.fromtimestamp(last_withdrawal_time)

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
    speakonomy = Speakonomy()
    try:
        deposit_amount = int(sys.argv[1])
    except:
        deposit_amount = 1

        last_withdrawal_time = speakonomy.get_last_withdrawal_time()
        if last_withdrawal_time > 0:
            minutes_since_last_withdrawal = (dt.datetime.now() - last_withdrawal_time).total_seconds() / 60
            deposit_amount = int((minutes_since_last_withdrawal + 9) / 10)

    print "Depositing {}...".format(deposit_amount)
    speakonomy.deposit_funds(deposit_amount)
    speakonomy.regulate_costs()