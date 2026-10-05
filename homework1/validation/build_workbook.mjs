import fs from 'node:fs/promises';
import path from 'node:path';
import { Workbook, SpreadsheetFile } from '@oai/artifact-tool';

const out=path.resolve('outputs/validation');
const data=JSON.parse(await fs.readFile(path.join(out,'workbook_data.json'),'utf8'));
const wb=Workbook.create();
const names=['Summary','Sensitivity','Concentration','Trades','Decisions','VWAP','Noise','Volatility','Daily Equity'];
const sheets=Object.fromEntries(names.map(n=>[n,wb.worksheets.add(n)]));
const checks=[];
const date=x=>new Date(x.length===10?x+'T00:00:00Z':x.endsWith('Z')?x:x.replace(' ','T')+'Z');
const key=x=>String(x).slice(0,10);
const col=n=>{let v='';for(;n;n=Math.floor((n-1)/26))v=String.fromCharCode(65+(n-1)%26)+v;return v;};
const numfmt='#,##0.00000;[Red](#,##0.00000);0.00000';
const pctfmt='0.00000%;[Red](0.00000%);0.00000%';
function put(s,cell,value){sheets[s].getRange(cell).values=[[value]];}
function formula(s,cell,f,expected){sheets[s].getRange(cell).formulas=[[f]];if(expected!==undefined)checks.push({sheet:s,cell,expected});}
function block(s,cell,values){sheets[s].getRange(cell).write(values);}
function format(s,range,fmt){sheets[s].getRange(range).setNumberFormat(fmt);}
function header(s,row,labels){
  block(s,`A${row}`,[labels]);
  sheets[s].getRange(`A${row}:${col(labels.length)}${row}`).format={fill:'#243B53',font:{name:'Arial',size:10,bold:true,color:'#FFFFFF'},wrapText:true,horizontalAlignment:'center',verticalAlignment:'center',rowHeight:36};
}
function init(s,title,note,rows,cols){
  const sh=sheets[s];sh.showGridLines=false;
  sh.getRange(`A1:${col(cols)}${rows}`).format={font:{name:'Arial',size:10,color:'#172B4D'},rowHeight:22,verticalAlignment:'center',columnWidth:16};
  put(s,'A2',title);sh.getRange('A2').format.font={name:'Arial',size:14,bold:true,color:'#172B4D'};
  put(s,'A3',note);sh.getRange('A3').format.font={name:'Arial',size:10,italic:true,color:'#52606D'};
  sh.freezePanes.freezeRows(6);
}

const dailyRow=new Map(data.daily.map((d,i)=>[d.date,i+7]));
const volSummaryRow=new Map(data.sizing.map((d,i)=>[d.date,i+7]));
const decisionRow=new Map(data.decisions.map((d,i)=>[String(d.timestamp),i+7]));
const findDecision=(t)=>{
  const wanted=new Date(t).getTime();const i=data.decisions.findIndex(d=>new Date(d.timestamp).getTime()===wanted);
  if(i<0)throw new Error('Missing decision '+t);return i+7;
};
const dayEnd=data.daily.length+6;

init('Summary','Model C: manual reconstruction and validation','Frozen baseline preserved. Formula tables reconstruct four selected days from source observations.',40,10);
header('Summary',6,['Date','Start equity ($)','Leverage','Shares','Gross P&L ($)','Commission ($)','Slippage ($)','Net P&L ($)','Daily return','Vs. replay ($)']);
header('Summary',15,['Baseline constant','Value']);
block('Summary','A16',[
  ['Initial equity ($)',100000],['Lookback sessions',14],['Daily target volatility',.02],['Sizing leverage cap',4],
  ['Commission / share ($)',.0035],['Slippage / share ($)',.001],['Sessions per year',252]
]);
format('Summary','B16:B22',numfmt);format('Summary','B18',pctfmt);format('Summary','B17','0');format('Summary','B19','0');format('Summary','B22','0');
block('Summary','A25',[
 ['Read the formulas in Noise, Volatility, VWAP and Decisions, then reconcile Trades.'],
 ['Daily Equity preserves all 168 sessions and independently reconstructed starting capital.'],
 ['Sensitivity tables are fixed run results, not an Excel backtester or a specification ranking.'],
 ['Local formula edits recalculate the manual arithmetic; they do not rerun all historical trading.'],
 ['All prices use the unchanged first-interval open proxy and inferred start-labeled timestamps.'],
 ['Separate source-row arithmetic and inventory P&L agree with the frozen baseline.'],
 ['Same AI and known conventions: this is not blind third-party or vendor-data validation.'],
 ['Source: supplied SPY workbook; exact sheet/cell addresses accompany all manual raw observations.']
]);
sheets.Summary.getRange('A15:B22').format.columnWidth=24;

