import fs from 'node:fs/promises';
import path from 'node:path';
import { Workbook, SpreadsheetFile } from '@oai/artifact-tool';

const root=path.resolve('.');
const data=JSON.parse(await fs.readFile('submission/submission_data.json','utf8'));
const out=path.join(root,'outputs','submission');
await fs.mkdir(out,{recursive:true});
const wb=Workbook.create();
const names=['Overview','Daily Results','Trade Log','Execution Log','Signal Inputs','April Noise','April Volatility','Sensitivity','Concentration','Source AV Clean','Source BBRG Daily','Source BBRG Intraday','Method Notes'];
const sh=Object.fromEntries(names.map(n=>[n,wb.worksheets.add(n)]));
const date=s=>s?new Date(String(s).replace(' ','T')+(String(s).includes('Z')?'':'Z')):null;
const v=x=>x===undefined||x===null||Number.isNaN(x)?null:x;
const c=n=>{let s='';for(;n;n=Math.floor((n-1)/26))s=String.fromCharCode(65+(n-1)%26)+s;return s;};
const put=(s,a,value)=>sh[s].getRange(a).values=[[value]];
const f=(s,a,value)=>sh[s].getRange(a).formulas=[[value]];
const block=(s,a,m)=>{if(m.length)sh[s].getRange(a).write(m);};
const fmt=(s,a,x)=>sh[s].getRange(a).setNumberFormat(x);
const nfmt='#,##0.00000;[Red](#,##0.00000);0.00000';
const pfmt='0.00000%;[Red](0.00000%);0.00000%';
function init(s,title,note,widths){
  const x=sh[s];x.showGridLines=false;x.getRange('A1:V5').format={font:{name:'Arial',size:10,color:'#172B4D'},rowHeight:22,verticalAlignment:'center'};
  put(s,'A2',title);x.getRange('A2').format.font={name:'Arial',size:15,bold:true,color:'#17365D'};
  put(s,'A3',note);x.getRange('A3').format.font={name:'Arial',size:10,italic:true,color:'#52606D'};
  x.freezePanes.freezeRows(6);
  widths.forEach((w,i)=>x.getRange(`${c(i+1)}:${c(i+1)}`).format.columnWidth=w);
}
function hdr(s,labels){block(s,'A6',[labels]);sh[s].getRange(`A6:${c(labels.length)}6`).format={fill:'#17365D',font:{name:'Arial',size:10,bold:true,color:'#FFFFFF'},wrapText:true,horizontalAlignment:'center',verticalAlignment:'center',rowHeight:38};}

