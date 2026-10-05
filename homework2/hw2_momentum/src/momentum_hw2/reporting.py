"""All content and figures derive from cached exported results; no network."""
import json,html,math,re
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,Image,PageBreak
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from .data_sources import ROOT

COLORS=['#172b4d','#537c8e','#b28743','#777777','#49694a','#8c5c65','#bbbbaa']
def table(name):return pd.read_csv(ROOT/'outputs/tables'/f'{name}.csv')
def daily(label):return pd.read_csv(ROOT/'outputs/tables'/f'{label}_daily.csv',index_col=0,parse_dates=True)
def pct(x):return f'{x*100:.2f}%'
def num(x):return f'{x:.5f}'
def clean_text(text):
    text=re.sub(r'(?<=[a-z])(?=\d)', ' ', text)
    text=re.sub(r',(?=\S)', ', ', text)
    text=re.sub(r'(?<=[a-zA-Z])(?=(?:19|20)\d{2}\b)', ' ', text)
    text=re.sub(r'(?<=\d)(?=(?:months|month|days|day|bps|points|times|years|year)\b)', ' ', text)
    for a,b in [('USD10m','USD 10 million'),('USD1m','USD 1 million'),('USD50m','USD 50 million'),('through2013','through 2013'),('from2020','from 2020'),('et al','et al'),('etal','et al.'),('top3','top 3'),('Top3','Top 3'),('section3','section 3'),('section4','section 4'),('section9','section 9'),('slide7','slide 7'),('notebook2','notebook 2'),('pp19','pp 19'),('pp59','pp 59'),('pp2','pp 2'),('pp221','pp 221'),('slides4','slides 4'),('slides22','slides 22'),('slides65','slides 65'),('Lecture3','Lecture 3'),('Lectures3','Lectures 3'),('Homework2','Homework 2')]:text=text.replace(a,b)
    return text

def figures():
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':15,'axes.spines.top':False,'axes.spines.right':False,'axes.grid':True,'grid.alpha':.15,'figure.dpi':150,'savefig.bbox':'tight'})
    for proto,labels,title in [('A',['A0','A1','A2','A3'],'A | Synthetic cash + Mom capital; gross'),('B',['B0','B1','B2','B3','60_40','SPY'],'B | ETF capital; modeled net 10bps / traded dollar')]:
        dates=daily(labels[0]).index
        fig,axs=plt.subplots(2,1,figsize=(11,6),sharex=True,gridspec_kw={'height_ratios':[2,1]})
        for j,label in enumerate(labels):
            d=daily(label);nav=d.nav
            axs[0].plot(d.index,nav,label=label,color=COLORS[j],lw=1.6)
            peak=np.maximum.accumulate(np.r_[1,nav.values])[1:]
            axs[1].plot(d.index,100*(nav/peak-1),color=COLORS[j],lw=1.2)
        axs[0].set_ylabel('NAV per initial $1 (log scale)');axs[0].set_yscale('log');axs[0].legend(ncol=3,loc='upper left',fontsize=13)
        axs[1].set_ylabel('Daily drawdown (%)');axs[0].set_title(f'{title}\nExecution inception {dates[0].date()} - {dates[-1].date()}')
        fig.tight_layout();fig.savefig(ROOT/'outputs/figures'/f'{proto}_nav_drawdown.png');plt.close(fig)
    d=pd.read_csv(ROOT/'outputs/audits/factor_decisions.csv',index_col=0,parse_dates=True)
    fig,axs=plt.subplots(2,1,figsize=(11,5),sharex=True)
    for j,l in enumerate(['A1','A2','A3']):axs[0].step(d.index,d[l],label=l,color=COLORS[j],where='post')
    axs[0].set_ylabel('Mom unit exposure');axs[0].legend(ncol=3);axs[0].set_title('A | Exposure set at execution close; next session earns new exposure')
    axs[1].plot(d.index,d.VIX,color=COLORS[0],lw=1);axs[1].axhline(25,color=COLORS[2],ls='--');axs[1].fill_between(d.index,0,80,where=d.bear.astype(bool),color=COLORS[3],alpha=.14,label='24-month bear state');axs[1].set_ylabel('VIX points');axs[1].legend();fig.tight_layout();fig.savefig(ROOT/'outputs/figures/A_exposure_regime.png');plt.close(fig)
    h=pd.read_csv(ROOT/'outputs/audits/B3_holdings_daily.csv',index_col=0,parse_dates=True).resample('ME').last()
    fig,ax=plt.subplots(figsize=(11,4.3));ax.stackplot(h.index,h[['SPY','EFA','EEM','IEF','TLT','GLD','DBC','VNQ','CASH']].T,labels=['SPY','EFA','EEM','IEF','TLT','GLD','DBC','VNQ','CASH'],colors=['#172b4d','#345676','#537c8e','#b28743','#d0b778','#49694a','#76937b','#8c5c65','#cccccc']);ax.set_ylim(0,1);ax.set_ylabel('Drifted month-end capital weight');ax.set_title('B3 | Holdings and cash; 2007-08-31 - 2026-08-31');ax.legend(ncol=9,fontsize=9,loc='upper center',bbox_to_anchor=(.5,-.10));fig.tight_layout();fig.savefig(ROOT/'outputs/figures/B_allocations.png');plt.close(fig)
    perf=table('performance').query("sample=='full' and basis=='modeled net 10bps per risky dollar'").set_index('variant').loc[['B0','B1','B2','B3','60_40','SPY']]
    fig,axs=plt.subplots(1,3,figsize=(11,4));
    for ax,col,title in zip(axs,['CAGR','max_daily_drawdown','average_exposure'],['CAGR (%)','Maximum daily drawdown (%)','Average risky exposure (%)']):
        ax.bar(perf.index,perf[col]*100,color=COLORS[:len(perf)]);ax.set_title(title);ax.tick_params(axis='x',rotation=25)
    fig.suptitle('ETF component attribution | identical dates, 10bps assumed costs');fig.tight_layout();fig.savefig(ROOT/'outputs/figures/B_components.png');plt.close(fig)
    s=table('sensitivities').query("prototype=='B' and component=='B3'")
    names={'primary':'Primary','lookback_months_6':'6 months','lookback_months_9':'9 months','top_k_2':'Top 2','top_k_4':'Top 4','skip_latest_month_True':'Skip month','cost_bps_per_traded_dollar_50':'50bps costs','remove_GLD':'Remove GLD','execution_delay_one_session':'Delay +1 session'}
    s=s[s.variant.isin(names)].copy();fig,ax=plt.subplots(figsize=(11,4.5));ax.barh(s.variant.map(names),s.Sharpe,color=COLORS[0]);ax.set_xlabel('Monthly cash-adjusted Sharpe');ax.set_title(f'B3 | Predetermined diagnostics; {s.start.iloc[0]} - {s.end.iloc[0]}\nAlternatives remain diagnostics; primary parameters unchanged');fig.tight_layout();fig.savefig(ROOT/'outputs/figures/B_robustness.png');plt.close(fig)