init('Daily Equity','Model C: independent daily inventory ledger','Gross P&L and cost inputs are snapshots of the separate replay. Equity and daily returns below are formulas.',dayEnd,13);
header('Daily Equity',6,['Date','Start equity ($)','Gross P&L ($)','Commission ($)','Slippage ($)','Total costs ($)','Net P&L ($)','End equity ($)','Daily return','Growth factor','Drawdown','Shares','Leverage']);
data.daily.forEach((d,i)=>{
  const r=i+7;block('Daily Equity',`A${r}`,[[date(d.date),null,d.gross_pnl,d.commission,d.slippage,null,null,null,null,null,null,d.shares,d.sizing_leverage]]);
  formula('Daily Equity',`B${r}`,i?`=H${r-1}`:"='Summary'!B16",d.start_equity);
  formula('Daily Equity',`F${r}`,`=D${r}+E${r}`,d.costs);
  formula('Daily Equity',`G${r}`,`=C${r}-F${r}`,d.net_pnl);
  formula('Daily Equity',`H${r}`,`=B${r}+G${r}`,d.equity);
  formula('Daily Equity',`I${r}`,`=G${r}/B${r}`,d.daily_return);
  formula('Daily Equity',`J${r}`,`=1+I${r}`);
  formula('Daily Equity',`K${r}`,`=H${r}/MAX('Summary'!$B$16,H$7:H${r})-1`);
});
format('Daily Equity',`A7:A${dayEnd}`,'yyyy-mm-dd');format('Daily Equity',`B7:H${dayEnd}`,numfmt);
format('Daily Equity',`I7:I${dayEnd}`,pctfmt);format('Daily Equity',`K7:K${dayEnd}`,pctfmt);format('Daily Equity',`J7:J${dayEnd}`,numfmt);
format('Daily Equity',`L7:L${dayEnd}`,'0');format('Daily Equity',`M7:M${dayEnd}`,numfmt);

init('Noise','Noise Area: every historical source observation','Source: AV.Clean in supplied SPY workbook. Slot is availability time; source labels appear separately.',data.noise.length+6,12);
header('Noise',6,['Target day','Slot','Historical day','Open proxy ($)','Slot price ($)','Price / open - 1','Absolute move','Available','Open source cell','Price source cell','Price source label','Available at']);
const noiseGroups=new Map();
data.noise.forEach((n,i)=>{
  const r=i+7;const k=n.target_date+' '+n.slot;
  if(!noiseGroups.has(k))noiseGroups.set(k,[]);noiseGroups.get(k).push(r);
  block('Noise',`A${r}`,[[date(n.target_date),n.slot,date(n.historical_date),n.open_proxy,n.historical_price,null,null,n.available,
    n.open_cell,n.price_cell,n.historical_source_timestamp?date(n.historical_source_timestamp):null,n.historical_available_timestamp?date(n.historical_available_timestamp):null]]);
  formula('Noise',`F${r}`,`=IF(H${r}=1,E${r}/D${r}-1,"")`);
  formula('Noise',`G${r}`,`=IF(H${r}=1,ABS(F${r}),"")`,n.absolute_move===null?undefined:n.absolute_move);
});
const noiseEnd=data.noise.length+6;
format('Noise',`A7:A${noiseEnd}`,'yyyy-mm-dd');format('Noise',`C7:C${noiseEnd}`,'yyyy-mm-dd');
format('Noise',`D7:E${noiseEnd}`,numfmt);format('Noise',`F7:G${noiseEnd}`,pctfmt);format('Noise',`K7:L${noiseEnd}`,'yyyy-mm-dd hh:mm');
sheets.Noise.getRange(`I1:L${noiseEnd}`).format.columnWidth=24;
sheets.Noise.getRange(`B7:B${noiseEnd}`).format.horizontalAlignment='center';

