/* User-supplied inclusive pixel geometry, preserved at 1190 × 740. */
const $ = id => document.getElementById(id);
const S = { main:'osc', fx:0, env:0, lfo:0, filter:0 };
const TABS = ['osc','mix','fx','matrix','global'];
const oscCols = [[76,343],[346,613],[616,883]];
const OSC = [
  ['SUB',2,69,73,386,'module:Oscillator4'], ['NOISE',886,69,983,386,'module:Oscillator3'],
  ['FILTER 1 / 2',986,69,1187,386,'module:filter'],
  ['SUB TITLE',2,69,73,94,'sub'], ['WAVE SELECT',2,95,73,261,'sub'], ['PAN / LEVEL',2,264,73,386,'sub'],
  ['NOISE TITLE',886,69,983,94,'sub'], ['NOISE DISPLAY',886,95,983,261,'sub'], ['FINE PAN PITCH LEVEL',886,264,983,386,'sub'],
  ['FILTER 1',986,69,1085,94,'sub'], ['FILTER 2',1088,69,1187,94,'sub'], ['FILTER RESPONSE',986,95,1187,243,'sub'],
  ['S A B C N',986,244,1187,261,'sub'], ['CUTOFF RES DRIVE FAT',986,264,1099,386,'sub'], ['PAN MIX LEVEL',1101,264,1187,386,'sub'],
  ...oscCols.flatMap(([a,b],i) => { const n='OSC '+'ABC'[i]; return [
    [n,a,69,b,386,'module:Oscillator'+i], [n+' TITLE',a,69,b,94,'sub'], ['WAVETABLE NAME',a,95,b,117,'sub'],
    ['OCT SEM FIN CRS',a,118,b,139,'sub'], ['WAVE DISPLAY',a,140,b,240,'sub'], ['PHASE / RAND',a,241,b,261,'sub'],
    ['WT POS · UNISON · DETUNE · BLEND · WARP',a,264,a+214,386,'sub'], ['PAN / LEVEL',a+216,264,b,386,'sub']]; }),
];
const FX = [
  ['EFFECTS RACK',2,69,1187,386,'module:fx'],
  ['MAIN',30,69,107,94,'tab:fx:0'], ['BUS 1',110,69,186,94,'tab:fx:1'], ['BUS 2',189,69,265,94,'tab:fx:2'],
];
const FIXED = [
  ['PRESET MANGLER',2,2,163,65],
  ...TABS.map((t,i)=>[t.toUpperCase(),166+68*i,2,231+68*i,65,'tab:main:'+t]),
  ['CONTROLS',506,2,1187,65,'controls'],
  ['MACROS',2,393,163,417],
  ...[0,1].flatMap(c=>[0,1,2,3].map(r=>[String(c*4+r+1),c?84:2,[420,478,536,594][r],c?163:81,[475,533,591,649][r],'module:Macro'+(c*4+r)])),
  ['ENVELOPES (1–4)',166,393,515,649,'module:env'], ['LFOs',518,393,1037,649,'module:lfo'],
  ['VELO',1040,393,1112,417], ['NOTE',1115,393,1187,417], ['VELO CURVE',1040,420,1187,560],
  ['VOICING · ALWAYS/SCALED · PORTA/CURVE',1040,562,1187,737,'div:91,120'],
  ['PITCH / MOD WHEELS',2,656,163,737], ['PITCH',14,660,32,734,'sub'], ['BEND RANGE',42,672,88,726,'sub'], ['MOD',104,660,120,734,'sub'],
  ['CLIP',166,656,269,681], ['CLIP KEYS',166,684,269,737,'sub'], ['ARP',280,656,383,681], ['ARP KEYS',280,684,383,737,'sub'],
  ['TRANSPOSE · KEY · SCALE · SWING · OSC MAPPING',394,656,1037,681], ['KEYBOARD',394,684,1037,737],
];

function box(parent,[label,x0,y0,x1,y1,options='']) {
  const d=document.createElement('div'); d.className='box'; d.setAttribute('aria-label',label);
  // Sub-boxes are decorative grid lines; their text is hidden because the background screenshot already shows it.
  if(options.split(' ').includes('sub')) d.classList.add('sub'); else d.textContent=label;
  if(x1-x0<120) d.classList.add('narrow');
  if(y1-y0<80) d.classList.add('compact');
  d.style.cssText=`left:${x0}px;top:${y0}px;width:${x1-x0+1}px;height:${y1-y0+1}px`;
  for(const option of options.split(' ')) {
    if(option==='sub') d.classList.add('sub');
    if(option==='controls') makeControls(d);
    if(option.startsWith('div:')) for(const y of option.slice(4).split(',')) {
      const line=document.createElement('div'); line.className='ln'; line.style.top=(y-1)+'px'; d.append(line);
    }
    if(option.startsWith('module:')) makeModule(d,label,option.slice(7));
    if(option.startsWith('tab:')) {
      const [,group,key]=option.split(':'); d.classList.add('tab'); d.setAttribute('role','button');
      const enabled=group==='fx'||['osc','fx'].includes(key);
      d.classList.toggle('on',String(S[group])===key);
      d.setAttribute('aria-disabled',String(!enabled)); d.tabIndex=enabled?0:-1;
      if(!enabled) { d.style.opacity='.4'; d.style.cursor='default'; }
      const activate=()=>{ if(enabled) { S[group]=group==='fx'?Number(key):key; drawTop(); } };
      d.onclick=activate; d.onkeydown=e=>{ if(['Enter',' '].includes(e.key)) { e.preventDefault(); activate(); } };
    }
  }
  parent.append(d);
}

function drawTop() {
  $('top').replaceChildren(); const view=S.main==='fx'?FX:OSC;
  // Decorative subdivisions sit beneath the interactive whole-module surfaces.
  [...view.filter(b=>b[5]==='sub'),...view.filter(b=>b[5]!=='sub')].forEach(b=>box($('top'),b));
  $('under').src='assets/serum2ui_'+S.main.toUpperCase()+'.png';
  document.querySelectorAll('#fixed .tab').forEach((e,i)=>e.classList.toggle('on',TABS[i]===S.main));
}
const fit=()=>$('stage').style.transform=`translate(-50%,-50%) scale(${Math.min($('workspace').clientWidth/1190,(innerHeight-64)/740)*.98})`;
addEventListener('resize',fit);
