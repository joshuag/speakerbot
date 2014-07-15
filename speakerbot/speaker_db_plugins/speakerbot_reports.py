

def get_lucky_numbers(self):
    return self.execute("select lucky_number, count(lucky_number) as occurences, sum(case when outcome < 1 then 1 else 0 end) as negative_outcomes, sum(case when outcome > 1 then 1 else 0 end)  as successful_outcomes from wager_history where lucky_number <> 0 group by lucky_number")

def get_number_occurence(self):
    return self.execute("select chosen_number, count(chosen_number) as occurences, sum(case when outcome < 1 then 1 else 0 end) as negative_outcomes, sum(case when outcome > 1 then 1 else 0 end)  as successful_outcomes from wager_history group by chosen_number")

def get_multiplier_occurence(self):
    return self.execute("select win_multiplier, count(win_multiplier) as occurences, sum(case when outcome < 1 then 1 else 0 end) as negative_outcomes, sum(case when outcome > 1 then 1 else 0 end)  as successful_outcomes from wager_history group by win_multiplier")

def get_wagers_and_outcomes_by_day(self, limit=30):

    return self.execute("select date(wager_time, 'unixepoch') as wager_date, case when sum(wager) > 100000 then 100000 else sum(wager) end as amount_wagered, case when sum(outcome) > 100000 then 100000 when sum(outcome) < -100000 then -100000 else sum(outcome) end as outcome from wager_history group by date(wager_time, 'unixepoch') limit ?", [limit])

def get_wagers_by_outcome(self, limit=15):

    return self.execute("select wager, sum(case when outcome > 1 then 1 else 0 end)  as successful_outcomes, sum(case when outcome < 1 then 1 else 0 end) as negative_outcomes from wager_history group by wager order by count(wager) desc limit ?", [limit])

def get_lucky_and_chosen_cooccurence(self):

    return self.execute("select lucky.number, lucky.lucky_numero, chosen.chosen_numero, case when coc.cooccurrence is null then 0 else coc.cooccurrence end as cooccurence from (select chosen_number as number, count(chosen_number) as chosen_numero, null as lucky_number from wager_history group by chosen_number) chosen inner join (select lucky_number as number, null as chosen_number, count(lucky_number) as lucky_numero from wager_history group by lucky_number) lucky on lucky.number=chosen.number left join (select lucky_number as number, count(*) as cooccurrence from wager_history where lucky_number = chosen_number group by number) coc on lucky.number=coc.number")

def get_aggregate_wager_stats(self, start=0, end=4000000000):

    results = self.execute("""
            SELECT 
                count(*) as spins,
                AVG(wager) as avg_wgr, 
                AVG(outcome) as avg_out, 
                MAX(wager) as max_wgr, 
                SUM(wager) as ttl_wgr, 
                SUM(outcome) as net_win, 
                AVG(win_multiplier) as avg_multi,
                SUM(cheated_death) as cheat_death
            FROM 
            wager_history
            where wager_time > ? and wager_time < ?
            """, [start, end])
    try:
        results = results.next()
        results["avg_out"] = int(round(results["avg_out"]))
        results["avg_wgr"] = int(round(results["avg_wgr"]))
        results["avg_multi"] = int(round(results["avg_multi"]))
        results["roi"] = str(int(round(results["avg_out"] / results["avg_wgr"], 2) * 100)) + "%"
    except:
        results = None
        pass

    return results

def get_wager_history(self, limit=50):

        return self.execute ("select datetime(wager_time, 'unixepoch') as time, lucky_number, wager, outcome, chosen_number, win_multiplier, cheated_death from wager_history order by wager_time desc LIMIT ?", [limit])