init('Volatility','Lagged daily volatility and Model C sizing','Source: BBRG.Daily closing-price cells and AV.Clean anchor cells. All 14 returns precede each target day.',data.volatility.length+16,12);
header('Volatility',6,['Target day','Start equity ($)','Open proxy ($)','Prior close ($)','Mean daily return','Sum squared dev.','Daily volatility','Leverage','Unrounded shares','Floor shares','Open source cell','Prior-close source']);
header('Volatility',16,['Target day','Return date','Prior date','Prior close ($)','Close ($)','Daily return','Mean return','Deviation','Squared deviation','Prior-close source','Close source']);
data.volatility.forEach((v,i)=>{
  const r=i+17;const sr=volSummaryRow.get(v.target_date);
  block('Volatility',`A${r}`,[[date(v.target_date),date(v.return_date),date(v.prior_date),v.previous_close,v.close,null,null,null,null,v.previous_close_cell,v.close_cell]]);
  formula('Volatility',`F${r}`,`=E${r}/D${r}-1`,v.spy_return);
  formula('Volatility',`G${r}`,`=$E$${sr}`,v.mean_return);
  formula('Volatility',`H${r}`,`=F${r}-G${r}`,v.deviation);
  formula('Volatility',`I${r}`,`=H${r}^2`,v.squared_deviation);
});
data.sizing.forEach((d,i)=>{
  const r=i+7;const start=17+i*14,end=start+13,dr=dailyRow.get(d.date);
  block('Volatility',`A${r}`,[[date(d.date),null,d.open_proxy,d.previous_close,null,null,null,null,null,null,d.open_source_cell,d.previous_close_cell]]);
  formula('Volatility',`B${r}`,`='Daily Equity'!B${dr}`,d.start_equity);
  formula('Volatility',`E${r}`,`=AVERAGE(F${start}:F${end})`,d.mean_return);
  formula('Volatility',`F${r}`,`=SUM(I${start}:I${end})`,d.squared_deviation_sum);
  formula('Volatility',`G${r}`,`=SQRT(F${r}/('Summary'!$B$17-1))`,d.prior_vol);
  formula('Volatility',`H${r}`,`=MIN('Summary'!$B$19,'Summary'!$B$18/G${r})`,d.sizing_leverage);
  formula('Volatility',`I${r}`,`=B${r}*H${r}/C${r}`);
  formula('Volatility',`J${r}`,`=INT(I${r})`,d.shares);
});
format('Volatility','A7:A10','yyyy-mm-dd');format('Volatility','B7:D10',numfmt);format('Volatility','E7:E10',pctfmt);
format('Volatility','F7:F10','0.0000000000');format('Volatility','G7:G10',pctfmt);format('Volatility','H7:I10',numfmt);format('Volatility','J7:J10','0');
format('Volatility',`A17:C${data.volatility.length+16}`,'yyyy-mm-dd');format('Volatility',`D17:E${data.volatility.length+16}`,numfmt);
format('Volatility',`F17:H${data.volatility.length+16}`,pctfmt);format('Volatility',`I17:I${data.volatility.length+16}`,'0.0000000000');
sheets.Volatility.getRange('J1:L80').format.columnWidth=24;

const de=data.decisions.length+6;
init('VWAP','Endpoint VWAP proxy: raw weights and running sums','Source: AV.Clean. Volumes are interval increments; unallocated closing residual volumes are excluded.',de,11);
header('VWAP',6,['Day','Available at','Source label','Interval price ($)','Interval volume','Price x volume','Cum. price x vol.','Cum. volume','VWAP proxy ($)','Price source cell','Volume source cell']);
let groupStart=7,previousDate=null;
data.decisions.forEach((d,i)=>{
  const r=i+7;if(previousDate!==d.date)groupStart=r;
  block('VWAP',`A${r}`,[[date(d.date),date(d.timestamp),date(d.source_timestamp),d.interval_price,d.volume,null,null,null,null,d.interval_price_cell,d.volume_cell]]);
  formula('VWAP',`F${r}`,`=D${r}*E${r}`,d.interval_price_times_volume);
  formula('VWAP',`G${r}`,`=SUM(F${groupStart}:F${r})`,d.cumulative_price_volume);
  formula('VWAP',`H${r}`,`=SUM(E${groupStart}:E${r})`,d.cumulative_volume);
  formula('VWAP',`I${r}`,`=G${r}/H${r}`,d.vwap_endpoint);
  previousDate=d.date;
});
format('VWAP',`A7:A${de}`,'yyyy-mm-dd');format('VWAP',`B7:C${de}`,'yyyy-mm-dd hh:mm');
format('VWAP',`D7:D${de}`,numfmt);format('VWAP',`E7:H${de}`,'#,##0.00000');format('VWAP',`I7:I${de}`,numfmt);
sheets.VWAP.getRange(`B1:C${de}`).format.columnWidth=24;sheets.VWAP.getRange(`F1:G${de}`).format.columnWidth=24;sheets.VWAP.getRange(`J1:K${de}`).format.columnWidth=23;

