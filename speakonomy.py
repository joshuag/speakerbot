import datetime as dt
import os
import sys
from speaker_db import SpeakerDB

class Speakonomy:

    def __init__(self, speakerbot=None, disabled=False):
        self.db = SpeakerDB()
        self.speakerbot = speakerbot
        self.disabled = disabled

    def check_affordability(self, sound_name=None, cost=None):
        if not self.is_active():
            return True
        if not cost:
            cost = self.db.execute("SELECT cost FROM sounds WHERE name=?", [sound_name,]).fetchone()['cost']
        balance = self.get_speakerbuck_balance()
        if cost <= balance:
            return True
        return False

    def deposit_funds(self, amount=1):
        assert isinstance(amount,int)
        self.db.execute("UPDATE bank_account set balance=balance+{}".format(amount))

    def get_free_play_timeout(self):
        expiration_timestamp = self.db.execute("SELECT free_play_timeout FROM bank_account").fetchone()['free_play_timeout']
        return dt.datetime.fromtimestamp(expiration_timestamp)

    def get_last_withdrawal_time(self, include_sbpm=False):
        last_withdrawal_time = self.db.execute("SELECT last_withdrawal_time FROM bank_account").fetchone()['last_withdrawal_time']
        last_withdrawal_time = dt.datetime.fromtimestamp(last_withdrawal_time)
        if not include_sbpm:
            return last_withdrawal_time

        today_time = dt.datetime.combine(dt.date.today(), dt.time(8, 00))
        if last_withdrawal_time < today_time:
            last_withdrawal_time = today_time

        minutes_since_last_withdrawal = (dt.datetime.now() - last_withdrawal_time).total_seconds() / 60
        
        spbm = int((minutes_since_last_withdrawal + 9) / 10)
        return last_withdrawal_time, spbm

    def get_speakerbuck_balance(self):
        balance = self.db.execute("SELECT balance FROM bank_account").fetchone()
        if balance:
            return balance['balance']
        return 0

    def is_active(self):
        return True
        if self.disabled:
            return False
        if dt.datetime.today().weekday() in [5,6]:
            return False
            
        current_hour = dt.datetime.now().hour
        if current_hour < 8 or current_hour > 18:
            return False

        if dt.datetime.now() < self.get_free_play_timeout():
            return False

        return True

    def regulate_costs(self):
        self.db.execute("UPDATE sounds set cost=CAST(0.95*cost+0.05*base_cost AS INT) WHERE cost > base_cost")
        self.db.execute("UPDATE sounds set cost=base_cost WHERE cost < base_cost")

    def sell_sound(self, sound_name, **kwargs):
        if self.is_active():
            cost = self.db.execute("SELECT cost FROM sounds WHERE name=?", [sound_name,]).fetchone()['cost']
            self.withdraw_funds(cost)
            self.db.execute("UPDATE sounds set cost=cost*2 where name=?", [sound_name,])

    def set_free_play_timeout(self, expiration_datetime=None, hours=0, minutes=0):
        if not expiration_datetime:
            expiration_datetime = dt.datetime.now() + dt.timedelta(hours=hours, minutes=minutes)
        expiration_timestamp = expiration_datetime.strftime("%s")
        self.db.execute("UPDATE bank_account SET free_play_timeout=?", [expiration_timestamp,])

    def get_sound_base_cost(self, sound_path):
        try:
            sound_size = os.stat(sound_path).st_size
            sound_cost = int(sound_size/1024 * 0.0854455 - 0.0953288 + 0.5)
            if sound_cost < 1:
                sound_cost = 1
        except:
            sound_cost = 0
        return sound_cost

    def set_sound_base_costs(self, sound_dir="sounds"):
        assert self.speakerbot != None
        if not self.speakerbot.sounds:
            self.speakerbot.load_sounds()

        for sound_name in self.speakerbot.sounds:
            
            sound_path = '{}/{}'.format(sound_dir, self.speakerbot.sounds[sound_name][0])
            sound_cost = self.get_sound_base_cost(sound_path)

            self.db.execute("UPDATE sounds SET base_cost={} where name='{}'".format(sound_cost, sound_name))

    def withdraw_funds(self, amount):
        self.deposit_funds(amount=-1*amount)
        withdrawal_time = dt.datetime.now().strftime("%s")
        self.db.execute("UPDATE bank_account SET last_withdrawal_time={}".format(withdrawal_time))    

    
if __name__ == "__main__":
    speakonomy = Speakonomy()
    if not speakonomy.is_active():
        pass
    try:
        deposit_amount = int(sys.argv[1])
    except:
        last_withdrawal_time, deposit_amount = speakonomy.get_last_withdrawal_time(include_sbpm=True)
        
        if deposit_amount < 1:
            deposit_amount = 1

    print "Depositing {}...".format(deposit_amount)
    speakonomy.deposit_funds(deposit_amount)
    speakonomy.regulate_costs()