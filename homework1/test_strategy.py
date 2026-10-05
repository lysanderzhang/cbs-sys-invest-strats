"""Deterministic correctness checks, not independent validation against authors."""
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace
import unittest

import numpy as np
import pandas as pd
import strategy as s

SOURCE = Path("/Users/lysanzh/Library/CloudStorage/OneDrive-Personal/MacBook/curriculum/1 courses/sem-3 2026 fall/FINC9339 systematic investment strategies/homework/hw1/hw1.spy.20250313-20251201.intra-30m.xlsx")


class StrategyChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cfg = s.Config()
        _, cls.clean, cls.sd = s.load_workbook(SOURCE)
        cls.f, cls.d, _ = s.build_features(cls.clean, cls.sd, cls.cfg)

    def test_volume_rejects_false_cumulative(self):
        with self.assertRaises(ValueError):
            s.incremental_volume(self.f, "cumulative")
        a = pd.DataFrame({"date":[1,1,1,2,2], "volume":[5,12,20,3,9]})
        self.assertEqual(s.incremental_volume(a,"cumulative").incremental_volume.tolist(),[5,7,8,3,6])

    def test_hand_vwap(self):
        a = pd.DataFrame({"date":[1,1,1], "volume":[2,3,5], "interval_price":[100,110,90],
                          "upper":[105]*3,"lower":[95]*3})
        r = s.approximate_vwap(s.incremental_volume(a))
        np.testing.assert_allclose(r.vwap_approx,[100,106,98])

    def test_noise_manual_and_half_day_window(self):
        for day,slot in [("2025-04-02","11:00"),("2025-07-07","14:00"),("2025-12-01","14:00")]:
            date = pd.Timestamp(day)
            prior_dates = self.d.index[self.d.index<date][-14:]
            a = self.f[self.f.date.isin(prior_dates) & self.f.slot.eq(slot)]
            expected = sum(abs(row.price/row.open_proxy-1) for row in a.itertuples())/len(a)
            r = self.f[self.f.date.eq(date) & self.f.slot.eq(slot)].iloc[0]
            self.assertAlmostEqual(r.noise_sigma,expected,places=14)
            self.assertEqual(r.noise_count,len(a))
            self.assertEqual(len(a),14 if day=="2025-04-02" else 13)

    def test_lagged_volatility_manual(self):
        date = self.d.index[14]
        series = self.sd.sort_values("date").set_index("date").close
        history = series[series.index<date].iloc[-15:].to_numpy()
        returns = history[1:]/history[:-1]-1
        expected = np.sqrt(sum((returns-returns.mean())**2)/13)
        self.assertAlmostEqual(expected,self.d.loc[date,"spy_vol_prior14"],places=14)
        shares,lev=s.dynamic_position_size(100000,500,.01,"C",self.cfg)
        self.assertEqual((shares,lev),(400,2))
        self.assertEqual(s.dynamic_position_size(100000,500,.001,"C",self.cfg),(800,4))

    def test_future_mutation_preserves_earlier_features_and_trades(self):
        cutoff=pd.Timestamp("2025-08-01 12:00")
        altered=self.clean.copy()
        # Start-labeled row at 12:00 is available only at 12:30.
        mask=altered.source_timestamp>=cutoff
        altered.loc[mask,"price"]*=1.1
        altered.loc[mask,"volume"]*=2
        sd=self.sd.copy()
        sd.loc[sd.date>=cutoff.normalize(),"close"]*=1.1
        f2,d2,_=s.build_features(altered,sd,self.cfg)
        cols=["timestamp","price","upper","lower","vwap_approx","noise_sigma"]
        pd.testing.assert_frame_equal(self.f.loc[self.f.timestamp<=cutoff,cols].reset_index(drop=True),
                                      f2.loc[f2.timestamp<=cutoff,cols].reset_index(drop=True))
        for model in "ABC":
            e1=s.execute_trades(self.f,self.d,model,self.cfg)[1]
            e2=s.execute_trades(f2,d2,model,self.cfg)[1]
            pd.testing.assert_frame_equal(e1[e1.timestamp<=cutoff].reset_index(drop=True),
                                          e2[e2.timestamp<=cutoff].reset_index(drop=True))

    def test_state_rules(self):
        r=SimpleNamespace(is_close=False,timestamp=pd.Timestamp("2025-04-02 11:00"),
                          anchor_available_at=pd.Timestamp("2025-04-02 10:00"),eligible_day=True,
                          price=100.,upper=101.,lower=99.,vwap_approx=100.5)
        self.assertEqual(s.generate_signal(r,1,"A",self.cfg)[0],1)
        self.assertEqual(s.generate_signal(r,1,"B",self.cfg)[0],0)
        r.price=98
        self.assertEqual(s.generate_signal(r,1,"A",self.cfg)[0],-1)
        self.assertEqual(s.generate_signal(r,1,"B",self.cfg)[0],-1)
        r.price=101
        self.assertEqual(s.generate_signal(r,0,"A",self.cfg)[0],0)
        r.price=102
        r.vwap_approx=103
        self.assertEqual(s.generate_signal(r,0,"B",self.cfg)[0],1)
        self.assertEqual(s.generate_signal(r,0,"B",replace(self.cfg,entry_vwap_filter=True))[0],0)
        r.is_close=True
        self.assertEqual(s.generate_signal(r,-1,"A",self.cfg)[0],0)

    def test_known_reversal_pnl_and_costs(self):
        date=pd.Timestamp("2025-04-02")
        rows=[]
        for clock,p in [("10:00",100),("10:30",102),("11:00",98),("16:00",97)]:
            t=pd.Timestamp(f"2025-04-02 {clock}")
            rows.append(dict(date=date,timestamp=t,source_timestamp=t-pd.Timedelta(minutes=30),price_source_timestamp=t,
                price=p,upper=101.,lower=99.,vwap_approx=100.,noise_sigma=.01,noise_count=14,
                long_stop=101.,short_stop=99.,is_close=clock=="16:00",eligible_day=True,
                anchor_available_at=pd.Timestamp("2025-04-02 10:00")))
        daily=pd.DataFrame([dict(date=date,eligible=True,open_proxy=100,spy_vol_prior14=.01)]).set_index("date")
        days,events,trades,_=s.execute_trades(pd.DataFrame(rows),daily,"A",self.cfg)
        # 1,000 shares: long loses 4,000; short gains 1,000; four legs cost 18.
        self.assertEqual(len(events),4)
        self.assertEqual(len(trades),2)
        self.assertAlmostEqual(days.net_pnl.iloc[0],-3018)
        self.assertEqual(events.action.tolist(),["ENTRY","EXIT","ENTRY","EXIT"])
        delayed=s.execute_trades(pd.DataFrame(rows),daily,"A",replace(self.cfg,execution_delay=1))[1]
        self.assertEqual(delayed.iloc[0].timestamp,pd.Timestamp("2025-04-02 11:00"))
        self.assertEqual(delayed.iloc[0].signal_timestamp,pd.Timestamp("2025-04-02 10:30"))

    def test_full_ledgers_and_session_close(self):
        for model in "ABC":
            days,events,trades,positions=s.execute_trades(self.f,self.d,model,self.cfg)
            ledger=s.daily_pnl_equity(events,days.index,self.cfg.initial_equity)
            np.testing.assert_allclose(ledger.equity,days.equity,atol=1e-7,rtol=0)
            np.testing.assert_allclose(trades.net_pnl.sum(),days.net_pnl.sum(),atol=1e-7,rtol=0)
            self.assertTrue((positions.groupby("date").direction.last()==0).all())
            self.assertTrue((events.timestamp.dt.strftime("%H:%M")>="10:30").all())
            np.testing.assert_allclose(events.costs,events.shares*.0045,atol=1e-12,rtol=0)
            for date in s.EARLY_CLOSES:
                ev=events[events.date.eq(pd.Timestamp(date))]
                self.assertTrue((ev.timestamp.dt.hour<=13).all())
                self.assertFalse(((ev.timestamp.dt.hour==13)&ev.action.eq("ENTRY")).any())
            if model=="C": self.assertTrue((days.sizing_leverage<=4).all())


if __name__=="__main__":
    unittest.main(verbosity=2)