init('Decisions','Every Model C decision and interval P&L','Price uses the scheduled closing print on the final row. Held-before inventory earns the price change before the decision.',de,24);
header('Decisions',6,['Day','Available at','Price ($)','At close?','Noise count','Noise sigma','Upper ($)','Lower ($)','VWAP proxy ($)','Long stop ($)','Short stop ($)','Held before','Band signal','Stop crossed?','Held after','Action','Shares','Shares traded','Interval gross ($)','Commission ($)','Slippage ($)','Interval net ($)','Marked equity ($)','Price source cell']);
previousDate=null;
data.decisions.forEach((d,i)=>{
  const r=i+7,sr=volSummaryRow.get(d.date),nr=noiseGroups.get(d.date+' '+d.slot);
  const isFirst=previousDate!==d.date;
  block('Decisions',`A${r}`,[[date(d.date),date(d.timestamp),d.price,d.is_close?1:0,...Array(19).fill(null),d.execution_price_cell]]);
  formula('Decisions',`E${r}`,`=COUNT('Noise'!G${nr[0]}:G${nr.at(-1)})`,d.noise_count);
  formula('Decisions',`F${r}`,`=AVERAGE('Noise'!G${nr[0]}:G${nr.at(-1)})`,d.noise_sigma);
  formula('Decisions',`G${r}`,`=MAX('Volatility'!C${sr},'Volatility'!D${sr})*(1+F${r})`,d.upper);
  formula('Decisions',`H${r}`,`=MIN('Volatility'!C${sr},'Volatility'!D${sr})*(1-F${r})`,d.lower);
  formula('Decisions',`I${r}`,`='VWAP'!I${r}`,d.vwap_endpoint);
  formula('Decisions',`J${r}`,`=MAX(G${r},I${r})`,d.long_stop);
  formula('Decisions',`K${r}`,`=MIN(H${r},I${r})`,d.short_stop);
  formula('Decisions',`L${r}`,isFirst?'=0':`=O${r-1}`,d.held_before);
  formula('Decisions',`M${r}`,`=IF(C${r}>G${r},1,IF(C${r}<H${r},-1,0))`);
  formula('Decisions',`N${r}`,`=IF(OR(AND(L${r}=1,C${r}<J${r}),AND(L${r}=-1,C${r}>K${r})),1,0)`);
  formula('Decisions',`O${r}`,isFirst?'=0':`=IF(D${r}=1,0,IF(L${r}=0,M${r},IF(N${r}=1,IF(M${r}=-L${r},M${r},0),L${r})))`,d.held_after);
  formula('Decisions',`P${r}`,`=IF(O${r}=L${r},IF(O${r}=0,"FLAT","HOLD"),IF(L${r}=0,"ENTRY",IF(O${r}=0,"EXIT","REVERSE")))`);
  formula('Decisions',`Q${r}`,`='Volatility'!J${sr}`,d.shares);
  formula('Decisions',`R${r}`,`=ABS(O${r}-L${r})*Q${r}`,d.turnover_shares);
  formula('Decisions',`S${r}`,isFirst?'=0':`=L${r}*Q${r}*(C${r}-C${r-1})`,d.interval_gross_pnl);
  formula('Decisions',`T${r}`,`=R${r}*'Summary'!$B$20`,d.commission);
  formula('Decisions',`U${r}`,`=R${r}*'Summary'!$B$21`,d.slippage);
  formula('Decisions',`V${r}`,`=S${r}-T${r}-U${r}`,d.interval_net_pnl);
  formula('Decisions',`W${r}`,isFirst?`='Volatility'!B${sr}+V${r}`:`=W${r-1}+V${r}`,d.marked_equity);
  previousDate=d.date;
});
format('Decisions',`A7:A${de}`,'yyyy-mm-dd');format('Decisions',`B7:B${de}`,'yyyy-mm-dd hh:mm');
format('Decisions',`C7:C${de}`,numfmt);format('Decisions',`F7:F${de}`,pctfmt);format('Decisions',`G7:K${de}`,numfmt);
format('Decisions',`S7:W${de}`,numfmt);sheets.Decisions.getRange(`B1:B${de}`).format.columnWidth=24;
sheets.Decisions.getRange(`X1:X${de}`).format.columnWidth=23;sheets.Decisions.getRange(`S1:W${de}`).format.columnWidth=20;