init('Overview','FINCB9339 Homework 1 | Strategy replication','Submission workbook | scored 2025-04-02 to 2025-12-01 | 168 sessions | initial capital $100,000',[38,22,22,22,22]);
hdr('Overview',['Performance measure','Model A','Model B','Model C','SPY gross']);
const perf=Object.fromEntries(data.performance.map(x=>[x.model,x]));
const metrics=[
 ['Cumulative return','cumulative_return',pfmt],['Annualized geometric return','annualized_return',pfmt],
 ['Annualized volatility','annualized_volatility',pfmt],['Sharpe, zero risk-free','sharpe_zero_rf',nfmt],
 ['Maximum drawdown','maximum_drawdown',pfmt],['Final equity ($)','final_equity',nfmt],
 ['Completed round trips','number_of_round_trips','0'],['Total transaction costs ($)','total_costs',nfmt],
 ['Trade hit ratio','trade_hit_ratio',pfmt],['Average trade net P&L ($)','average_trade_net_pnl',nfmt],
 ['Best day return','best_day_return',pfmt],['Worst day return','worst_day_return',pfmt],
 ['Annualized alpha vs SPY','alpha_annual_arithmetic',pfmt],['Beta vs SPY','beta',nfmt],
 ['HAC alpha p-value','alpha_pvalue_hac5',nfmt]
];
metrics.forEach(([label,key,format],i)=>{let r=i+7;block('Overview',`A${r}`,[[label,...['A','B','C','SPY_gross'].map(m=>v(perf[m]?.[key]))]]);fmt('Overview',`B${r}:E${r}`,format);});
put('Overview','A24','Method and source');
block('Overview','A25',[
 ['Model A — 14 prior sessions; gap-adjusted Noise Area; opposite boundary exit.'],
 ['Model B — Model A entry; long stop max(upper,VWAP proxy), short stop min(lower,VWAP proxy).'],
 ['Model C — Model B plus min(4,2% / prior-14-day daily SPY volatility) sizing.'],
 ['Execution — 30-minute grid, observed price reference, daily close liquidation.'],
 ['Costs — $0.0035/share commission + $0.001/share slippage on each execution leg.'],
 ['Data limits — first interval open proxy; endpoint price-volume VWAP proxy.'],
 ['Half days — July 3 and November 28 liquidated at 13:00; stale prints excluded.'],
 ['Audit — Daily Results → Trade Log → Execution Log / Signal Inputs → source tabs.'],
 ['Validation — April Noise/Volatility show live formulas; sensitivities are fixed independent runs.'],
 [`Source SHA-256 — ${data.source_sha256}`],
]);
sh.Overview.getRange('A24:E24').format={fill:'#D9EAF5',font:{name:'Arial',size:11,bold:true,color:'#17365D'}};

init('Daily Results','Baseline daily results | common scored dates','Frozen Python backtest values. Three Excel SUMIFS columns reconcile each day to completed trade net P&L.',[14,16,16,14,14,16,16,14,14,16,16,14,14,16,16,14,14,16,16,14,14,16,16,16,16,16,15,15,15]);
hdr('Daily Results',['Date','A start $','A gross $','A costs $','A net $','A end $','A return','B start $','B gross $','B costs $','B net $','B end $','B return','C start $','C gross $','C costs $','C net $','C end $','C return','SPY return','SPY equity $','A trade net $','B trade net $','C trade net $','A Δ $','B Δ $','C Δ $']);
const dayRows=[];
for(let i=0;i<data.A_daily.length;i++){
 const a=data.A_daily[i],b=data.B_daily[i],cc=data.C_daily[i],spy=data.SPY_gross_daily[i];
 if(a.date!==b.date||a.date!==cc.date||a.date!==spy.date)throw new Error('Daily date mismatch');
 dayRows.push([date(a.date),a.start_equity,a.gross_pnl,a.costs,a.net_pnl,a.equity,a.daily_return,b.start_equity,b.gross_pnl,b.costs,b.net_pnl,b.equity,b.daily_return,cc.start_equity,cc.gross_pnl,cc.costs,cc.net_pnl,cc.equity,cc.daily_return,spy.daily_return,spy.equity,...Array(6).fill(null)]);
}
block('Daily Results','A7',dayRows);
const dailyEnd=dayRows.length+6;
for(let r=7;r<=dailyEnd;r++){
 for(const [col,model] of [['V','A'],['W','B'],['X','C']])f('Daily Results',`${col}${r}`,`=SUMIFS('Trade Log'!$N$7:$N$371,'Trade Log'!$A$7:$A$371,"${model}",'Trade Log'!$C$7:$C$371,A${r})`);
 f('Daily Results',`Y${r}`,`=V${r}-E${r}`);f('Daily Results',`Z${r}`,`=W${r}-K${r}`);f('Daily Results',`AA${r}`,`=X${r}-Q${r}`);
}
fmt('Daily Results',`A7:A${dailyEnd}`,'yyyy-mm-dd');
for(const col of ['G','M','S','T'])fmt('Daily Results',`${col}7:${col}${dailyEnd}`,pfmt);
for(const col of ['B','C','D','E','F','H','I','J','K','L','N','O','P','Q','R','U','V','W','X','Y','Z','AA'])fmt('Daily Results',`${col}7:${col}${dailyEnd}`,nfmt);