def pdf_report(sections,primary,partitions,sensitivity,bootstrap,capacity):
    styles=getSampleStyleSheet();styles.add(ParagraphStyle(name='BodySmall',fontName='Helvetica',fontSize=9.5,leading=14,spaceAfter=7))
    styles['Heading1'].fontSize=19;styles['Heading1'].leading=23;styles['Heading1'].keepWithNext=True
    story=[]
    def para(x):return Paragraph(html.escape(str(x)).replace('\n','<br/>'),styles['BodySmall'])
    def tbl(df):
        formatted=df.copy()
        for c in formatted.select_dtypes('number'):formatted[c]=formatted[c].map(lambda x:f'{x:.5f}' if pd.notna(x) else '-')
        formatted=formatted.rename(columns={'variant':'Strategy','sample':'Sample','annual_vol':'Ann. vol','max_daily_drawdown':'Daily DD','average_exposure':'Exposure','Sharpe_difference':'Sharpe diff.','Sharpe_difference_low':'95% low','Sharpe_difference_high':'95% high','fraction_above_1pct':'Above 1%','fraction_above_5pct':'Above 5%','maximum':'Max.','ticker':'Ticker'})
        values=[[para(x) for x in formatted.columns]]+[[para(x) for x in row] for row in formatted.astype(str).values]
        t=Table(values,colWidths=[(7.1*72)/len(formatted.columns)]*len(formatted.columns),repeatRows=1,hAlign='LEFT')
        t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#edf1f4')),('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,0),.7,colors.HexColor('#172b4d')),('BOTTOMPADDING',(0,0),(-1,-1),5)]))
        return t
    for title,text in sections:
        story.append(Paragraph(html.escape(title),styles['Heading1']));story.extend(para(x) for x in text.split('\n\n') if x)
        if title.startswith('5.'):
            story.append(tbl(primary[['variant','CAGR','annual_vol','Sharpe','max_daily_drawdown','average_exposure']]))
            for image in ['A_nav_drawdown.png','B_nav_drawdown.png','B_components.png']:
                im=Image(str(ROOT/'outputs/figures'/image));ratio=im.imageHeight/im.imageWidth;im.drawWidth=7.1*72;im.drawHeight=ratio*im.drawWidth;story.append(im)
        if title.startswith('6.'):
            story.append(tbl(partitions[['variant','sample','CAGR','Sharpe','max_daily_drawdown']]))
            small=bootstrap.query("prototype=='B' and sample=='full'")[['left','right','Sharpe_difference','Sharpe_difference_low','Sharpe_difference_high']]
            story.append(tbl(small))
            im=Image(str(ROOT/'outputs/figures/B_robustness.png'));ratio=im.imageHeight/im.imageWidth;im.drawWidth=7.1*72;im.drawHeight=ratio*im.drawWidth;story.append(im)
        if title.startswith('7.'):
            story.append(tbl(capacity.query("variant=='B3' and initial_aum==10000000")[['ticker','maximum','p95','fraction_above_1pct','fraction_above_5pct']]))
        story.append(Spacer(1,12))
    def footer(c,d):
        c.setFont('Helvetica',8);c.setFillColor(colors.HexColor('#537c8e'));c.drawString(43,26,'FINCB9339 HW2 | Hanyu Zhang | Historical research, October 4, 2026');c.drawRightString(569,26,str(d.page))
    SimpleDocTemplate(str(ROOT/'deliverables/HW2_Momentum_Research_Report.pdf'),pagesize=(612,792),rightMargin=43,leftMargin=43,topMargin=42,bottomMargin=43).build(story,onFirstPage=footer,onLaterPages=footer)