const te=data.trades.length+6;
init('Trades','Model C: selected completed trades','All arithmetic uses Decisions and Volatility formulas; commission and slippage include both execution legs.',te,18);
header('Trades',6,['Day','Trade ID','Direction','Entry time','Exit time','Shares','Entry price ($)','Exit price ($)','Gross P&L ($)','Commission ($)','Slippage ($)','Net P&L ($)','Entry upper ($)','Entry lower ($)','Entry VWAP ($)','Exit upper ($)','Exit lower ($)','Exit VWAP ($)']);
data.trades.forEach((t,i)=>{
  const r=i+7,en=findDecision(t.entry_timestamp),ex=findDecision(t.exit_timestamp);
  block('Trades',`A${r}`,[[date(t.date),t.trade_id,t.direction,date(t.entry_timestamp),date(t.exit_timestamp),...Array(13).fill(null)]]);
  formula('Trades',`F${r}`,`='Decisions'!Q${en}`,t.shares);
  formula('Trades',`G${r}`,`='Decisions'!C${en}`,t.entry_price);formula('Trades',`H${r}`,`='Decisions'!C${ex}`,t.exit_price);
  formula('Trades',`I${r}`,`=C${r}*F${r}*(H${r}-G${r})`,t.gross_pnl);
  formula('Trades',`J${r}`,`=2*F${r}*'Summary'!$B$20`,t.commission);
  formula('Trades',`K${r}`,`=2*F${r}*'Summary'!$B$21`,t.slippage);
  formula('Trades',`L${r}`,`=I${r}-J${r}-K${r}`,t.net_pnl);
  for(const [c,dc,rr] of [['M','G',en],['N','H',en],['O','I',en],['P','G',ex],['Q','H',ex],['R','I',ex]])formula('Trades',`${c}${r}`,`='Decisions'!${dc}${rr}`);
});
format('Trades',`A7:A${te}`,'yyyy-mm-dd');format('Trades',`D7:E${te}`,'hh:mm');format('Trades',`G7:R${te}`,numfmt);
sheets.Trades.getRange(`I1:L${te}`).format.columnWidth=20;
data.sizing.forEach((d,i)=>{
  const r=i+7,sr=volSummaryRow.get(d.date),dr=dailyRow.get(d.date);
  put('Summary',`A${r}`,date(d.date));formula('Summary',`B${r}`,`='Volatility'!B${sr}`);
  formula('Summary',`C${r}`,`='Volatility'!H${sr}`);formula('Summary',`D${r}`,`='Volatility'!J${sr}`);
  for(const [c,tc] of [['E','I'],['F','J'],['G','K'],['H','L']])formula('Summary',`${c}${r}`,`=SUMIFS('Trades'!${tc}$7:${tc}$${te},'Trades'!A$7:A$${te},A${r})`);
  formula('Summary',`I${r}`,`=H${r}/B${r}`);
  formula('Summary',`J${r}`,`=ROUND(H${r}-'Daily Equity'!G${dr},8)`,0);
});
format('Summary','A7:A10','yyyy-mm-dd');format('Summary','B7:C10',numfmt);format('Summary','D7:D10','0');
format('Summary','E7:H10',numfmt);format('Summary','I7:I10',pctfmt);format('Summary','J7:J10',numfmt);