const allTrades=['A','B','C'].flatMap(m=>data[`${m}_trades`]);
const execMap=new Map(['A','B','C'].flatMap(m=>data[`${m}_executions`].map(x=>[`${m}:${x.trade_id}:${x.action}`,x])));
if(allTrades.length!==365)throw new Error(`Expected 365 completed trades; got ${allTrades.length}`);
init('Trade Log','Completed trade ledger | Models A, B, C','Entry/exit prices and signal levels are frozen inputs; Excel formulas independently recalculate gross, cost, and net P&L.',[11,10,14,21,21,11,11,17,17,18,17,17,17,18,17,17,17,17,17,17,20]);
hdr('Trade Log',['Model','Trade ID','Date','Entry time','Exit time','Direction','Shares','Entry price $','Exit price $','Gross P&L $','Commission $','Slippage $','Total costs $','Net P&L $','Entry upper $','Entry lower $','Entry VWAP $','Exit upper $','Exit lower $','Exit VWAP $','Exit reason']);
block('Trade Log','A7',allTrades.map(t=>{
 const en=execMap.get(`${t.model}:${t.trade_id}:ENTRY`),ex=execMap.get(`${t.model}:${t.trade_id}:EXIT`);
 if(!en||!ex)throw new Error(`Missing execution for ${t.model}:${t.trade_id}`);
 return [t.model,t.trade_id,date(t.date),date(t.entry_timestamp),date(t.exit_timestamp),t.direction,t.shares,t.entry_price,t.exit_price,null,null,null,null,null,en.upper,en.lower,en.vwap_approx,ex.upper,ex.lower,ex.vwap_approx,t.exit_reason];
}));
const tradeEnd=allTrades.length+6;
for(let r=7;r<=tradeEnd;r++){
 f('Trade Log',`J${r}`,`=F${r}*G${r}*(I${r}-H${r})`);
 f('Trade Log',`K${r}`,`=2*G${r}*'Method Notes'!$B$8`);
 f('Trade Log',`L${r}`,`=2*G${r}*'Method Notes'!$B$9`);
 f('Trade Log',`M${r}`,`=K${r}+L${r}`);
 f('Trade Log',`N${r}`,`=J${r}-M${r}`);
}
fmt('Trade Log',`C7:C${tradeEnd}`,'yyyy-mm-dd');fmt('Trade Log',`D7:E${tradeEnd}`,'yyyy-mm-dd hh:mm');fmt('Trade Log',`H7:T${tradeEnd}`,nfmt);

const allExec=['A','B','C'].flatMap(m=>data[`${m}_executions`]);
init('Execution Log','Every execution leg | Models A, B, C','A same-timestamp reversal appears as separate exit and entry legs. Event P&L and costs are frozen baseline values.',[10,10,14,21,21,12,10,11,11,17,17,17,17,17,17,17,10,16,16,16,16,16,20]);
hdr('Execution Log',['Model','Trade ID','Date','Execution time','Signal time','Action','Side','Direction','Shares','Price $','Upper $','Lower $','Noise σ','VWAP proxy $','Long stop $','Short stop $','Leverage','Gross P&L $','Commission $','Slippage $','Net P&L $','Reason','Source timestamp']);
block('Execution Log','A7',allExec.map(x=>[x.model,x.trade_id,date(x.date),date(x.timestamp),date(x.signal_timestamp),x.action,x.order_side,x.direction,x.shares,x.price,x.upper,x.lower,x.noise_sigma,x.vwap_approx,x.long_stop,x.short_stop,x.sizing_leverage,x.gross_pnl,x.commission,x.slippage,x.net_pnl,x.reason,date(x.source_timestamp)]));
fmt('Execution Log',`C7:C${allExec.length+6}`,'yyyy-mm-dd');fmt('Execution Log',`D7:E${allExec.length+6}`,'yyyy-mm-dd hh:mm');fmt('Execution Log',`W7:W${allExec.length+6}`,'yyyy-mm-dd hh:mm');fmt('Execution Log',`J7:V${allExec.length+6}`,nfmt);