def report(config):
    figures();perf=table('performance');s=table('sensitivities');boot=table('bootstrap');cap=table('capacity_summary');stress=table('stress_periods');meta=json.loads((ROOT/'outputs/audits/run_metadata.json').read_text())
    primary=perf.query("sample=='full' and basis!='gross zero modeled trading costs'");b=primary.set_index('variant');b3=b.loc['B3'];b2=b.loc['B2'];b1=b.loc['B1'];bal=b.loc['60_40'];a3=b.loc['A3'];a0=b.loc['A0']
    partitions=perf.query("sample in ['development','validation','historical_holdout'] and variant in ['B0','B1','B2','B3','60_40']")
    hold=partitions.query("sample=='historical_holdout'").set_index('variant')
    bb=boot.query("left=='B3' and right=='60_40' and sample=='full'").iloc[0]
    risk=boot.query("left=='B3' and right=='B2' and sample=='full'").iloc[0]
    variants=len(table('variant_ledger'))
    worstcap=cap.query("variant=='B3' and initial_aum==10000000").sort_values('maximum',ascending=False).iloc[0]
    ss=s.query("prototype=='B' and component=='B3'")
    sections=[
    ('Executive summary',f'''Objective: raise assets for a transparent monthly cross-asset ETF portfolio. The default illustrative USD10m mandate is a research scenario, not a capacity commitment. Recommend B3 as a research-stage risk-limited portfolio, with a USD1m execution-validation scenario before considering USD10m. No live-capital readiness or superior-return promise is established.

On the identical ETF capital window {meta['etf_execution_start']} to {meta['endpoint']} (first invested return {meta['etf_first_return']}), B3 modeled net CAGR is {pct(b3.CAGR)}, monthly Sharpe {b3.Sharpe:.5f}, and maximum daily drawdown {pct(b3.max_daily_drawdown)}. B1 achieves {pct(b1.CAGR)} CAGR; monthly 60/40 achieves {pct(bal.CAGR)} and Sharpe {bal.Sharpe:.5f}. B3 has {pct(b3.cash_fraction)} average cash, versus {pct(b2.cash_fraction)} for B2. Downside improvement comes with lower risky exposure and lower returns.

The B3-minus-60/40 paired six-month bootstrap Sharpe difference is {bb.Sharpe_difference:.5f}, 95% interval [{bb.Sharpe_difference_low:.5f}, {bb.Sharpe_difference_high:.5f}]. This does not establish superiority. Historical holdout B3 CAGR is {pct(hold.loc['B3','CAGR'])}, Sharpe {hold.loc['B3','Sharpe']:.5f}; these dates are publicly known, and cross-strategy selection inspected them.

The distinct factor experiment runs {meta['factor_execution_start']} to {meta['endpoint']}, first return {meta['factor_first_return']}. A3 synthetic cash-plus-Mom gross CAGR is {pct(a3.CAGR)}, versus {pct(a0.CAGR)} static; maximum daily drawdowns are {pct(a3.max_daily_drawdown)} versus {pct(a0.max_daily_drawdown)}. These are aggregate factor exposure experiments with incomplete funding/borrow/cost assumptions, not executable stock portfolios.

French RF/Mom stop in August2026; September ETF/VIX data are cached but unused. Capacity is provisional: the evolving USD10m B3 scenario reaches {pct(worstcap.maximum)} of ADV20 for {worstcap.ticker}. A single close cannot be justified from all-day vendor volume alone.'''),
    ('1. Landscape and published research', '''The instructor uses time-series/absolute momentum for an asset's own past performance and cross-sectional/relative momentum for rankings across assets. Dual momentum combines the two. Buy-and-hold retains market exposure; a stock momentum ETF ranks securities within equities; diversified futures trend following can short falling markets and normalize instrument risk. Our B ranks eight US-listed ETFs, is long-only, and routes failed slots to cash. It cannot profit directly from shorting a persistent decline.

The lecture's dual momentum modules use 12 months including the latest month and a cash hurdle. B adopts these concepts but uses three fixed slots across a different eight-ETF universe. It is not a replication of the four-module permanent portfolio. Equal slots are capital weighting, not equal marginal volatility (EMV).

Daniel and Moskowitz, Momentum crashes (2016), describe panic states after market declines and high ex-ante volatility, with past losers rebounding strongly. Their conditional-mean/variance strategy differs from our fixed bear/VIX heuristic and inverse-volatility overlay. Their published improvements are not our results. Their decile WML construction also differs from French's six size/momentum portfolios. Lecture slides 65-88 explain these mechanisms. Some extracted equations have scrambled two-column text; no ambiguous extracted formula was coded.

Asness et al., Fact, Fiction and Momentum Investing (2014), discuss broad evidence, implementation, costs and diversification with value. Their long-run stock results, institutional trading-cost evidence and tax findings do not validate this ETF design. Their argument for simple definitions motivates frozen parameters and retaining adverse periods.

Kolanovic and Wei (2015), pp19-20 and59-60, distinguish absolute versus relative signals, use a one-business-day information gap, and show that portfolio volatility targeting is not invariably beneficial. Their VIX threshold25 example motivates one part of A but is not the same combined rule. Baltas and Kosowski (supplied January2013 version), section3, use signed futures trends and inverse-volatility normalization; they study frequencies and futures/CTA capacity. Those results cannot be transferred to our eight ETFs. Contribution: a transparent controlled implementation and audit trail, not a new anomaly.'''),
    ('2. Data, coverage and biases', '''Inputs are real downloaded snapshots. Kenneth French official daily/monthly US Mom and Fama-French market/RF/SMB/HML archives; Cboe official VIX closing levels; Yahoo Finance through yfinance1.7.0. Request options explicitly preserve Close, Adj Close, Volume and actions: auto_adjust=False, back_adjust=False, actions=True, repair=False, keepna=True, rounding=False, prepost=False; end2026-10-01 is exclusive, and records are filtered through September30. Filenames, timestamps, SHA256, adapter signature/options, units, coverage and original headers are in data/manifests.

French daily Mom coverage1926-11-03 to2026-08-31, monthly Mom1927-01 to2026-08. VIX starts1990-01-02 and reaches cutoff. ETF observations begin SPY1993-01-29, EFA2001-08-27, EEM2003-04-14, IEF/TLT2002-07-30, GLD2004-11-18, DBC2006-02-06, VNQ2004-09-29, and all reach2026-09-30. Issuer inception dates can precede first vendor observations; no missing early days are manufactured. DBC binds common price history. All actual analysis sessions match the French market calendar with no missing prices.

Percent factor entries are divided by100 once; missing markers become NaN; only date-shaped daily/monthly blocks are parsed, excluding annual summaries. VIX is joined backward, source dates/staleness exported, with gaps over7 calendar days rejected. Two >20% EEM daily gains in October2008 are flagged and retained as crisis observations; they were not clipped or removed. Independent validation of these extremes remains a data-risk limitation.

Adj Close is the vendor total-return proxy; dividends are not added again. Internal dividend-date comparisons are exported, not called independent-source verification. Close/Volume conventions and distribution revisions remain provider risks. Observed split events, if any, are preserved; no synthetic split validation is claimed. Volume capacity uses reported Close times daily share Volume, not Adj Close. The eight-ticker retrospective universe choice creates selection/survivorship risk even with proper inception timing. ETF expenses are embedded in returns, not deducted again; tax, fee and execution assumptions are separate.

French transitioned from legacy FIZ to CIZ with the January2025 release; this current snapshot can revise old observations. Daily Mom's underlying portfolios are formed daily; official monthly Mom is formed monthly. We do not splice them, and daily-derived capital returns need not match official monthly spread returns. No WRDS/CRSP query or stock reconstruction was attempted. Databento was unused and no data fees incurred. Cached public inputs are for authorized personal academic use; public redistribution rights are not presumed.'''),
    ('3. Equations and timing', '''Let m_d denote daily French Mom and f_d daily RF. French Mom =0.5(Small High + Big High)-0.5(Small Low + Big Low), using six value-weight portfolios from size and prior-return sorts. Unit factor exposure has conventional long-one/short-one gross notional about2 per modeled dollar of capital. Our daily synthetic capital return r_d=f_d+a_previous*m_d-cost_d. The factor spread is already an excess component; do not subtract RF a second time. RF on collateral, financing, margin and stock borrowing are stylized; factor-return data cannot establish stock capacity or sector neutrality.

At penultimate trading close s_t, sigma_t=sqrt(252)*sample_sd(last126 Mom daily returns), ddof=1. Volatility exposure a_vol=min(1.5,0.10/max(sigma_t,0.05)). Market TR compounds Mkt-RF+RF. Bear=1[market_TR(s_t)/market_TR(s_(t-24))-1<0]. HighVol=1[VIX(s_t)>25 index points]. State scale g equals1 with neither flag,0.5 with one,0 with both. A0=1; A1=a_vol; A2=g; A3=a_vol*g. Exposure is held until next monthly execution. A is gross; illustrative change charges2*abs(delta a)*cost and annual exposure drags omit internal stock turnover and borrow.

For ETF i, M_i=AdjClose_i(s_t)/AdjClose_i(s_(t-12))-1. Cash hurdle C=product(1+RF_d)-1 over exactly (s_(t-12),s_t]. Rank all eight by descending M, alphabetical ties; top3 each receive1/3 slots. B1 invests each slot. B2 invests only if M_i>C; failed slots remain cash, without refill or survivor renormalization. B0 resets equal1/8 monthly. SPY benchmark holds after initial trade;60/40 resets SPY60%, IEF40% monthly; cash earns observed RF.

B3 first requires126 days of the historical unscaled gross B2 strategy's daily excess path after B2 starts trading. q=min(1,0.10/max(sqrt(252)*sd(B2 excess126),0.05)). Multiply B2 risky targets by q; allocate the balance to cash. It is a volatility cap, never leverage to hit10%. Forecast uses past strategy returns, so can lag changes in holdings or covariance. The primary common start includes this extra warmup; all benchmarks begin from cash on that same date.

Decision after penultimate close; execute final close with old holdings earning the execution-day return; new holdings earn from the following session. Signal/decision/execution/first-return fields are exported. Signals compare monthly snapshots, not252 days. VIX publishing time and foreign underlying markets may differ from equity close; the one-session gap is conservative but not a fill guarantee. An additional-session delay diagnostic preserves the original snapshot.

Weights drift daily: gross return=sum(w_previous*r_asset)+w_cash*RF; pretrade weight_i=w_previous_i*(1+r_i)/(1+gross). Risky turnover T=sum_i|target_i-pretrade_i| excludes cash but counts both buys and sells. Cost fraction=c*T, c=0.001 (10bps). NAV_after=NAV_before*(1+gross)*(1-c*T); allocate post-cost NAV at target weights. This proportional haircut is the specified approximation; realized trade dollars differ slightly from the pre-cost notional used to size costs. Initial investments incur charges. No daily rebalance or hidden leverage. If return<=-100% or NAV<=0, halt and declare ruin; no clipping or restart.

Initial close has no prior invested return. Its initial charge is stored on execution day in daily accounting and combined into the first full holding month's return for monthly statistics, preserving cumulative wealth. ACT/365.25 CAGR uses inclusive elapsed calendar days from initial execution. Partitions use actual inherited returns without resetting signal history. All primary comparisons within each prototype use identical dates; cross-prototype headline CAGR comparisons are inappropriate because investability/capital conventions differ.'''),
    ('4. Worked examples and intermediate steps', '''Arithmetic example (illustrative, not empirical performance): at a snapshot selected ETF signals are12%,8%,1%; matched cash is2%. Relative selection gives1/3 to each. Absolute filtering keeps the first two and sends the third1/3 to cash. If forecast B2 volatility is16%, q=10%/16%=0.625; B3 targets are0.20833333,0.20833333,0 cash-failed risky slot, and0.58333333 cash. No lower-ranked asset replaces the failure.

Drift example: start with50% A,50% B; A returns10%, B0%. Gross NAV rises1.05; weights become0.55/1.05=0.52380952 and0.50/1.05=0.47619048. Target100% B gives T=|0-0.52380952|+|1-0.47619048|=1.04761905. At10bps, cost fraction0.00104762. Post-cost NAV=1.05*(1-0.00104761905)=1.04890000, then allocate B100%. A full100% A-to-B switch has T=2 and20bps cost, not10bps.

Reproduction of a real decision: open outputs/audits/etf_signals.csv, filter the desired execution_date, and verify lookback_start/end against processed/etf_adjclose.csv; compare the matched cash index from etf_cash.csv. Then verify B3 q in etf_risk_sizing.csv and targets/trades/holdings. The notebooks print an actual eligible row and reproduce its endpoints. Unit tests implement the worked arithmetic; actual-path audits independently reconcile trades, return weights and NAV.

Monthly return=product daily NAV growth factors-1. Monthly excess=capital monthly return-compounded daily cash. Sharpe=sqrt(12)*mean(excess)/sample_sd(excess). Sortino=sqrt(12)*mean(excess)/sqrt(mean(min(excess,0)^2)), including all months in the downside denominator. Annual arithmetic mean=12*mean(monthly capital returns); annual volatility=sqrt(12)*sample_sd(monthly capital returns). Sample adjusted skewness and Fisher excess kurtosis use pandas estimators. VaR95 is minus5th-percentile monthly capital return; ES averages returns at/below that cutoff, with tail_n. Daily maximum drawdown uses prior peak including initial NAV1; recovery reports peak-to-recovery calendar days or elapsed unrecovered duration. Daily and monthly-end drawdowns are separate columns.'''),
    ('5. Primary measured results and attribution',f'''Exact decimal return statistics appear below (five decimals); all full-precision outputs are CSV. Factor rows are synthetic gross; ETF rows use10bps assumed traded-dollar costs. Dates: A {meta['factor_execution_start']} to {meta['endpoint']}; B {meta['etf_execution_start']} to {meta['endpoint']}. Initial execution charge enters the first holding month, not an artificial partial month.

A3 lowers drawdown from{pct(a0.max_daily_drawdown)} to{pct(a3.max_daily_drawdown)} and realized annual monthly capital volatility from{pct(a0.annual_vol)} to{pct(a3.annual_vol)}. Average factor exposure falls to{a3.average_exposure:.5f}, with dynamic timing as well as volatility management; these controls cannot guarantee future crash avoidance. March-May2009 gross static synthetic capital loses45.64%, while the regime/combined experiments sit at zero factor exposure and earn the period's zero recorded RF. That is avoidance through de-risking, not a stock hedge replication. Exposure diagnostics retain both-stress and cap frequencies.

ETF relative selection B1 increases full-sample CAGR from equal weight{pct(b.loc['B0','CAGR'])} to{pct(b1.CAGR)} but portfolio concentration and whipsaw remain. B2 absolute filtering reduces CAGR to{pct(b2.CAGR)} and barely changes worst full-history drawdown ({pct(b1.max_daily_drawdown)} versus{pct(b2.max_daily_drawdown)}). The downside hypothesis is not uniformly supported. B3 reduces the drawdown to{pct(b3.max_daily_drawdown)} and volatility to{pct(b3.annual_vol)}, with average cash{pct(b3.cash_fraction)}; CAGR declines to{pct(b3.CAGR)}. This is a paid risk reduction.60/40 has higher full-sample Sharpe ({bal.Sharpe:.5f} versus{b3.Sharpe:.5f}), and SPY has higher CAGR{pct(b.loc['SPY','CAGR'])} with deeper drawdowns. We do not select solely by Sharpe.

2020 B3 returns7.77%, B2/B1 10.22%,60/40 15.99%, SPY18.33%: the lower-risk design misses upside.2022 B3 loses5.03%, B2 9.45%,60/40 16.67%, SPY18.18%: the cap helps but does not eliminate simultaneous stock/bond weakness. Crisis-specific returns are descriptive and retained inside all primary metrics. Regressions use monthly excess, CAPM and contextual market/SMB/HML attribution with HAC3 standard errors; A additionally includes daily-derived static factor capital excess. Intercepts are not causal alpha or proof of a new premium; omitted bond/gold exposures can matter for B.'''),
    ('6. Robustness and uncertainty',f'''Primary rules were frozen before downloaded performance was viewed. Development through2013, validation2014-2019, historical holdout2020-{meta['endpoint']}; histories carry across boundaries. Holdout is public historical evidence, not unseen future performance. Recommendation across variants uses those inspected outcomes; selection uncertainty persists. The variant ledger has{variants} evaluated rows, including gross attribution, adverse sensitivities and incomplete factor costs. No winning alternative replaced the frozen parameters.

B3 holdout CAGR{pct(hold.loc['B3','CAGR'])}, Sharpe{hold.loc['B3','Sharpe']:.5f}; B1 holdout CAGR{pct(hold.loc['B1','CAGR'])}, Sharpe{hold.loc['B1','Sharpe']:.5f}. B3 improves full-sample Sharpe versus B2 by{risk.Sharpe_difference:.5f}, but its95% block-bootstrap interval [{risk.Sharpe_difference_low:.5f},{risk.Sharpe_difference_high:.5f}] includes zero. Its comparison with60/40 likewise includes zero. Uncertainty does not support a guaranteed advantage.

Paired moving-block bootstrap uses6-month noncircular overlapping blocks,1000 replications, seed9339, identical indices for compared strategies; report annualized mean-excess differences and Sharpe differences. This resamples precomputed historical paths, not new signals/markets, does not remove universe/parameter selection bias, and has limited crisis-tail observations. HAC3 regressions are contextual, and multiple variants do not create independent discoveries.

A one-at-a-time windows63/252, targets8%/12%, VIX20/30, bear12/36 months and cap1 use a common eligible window; zero-cost and separate10/25bps exposure charges and1%/2% annual drags are labeled incomplete. Long-history A0/A1 begin after126 observations without VIX and stay separate. B2/B3 test6/9-month signals, top2/top4, skip month,0/5/25/50bps, each single exclusion, and one additional execution-session delay. B3 skip-month needs more warmup; before interpreting sensitivity performance the comparison is shifted to a shared2007-10-31 execution start, preserving all data. Primary remains2007-08-31.

For B3 the nine-month diagnostic is stronger than primary; it is not adopted. Skipping a month deepens drawdown to24.73%, while removing GLD lowers CAGR to5.28% on sensitivity dates. These show dependence on signal timing and gold diversification. At50bps costs sensitivity CAGR falls to5.20%. The universe is correlated: four equity/real-estate tickers and two Treasury-duration tickers do not provide eight independent economic bets. Daily equity/duration exposure and concentration are exported. Worst strategy months are selected mechanically and retained.'''),
    ('7. Feasibility, costs and capital',f'''B3 risky-asset turnover averages{b3.turnover_annual:.5f} times capital annually (both sides counted);10bps per traded dollar implies about{pct(b3.turnover_annual*.001)} annual simple modeled cost allowance. Full-history sum of cost fractions is{b3.cost_fraction_sum:.5f}, not a CAGR difference; gross reruns isolate compounded drag. Spread/slippage/commission allowance is assumed, not measured. ETF expenses embedded in prices are not deducted again; investor management fees, tax, whole-share rounding and operational cash-vehicle differences are excluded.

At each rebalance ADV20 is mean(Close*Volume) over20 sessions through the previous signal close. Participation=initial_AUM*pretrade_NAV*abs(delta weight)/ADV20. Scenarios begin1m/10m/50m and grow with B2/B3 net NAV, with no flows. Report p95/max per ticker over rebalance opportunities (including zero-trade dates), and additionally nonzero-trade summaries. The table below is the evolving10m B3 scenario; fractions are decimals. It is an all-day vendor-volume screen, not certified consolidated or auction liquidity.

{worstcap.ticker} reaches{pct(worstcap.maximum)} participation in the10m scenario; therefore a universal single-close10m mandate is not justified by this evidence. The1m scenario scales participation one tenth, but remains provisional. Report1% and5% ADV illustrative maximum trade-size constraints by event; they are governance screens, not guaranteed safe capacity.50m magnifies these concerns. Current liquidity alone cannot justify historical capacity.

A practical mandate would require independent consolidated-volume and distribution checks, historical spreads/auction volume, stressed fill analysis, and an order deadline policy. Consider slicing orders across sessions only as a prospective rule to validate, because it changes current close-execution assumptions. ETF creation/redemption and underlying foreign-equity, Treasury or commodity liquidity affect spreads. GLD is a bullion trust; DBC is a futures commodity pool with roll/collateral/tax considerations; neither is a generic equity fund. Existing holdings are preserved if a feed/rebalance fails until data are verified and the issue escalated; no synthetic returns or silent substitution.

A's factor data cannot substantiate stock-level turnover, borrow availability, margin/funding access, or capacity. The conventional gross notional2a can reach3 per unit capital under cap1.5. Illustrative exposure charges omit trading inside Mom and are not complete net evidence. A is suitable for course mechanism research, not an executable AUM pitch.'''),
    ('8. Recommendation and limitations', '''Recommend a research-stage B3 pitch for investors who value explicit risk limits and accept lower participation in gains. The executable ETF holdings, monthly audit trail and no-leverage cap fit the assets objective better than a synthetic factor. B1 should remain a serious comparator because it produces higher historical return; B2's simpler filter offers little improvement in the worst drawdown here. B3's downside reduction is useful but largely consistent with lower exposure, and full-sample60/40 Sharpe is higher. No reliable superiority claim survives uncertainty and all practical assumptions.

The initial10m proposal remains illustrative, contingent on execution validation. The next milestone is independent data and auction/impact checks on a1m scenario, then prospective paper decisions recorded before realized returns, without tuning the primary rule from the inspected holdout. Do not allocate live capital based on this homework. This is the specification's honest research-stage outcome when evidence is mixed.

Principal risks: trend reversals and fast rebounds, range-bound whipsaw, persistent regime change, simultaneous stock/bond weakness, correlated equity/duration concentration, gold dependence, cash opportunity cost and vehicle/credit/reinvestment risk, provider revisions/outages, tax and fee exclusions, and historical universe choice. A cap estimates historical risk and is not a maximum loss guarantee. A fully independent data source, richer execution estimates, longer genuine prospective evidence or sustained net advantage could change the conclusion. Material unexplained data differences, failed NAV/timing checks, repeat operational failures or liquidity breaches would suspend new rebalances and trigger review. Do not retrofit a shutdown rule into the historical backtest.'''),
    ('9. Investor questions and answers', '''Why might momentum persist? Delayed information incorporation, behavioral feedback and risk compensation are plausible published explanations; none guarantees our portfolio's premium.

What is new? Transparent controlled comparisons and an auditable implementation; relative/absolute momentum and volatility caps are established. No discovery of sector-neutral stock selection or new alpha.

How does it differ from buy-and-hold, stock momentum ETFs and CTAs? We rotate long-only cross-asset ETF slots, compare each selected slot to cash and optionally cap risk. Stock momentum ETFs select within equities; futures CTAs can short declines and engineer rolls/collateral. We do neither.

Is reduced drawdown just less risk? Much of B3's protection is accompanied by22.82% average cash and lower volatility/return. A1's full-history mean unit exposure is close to1, but its timing changes which periods carry risk. No free alpha claim.

When does it fail? Fast reversals, noisy range-bound markets and concentrated long exposures can lose or miss rebounds. In2020 B3 lagged SPY/60-40 despite less downside; in2022 it still lost money.

How were tickers/parameters selected and how many variants tried? They were specified before this execution, fixed before downloads/performance, with the complete ledger exported. Today's eight ETFs create retrospective selection bias; no alternative winner was promoted.

Is holdout future evidence? No:2020 onward is publicly known historical validation and was inspected for comparisons. Prospective time-stamped paper trading is the next test.

What is excluded? Measured spreads/impact, funding/borrow for A, investor fees/taxes, precise auction fills, cash implementation and vendor revisions. ETF expenses remain embedded.

How much capital?1m/10m/50m are modeled scenarios. Historical all-day vendor ADV flags show10m is not universally compatible with small participation; no certified safe capacity. Need auction and underlying-market evidence.

What invalidates the thesis? A persistent failure of net return/risk tradeoffs in prospective frozen-rule evidence, unexplained data/accounting defects, repeated execution problems or capacity breaches warrants formal review and suspension of new decisions.

What follows a missing feed or failed rebalance? Preserve existing holdings pending verified data, escalate and log the missed decision; never invent data or silently change the rule.'''),
    ('10. Reproduction and references', '''README.md contains commands: install pinned requirements, validate cached inputs, pytest, run --offline, report --offline, execute notebooks, and compare clean-run hashes. Python source modules implement one shared backtest; notebooks explain and call them. Data/return/holdings tables retain full precision; report decimal metrics show five digits. Tests and cached reproduction evidence are in outputs/audits, with an acceptance checklist in research.

Uploaded sources: Achilles Venetoulias, B9339 Lectures3-5 Momentum, Fall2026, slides4-7,17-23,42-49,65-88; Homework2 handout. Daniel & Moskowitz (2016), Momentum crashes, Journal of Financial Economics122,221-247. Asness, Frazzini, Israel & Moskowitz (2014), Fact, Fiction and Momentum Investing, Journal of Portfolio Management. Kolanovic & Wei (2015), Momentum Strategies Across Asset Classes: Risk Factor Approach to Trend Following, pp19-20,59-60. Baltas & Kosowski (supplied January5,2013 version), Momentum Strategies in Futures Markets and Trend-Following Funds, section3. Exact local excerpt locations and issuer URLs: research/source_map.md.

Provider methodology: https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/Data_Library/det_mom_factor_daily.html ; https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/Data_Library/det_mom_factor.html ; https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/Data_Library/changes_crsp.html ; https://www.cboe.com/tradable_products/vix/vix_historical_data ; https://ranaroussi.github.io/yfinance/reference/api/yfinance.download.html . Accessed October4,2026. Input URLs and acquisition vintages are in manifests/inputs.json. Yahoo data are personal academic caches, not a public redistribution authorization.''')]
    sections=[(clean_text(title),clean_text(text)) for title,text in sections]
    sections=[(title,text.replace('Observed split events, if any, are preserved; no synthetic split validation is claimed.', 'EFA2005 and EEM2005/2008 split events are preserved and included in internal return checks. Yahoo Close is already split-normalized, not an original pre-split transaction price. Close times vendor Volume is a dollar-volume proxy; historical volume normalization remains uncertified, strengthening the provisional capacity limitation. Targeted issuer/venue action checks are in research/corporate_actions.md; full independent price and month-end return validation remains unavailable.')) for title,text in sections]
    md='# HW2 Momentum Research Report\n\nHanyu Zhang | FINCB9339 | October 4, 2026\n\n'
    for title,text in sections:
        md+='## '+title+'\n\n'+text+'\n\n'
        if title.startswith('5.'):md+=primary[['variant','basis','CAGR','annual_vol','Sharpe','max_daily_drawdown','average_exposure']].to_markdown(index=False,floatfmt='.5f')+'\n\n'
        if title.startswith('6.'):
            md+=partitions[['variant','sample','CAGR','Sharpe','max_daily_drawdown']].to_markdown(index=False,floatfmt='.5f')+'\n\n'+boot.to_markdown(index=False,floatfmt='.5f')+'\n\n'
        if title.startswith('7.'):md+=cap.query("variant=='B3' and initial_aum==10000000").to_markdown(index=False,floatfmt='.5f')+'\n\n'
    (ROOT/'deliverables/HW2_Momentum_Research_Report.md').write_text(md)
    pdf_report(sections,primary,partitions,s,boot,cap)
    (ROOT/'research/recommendation.md').write_text(sections[0][1]+'\n\n'+sections[8][1])
    slides=make_slides(b,hold,bb,risk,cap,variants,meta)
    slides=[{k:clean_text(v) if k!='figure' and isinstance(v,str) else v for k,v in x.items()} for x in slides]
    (ROOT/'deliverables/slides.json').write_text(json.dumps(slides,indent=2))
    manuscript='# Investor presentation: 12 substantive slides + appendix\n\n'
    for j,x in enumerate(slides,1):
        manuscript+=f'## {j}. {x["title"]}\n\n'+x['body']+'\n\n'
        if x.get('figure'):manuscript+=f'Figure: ../outputs/figures/{x["figure"]}\n\n'
        manuscript+='Speaker notes: '+x['notes']+'\n\n'
    (ROOT/'deliverables/HW2_Investor_Presentation_Manuscript.md').write_text(manuscript)
    slides_pdf(slides)
    print('Report, figures, slide manuscript and PDF generated from results.')