const labels={baseline_replay:'Baseline replay',midpoint_vwap:'Midpoint VWAP',delay_30m:'30-minute delay',vwap_entry_gate:'VWAP entry gate',exclude_incomplete_slots:'Exclude incomplete slots',higher_costs:'Higher costs'};
init('Sensitivity','One-change-at-a-time implementation sensitivity','Fixed independent-run results; no combined changes, optimization, ranking or baseline replacement.',39,12);
header('Sensitivity',6,['Case','Model','Cumulative return','Annual volatility','Sharpe','Max drawdown','Round trips','Total costs ($)','Baseline trades changed','Baseline trades unchanged','New/changed variant trades','Quantity-only changes']);
block('Sensitivity','A7',data.sensitivity.map(x=>[labels[x.case],x.model,x.cumulative_return,x.annualized_volatility,x.sharpe,x.maximum_drawdown,x.trades,x.total_costs,x.baseline_trades_changed,x.baseline_trades_unchanged,x.new_or_changed_variant_trades,x.shares_changed_same_episode]));
format('Sensitivity','C7:D24',pctfmt);format('Sensitivity','E7:E24',numfmt);format('Sensitivity','F7:F24',pctfmt);format('Sensitivity','H7:H24',numfmt);
sheets.Sensitivity.getRange('A1:A39').format.columnWidth=28;sheets.Sensitivity.getRange('I1:L39').format.columnWidth=22;
header('Sensitivity',28,['Case','VWAP','Delay intervals','Entry VWAP gate','Full 14 slots?','Commission/share','Slippage/share']);
block('Sensitivity','A29',data.case_definitions.map(x=>[labels[x.name],x.midpoint?'midpoint':'endpoint',x.delayed?1:0,x.vwap_entry_gate?1:0,x.full_history_only?1:0,x.commission,x.slippage]));
format('Sensitivity','F29:G34',numfmt);
put('Sensitivity','A36','Changed = baseline episode lacks exact same direction, entry/exit times and prices; removed trades count.');
put('Sensitivity','A37','Quantity-only changes exclude timing/price changes and reflect the changed daily equity path.');
put('Sensitivity','A38','Full-14 case suppresses discretionary decisions at missing-history slots; forced closing exits remain.');
put('Sensitivity','A39','Delay case queues decisions one grid step; closing liquidation overrides and cancels pending orders.');

init('Concentration','Model C: dependence on best and worst days','Rank by baseline daily return. Removal sets selected net returns to zero; all 168 dates remain, with no strategy rerun.',34,9);
header('Concentration',6,['Tail','Days removed','Selected net P&L ($)','Share of total profit','Selected compounded return','Return without days','Return difference','Difference / total return','Selected dates']);
header('Concentration',19,['Tail','Rank','Date','Daily return','Net P&L ($)','Start equity ($)','Growth factor','Profit share']);
data.ranked_days.forEach((d,i)=>{
  const r=i+20,dr=dailyRow.get(d.date);
  block('Concentration',`A${r}`,[[d.tail,d.rank,date(d.date),null,null,null,null,null]]);
  formula('Concentration',`D${r}`,`='Daily Equity'!I${dr}`,d.daily_return);
  formula('Concentration',`E${r}`,`='Daily Equity'!G${dr}`,d.net_pnl);
  formula('Concentration',`F${r}`,`='Daily Equity'!B${dr}`,d.start_equity);
  formula('Concentration',`G${r}`,`=1+D${r}`);
  formula('Concentration',`H${r}`,`=E${r}/('Daily Equity'!H${dayEnd}-'Summary'!B16)`,d.dollar_pnl_share_total_profit);
});
put('Concentration','A16','Baseline cumulative return');formula('Concentration','B16',`='Daily Equity'!H${dayEnd}/'Summary'!B16-1`);
data.concentration.forEach((d,i)=>{
  const r=i+7,start=d.tail==='best'?20:25,end=start+d.k-1;
  block('Concentration',`A${r}`,[[d.tail,d.k,null,null,null,null,null,null,d.dates]]);
  formula('Concentration',`C${r}`,`=SUM(E${start}:E${end})`,d.selected_net_pnl);
  formula('Concentration',`D${r}`,`=C${r}/('Daily Equity'!H${dayEnd}-'Summary'!B16)`,d.selected_dollar_pnl_share);
  formula('Concentration',`E${r}`,`=PRODUCT(G${start}:G${end})-1`,d.selected_compound_return);
  formula('Concentration',`F${r}`,`=(1+$B$16)/(1+E${r})-1`,d.cumulative_return_without);
  formula('Concentration',`G${r}`,`=$B$16-F${r}`,d.return_difference);
  formula('Concentration',`H${r}`,`=G${r}/$B$16`,d.return_difference_share);
});
format('Concentration','C7:C12',numfmt);format('Concentration','D7:H12',pctfmt);format('Concentration','B16',pctfmt);
format('Concentration','C20:C29','yyyy-mm-dd');format('Concentration','D20:D29',pctfmt);format('Concentration','E20:G29',numfmt);format('Concentration','H20:H29',pctfmt);
sheets.Concentration.getRange('A1:A34').format.columnWidth=28;sheets.Concentration.getRange('C1:H34').format.columnWidth=22;
sheets.Concentration.getRange('I1:I34').format.columnWidth=72;sheets.Concentration.getRange('I7:I12').format.wrapText=true;
sheets.Concentration.getRange('A7:I12').format.rowHeight=34;
put('Concentration','A32','Dollar P&L share is additive attribution on the actual equity path; it may exceed 100%.');
put('Concentration','A33','Return difference is baseline cumulative return minus compounded return after zeroing selected days.');
put('Concentration','A34','Day rankings are fixed baseline observations. Removing them is a hindsight stress, not a trading rule.');