init('Signal Inputs','Intraday signal and VWAP build | all sessions','Prepared rows from the unchanged baseline. Time = inferred availability, source label = original workbook timestamp.',[21,21,14,17,18,17,17,16,15,12,15,17,17,17,17,17,17,12,12,24]);
hdr('Signal Inputs',['Source label','Available at','Date','Observed price $','Source volume','Interval volume','Cumulative volume','Open proxy $','Prior close $','Noise count','Noise σ','Upper $','Lower $','VWAP proxy $','Long stop $','Short stop $','Eligible','At close','Scheduled close','Source AV row']);
const rawRowMap=new Map(data.raw.map(x=>[String(x['Time Stamp']).replace('T',' ').slice(0,19),x.source_excel_row]));
block('Signal Inputs','A7',data.features.map(x=>[date(x.source_timestamp),date(x.timestamp),date(x.date),x.price,x.volume,x.incremental_volume,x.cumulative_observed_volume,x.open_proxy,x.previous_close,x.noise_count,v(x.noise_sigma),v(x.upper),v(x.lower),v(x.vwap_approx),v(x.long_stop),v(x.short_stop),x.eligible_day?1:0,x.is_close?1:0,date(x.scheduled_close),v(rawRowMap.get(x.source_timestamp))]));
const featEnd=data.features.length+6;
fmt('Signal Inputs',`A7:B${featEnd}`,'yyyy-mm-dd hh:mm');fmt('Signal Inputs',`C7:C${featEnd}`,'yyyy-mm-dd');fmt('Signal Inputs',`D7:P${featEnd}`,nfmt);fmt('Signal Inputs',`S7:S${featEnd}`,'yyyy-mm-dd hh:mm');

init('April Noise','April 2 at 11:30 | 14 prior time-of-day observations','Source cell addresses refer to the original AV.Clean sheet; source rows are copied into Source AV Clean.',[15,12,15,18,18,20,20,21,21,22]);
hdr('April Noise',['Target day','Slot','Historical day','Open proxy $','Slot price $','Absolute move','Open source cell','Price source cell','Source label','Available at']);
block('April Noise','A7',data.noise_april.map(x=>[date(x.target_date),x.slot,date(x.historical_date),x.open_proxy,x.historical_price,null,x.open_cell,x.price_cell,date(x.historical_source_timestamp),date(x.historical_available_timestamp)]));
for(let r=7;r<=20;r++)f('April Noise',`F${r}`,`=ABS(E${r}/D${r}-1)`);
put('April Noise','D22','Mean Noise σ');f('April Noise','E22','=AVERAGE(F7:F20)');
put('April Noise','D23','April 2 open proxy');put('April Noise','E23',555.3837);
put('April Noise','D24','Prior close');put('April Noise','E24',557.7698);
put('April Noise','D25','Upper boundary');f('April Noise','E25','=MAX(E23,E24)*(1+E22)');
put('April Noise','D26','Lower boundary');f('April Noise','E26','=MIN(E23,E24)*(1-E22)');
put('April Noise','D27','Observed 11:30 price');put('April Noise','E27',560.0867);
put('April Noise','D28','Long signal (1=yes)');f('April Noise','E28','=IF(E27>E25,1,0)');
fmt('April Noise','A7:A20','yyyy-mm-dd');fmt('April Noise','C7:C20','yyyy-mm-dd');fmt('April Noise','D7:E28',nfmt);fmt('April Noise','F7:F20','0.000000000000');fmt('April Noise','I7:J20','yyyy-mm-dd hh:mm');

