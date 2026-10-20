const state={mode:null,ready:false,modules:new Set(),baseModules:[],sourceModules:[],mutated:new Set(),generated:new Map(),
  amount:30,busy:false,loaded:false,input:'',output:'',settings:{library:'',valid:false},families:[],
  gen:{mode:'random',family:'random',count:1,mutation:0,interpolation:0,seed:null,dry_run:false,output:'preset-generations'}};
const families={env:['Env','Envelope'],lfo:['LFO','LFO'],filter:['VoiceFilter','Filter'],fx:['FXRack','FX rack']};
const selectedKey=key=>families[key]?families[key][0]+S[key]:key;
const status=message=>$('status').textContent=message;

function makeModule(d,label,key) {
  d.classList.add('module');d.dataset.module=key;d.replaceChildren();
  const caption=element('span','caption');d.append(caption);
  if(families[key]&&key!=='fx') {
    d.classList.add('has-selector');const select=element('select');select.setAttribute('aria-label',label);
    for(const name of [...state.modules].filter(n=>n.startsWith(families[key][0])).sort((a,b)=>Number(a.match(/\d+$/)[0])-Number(b.match(/\d+$/)[0]))) {
      const index=Number(name.match(/\d+$/)[0]);select.add(new Option(families[key][1]+' '+(index+1),index));
    }
    select.value=S[key];select.onchange=()=>{S[key]=Number(select.value);refresh();};d.append(select);
  }
  const generating=state.mode==='generate';
  const options=generating?[
    ['generate','Generate','Copy this module only. Click again to keep Init.'],
    ['modulations','Generate (+ Any Modulations)','Copy this module and matching routes. Click again to keep Init.'],
  ]:[['Keep','Keep','Leave this module untouched.'],['Mutate','Mutate','Vary this module’s stored float values.']];
  subdivide(d,options,action=>{
    if(state.busy)return;const name=selectedKey(key);
    if(generating) state.generated.get(name)===action?state.generated.delete(name):state.generated.set(name,action);
    else action==='Mutate'?state.mutated.add(name):state.mutated.delete(name);
    refresh();
  });
  d.update=()=>{
    const name=selectedKey(key),available=state.modules.has(name),action=generating?state.generated.get(name):state.mutated.has(name)?'Mutate':'Keep';
    d.classList.toggle('unavailable',!available);d.classList.toggle('mutate',generating?!!action:action==='Mutate');d.tabIndex=available?0:-1;
    const description=generating?({generate:'Generate',modulations:'Generate + Mods'}[action]||'Keep Init'):action;
    caption.textContent=(families[key]?families[key][1]+' '+(S[key]+1):label)+' · '+(available?description:'not loaded');
    d.querySelectorAll('button').forEach(b=>{b.disabled=!available||state.busy;b.classList.toggle('selected',b.dataset.action===action);});
  };d.update();
}

function drawLayout() {
  $('fixed').replaceChildren();FIXED.forEach(b=>box($('fixed'),b));drawTop();
}

function refresh() {
  document.querySelectorAll('.module').forEach(d=>d.update());
  const generating=state.mode==='generate',active=generating?state.generated.size:state.mutated.size;
  $('summary').textContent=state.mode==='settings'?'Settings':state.mode?
    `${generating?state.gen.mode.toUpperCase():'MUTATE'} · ${active} selected module(s)`:'Choose a mode';
  $('reset').hidden=!['mutate','generate'].includes(state.mode)||!generating&&!state.loaded;
  if($('export')) {$('export').disabled=state.busy;$('export').textContent=generating?(state.gen.dry_run?'Preview generation':'Generate & save'):'Mangle & save';}
  document.querySelectorAll('#io input,#io button,#modes button,#reset,#settings-page button,.module select').forEach(e=>e.disabled=state.busy);
}

async function run(action) {
  if(state.busy)return;state.busy=true;refresh();
  try {await action();}catch(error){status('Error: '+error.message);}
  finally{state.busy=false;refresh();}
}

function applySource(result) {
  if(result.error)throw Error(result.error);
  state.sourceModules=result.modules;state.mutated.clear();state.loaded=true;state.input=result.input;state.output=result.output;
  for(const key of Object.keys(families))S[key]=0;
}
async function load(path,encoded) {
  const result=await pywebview.api.load(path.trim(),encoded);applySource(result);
  state.mode='mutate';state.modules=new Set(state.sourceModules);
  $('empty').hidden=true;$('stage').hidden=false;$('settings-page').hidden=true;
  drawNavigation();drawSidebar();drawLayout();refresh();fit();status('Loaded '+result.input+' · Keep is the default for every module.');
}

async function exportPreset() {
  let result;
  if(state.mode==='generate') {
    state.gen.output=$('output').value;result=await pywebview.api.generate(state.gen.output,Object.fromEntries(state.generated),state.gen);
  } else {
    const destination=$('output').value;
    if(!state.loaded)await load($('input').value);
    if(destination)$('output').value=destination;
    state.output=$('output').value;result=await pywebview.api.export(state.output,[...state.mutated],state.amount);
  }
  if(result.error)throw Error(result.error);
  if(!result.cancelled){status(result.message);$('report').querySelector('pre').textContent=[result.message,...result.report].join('\n');$('report').showModal();}
}

drawNavigation();refresh();fit();
$('reset').onclick=()=>{state.mode==='generate'?state.generated.clear():state.mutated.clear();refresh();};
$('report').querySelector('button').onclick=()=>$('report').close();
document.addEventListener('dragover',e=>{e.preventDefault();if(state.mode==='mutate')document.body.classList.add('dragging');});
document.addEventListener('dragleave',e=>{if(!e.relatedTarget)document.body.classList.remove('dragging');});
document.addEventListener('drop',e=>{
  e.preventDefault();document.body.classList.remove('dragging');if(state.mode!=='mutate')return;
  const files=e.dataTransfer.files;
  if(files.length!==1||!files[0].name.toLowerCase().endsWith('.serumpreset')){status('Drop one .SerumPreset file.');return;}
  run(async()=>{const encoded=await new Promise((resolve,reject)=>{const r=new FileReader();r.onload=()=>resolve(r.result.split(',')[1]);r.onerror=()=>reject(Error('Unable to read dropped file.'));r.readAsDataURL(files[0]);});await load(files[0].name,encoded);});
});
addEventListener('pywebviewready',()=>run(async()=>{
  const result=await pywebview.api.startup();state.settings=result.settings;state.baseModules=result.modules;state.families=result.families;
  if(result.source)applySource(result.source);
  const defaults=['Oscillator0','Env0','LFO0','VoiceFilter0',...state.baseModules.filter(key=>key.startsWith('Macro'))];
  for(const key of defaults)if(state.baseModules.includes(key))state.generated.set(key,'modulations');
  drawNavigation();drawSettings();state.ready=true;
}));
