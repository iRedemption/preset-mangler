/* Stats page: one bridge call, quick-glance cards and interactive ECharts panels. */
const charts=[];
const pct=(part,total)=>total?Math.round(100*part/total)+'%':'0%';
const topName=list=>list&&list.length?list[0][0]:'—';
const barOption=(rows,{horizontal=false,color='#9ce2ef'}={})=>({
  tooltip:{trigger:'axis',axisPointer:{type:'shadow'}},
  grid:{left:horizontal?150:36,right:16,top:16,bottom:horizontal?24:52,containLabel:!horizontal},
  xAxis:horizontal?{type:'value'}:{type:'category',data:rows.map(r=>r[0]),axisLabel:{rotate:rows.length>6?30:0}},
  yAxis:horizontal?{type:'category',data:rows.map(r=>r[0]),inverse:true}:{type:'value'},
  series:[{type:'bar',data:rows.map(r=>r[1]),itemStyle:{color},label:{show:true,position:horizontal?'right':'top'}}],
});

function statsCard(label,value) {
  const card=element('div','stat-card');card.append(element('span','stat-value',String(value)),element('span','stat-label',label));return card;
}

const MAXIMIZE_ICON='path://M3 3h6v2H5v4H3V3zm12 0h6v6h-2V5h-4V3zM3 15h2v4h4v2H3v-6zm16 4v-4h2v6h-6v-2h4z';

function setMaximized(panel,chart,on) {
  panel.classList.toggle('maximized',on);
  chart.setOption({toolbox:{feature:{myTool:{title:on?'Restore':'Maximize'}}}});
  chart.resize();
}

function statsPanel(grid,title,render) {
  const panel=element('div','chart-card');panel.append(element('h3','',title));
  const box=element('div','chart-box');panel.append(box);grid.append(panel);
  const chart=echarts.init(box,'dark');charts.push(chart);
  const maximize={show:true,title:'Maximize',icon:MAXIMIZE_ICON,onclick:()=>setMaximized(panel,chart,!panel.classList.contains('maximized'))};
  chart.setOption({backgroundColor:'transparent',...render(),toolbox:{right:8,feature:{myTool:maximize,saveAsImage:{title:'PNG'},dataView:{readOnly:true,title:'Data'}}}});
}

document.addEventListener('keydown',e=>{
  if(e.key!=='Escape')return;
  document.querySelectorAll('.chart-card.maximized').forEach(panel=>{
    const chart=charts.find(c=>c.getDom()===panel.querySelector('.chart-box'));
    if(chart)setMaximized(panel,chart,false);
  });
});