init('April Volatility','April 2 | 14 lagged daily SPY returns and sizing','Sample standard deviation uses denominator 13. Input close cells refer to the original BBRG.Daily sheet.',[15,15,15,18,18,19,21,21]);
hdr('April Volatility',['Target day','Return day','Prior day','Prior close $','Close $','Daily return','Prior source cell','Close source cell']);
block('April Volatility','A7',data.vol_april.map(x=>[date(x.target_date),date(x.return_date),date(x.prior_date),x.previous_close,x.close,null,x.previous_close_cell,x.close_cell]));
for(let r=7;r<=20;r++)f('April Volatility',`F${r}`,`=E${r}/D${r}-1`);
put('April Volatility','D22','Mean return');f('April Volatility','E22','=AVERAGE(F7:F20)');
put('April Volatility','D23','Daily SPY volatility');f('April Volatility','E23','=STDEV.S(F7:F20)');
put('April Volatility','D24','Target volatility');f('April Volatility','E24',"='Method Notes'!B6");
put('April Volatility','D25','Leverage cap');f('April Volatility','E25',"='Method Notes'!B7");
put('April Volatility','D26','Model C leverage');f('April Volatility','E26','=MIN(E25,E24/E23)');
put('April Volatility','D27','Start equity $');f('April Volatility','E27',"='Method Notes'!B5");
put('April Volatility','D28','Open proxy $');f('April Volatility','E28',"='April Noise'!E23");
put('April Volatility','D29','Shares');f('April Volatility','E29','=INT(E27*E26/E28)');
fmt('April Volatility','A7:C20','yyyy-mm-dd');fmt('April Volatility','D7:E29',nfmt);fmt('April Volatility','F7:F20','0.000000000000');

init('Sensitivity','Implementation ambiguity | one change at a time','Fixed independent-run outputs. Baseline cases preserve original assumptions; changed trade count excludes quantity-only changes.',[27,10,19,19,14,19,14,17,19,21]);
hdr('Sensitivity',['Case','Model','Cumulative return','Annual volatility','Sharpe','Max drawdown','Round trips','Total costs $','Baseline trades changed','Quantity-only changes']);
block('Sensitivity','A7',data.sensitivity.map(x=>[x.case,x.model,x.cumulative_return,x.annualized_volatility,x.sharpe,x.maximum_drawdown,x.trades,x.total_costs,x.baseline_trades_changed,x.shares_changed_same_episode]));
fmt('Sensitivity','C7:D24',pfmt);fmt('Sensitivity','E7:E24',nfmt);fmt('Sensitivity','F7:F24',pfmt);fmt('Sensitivity','H7:H24',nfmt);

init('Concentration','Model C | best/worst day dependence','Removal sets selected daily net returns to zero without rerunning the strategy; rankings are hindsight diagnostics.',[12,14,63,20,20,20,20,20]);
hdr('Concentration',['Tail','Days removed','Selected dates','Selected net P&L $','Share of total profit','Return without','Change vs baseline','Selected compounded return']);
block('Concentration','A7',data.concentration.map(x=>[x.tail,x.k,x.dates,x.selected_net_pnl,x.selected_dollar_pnl_share,x.cumulative_return_without,x.return_difference,x.selected_compound_return]));
fmt('Concentration','D7:D12',nfmt);fmt('Concentration','E7:H12',pfmt);
put('Concentration','A16','Selected day ranking');
block('Concentration','A18',[['Tail','Rank','Date','Daily return','Net P&L $','Start equity $','Share of total profit']]);
sh.Concentration.getRange('A18:G18').format={fill:'#17365D',font:{name:'Arial',bold:true,color:'#FFFFFF'},rowHeight:28};
block('Concentration','A19',data.ranked_days.map(x=>[x.tail,x.rank,date(x.date),x.daily_return,x.net_pnl,x.start_equity,x.dollar_pnl_share_total_profit]));
fmt('Concentration','C19:C28','yyyy-mm-dd');fmt('Concentration','D19:D28',pfmt);fmt('Concentration','E19:F28',nfmt);fmt('Concentration','G19:G28',pfmt);