def make_slides(b,hold,bb,risk,cap,variants,meta):
    def sl(title,body,notes,figure=None):return dict(title=title,body=body,notes=notes,figure=figure)
    sample='ETF capital: 2007-08-31 execution inception to2026-08-31; modeled net10bps/traded dollar.'
    return [
    sl('Cross-asset dual momentum',f'Raising assets for a transparent monthly ETF portfolio\nResearch-stage B3: risk cap, explicit cash, no leverage\nCAGR {pct(b.loc["B3","CAGR"])} | daily max drawdown {pct(b.loc["B3","max_daily_drawdown"])}\nIllustrative USD10m mandate; execution validation starts with a USD1m scenario',sample+' Objective is raising assets, not working capital. Performance is historical and mixed; no live readiness. Hanyu Zhang, FINCB9339 Homework2.'),
    sl('Momentum strategy landscape','Buy-and-hold: continuous market exposure\nRelative momentum: rank assets against peers\nAbsolute momentum: compare an asset with its cash hurdle\nOur dual design: three selected ETF slots, failed slots to cash\nFutures CTAs can short declining markets; this portfolio cannot','Lecture slides4-7,22-23,42-44; Asness etal2014 pp2-4. Stock momentum ETFs rank stocks within equities. Eight tickers do not equal eight independent exposures.'),
    sl('Economic mechanism and contribution','Published hypotheses: delayed information, feedback and risk premia\nEquity factor crashes: past losers rebound after panic states\nETF long/cash risks differ from short-loser equity momentum\nContribution: controlled comparisons with reproducible timing and accounting','Daniel & Moskowitz2016 introduction pp221-223; Asness etal2014 Myth10; Kolanovic & Wei2015 pp19-20. Published findings are motivation, not our measured returns. No new anomaly, sector neutrality or conditional-mean replication claimed.'),
    sl('Exact monthly holdings rule','Universe: SPY EFA EEM IEF TLT GLD DBC VNQ\nRank12-month total returns; choose top3\nEach1/3 slot invests only if its return exceeds matched cash\nExample signals12%,8%,1%; cash2% -> two1/3 ETFs +1/3 cash\nVol16% -> q0.625 ->20.83%,20.83%,58.33% cash','Signals use comparable penultimate monthly snapshots, not252 days. Alphabetical tie break. No refill or renormalization. Worked numbers here are illustrative arithmetic, not historical signals. Actual decisions and endpoints are in etf_signals.csv; see notebook2.'),
    sl('Risk cap and opportunity cost',f'B3 estimates126-day gross B2 excess volatility\nq=min(1,10%/max(volatility,5%)); remainder cash\nAverage cash {pct(b.loc["B3","cash_fraction"])} versus B2 {pct(b.loc["B2","cash_fraction"])}\nProtection reduces upside and does not guarantee maximum loss','Forecast is trailing strategy volatility, not a current-holdings covariance forecast. Monthly decisions persist; weights drift. B3 never leverages to reach10%. Baltas & Kosowski2013 section3 motivates volatility normalization, but futures positions and estimator differ.','B_allocations.png'),
    sl('Data, timing and historical validation','Real French, Cboe and Yahoo/yfinance snapshots\nSeptember cutoff; French RF/Mom available only through August\nSignal penultimate close -> execute final close -> next-session return\nAll8 ETF history begins2006; B3 warmup -> September2007 returns\nDevelopment to2013 | validation2014-19 | historical holdout2020-26','ETF first common execution2007-08-31; first invested return2007-09-04. Factor first execution1990-01-31; first return1990-02-01. RF cash endpoints bind August31. Adj Close includes distributions; no double counting. Current vintages may revise history. Holdout is publicly known and inspected.'),
    sl('Modeled net results versus benchmarks', '\n'.join(f'{x}: CAGR {pct(b.loc[x,"CAGR"])} | Sharpe {b.loc[x,"Sharpe"]:.3f} | max DD {pct(b.loc[x,"max_daily_drawdown"])}' for x in ['B0','B1','B2','B3','60_40','SPY']),sample+' Sharpe is monthly cash-adjusted, ddof1. Drawdown is daily;60/40 rebalances monthly. Initial order costs included. Benchmark60/40 has higher full-history Sharpe than B3. See performance.csv for five-decimal output.'),
    sl('Lower drawdown comes with lower return','Relative selection improves historical return over equal weighting\nAbsolute filter scarcely improves worst drawdown here\nVolatility cap provides the strongest ETF drawdown reduction\nB3 trails SPY and60/40 in full-history CAGR',sample+' Comparing component risks and mean exposures prevents presenting lower cash-adjusted risk as costless alpha. B1 CAGR8.66%, B2 7.95%, B3 6.89%; values trace to performance.csv.','B_nav_drawdown.png'),
    sl('Robustness and uncertainty',f'Historical holdout B3: CAGR {pct(hold.loc["B3","CAGR"])} | Sharpe {hold.loc["B3","Sharpe"]:.3f}\nB3-minus60/40 Sharpe95% CI: [{bb.Sharpe_difference_low:.3f}, {bb.Sharpe_difference_high:.3f}]\nSkip-month diagnostic worsens drawdown; gold exclusion hurts\nAll {variants} ledger rows retained; stronger9-month result is not adopted','1000 paired moving-block draws,6-month blocks, seed9339. No future out-of-sample claim; cross-strategy selection inspected holdout. Sensitivity common start2007-10-31 accommodates skip-month warmup. CI includes zero; resampling historical returns does not remove selection bias.','B_robustness.png'),
    sl('Costs, liquidity and mandate size',f'B3 turnover {b.loc["B3","turnover_annual"]:.2f}x NAV/year; assumed10bps per dollar\n1m/10m/50m AUM scenarios evolve with net NAV\n10m B3 maximum DBC participation {pct(cap.query("variant==\"B3\" and ticker==\"DBC\" and initial_aum==10000000").iloc[0].maximum)} of lagged ADV20\nAll-day vendor ADV does not certify closing-auction capacity\nValidate1m scenario first;10m single-close fills are not established','Participation from raw Close*Volume through snapshot, abs delta weights, pretrade evolving NAV. Cost is an assumption, not measured spread.1%/5% ADV are illustrative constraints. Auction/impact/underlying liquidity and independent data checks needed. Taxes and investor fees excluded.'),
    sl('Evidence-supported advantages and risks','Advantages: explicit holdings, fixed rules, no leverage, cash audit\nB3 reduced losses in2022; it missed upside in2020\nRisks: whipsaw, reversals, gold dependence and duration overlap\nHigher full-sample Sharpe than60/40 is not demonstrated','2020 B3 return7.77% vs60/40 15.99%;2022 B3 -5.03% vs60/40 -16.67%. Daily exposure/cost files substantiate implementation transparency. This is a design advantage, not a claim of statistical alpha. Provider revisions and retrospective universe selection remain.'),
    sl('Proposed research mandate and investor Q&A','Proposal: B3 research-stage risk-limited ETF design\nWhy more cash? It buys lower exposure and sacrifices return\nWhy not B1? Keep it as the higher-return comparator\nNext milestone: independent data, auction costs, prospective paper signals\nFeed failure: preserve holdings, verify data, escalate and log','Raising assets remains the objective, with illustrative10m contingent on evidence. No trades or assignment submission authorized. Suspend new decisions after material data/accounting defects, repeated operational failures or participation breaches; do not retrofit these rules into historical returns. Full investor Q&A is in report section9.'),
    sl('Appendix | Factor experiment',f'A0 gross synthetic CAGR {pct(b.loc["A0","CAGR"])} | drawdown {pct(b.loc["A0","max_daily_drawdown"])}\nA3 gross synthetic CAGR {pct(b.loc["A3","CAGR"])} | drawdown {pct(b.loc["A3","max_daily_drawdown"])}\nBear24months + VIX>25 -> exposure0 when both flags\nRF + a*Mom: funding/borrow/internal turnover not measured','A dates1990-01-31 to2026-08-31. French Mom six size/momentum portfolios, daily formed daily; monthly official series separate. Unit factor gross notional2, cap1.5 permits gross3. A is not an executable stock strategy. Daniel-Moskowitz conditional mean/variance sizing is not replicated.','A_nav_drawdown.png'),
    sl('Appendix | Factor exposures and panic states','A0=1 | A1=vol scale | A2=state scale | A3=combined\na_vol=min(1.5,10%/max(sigma126,5%))\nMarket total return compounds Mkt-RF + RF\nPublished loser-rebound mechanism motivates the fixed heuristic','Signals use past24 comparable monthly snapshots and backward VIX. Exposure decisions held after execution; neither VIX nor market rebound from future periods enters signal. March-May2009 static capital loses45.64%; zero factor exposure avoids it in A2/A3. Internal Mom turnover, financing and borrow omitted.','A_exposure_regime.png'),
    sl('Appendix | Accounting and statistical conventions','Daily weights drift; rebalance only at execution close\nT=sum risky |target-pretrade|; full A-to-B switch T=2\nNAV_after=NAV_before*(1+gross)*(1-0.001*T)\nSharpe=sqrt(12)*mean(monthly excess)/sample_sd\nCAGR ACT/365.25 | HAC3 | downside RMS Sortino','Worked50/50 drift example in report section4 and tests. Targets are post-cost allocations using proportional NAV haircut. Initial execution charge combined into first holding month. Cash is compounded daily RF; empirical monthly VaR/ES loss-positive with tail count. Undefined Sharpe for deterministic excess cash.'),
    sl('Appendix | Exact component evidence','Decimals to five places; ETF modeled net, factor synthetic gross\n'+'\n'.join(f'{x}: CAGR {b.loc[x,"CAGR"]:.5f}; Sharpe {b.loc[x,"Sharpe"]:.5f}; DD {b.loc[x,"max_daily_drawdown"]:.5f}' for x in ['A0','A1','A2','A3','B0','B1','B2','B3']), 'Full numeric precision, dates, gross/net basis, costs and exposures are exported in performance.csv. Tables are reproducible, not hand-entered. Additional SPY/60-40 benchmarks are on slide7 and in CSV.'),
    sl('Appendix | Sources and reproduction','Course lecture Momentum; Homework2 handout\nDaniel-Moskowitz2016; Asness etal2014\nKolanovic-Wei2015; Baltas-Kosowski supplied2013 version\nFrench official library | Cboe VIX | Yahoo via yfinance1.7.0\nREADME: cached run, tests, reports and executed notebooks','Exact paths/pages/lines and URLs: research/source_map.md. Cached inputs/manifests record acquired UTC timestamps, SHA256 and options. Run python -m momentum_hw2.cli validate-data --offline; pytest; run --offline; report --offline. No WRDS, new charges, publishing or submission.')]

