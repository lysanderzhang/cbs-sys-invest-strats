"""Paper-only, auditable SPY replication. Read PRE_IMPLEMENTATION.md first.

No author code was consulted. Prices are retrospective vendor observations;
causality is conditional on the explicitly selected timestamp convention.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import hashlib
import json
import os
from pathlib import Path

import numpy as np
import pandas as pd

EARLY_CLOSES = {"2025-07-03", "2025-11-28"}  # supplied assignment, not inferred by P&L


@dataclass(frozen=True)
class Config:
    lookback: int = 14
    initial_equity: float = 100_000.0
    target_vol: float = .02
    leverage_cap: float = 4.0
    commission: float = .0035
    slippage: float = .001
    timestamp_mode: str = "start"
    vwap_method: str = "endpoint"
    execution_delay: int = 0
    entry_vwap_filter: bool = False
    annual_days: int = 252


def load_workbook(path):
    sheets = pd.read_excel(path, sheet_name=None)
    raw = sheets["BBRG.Intraday"].rename(columns={"Time Stamp": "source_timestamp", "Last Price": "price", "Volume": "volume"})
    clean = sheets["AV.Clean"].rename(columns={"Time Stamp": "source_timestamp", "Last Price": "price", "Volume, AV": "volume"})
    daily = sheets["BBRG.Daily"].rename(columns={"Time Stamp": "date", "Last Price": "close", "Volume": "volume"})
    return raw, clean, daily


def audit_data(raw, clean, daily):
    a = clean.copy().sort_values("source_timestamp")
    a["date"] = a.source_timestamp.dt.normalize()
    a["time"] = a.source_timestamp.dt.strftime("%H:%M")
    dd = daily.set_index("date").sort_index()
    day = a.groupby("date").agg(rows=("price", "size"), volume_sum=("volume", "sum"), closing_print=("price", "last"))
    day["daily_volume"] = dd.volume
    day["volume_difference"] = day.volume_sum - day.daily_volume
    day["daily_close"] = dd.close
    day["close_difference"] = day.closing_print - day.daily_close
    day["early_close"] = day.index.strftime("%Y-%m-%d").isin(EARLY_CLOSES)
    joined = a.merge(raw[["source_timestamp", "volume", "price"]], on="source_timestamp", how="left", suffixes=("", "_raw"))
    changes = joined.loc[(joined.volume != joined.volume_raw) | (joined.price != joined.price_raw)].copy()
    summary = dict(sessions=len(day), cleaned_rows=len(a), raw_rows=len(raw), daily_rows=len(dd),
                   missing_cells=int(clean.isna().sum().sum()), duplicates=int(a.source_timestamp.duplicated().sum()),
                   negative_volume=int((a.volume < 0).sum()), nonpositive_price=int((a.price <= 0).sum()),
                   volume_decreases=int((a.groupby("date").volume.diff() < 0).sum()),
                   volume_mismatch_days=int((day.volume_difference != 0).sum()),
                   missing_daily_sessions=[str(x.date()) for x in dd.loc[day.index.min():day.index.max()].index.difference(day.index)])
    return summary, day, changes


def prepare_data(clean, cfg):
    """Validate and expose observed price availability, preserving source labels.

    No fill/interpolation. Structural half-day afternoon records are excluded.
    Separate closing prints are available ONLY at the scheduled liquidation time.
    """
    a = clean.copy().sort_values("source_timestamp").reset_index(drop=True)
    if a.isna().any().any() or a.source_timestamp.duplicated().any():
        raise ValueError("Missing cells or duplicate timestamps require explicit resolution")
    if (a.price <= 0).any() or (a.volume < 0).any():
        raise ValueError("Invalid price/volume")
    a["date"] = a.source_timestamp.dt.normalize()
    groups, excluded = [], []
    for date, g in a.groupby("date", sort=True):
        end = date + pd.Timedelta(hours=13 if str(date.date()) in EARLY_CLOSES else 16)
        start = date + pd.Timedelta(hours=9, minutes=30)
        expected = pd.date_range(start, end, freq="30min", inclusive="left")
        bars = g[g.source_timestamp.isin(expected)].copy()
        if len(bars) != len(expected):
            raise ValueError(f"Unexpected missing half-hour interval: {date}")
        closing = g[g.source_timestamp == end]
        if len(closing) != 1:
            raise ValueError(f"Missing scheduled closing print: {date}")
        excluded.append(g[~g.source_timestamp.isin(expected)])
        bars["timestamp"] = bars.source_timestamp + pd.Timedelta(minutes=30 if cfg.timestamp_mode == "start" else 0)
        bars["interval_price"] = bars.price
        bars["price_source_timestamp"] = bars.source_timestamp
        bars["is_close"] = False
        # In the default convention the last interval and closing print share
        # one decision time; retain interval price separately for VWAP.
        if cfg.timestamp_mode == "start":
            bars.loc[bars.index[-1], "price"] = closing.price.iloc[0]
            bars.loc[bars.index[-1], "price_source_timestamp"] = closing.source_timestamp.iloc[0]
            bars.loc[bars.index[-1], "is_close"] = True
        else:
            extra = closing.copy()
            extra["timestamp"] = end
            extra["interval_price"] = extra.price
            extra["price_source_timestamp"] = extra.source_timestamp
            extra["volume"] = 0.0  # do not treat residual as a regular interval
            extra["is_close"] = True
            bars = pd.concat([bars, extra])
        bars["scheduled_close"] = end
        bars["anchor_available_at"] = bars.timestamp.iloc[0]
        bars["open_proxy"] = bars.price.iloc[0]
        bars["slot"] = bars.timestamp.dt.strftime("%H:%M")
        groups.append(bars)
    return pd.concat(groups, ignore_index=True), pd.concat(excluded, ignore_index=True)


def construct_daily(bars, source_daily, cfg):
    """Daily closes can be retained retrospectively, but intraday uses are lagged."""
    sd = source_daily.sort_values("date").set_index("date")
    if sd.index.duplicated().any() or sd.close.isna().any():
        raise ValueError("Invalid daily data")
    daily = bars.groupby("date").agg(open_proxy=("open_proxy", "first"), observed_close=("price", "last"),
                                     anchor_available_at=("anchor_available_at", "first"), scheduled_close=("scheduled_close", "first"))
    daily["close"] = sd.close.reindex(daily.index)
    daily["previous_close"] = sd.close.shift(1).reindex(daily.index)
    returns = sd.close.pct_change(fill_method=None)
    daily["spy_return"] = returns.reindex(daily.index)
    daily["spy_vol_prior14"] = returns.rolling(cfg.lookback, min_periods=cfg.lookback).std(ddof=1).shift(1).reindex(daily.index)
    daily["prior_sessions"] = np.arange(len(daily))
    daily["eligible"] = (daily.prior_sessions >= cfg.lookback) & daily.spy_vol_prior14.notna() & daily.previous_close.notna()
    return daily


def incremental_volume(frame, convention="interval"):
    """Cumulative counter inputs must be monotone within a day; never abs/clip diffs."""
    out = frame.copy()
    if convention == "interval":
        inc = out.volume.astype(float)
    elif convention == "cumulative":
        inc = out.groupby("date").volume.diff()
        first = out.groupby("date").cumcount() == 0
        inc.loc[first] = out.loc[first, "volume"]
    else:
        raise ValueError(convention)
    if inc.isna().any() or (inc < 0).any():
        raise ValueError("Not a valid within-session cumulative volume counter")
    out["incremental_volume"] = inc
    out["cumulative_observed_volume"] = inc.groupby(out.date).cumsum()
    return out


def calculate_noise_area(bars, daily, cfg):
    out = bars.copy()
    out["absolute_move"] = (out.price / out.open_proxy - 1).abs()
    moves = out.pivot(index="date", columns="slot", values="absolute_move").reindex(daily.index)
    # Rectangular session x clock-time panel: never roll over last 14 nonmissing
    # observations, which would reach too far back after a half day.
    prior = moves.shift(1)
    means = prior.rolling(cfg.lookback, min_periods=1).mean()
    counts = prior.rolling(cfg.lookback, min_periods=1).count()
    means.iloc[:cfg.lookback] = np.nan
    keys = pd.MultiIndex.from_frame(out[["date", "slot"]])
    out["noise_sigma"] = means.stack().reindex(keys).to_numpy()
    out["noise_count"] = counts.stack().reindex(keys).to_numpy()
    out["previous_close"] = out.date.map(daily.previous_close)
    out["upper"] = np.maximum(out.open_proxy, out.previous_close) * (1 + out.noise_sigma)
    out["lower"] = np.minimum(out.open_proxy, out.previous_close) * (1 - out.noise_sigma)
    out["eligible_day"] = out.date.map(daily.eligible)
    return out


def approximate_vwap(bars, method="endpoint"):
    """Observed-interval VWAP approximation, NOT exchange/trade-level VWAP.

    Endpoint is the only interval price supplied. Midpoint assumes a linear
    price path and uses the first endpoint alone for the first interval.
    Neither method allocates final daily-volume residuals backwards.
    """
    out = bars.copy()
    p = out.interval_price
    if method == "midpoint":
        lag = out.groupby("date").interval_price.shift(1)
        p = (p + lag.fillna(p)) / 2
    elif method != "endpoint":
        raise ValueError(method)
    out["vwap_weight_price"] = p
    numerator = (p * out.incremental_volume).groupby(out.date).cumsum()
    out["vwap_approx"] = numerator / out.cumulative_observed_volume.replace(0, np.nan)
    out["long_stop"] = np.maximum(out.upper, out.vwap_approx)
    out["short_stop"] = np.minimum(out.lower, out.vwap_approx)
    return out


def generate_signal(row, direction, model, cfg):
    """Return next desired direction + reason; no trade accounting here."""
    if row.is_close:
        return 0, "session_close"
    if row.timestamp <= row.anchor_available_at or not row.eligible_day or not np.isfinite(row.upper):
        return direction, "not_ready"
    p, u, l, v = row.price, row.upper, row.lower, row.vwap_approx
    breakout = 1 if p > u else (-1 if p < l else 0)
    if model == "A":
        return (breakout, "breakout_or_reverse") if breakout else (direction, "hold_inside_noise")
    if not np.isfinite(v):
        return direction, "vwap_unavailable"
    candidate = breakout
    if cfg.entry_vwap_filter and ((candidate == 1 and p <= v) or (candidate == -1 and p >= v)):
        candidate = 0
    stop = (direction == 1 and p < max(u, v)) or (direction == -1 and p > min(l, v))
    if stop:
        # Prohibit immediate reentry in the direction just stopped out.
        return (candidate if candidate == -direction else 0), "stop_or_reverse"
    if direction:
        return direction, "hold"
    return candidate, "entry" if candidate else "flat"


def transaction_costs(shares, cfg):
    return abs(shares) * cfg.commission, abs(shares) * cfg.slippage


def dynamic_position_size(equity, open_proxy, prior_vol, model, cfg):
    if equity <= 0:
        raise ValueError("Insolvent portfolio; do not continue with negative sizing")
    if model == "C":
        if not np.isfinite(prior_vol) or prior_vol < 0:
            raise ValueError("Invalid lagged volatility")
        leverage = cfg.leverage_cap if prior_vol == 0 else min(cfg.leverage_cap, cfg.target_vol / prior_vol)
    else:
        leverage = 1.0
    return int(np.floor(equity * leverage / open_proxy)), leverage


def execute_trades(features, daily, model, cfg):
    """Explicit event loop; realized P&L ledger plus mark-to-market snapshots.

    Fill reference equals observed price. Adverse slippage is a separate debit,
    not also embedded in gross P&L. A reversal is two charged executions.
    """
    equity = cfg.initial_equity
    events, trades, days, snapshots = [], [], [], []
    for date, g in features.groupby("date", sort=True):
        d = daily.loc[date]
        if not d.eligible:
            continue
        start_equity = equity
        shares, leverage = dynamic_position_size(start_equity, d.open_proxy, d.spy_vol_prior14, model, cfg)
        direction, entry, entry_cost, entry_time, trade_id = 0, np.nan, 0., None, None
        pending = None
        day_gross, day_cost, day_comm, day_slip = 0., 0., 0., 0.
        for r in g.itertuples(index=False):
            signal_time = r.timestamp
            if r.is_close:
                desired, reason = 0, "session_close"
                pending = None
            elif cfg.execution_delay:
                if pending is None:
                    desired, reason = direction, "no_pending_order"
                else:
                    desired, reason, signal_time = pending
            else:
                desired, reason = generate_signal(r, direction, model, cfg)
            if shares == 0:
                desired = 0
            if desired != direction:
                if direction:
                    comm, slip = transaction_costs(shares, cfg)
                    gross = direction * shares * (r.price - entry)
                    net_trade = gross - entry_cost - comm - slip
                    day_gross += gross
                    day_cost += comm + slip
                    day_comm += comm
                    day_slip += slip
                    equity += gross - comm - slip
                    trades.append(dict(model=model, trade_id=trade_id, date=date, entry_timestamp=entry_time,
                                       exit_timestamp=r.timestamp, direction=direction, entry_price=entry, exit_price=r.price,
                                       shares=shares, sizing_leverage=leverage, entry_equity=start_equity,
                                       gross_pnl=gross, costs=entry_cost+comm+slip, net_pnl=net_trade,
                                       return_on_entry_notional=net_trade/(shares*entry),
                                       return_on_start_equity=net_trade/start_equity,
                                       pnl_per_share=net_trade/shares, exit_reason=reason))
                    events.append(event_record(r, model, trade_id, "EXIT", direction, shares, leverage, start_equity,
                                               gross, comm, slip, reason, signal_time))
                    direction = 0
                if desired:
                    direction, entry, entry_time = desired, r.price, r.timestamp
                    trade_id = len(trades) + 1
                    comm, slip = transaction_costs(shares, cfg)
                    entry_cost = comm + slip
                    equity -= entry_cost
                    day_cost += entry_cost
                    day_comm += comm
                    day_slip += slip
                    events.append(event_record(r, model, trade_id, "ENTRY", direction, shares, leverage, start_equity,
                                               0., comm, slip, reason, signal_time))
            if cfg.execution_delay and not r.is_close:
                target, why = generate_signal(r, direction, model, cfg)
                pending = (target, why, r.timestamp)
            marked = equity + (direction * shares * (r.price - entry) if direction else 0.)
            snapshots.append(dict(model=model, date=date, timestamp=r.timestamp, direction=direction,
                                  held_shares=direction*shares, equity_marked=marked,
                                  marked_leverage=abs(direction*shares*r.price)/marked if marked>0 else np.nan))
        assert direction == 0
        days.append(dict(model=model, date=date, start_equity=start_equity, gross_pnl=day_gross,
                         commission=day_comm, slippage=day_slip, costs=day_cost, net_pnl=equity-start_equity,
                         equity=equity, daily_return=equity/start_equity-1, shares=shares, sizing_leverage=leverage))
    return pd.DataFrame(days).set_index("date"), pd.DataFrame(events), pd.DataFrame(trades), pd.DataFrame(snapshots)


def event_record(r, model, trade_id, action, direction, shares, leverage, equity, gross, comm, slip, reason, signal_time):
    side = direction if action == "ENTRY" else -direction
    return dict(model=model, trade_id=trade_id, date=r.date, timestamp=r.timestamp, signal_timestamp=signal_time,
                source_timestamp=r.source_timestamp, price_source_timestamp=r.price_source_timestamp,
                action=action, order_side="BUY" if side==1 else "SELL",
                direction=direction, price=r.price, upper=r.upper, lower=r.lower, noise_sigma=r.noise_sigma,
                noise_count=r.noise_count, vwap_approx=r.vwap_approx, long_stop=r.long_stop, short_stop=r.short_stop,
                shares=shares, sizing_leverage=leverage, execution_notional_leverage=shares*r.price/equity,
                gross_pnl=gross, commission=comm, slippage=slip, costs=comm+slip,
                net_pnl=gross-comm-slip, reason=reason)


def daily_pnl_equity(events, dates, initial_equity):
    """Independent ledger aggregation; event net P&L includes each cost once."""
    pnl = events.groupby("date").net_pnl.sum().reindex(dates, fill_value=0.)
    return pd.DataFrame({"net_pnl": pnl, "equity": initial_equity + pnl.cumsum()})


def buy_and_hold(daily, dates, cfg):
    """Fractional-share price-series benchmark, entered at prior session close.

    No separate dividends: adjustment status unknown. Gross comparator matches
    daily close-to-close regression; net comparator pays entry and final exit.
    """
    d = daily.loc[dates]
    p0 = d.previous_close.iloc[0]
    gross = cfg.initial_equity * d.close / p0
    unit_cost = cfg.commission + cfg.slippage
    q = cfg.initial_equity / (p0 + unit_cost)
    net = q * d.close
    net.iloc[-1] -= q * unit_cost
    def frame(equity):
        previous = equity.shift(1).fillna(cfg.initial_equity)
        return pd.DataFrame(dict(equity=equity, daily_return=equity/previous-1, net_pnl=equity-previous))
    return frame(gross), frame(net)


def performance_statistics(day, trades, benchmark_returns, cfg):
    import statsmodels.api as sm
    r = day.daily_return
    total = day.equity.iloc[-1]/cfg.initial_equity - 1
    vol = r.std(ddof=1)
    peak = day.equity.cummax().clip(lower=cfg.initial_equity)
    result = dict(sessions=len(r), cumulative_return=total,
                  annualized_return=(1+total)**(cfg.annual_days/len(r))-1,
                  annualized_volatility=vol*np.sqrt(cfg.annual_days),
                  sharpe_zero_rf=r.mean()/vol*np.sqrt(cfg.annual_days) if vol>0 else np.nan,
                  maximum_drawdown=(day.equity/peak-1).min(),
                  daily_hit_ratio_all_days=(r>0).mean(), daily_hit_ratio_nonzero_days=(r[r!=0]>0).mean(),
                  best_day_return=r.max(), best_day_date=str(r.idxmax().date()),
                  worst_day_return=r.min(), worst_day_date=str(r.idxmin().date()),
                  final_equity=day.equity.iloc[-1])
    if trades is not None:
        result.update(number_of_round_trips=len(trades), number_of_executions=2*len(trades),
                      trade_hit_ratio=(trades.net_pnl>0).mean() if len(trades) else np.nan,
                      average_trade_net_pnl=trades.net_pnl.mean() if len(trades) else np.nan,
                      average_trade_return_notional=trades.return_on_entry_notional.mean() if len(trades) else np.nan,
                      average_trade_return_equity=trades.return_on_start_equity.mean() if len(trades) else np.nan,
                      average_trade_net_pnl_per_share=trades.pnl_per_share.mean() if len(trades) else np.nan,
                      total_costs=day.costs.sum())
    # Paper's raw-return regression, with both conventional and HAC uncertainty.
    if benchmark_returns is None:
        return result
    reg = pd.concat([r.rename("strategy"), benchmark_returns.rename("spy")], axis=1).dropna()
    if len(reg) >= 30 and reg.spy.std() > 0:
        x = sm.add_constant(reg.spy)
        fit = sm.OLS(reg.strategy, x).fit()
        hac = fit.get_robustcov_results(cov_type="HAC", maxlags=5)
        ci = hac.conf_int()
        result.update(alpha_daily=fit.params["const"], alpha_annual_arithmetic=fit.params["const"]*cfg.annual_days,
                      beta=fit.params["spy"], regression_n=len(reg), regression_r_squared=fit.rsquared,
                      alpha_pvalue_ols=fit.pvalues["const"], beta_pvalue_ols=fit.pvalues["spy"],
                      alpha_pvalue_hac5=hac.pvalues[0], beta_pvalue_hac5=hac.pvalues[1],
                      alpha_annual_ci_low_hac5=ci[0,0]*cfg.annual_days, alpha_annual_ci_high_hac5=ci[0,1]*cfg.annual_days,
                      beta_ci_low_hac5=ci[1,0], beta_ci_high_hac5=ci[1,1])
    return result


def build_features(clean, source_daily, cfg):
    bars, excluded = prepare_data(clean, cfg)
    daily = construct_daily(bars, source_daily, cfg)
    features = approximate_vwap(calculate_noise_area(incremental_volume(bars), daily, cfg), cfg.vwap_method)
    return features, daily, excluded


def create_plots(features, models, benchmarks, out, cfg):
    os.environ.setdefault("MPLCONFIGDIR", str(out / ".matplotlib"))
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(2, 1, figsize=(11, 7), sharex=True, gridspec_kw={"height_ratios": [2,1]})
    all_days = {**{k:v[0] for k,v in models.items()}, "SPY gross": benchmarks[0]}
    for name, day in all_days.items():
        eq = day.equity
        initial_date = eq.index[0] - pd.Timedelta(days=1)
        path = pd.concat([pd.Series([cfg.initial_equity], index=[initial_date]), eq])
        axes[0].plot(path.index, path/cfg.initial_equity, label=name)
        axes[1].plot(path.index, 100*(path/path.cummax()-1))
    axes[0].set(title="First implementation: data-constrained SPY replication", ylabel="Equity / initial equity")
    axes[0].legend(ncol=4)
    axes[1].set(ylabel="Drawdown (%)", xlabel="2025 trading dates")
    for ax in axes: ax.grid(alpha=.2)
    fig.tight_layout()
    fig.savefig(out/"equity_drawdown.png", dpi=160)
    plt.close(fig)
    # Auditable examples: first traded day, biggest C loss/win, and half days.
    cday, events, _, _ = models["C"]
    dates = sorted(set([events.date.min(), cday.daily_return.idxmax(), cday.daily_return.idxmin(),
                        *[pd.Timestamp(x) for x in EARLY_CLOSES]]))
    fig, axes = plt.subplots(len(dates),1,figsize=(11,3*len(dates)))
    for date, ax in zip(dates, axes):
        g = features[features.date==date]
        ax.plot(g.timestamp, g.price, label="Observed price", color="black")
        ax.plot(g.timestamp, g.upper, label="Upper", color="#2166ac")
        ax.plot(g.timestamp, g.lower, label="Lower", color="#b2182b")
        ax.plot(g.timestamp, g.vwap_approx, label="Approx. VWAP", color="#d18b00")
        ev = events[events.date==date]
        for action, marker in [("ENTRY","^"),("EXIT","x")]:
            q = ev[ev.action==action]
            ax.scatter(q.timestamp,q.price,marker=marker,s=55,label=action,zorder=5)
        ax.set_title(str(date.date())+" — Model C")
        ax.grid(alpha=.2)
        ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%H:%M"))
    axes[0].legend(ncol=6,fontsize=8)
    fig.tight_layout()
    fig.savefig(out/"spot_check_days.png", dpi=150)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workbook", type=Path)
    parser.add_argument("--output", type=Path, default=Path("outputs/baseline"))
    parser.add_argument("--timestamp-mode", choices=["start","as_labeled"], default="start")
    parser.add_argument("--vwap-method", choices=["endpoint","midpoint"], default="endpoint")
    parser.add_argument("--execution-delay", type=int, choices=[0,1], default=0)
    parser.add_argument("--entry-vwap-filter", action="store_true", help="Optional ambiguity sensitivity; baseline entries use Noise boundaries only")
    args = parser.parse_args()
    cfg = Config(timestamp_mode=args.timestamp_mode, vwap_method=args.vwap_method, execution_delay=args.execution_delay,
                 entry_vwap_filter=args.entry_vwap_filter)
    out = args.output
    out.mkdir(parents=True,exist_ok=True)
    raw, clean, sd = load_workbook(args.workbook)
    audit, audit_days, changes = audit_data(raw,clean,sd)
    features, daily, excluded = build_features(clean,sd,cfg)
    audit_days.to_csv(out/"data_audit_by_day.csv")
    changes.to_csv(out/"cleaning_changes.csv",index=False)
    excluded.to_csv(out/"excluded_rows.csv",index=False)
    features.to_csv(out/"features.csv",index=False)
    daily.to_csv(out/"daily_inputs.csv")
    (out/"data_audit.json").write_text(json.dumps(audit,indent=2))
    models = {m:execute_trades(features,daily,m,cfg) for m in "ABC"}
    dates = models["A"][0].index
    benchmarks = buy_and_hold(daily,dates,cfg)
    metrics = {}
    for m,(days,events,trades,snapshots) in models.items():
        ledger = daily_pnl_equity(events,dates,cfg.initial_equity)
        np.testing.assert_allclose(ledger.equity,days.equity,rtol=0,atol=1e-7)
        np.testing.assert_allclose(trades.net_pnl.sum(), days.net_pnl.sum(),rtol=0,atol=1e-7)
        for name,data in [("daily",days),("executions",events),("trades",trades),("positions",snapshots)]:
            data.to_csv(out/f"{m}_{name}.csv",index=(name=="daily"))
        metrics[m] = performance_statistics(days,trades,daily.loc[dates,"spy_return"],cfg)
    for name, data in zip(["SPY_gross","SPY_net"],benchmarks):
        data.to_csv(out/f"{name}_daily.csv")
        metrics[name] = performance_statistics(data,None,None,cfg)
    pd.DataFrame(metrics).T.to_csv(out/"performance.csv",float_format="%.10f")
    provenance = dict(config=asdict(cfg),input_path=str(args.workbook.resolve()),
                      input_sha256=hashlib.sha256(args.workbook.read_bytes()).hexdigest(),
                      source_code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                      first_scored_session=str(dates[0].date()),last_scored_session=str(dates[-1].date()),
                      author_code_consulted=False, external_market_data_used=False,
                      pandas=pd.__version__,numpy=np.__version__)
    (out/"run_manifest.json").write_text(json.dumps(provenance,indent=2))
    create_plots(features,models,benchmarks,out,cfg)
    print(pd.DataFrame(metrics).T[["cumulative_return","annualized_return","annualized_volatility","sharpe_zero_rf","maximum_drawdown","number_of_round_trips"]].to_string(float_format=lambda x:f"{x:.5f}"))


if __name__ == "__main__":
    main()