init('Source AV Clean','Supplied workbook | AV.Clean','Unmodified values and original Excel row numbers. Descending date order matches the source sheet.',[20,23,17,19]);
hdr('Source AV Clean',['Original row','Time Stamp','Last Price $','Volume, AV']);
block('Source AV Clean','A7',data.raw.map(x=>[x.source_excel_row,date(x['Time Stamp']),v(x['Last Price']),v(x['Volume, AV'])]));
fmt('Source AV Clean',`B7:B${data.raw.length+6}`,'yyyy-mm-dd hh:mm');fmt('Source AV Clean',`C7:C${data.raw.length+6}`,nfmt);

init('Source BBRG Daily','Supplied workbook | BBRG.Daily','Unmodified daily close and volume values. Original Excel row numbers allow direct comparison with attached dataset.',[20,23,17,19,19]);
hdr('Source BBRG Daily',['Original row','Time Stamp','Last Price $','Volume','SMAVG (15)']);
block('Source BBRG Daily','A7',data.raw_daily.map(x=>[x.source_excel_row,date(x['Time Stamp']),v(x['Last Price']),v(x.Volume),v(x['SMAVG (15)'])]));
fmt('Source BBRG Daily',`B7:B${data.raw_daily.length+6}`,'yyyy-mm-dd');fmt('Source BBRG Daily',`C7:C${data.raw_daily.length+6}`,nfmt);

init('Source BBRG Intraday','Supplied workbook | BBRG.Intraday','Original intraday values kept for source comparison; AV.Clean is the baseline source after volume cleaning.',[20,23,17,19,19]);
hdr('Source BBRG Intraday',['Original row','Time Stamp','Last Price $','Volume','SMAVG (15)']);
block('Source BBRG Intraday','A7',data.raw_intraday.map(x=>[x.source_excel_row,date(x['Time Stamp']),v(x['Last Price']),v(x.Volume),v(x['SMAVG (15)'])]));
fmt('Source BBRG Intraday',`B7:B${data.raw_intraday.length+6}`,'yyyy-mm-dd hh:mm');fmt('Source BBRG Intraday',`C7:C${data.raw_intraday.length+6}`,nfmt);

init('Method Notes','Method, fixed inputs, and workbook scope','This workbook packages the finished Python backtest; editing source data does not rerun the full trade-state machine.',[37,90]);
block('Method Notes','A11',[['Parameter / issue','Value or interpretation']]);
sh['Method Notes'].getRange('A11:B11').format={fill:'#17365D',font:{name:'Arial',size:10,bold:true,color:'#FFFFFF'},rowHeight:28};
block('Method Notes','A12',[
 ['Noise lookback sessions',14],
 ['Commission per share per execution',0.0035],
 ['Slippage per share per execution',0.001],
 ['Trading days per year',252],
 ['First scored date','2025-04-02'],
 ['Last scored date','2025-12-01'],
 ['Open proxy','First available half-hour observation; true 9:30 opening transaction unavailable.'],
 ['VWAP proxy','Cumulative sum of observed interval-end price × interval volume / cumulative observed interval volume.'],
 ['Timestamp convention','Inferred start-labeled source intervals. First interval becomes available at 10:00.'],
 ['Noise Area','Mean of |historical time-slot price / historical open proxy - 1| over available prior 14 sessions.'],
 ['Upper / lower','max(open proxy, previous close) × (1 + noise); min(open proxy, previous close) × (1 - noise).'],
 ['Model C shares','floor(starting equity × min(4, 0.02 / prior-14-day sample SPY volatility) / open proxy).'],
 ['Early closes','2025-07-03 and 2025-11-28 force 13:00 close; later stale prints remain in raw source only.'],
 ['Trade costs','2 × shares × (commission + slippage) for a completed round trip.'],
 ['Annualization','252 sessions/year; zero risk-free rate.'],
 ['Workbook formula scope','April manual arithmetic, trade P&L, and daily trade-net reconciliations recalculate in Excel.'],
 ['Frozen output scope','Full historical signals, state transitions, daily equity, sensitivity, and summary statistics are verified Python output snapshots.'],
 ['Original source SHA-256',data.source_sha256],
 ['Author code','Not consulted or reproduced.'],
]);
// Authoritative parameters used by the live demonstration formulas.
put('Method Notes','D4','Live formula parameters');
block('Method Notes','A4',[]);
put('Method Notes','A5','Initial equity $');put('Method Notes','B5',100000);
put('Method Notes','A6','Target daily volatility');put('Method Notes','B6',0.02);
put('Method Notes','A7','Leverage cap');put('Method Notes','B7',4);
put('Method Notes','A8','Commission/share $');put('Method Notes','B8',0.0035);
put('Method Notes','A9','Slippage/share $');put('Method Notes','B9',0.001);
fmt('Method Notes','B5:B9',nfmt);
// Put detailed notes below the parameters to avoid any overlap with their formula references.
block('Method Notes','A27',[
 ['VWAP is approximate','No transaction-level prices or complete interval dollar turnover are supplied.'],
 ['Observed volume','The AV.Clean source contains cleaned cumulative/interval conventions; baseline Signal Inputs stores observed increments.'],
 ['Scored sample','182 sessions in source, first 14 used as Noise Area warm-up, 168 scored sessions.'],
 ['Sensitivity','Alternative implementations are independent fixed outputs, not selectable live Excel cases.'],
 ['Concentration','Removing days is an attribution stress, not a modified executable trading strategy.'],
]);