function renderStats(data) {
  charts.splice(0).forEach(c=>c.dispose());
  const page=$('stats-page');page.replaceChildren();
  if(!data.count){page.append(element('h1','','No presets found'),element('p','','Check the library directory in Settings.'));return;}
  const header=element('div','stats-header');
  const refresh=element('button','','Refresh');refresh.onclick=()=>loadStats();
  header.append(element('h1','',`Library stats · ${data.count} presets`),refresh);page.append(header);
  const cards=element('div','stat-cards');
  [['Presets',data.count],['Total size (MB)',(data.total_bytes/1048576).toFixed(1)],
   ['With mod routing',pct(data.with_mods,data.count)],['With FX',pct(data.with_fx,data.count)],
   ['Avg routes / preset',data.avg_routes],['Duplicates (identical files)',data.duplicates],
   ['Top category',topName(data.categories)],['Top oscillator engine',topName(data.engines)],
   ['Top filter',topName(data.filters)],['Unclassified by name',pct(data.unclassified,data.count)]]
    .forEach(([l,v])=>cards.append(statsCard(l,v)));
  page.append(cards);
  const grid=element('div','chart-grid');page.append(grid);
  statsPanel(grid,'Preset categories (from filename)',()=>({tooltip:{trigger:'item',formatter:'{b}: {c} ({d}%)'},legend:{bottom:0,type:'scroll',textStyle:{color:'#c9d6dc'}},
    series:[{type:'pie',radius:['40%','68%'],center:['50%','45%'],data:data.categories.map(([name,value])=>({name,value})),label:{formatter:'{b}'}}]}));
  statsPanel(grid,'Oscillator engines (OSC 1–3)',()=>barOption(data.engines,{color:'#59e4bc'}));
  statsPanel(grid,'Filter types',()=>barOption(data.filters,{color:'#f2b35c'}));
  statsPanel(grid,'Effects used (per FX slot)',()=>barOption(data.fx,{color:'#c792ea'}));
  statsPanel(grid,'Top modulation sources',()=>barOption(data.sources,{horizontal:true,color:'#59e4bc'}));
  statsPanel(grid,'Mod routes per preset',()=>barOption(data.route_hist,{color:'#9ce2ef'}));
  const heat=data.heatmap;
  statsPanel(grid,'Source → destination heatmap (top 12 each)',()=>({tooltip:{position:'top',formatter:p=>`${heat.sources[p.value[1]]} → ${heat.destinations[p.value[0]]}: ${p.value[2]}`},
    grid:{left:150,right:40,top:10,bottom:110,containLabel:true},
    xAxis:{type:'category',data:heat.destinations,axisLabel:{rotate:35,interval:0}},
    yAxis:{type:'category',data:heat.sources},
    visualMap:{min:0,max:Math.max(1,...heat.cells.map(c=>c[2])),calculable:true,orient:'horizontal',left:'center',bottom:0,inRange:{color:['#101820','#59e4bc']}},
    series:[{type:'heatmap',data:heat.cells,label:{show:false}}]}));
  statsPanel(grid,'Category → engine → filter flow',()=>({tooltip:{trigger:'item'},
    series:[{type:'sankey',emphasis:{focus:'adjacency'},nodeAlign:'left',lineStyle:{color:'gradient',curveness:0.5},
      data:data.sankey.nodes.map(name=>({name})),links:data.sankey.links.map(([source,target,value])=>({source,target,value}))}]}));
  statsPanel(grid,'Presets by file date (stacked by category)',()=>({tooltip:{trigger:'axis'},legend:{bottom:0,type:'scroll',textStyle:{color:'#c9d6dc'}},
    grid:{left:40,right:16,top:16,bottom:70},xAxis:{type:'category',data:data.monthly.months},yAxis:{type:'value'},
    series:Object.entries(data.monthly.series).map(([name,values])=>({name,type:'bar',stack:'m',emphasis:{focus:'series'},data:values}))}));
  if(data.calendar.length) {
    const days=data.calendar.map(d=>d[0]).sort();
    statsPanel(grid,'Activity calendar (file dates)',()=>({tooltip:{formatter:p=>`${p.value[0]}: ${p.value[1]} preset(s)`},
      visualMap:{min:0,max:Math.max(...data.calendar.map(d=>d[1])),orient:'horizontal',left:'center',bottom:0,inRange:{color:['#101820','#59e4bc']}},
      calendar:{top:30,left:30,right:30,cellSize:['auto',13],range:[days[0].slice(0,7),days[days.length-1].slice(0,7)],itemStyle:{borderWidth:0.5},yearLabel:{show:true}},
      series:[{type:'heatmap',coordinateSystem:'calendar',data:data.calendar}]}));
  }
  statsPanel(grid,'Tags',()=>barOption(data.tags,{horizontal:true,color:'#f2b35c'}));
  statsPanel(grid,'Authors',()=>barOption(data.authors,{horizontal:true,color:'#c792ea'}));
  if(data.unison.length) statsPanel(grid,'Unison voices (where stored)',()=>barOption(data.unison.map(([k,v])=>[`${k} voices`,v]),{color:'#9ce2ef'}));
}

async function loadStats() {
  await run(async()=>{
    status('Scanning library…');
    const data=await pywebview.api.library_stats();
    if(data.error)throw Error(data.error);
    renderStats(data);status(`Stats for ${data.count} preset(s).`);
  });
}

function drawStats() {
  if(!$('stats-page').childElementCount)loadStats();
}

window.addEventListener('resize',()=>charts.forEach(c=>c.resize()));