def slides_pdf(slides):
    from reportlab.pdfgen import canvas
    from reportlab.lib.utils import ImageReader
    c=canvas.Canvas(str(ROOT/'deliverables/HW2_Investor_Presentation.pdf'),pagesize=(960,540))
    for i,s in enumerate(slides,1):
        c.setFillColor(colors.white);c.rect(0,0,960,540,fill=1,stroke=0)
        c.setFillColor(colors.HexColor('#172b4d'));c.setFont('Helvetica-Bold',30);c.drawString(45,485,s['title'])
        if s.get('figure'):
            lines=s['body'].split('\n');font=17;y=440
            for line in lines:c.setFont('Helvetica',font);c.drawString(48,y,line);y-=25
            from PIL import Image as PILImage
            path=ROOT/'outputs/figures'/s['figure'];iw,ih=PILImage.open(path).size
            scale=min(850/iw,max(170,y-70)/ih);w,h=iw*scale,ih*scale
            c.drawImage(str(path),(960-w)/2,47,width=w,height=h)
        else:
            y=421;size=22 if len(s['body'].split('\n'))<=6 else 19
            for line in s['body'].split('\n'):
                # Wrap at measured width, preserving explicit paragraph spacing.
                words=line.split();text=''
                for word in words:
                    trial=(text+' '+word).strip()
                    if c.stringWidth(trial,'Helvetica',size)>865:
                        c.setFont('Helvetica',size);c.drawString(48,y,text);y-=size*1.3;text=word
                    else:text=trial
                c.setFont('Helvetica',size);c.drawString(48,y,text);y-=size*1.7
        c.setFont('Helvetica',9);c.setFillColor(colors.HexColor('#537c8e'));c.drawString(48,20,'FINCB9339 HW2 | Hanyu Zhang | Historical research; assumed costs; actual input endpoints');c.drawRightString(915,20,str(i));c.showPage()
    c.save()