wb.recalculate();
const checks=[];
function check(s,cell,expected,tol=1e-7){const actual=sh[s].getRange(cell).values[0][0];checks.push({sheet:s,cell,expected,actual,pass:typeof actual==='number'&&Math.abs(actual-expected)<=tol});}
check('April Noise','E22',0.003189207828893267,1e-10);
check('April Noise','E25',559.5486438128803,1e-7);
check('April Noise','E26',553.6124659559202,1e-7);
check('April Noise','E28',1,0);
check('April Volatility','E23',0.011891080580,1e-9);
check('April Volatility','E26',1.6819329299852241,1e-7);
check('April Volatility','E29',302,0);
check('Trade Log','N7',allTrades[0].net_pnl,1e-6);
check('Daily Results','V7',data.A_daily[0].net_pnl,1e-6);
check('Daily Results','X7',data.C_daily[0].net_pnl,1e-6);
const fails=checks.filter(x=>!x.pass);
await fs.writeFile(path.join(out,'submission_checks.json'),JSON.stringify({checks,failed:fails},null,2));
if(fails.length)throw new Error(`Formula checks failed: ${JSON.stringify(fails)}`);
const renders=[['Overview','A1:E23'],['Daily Results','A1:M12'],['Trade Log','A1:N12'],['Execution Log','A1:K12'],['Signal Inputs','A1:J12'],['April Noise','A18:F28'],['April Volatility','A18:F29'],['Sensitivity','A1:J14'],['Concentration','A1:H12'],['Source AV Clean','A1:D12'],['Source BBRG Daily','A1:E12'],['Source BBRG Intraday','A1:E12'],['Method Notes','A1:B19']];
const preview=path.join(out,'previews');await fs.mkdir(preview,{recursive:true});
for(const [s,range] of renders){const img=await wb.render({sheetName:s,range,scale:1.1,format:'png'});await fs.writeFile(path.join(preview,`${s.replaceAll(' ','_')}.png`),new Uint8Array(await img.arrayBuffer()));}
const file=path.join(out,'FINCB9339_HW1_Submission.xlsx');
const blob=await SpreadsheetFile.exportXlsx(wb);await blob.save(file);
console.log(JSON.stringify({file,sheets:names,sourceRows:data.raw.length,features:data.features.length,trades:allTrades.length,executions:allExec.length,scoredDays:data.A_daily.length,formulaChecks:checks.length}));
