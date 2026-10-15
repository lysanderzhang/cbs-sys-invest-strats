#!/usr/bin/env python3
"""Build every table, number macro and chart used by the investor presentation.

Reads ONLY the canonical CSV outputs of the original research package
(../../results/tables). Nothing in the strategy pipeline is rerun or
changed. Display rounding is applied here, from full-precision values.

Usage (from report/presentation/):
    "$HOME/.venvs/sys-inv/bin/python" scripts/build_assets.py [--tables ../../../results/tables]
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.ticker as mticker  # noqa: E402
import pandas as pd  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
GEN = ROOT / "generated"
FIG = ROOT / "figures"
ACCENT = "#1F4E79"

NAMES = {
    "B0": "Equal weight",
    "B1": "Relative momentum",
    "B2": "Dual momentum, cash hurdle",
    "B3": "Dual momentum + vol cap",
    "60_40": "Monthly 60/40",
    "SPY": "SPY buy-and-hold",
    "CASH": "Cash (French RF)",
    "A0": "Static factor",
    "A1": "Volatility scaling",
    "A2": "Bear/VIX regime",
    "A3": "Regime $\\times$ volatility",
}
CODE = {"60_40": "60/40", "SPY": "SPY", "CASH": "Cash"}


def code(v: str) -> str:
    return CODE.get(v, v)


def pct(x: float, d: int = 2) -> str:
    """Percent string with a true minus sign for LaTeX."""
    s = f"{100 * x:.{d}f}"
    return s.replace("-", "$-$") + "\\%"


def num(x: float, d: int = 2) -> str:
    return f"{x:.{d}f}".replace("-", "$-$")


def write(name: str, text: str) -> None:
    (GEN / name).write_text(text)


# ----------------------------------------------------------------------------
def setup_mpl() -> None:
    import matplotlib.font_manager as fm
    for f in Path("/usr/share/texmf/fonts/opentype/public/lm").glob("lmroman*.otf"):
        fm.fontManager.addfont(str(f))
    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": ["Latin Modern Roman", "DejaVu Serif"],
            "mathtext.fontset": "cm",
            "pdf.fonttype": 3,
            "font.size": 8.5,
            "axes.titlesize": 9,
            "axes.labelsize": 8,
            "legend.fontsize": 7.8,
            "xtick.labelsize": 7.5,
            "ytick.labelsize": 7.5,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.linewidth": 0.6,
            "xtick.major.width": 0.6,
            "ytick.major.width": 0.6,
            "lines.linewidth": 1.0,
            "savefig.bbox": "tight",
            "savefig.pad_inches": 0.02,
        }
    )


STYLE = {
    "B3": dict(color=ACCENT, lw=1.6, ls="-", zorder=5),
    "B1": dict(color="0.45", lw=0.9, ls="-", zorder=3),
    "B2": dict(color="0.45", lw=0.9, ls=(0, (1, 1.2)), zorder=3),
    "60_40": dict(color="black", lw=1.0, ls=(0, (4, 2)), zorder=4),
    "SPY": dict(color="0.72", lw=0.9, ls="-", zorder=2),
    "A0": dict(color="0.70", lw=0.9, ls="-", zorder=2),
    "A1": dict(color="0.40", lw=0.9, ls=(0, (1, 1.2)), zorder=3),
    "A2": dict(color="black", lw=0.9, ls=(0, (4, 2)), zorder=3),
    "A3": dict(color=ACCENT, lw=1.5, ls="-", zorder=5),
}


def nav_with_initial(path: Path) -> pd.Series:
    """Daily NAV with the initial capital of 1 prepended (day before execution).

    The execution-day NAV already contains the initial trading cost; it is not
    renormalised away. Peak tracking therefore starts at initial capital 1.
    """
    d = pd.read_csv(path, parse_dates=["date"])
    first = d["date"].iloc[0] - pd.Timedelta(days=1)
    s = pd.concat([pd.Series([1.0], index=[first]), d.set_index("date")["nav"]])
    return s


def drawdown(nav: pd.Series) -> pd.Series:
    return nav / nav.cummax() - 1.0


def wealth_dd_figure(tables: Path, variants, outfile: Path, ylim_dd, yticks_w, ncol=3, figsize=(6.9, 2.75), legend_ax=2, wealth_ylim=None):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
    mdd = {}
    handles = []
    for v in variants:
        nav = nav_with_initial(tables / f"{v}_daily.csv")
        dd = drawdown(nav)
        mdd[v] = dd.min()
        short = {"SPY": "buy-and-hold", "60_40": "monthly", "B1": "relative", "B2": "dual, cash hurdle",
                 "B3": "dual + vol cap", "A0": "static", "A1": "vol scaling", "A2": "bear/VIX regime",
                 "A3": "regime $\\times$ vol"}[v]
        dds = f"{100 * dd.min():.1f}%".replace("-", "\u2212")
        lab = f"{code(v)} {short} ({dds})"
        (h,) = ax1.plot(nav.index, nav.values, label=lab, **STYLE[v])
        handles.append(h)
        ax2.plot(dd.index, 100 * dd.values, **STYLE[v])
    ax1.set_yscale("log")
    ax1.yaxis.set_major_locator(mticker.FixedLocator(yticks_w))
    ax1.yaxis.set_minor_locator(mticker.NullLocator())
    ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda y, _: f"{y:g}"))
    ax1.set_title("Wealth of \\$1, log scale", loc="left")
    ax2.set_title("Daily drawdown from running peak (%)", loc="left")
    ax2.set_ylim(*ylim_dd)
    for ax in (ax1, ax2):
        ax.grid(axis="y", color="0.88", lw=0.5)
        ax.margins(x=0.01)
    if legend_ax == 2:
        ax2.legend(handles=handles[::-1], loc="lower right", frameon=True, facecolor="white", edgecolor="white",
                   framealpha=1, handlelength=2.4, borderaxespad=0.2, fontsize=7.2, labelspacing=0.3,
                   title="Max daily drawdown in brackets", title_fontsize=7, alignment="left")
    else:
        ax1.set_ylim(*wealth_ylim)
        ax1.legend(handles=handles[::-1], loc="upper left", frameon=False, handlelength=2.4,
                   borderaxespad=0.2, fontsize=7.2, labelspacing=0.3,
                   title="Max daily drawdown in brackets", title_fontsize=7, alignment="left")
    fig.tight_layout(w_pad=1.8)
    fig.savefig(outfile)
    plt.close(fig)
    return mdd


def exposure_figure(tables: Path, outfile: Path):
    d = pd.read_csv(tables / "B3_daily.csv", parse_dates=["date"]).set_index("date")
    risky = 1 - d["cash_weight_end"]
    b2 = pd.read_csv(tables / "B2_daily.csv", parse_dates=["date"]).set_index("date")
    risky2 = 1 - b2["cash_weight_end"]
    fig, ax = plt.subplots(figsize=(6.9, 2.3))
    ax.fill_between(risky.index, 0, 100 * risky.values, color=ACCENT, alpha=0.25, lw=0, label="B3 risky weight")
    ax.plot(risky.index, 100 * risky.values, color=ACCENT, lw=0.6)
    ax.plot(risky2.index, 100 * risky2.values, color="0.3", lw=0.6, ls=(0, (1, 1.2)), label="B2 risky weight")
    ax.set_ylim(0, 105)
    ax.set_ylabel("Risky weight (% of NAV)")
    ax.grid(axis="y", color="0.88", lw=0.5)
    ax.legend(loc="lower left", frameon=False, ncol=2)
    ax.margins(x=0.01)
    fig.tight_layout()
    fig.savefig(outfile)
    plt.close(fig)


# ----------------------------------------------------------------------------
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tables", default=str(ROOT.parents[1] / "results" / "tables"))
    args = ap.parse_args()
    T = Path(args.tables)
    GEN.mkdir(exist_ok=True)
    FIG.mkdir(exist_ok=True)
    setup_mpl()

    perf = pd.read_csv(T / "performance.csv")
    sens = pd.read_csv(T / "sensitivities.csv")
    boot = pd.read_csv(T / "bootstrap.csv")
    cap = pd.read_csv(T / "capacity_summary.csv")
    capa = pd.read_csv(T / "capacity_active_trades_summary.csv")
    stress = pd.read_csv(T / "stress_periods.csv")

    netB = perf[(perf.prototype == "B") & (perf.basis.str.startswith("modeled net"))]
    grossB = perf[(perf.prototype == "B") & (perf.basis.str.startswith("gross"))]
    A = perf[(perf.prototype == "A") & (perf["sample"] != "long_history_without_VIX")]

    def row(df, v, sample="full"):
        r = df[(df.variant == v) & (df["sample"] == sample)]
        assert len(r) == 1, (v, sample, len(r))
        return r.iloc[0]

    # ---- frozen-conclusion checks (user-specified rounded values) ---------
    expected = {
        "B1": (8.66, 0.607, -25.12),
        "B2": (7.95, 0.570, -25.15),
        "B3": (6.89, 0.614, -17.91),
        "60_40": (8.16, 0.719, -32.62),
    }
    checks = {}
    for v, (c, s, dd) in expected.items():
        r = row(netB, v)
        got = (round(100 * r.CAGR, 2), round(r.Sharpe, 3), round(100 * r.max_daily_drawdown, 2))
        checks[v] = {"expected": [c, s, dd], "csv_rounded": list(got), "match": got == (c, s, dd)}
        assert got == (c, s, dd), (v, got)
    b3cap10 = cap[(cap.variant == "B3") & (cap.ticker == "DBC") & (cap.initial_aum == 10_000_000)].iloc[0]
    assert round(100 * b3cap10.maximum, 2) == 19.17
    assert round(row(netB, "B3").turnover_annual, 2) == 3.15

    # ---- macros ----------------------------------------------------------
    m = {}
    for v in ["B0", "B1", "B2", "B3", "60_40", "SPY"]:
        r = row(netB, v)
        k = {"60_40": "Sixty", "SPY": "Spy"}.get(v, v.replace("B", "B"))
        k = {"B0": "Bzero", "B1": "Bone", "B2": "Btwo", "B3": "Bthree"}.get(v, k)
        m[f"{k}CAGR"] = pct(r.CAGR)
        m[f"{k}Vol"] = pct(r.annual_vol)
        m[f"{k}Sharpe"] = num(r.Sharpe, 3)
        m[f"{k}MDD"] = pct(r.max_daily_drawdown)
        m[f"{k}Turn"] = num(r.turnover_annual, 2)
        m[f"{k}Cash"] = pct(r.cash_fraction, 1) if pd.notna(r.cash_fraction) else "--"
    g3 = row(grossB, "B3")
    m["BthreeGrossCAGR"] = pct(g3.CAGR)
    m["BthreeCostDrag"] = num(100 * (g3.CAGR - row(netB, "B3").CAGR), 2)
    m["BthreeCostAllowance"] = num(100 * row(netB, "B3").turnover_annual * 0.001, 2)
    for v in ["A0", "A1", "A2", "A3"]:
        r = row(A, v)
        k = {"A0": "Azero", "A1": "Aone", "A2": "Atwo", "A3": "Athree"}[v]
        m[f"{k}CAGR"] = pct(r.CAGR)
        m[f"{k}Sharpe"] = num(r.Sharpe, 3)
        m[f"{k}MDD"] = pct(r.max_daily_drawdown)
    m["DBCtenMax"] = pct(b3cap10.maximum)
    m["DBCtenPninetyfive"] = pct(b3cap10.p95)
    b3cap1 = cap[(cap.variant == "B3") & (cap.ticker == "DBC") & (cap.initial_aum == 1_000_000)].iloc[0]
    m["DBConeMax"] = pct(b3cap1.maximum)
    bb = boot[(boot.left == "B3") & (boot.right == "60_40") & (boot["sample"] == "full")].iloc[0]
    m["BootSixtyDiff"] = num(bb.Sharpe_difference, 3)
    m["BootSixtyLo"] = num(bb.Sharpe_difference_low, 3)
    m["BootSixtyHi"] = num(bb.Sharpe_difference_high, 3)
    for v in ["B3", "60_40", "B1", "B2", "SPY"]:
        k = {"60_40": "Sixty", "SPY": "Spy", "B1": "Bone", "B2": "Btwo", "B3": "Bthree"}[v]
        for p in ["2020", "2022"]:
            s = stress[(stress.variant == v) & (stress.period == p)].iloc[0]
            m[f"{k}Y{'twenty' if p == '2020' else 'twentytwo'}"] = pct(s.cumulative_return, 1)
    write("macros.tex", "\n".join(f"\\newcommand{{\\{k}}}{{{v}}}" for k, v in m.items()) + "\n")

    # ---- main results table (slide 7) -----------------------------------
    # "Return/MaxDD" = CAGR / |max daily drawdown|, derived from performance.csv full precision.
    lines = []
    for v in ["B0", "B1", "B2", "B3", "60_40", "SPY"]:
        r = row(netB, v)
        calmar = r.CAGR / abs(r.max_daily_drawdown)
        line = (
            f"{code(v)} & {NAMES[v]} & {pct(r.CAGR)} & {pct(r.annual_vol)} & {num(r.Sharpe, 3)} & "
            f"{pct(r.max_daily_drawdown)} & {pct(r.worst_month, 1)} & {num(calmar, 2)} \\\\"
        )
        if v == "B3":
            line = "\\rowcolor{accentlight} " + line.replace(NAMES[v], "\\textbf{" + NAMES[v] + "}")
            for x in [pct(r.max_daily_drawdown), pct(r.worst_month, 1), num(calmar, 2)]:
                line = line.replace(f"& {x} ", f"& \\textbf{{{x}}} ", 1)
        if v == "60_40":
            lines.append("\\midrule")
        lines.append(line)
    write("tab_main.tex", "\n".join(lines) + "\n")

    # ---- downside / stress macros and table (slide 9) ----------------------
    extra = {}
    for v, k in [("B3", "Bthree"), ("60_40", "Sixty"), ("SPY", "Spy"), ("B1", "Bone")]:
        r = row(netB, v)
        extra[f"{k}WorstM"] = pct(r.worst_month, 1)
        extra[f"{k}WorstQ"] = pct(r.worst_three_month, 1)
        extra[f"{k}ES"] = pct(r.ES95_loss, 1)
        extra[f"{k}Calmar"] = num(r.CAGR / abs(r.max_daily_drawdown), 2)
        d = row(netB, v, "development")
        extra[f"{k}DevMDD"] = pct(d.max_daily_drawdown, 1)
        h = row(netB, v, "historical_holdout")
        extra[f"{k}HoldCAGR"] = pct(h.CAGR, 1)
        extra[f"{k}HoldSharpe"] = num(h.Sharpe, 2)
        extra[f"{k}HoldMDD"] = pct(h.max_daily_drawdown, 1)
    b3, s6 = row(netB, "B3"), row(netB, "60_40")
    extra["DDReduction"] = f"{100 * (1 - b3.max_daily_drawdown / s6.max_daily_drawdown):.0f}"
    extra["BthreeInvested"] = pct(b3.average_exposure, 0)
    with open(GEN / "macros.tex", "a") as fh:
        fh.write("\n".join(f"\\newcommand{{\\{k}}}{{{v}}}" for k, v in extra.items()) + "\n")
    srows = []
    for lab, field, smp, kind in [
        ("Max daily DD 2007--13 (incl.\\ 2008--09)", "max_daily_drawdown", "development", "perf"),
        ("Worst three months", "worst_three_month", "full", "perf"),
        ("Return in 2020", "2020", None, "stress"),
        ("Return in 2022 (stocks and bonds fell)", "2022", None, "stress"),
    ]:
        cells = [lab]
        for v in ["B3", "60_40", "SPY"]:
            if kind == "perf":
                x = row(netB, v, smp)[field]
            else:
                x = stress[(stress.variant == v) & (stress.period == field)].iloc[0].cumulative_return
            cells.append(pct(x, 1))
        cells[1] = "\\textbf{" + cells[1] + "}"
        srows.append(" & ".join(cells) + " \\\\")
    write("tab_stress.tex", "\n".join(srows) + "\n")

    # ---- subperiod table (slide 9) --------------------------------------
    labels = {
        "development": "Development 2007-08-31 to 2013-12-31",
        "validation": "Validation 2014--2019",
        "historical_holdout": "Historical holdout 2020-01 to 2026-08",
        "full": "Full sample 2007-08-31 to 2026-08-31",
    }
    lines = []
    for smp in ["development", "validation", "historical_holdout", "full"]:
        cells = [labels[smp].replace("2007-08-31 to 2013-12-31", "2007-09 to 2013-12").replace("2007-08-31 to 2026-08-31", "2007-09 to 2026-08")]
        for v in ["B3", "60_40"]:
            r = row(netB, v, smp)
            cells += [pct(r.CAGR, 1), num(r.Sharpe, 2), pct(r.max_daily_drawdown, 1)]
        if smp == "full":
            lines.append("\\midrule")
        lines.append(" & ".join(cells) + " \\\\")
    write("tab_sub.tex", "\n".join(lines) + "\n")

    blines = []
    for left, right, smp in [("B3", "60_40", "full"), ("B3", "60_40", "historical_holdout"), ("B3", "B2", "full"), ("B2", "B1", "full")]:
        b = boot[(boot.left == left) & (boot.right == right) & (boot["sample"] == smp)].iloc[0]
        lab = f"{code(left)} $-$ {code(right)}"
        blines.append(
            f"{lab} & {'Full (228 m)' if smp == 'full' else 'Holdout (80 m)'} & {num(b.Sharpe_difference, 3)} & "
            f"[{num(b.Sharpe_difference_low, 3)}, {num(b.Sharpe_difference_high, 3)}] & "
            f"{pct(b.annual_excess_mean_difference, 2)} \\\\"
        )
    write("tab_boot.tex", "\n".join(blines) + "\n")

    # ---- sensitivity table (slide 10) -----------------------------------
    sB = sens[(sens.prototype == "B") & (sens.component == "B3")].set_index("variant")
    order = [
        ("primary", "Frozen rule, sensitivity dates"),
        ("remove_GLD", "Exclude GLD"),
        ("skip_latest_month_True", "Skip latest month (12--1)"),
        ("cost_bps_per_traded_dollar_25", "Costs 25 bps per traded \\$"),
        ("cost_bps_per_traded_dollar_50", "Costs 50 bps per traded \\$"),
        ("execution_delay_one_session", "Execute one session later"),
        ("top_k_2", "Top 2 slots"),
        ("top_k_4", "Top 4 slots"),
        ("lookback_months_6", "6-month lookback (diagnostic)"),
        ("lookback_months_9", "9-month lookback (not adopted)"),
    ]
    base = sB.loc["primary"]
    lines = []
    for k, lab in order:
        r = sB.loc[k]
        assert r.start == "2007-10-31" and r.end == "2026-08-31"
        dc = "--" if k == "primary" else ("+" if r.CAGR >= base.CAGR else "") + num(100 * (r.CAGR - base.CAGR), 2)
        line = f"{lab} & {pct(r.CAGR)} & {dc} & {num(r.Sharpe, 3)} & {pct(r.max_daily_drawdown)} \\\\"
        if k == "primary":
            line = "\\rowcolor{accentlight} " + line
        if k == "lookback_months_6":
            lines.append("\\midrule")
        lines.append(line)
    write("tab_sens.tex", "\n".join(lines) + "\n")

    # ---- capacity table (slide 11) --------------------------------------
    lines = []
    c10 = cap[(cap.variant == "B3") & (cap.initial_aum == 10_000_000)].set_index("ticker")
    c1 = cap[(cap.variant == "B3") & (cap.initial_aum == 1_000_000)].set_index("ticker")
    a10 = capa[(capa.variant == "B3") & (capa.initial_aum == 10_000_000)].set_index("ticker")
    for t in c10.sort_values("maximum", ascending=False).index[:5]:
        r = c10.loc[t]
        lines.append(
            f"{t} & {pct(c1.loc[t].maximum, 2)} & {pct(r.maximum, 2)} & {pct(r.p95, 2)} & "
            f"{int(a10.loc[t].trades)} & {pct(a10.loc[t].fraction_above_5pct, 1)} \\\\"
        )
    write("tab_cap.tex", "\n".join(lines) + "\n")

    # ---- A table (appendix) ---------------------------------------------
    lines = []
    for v in ["A0", "A1", "A2", "A3"]:
        r = row(A, v)
        lines.append(
            f"{v} & {NAMES[v]} & {pct(r.CAGR)} & {pct(r.annual_vol)} & {num(r.Sharpe, 3)} & {pct(r.max_daily_drawdown)} & "
            f"{num(r.average_exposure, 2)} & {num(r.turnover_annual, 2)} \\\\"
        )
    write("tab_A.tex", "\n".join(lines) + "\n")
    alines = []
    for smp in ["development", "validation", "historical_holdout"]:
        cells = [labels[smp].split(" ")[0] if smp != "historical_holdout" else "Holdout"]
        for v in ["A0", "A3"]:
            r = row(A, v, smp)
            cells += [pct(r.CAGR, 1), num(r.Sharpe, 2), pct(r.max_daily_drawdown, 1)]
        alines.append(" & ".join(cells) + " \\\\")
    write("tab_A_sub.tex", "\n".join(alines) + "\n")

    # ---- five-decimal table (appendix) ----------------------------------
    lines = []
    for df, vs, basis in [
        (netB, ["B0", "B1", "B2", "B3", "60_40", "SPY", "CASH"], "net 10 bps"),
        (A, ["A0", "A1", "A2", "A3"], "synthetic gross"),
    ]:
        if basis.startswith("synthetic"):
            lines.append("\\midrule")
        for v in vs:
            r = row(df, v)
            sh = "--" if pd.isna(r.Sharpe) else f"{r.Sharpe:.5f}"
            so = "--" if pd.isna(r.Sortino) else f"{r.Sortino:.5f}"
            vals = [f"{r.CAGR:.5f}", f"{r.annual_vol:.5f}", sh, so, f"{r.max_daily_drawdown:.5f}", f"{r.turnover_annual:.5f}"]
            vals = [x if x == "--" else x.replace("-", "$-$") for x in vals]
            lines.append(f"{code(v)} & {r.start} & {basis} & " + " & ".join(vals) + " \\\\")
    write("tab_precise.tex", "\n".join(lines) + "\n")

    # ---- figures -----------------------------------------------------------
    mddB = wealth_dd_figure(
        T,
        ["SPY", "B1", "B2", "60_40", "B3"],
        FIG / "fig_B_wealth_drawdown.pdf",
        (-66, 2),
        [0.5, 1, 2, 4, 8],
    )
    for v, x in mddB.items():
        assert abs(x - row(netB, v).max_daily_drawdown) < 1e-9, v
    mddA = wealth_dd_figure(
        T,
        ["A0", "A1", "A2", "A3"],
        FIG / "fig_A_wealth_drawdown.pdf",
        (-68, 2),
        [1, 2, 5, 10, 20, 50],
        ncol=2,
        legend_ax=1,
        wealth_ylim=(0.85, 400),
    )
    for v, x in mddA.items():
        assert abs(x - row(A, v).max_daily_drawdown) < 1e-9, v
    exposure_figure(T, FIG / "fig_B3_exposure.pdf")

    (GEN / "verification.json").write_text(
        json.dumps(
            {
                "source_tables": str(T),
                "headline_checks": checks,
                "B3_DBC_10m_max_participation": float(b3cap10.maximum),
                "B3_turnover_annual": float(row(netB, "B3").turnover_annual),
                "chart_drawdowns_match_performance_csv": True,
            },
            indent=2,
        )
    )
    print("assets built; headline checks pass")


if __name__ == "__main__":
    main()