wb.recalculate();
const qa=[];
for(const c of checks){
  const actual=sheets[c.sheet].getRange(c.cell).values[0][0];
  const tol=Math.max(1e-7,Math.abs(c.expected)*1e-12);
  qa.push({...c,actual,tolerance:tol,pass:typeof actual==='number'&&Math.abs(actual-c.expected)<=tol});
}
await fs.writeFile(path.join(out,'workbook_formula_checks.json'),JSON.stringify(qa,null,2));
const bad=qa.filter(x=>!x.pass);
console.log(JSON.stringify({formulaChecks:qa.length,failures:bad.slice(0,10)}));
if(bad.length)throw new Error(`${bad.length} formula arithmetic comparisons failed`);

// A real input perturbation verifies that the documented formula chain responds.
const original=sheets.Noise.getRange('E7').values[0][0];
const before=sheets.Noise.getRange('G7').values[0][0];
put('Noise','E7',original+1);wb.recalculate();
const after=sheets.Noise.getRange('G7').values[0][0];
if(after===before)throw new Error('Input mutation did not recalculate the Noise formula');
put('Noise','E7',original);wb.recalculate();
await fs.writeFile(path.join(out,'workbook_recalculation_check.json'),JSON.stringify({cell:'Noise!E7',dependent:'Noise!G7',before,after,restored:sheets.Noise.getRange('G7').values[0][0]},null,2));

const errors=await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:100},summary:'Formula error scan'});
await fs.writeFile(path.join(out,'workbook_error_scan.txt'),errors.ndjson);
console.log(errors.ndjson);
await fs.mkdir(path.join(out,'previews'),{recursive:true});
const renders=[['Summary','A1:J11'],['Sensitivity','A5:L24'],['Concentration','A5:H16'],['Trades','A5:L12'],
  ['Decisions','A5:K19'],['Decisions','L5:X19'],['VWAP','A5:I19'],['Noise','A5:H21'],['Volatility','A5:J10'],
  ['Volatility','A15:I31'],['Daily Equity','A5:K19']];
for(let i=0;i<renders.length;i++){
  const [sheetName,range]=renders[i];
  const img=await wb.render({sheetName,range,scale:1.3,format:'png'});
  await fs.writeFile(path.join(out,'previews',`${i+1}-${sheetName.replaceAll(' ','_')}.png`),new Uint8Array(await img.arrayBuffer()));
}
const exported=await SpreadsheetFile.exportXlsx(wb);
await exported.save(path.join(out,'validation_tables.xlsx'));
await fs.writeFile(path.join(out,'workbook_build_summary.json'),JSON.stringify({sheets:names,formula_comparisons:qa.length,all_passed:true,rendered_ranges:renders,engine:'Artifact Tool; not tested in native Excel'},null,2));
console.log('Saved validation_tables.xlsx');
