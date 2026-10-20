/* Mode navigation and settings; shared controls also populate the measured header. */
function drawNavigation() {
  $('modes').replaceChildren();
  const group=subdivide($('modes'),[
    ['generate','Generate',state.settings.valid?'Generate new presets from a library directory.':'Set your Serum preset library in Settings first.'],
    ['mutate','Mutate','Vary selected modules in a source preset.'],
    ['stats','▦ Stats','Charts and quick-glance insights for your library.'],
    ['settings','⚙ Settings','Set your Serum preset library directory.'],
  ],chooseMode,'mode-options');
  const generate=group.children[0]; generate.id='generate-mode'; generate.setAttribute('aria-disabled',String(!state.settings.valid));
  group.children[3].classList.add('settings-mode');
  [...group.children].forEach(b=>b.classList.toggle('selected',b.dataset.action===state.mode));
}

function chooseMode(mode) {
  if(state.busy||mode==='generate'&&!state.settings.valid)return;
  state.mode=mode;
  state.modules=mode==='generate'?new Set(state.baseModules):new Set(state.sourceModules);
  $('settings-page').hidden=mode!=='settings';
  $('stats-page').hidden=mode!=='stats';
  $('empty').hidden=['settings','stats','generate'].includes(mode)||mode==='mutate'&&state.loaded;
  $('stage').hidden=!$('empty').hidden||['settings','stats'].includes(mode);
  if(mode==='mutate'&&!state.loaded) {
    $('empty').replaceChildren(element('div','drop-icon','⇩'),element('h1','','Drop a source preset'),element('p','','Drop a .SerumPreset here or click to browse.'));
    const browse=element('button','','Browse preset'); browse.onclick=()=>run(async()=>{const path=await pywebview.api.browse('input');if(path)await load(path);}); $('empty').append(browse);
  }
  drawNavigation();drawSidebar();if(!['settings','stats'].includes(mode))drawLayout();
  if(mode==='stats')drawStats();
  refresh();fit();
}

function drawSidebar() {
  $('io').replaceChildren();
  if(!['mutate','generate'].includes(state.mode))return;
  if(state.mode==='mutate') {
    const row=pathRow('input','Source preset','input',load);$('io').append(row); $('input').value=state.input;
    $('input').oninput=()=>{state.input=$('input').value;state.loaded=false;};
  } else $('io').append(tooltip(element('p','library-note',state.settings.library),'Library directory from Settings.'));
  const output=pathRow('output',state.mode==='generate'?'Output directory':'Output preset',()=>state.mode==='generate'?'directory':'output');
  $('io').append(output); $('output').value=state.mode==='generate'?state.gen.output:state.output;
  $('output').oninput=()=>{if(state.mode==='generate')state.gen.output=$('output').value;else state.output=$('output').value;};
  const save=element('button','','');save.id='export';save.onclick=()=>run(exportPreset);$('io').append(save);
}

function drawSettings() {
  $('settings-page').replaceChildren(element('h1','','Settings'),element('p','','Serum 2 preset library'));
  const row=pathRow('library','Library directory','library');$('settings-page').append(row); $('library').value=state.settings.library;
  const save=element('button','','Save library');save.id='save-library';save.onclick=()=>run(async()=>{
    const result=await pywebview.api.settings($('library').value.trim());if(result.error)throw Error(result.error);
    state.settings=result;drawNavigation();status(`Library saved · ${result.count} presets. Generate is ready.`);
  });
  $('settings-page').append(element('p','hint','Choose a folder containing .SerumPreset files. Subfolders are not scanned.'),save);
}

function makeControls(d) {d.classList.add('controls');d.id='header-controls';d.replaceChildren();fillHeader(d);}
function drawHeader() {if($('header-controls'))fillHeader($('header-controls'));}
function fillHeader(d) {
  d.replaceChildren();
  const generating=state.mode==='generate';
  d.append(knob('Mutation',generating?state.gen.mutation:state.amount,n=>{if(generating)state.gen.mutation=n;else state.amount=n;refresh();},'Vary stored floats by ± the selected percentage.'));
  if(!generating) {d.append(element('span','hint','Hover a module to choose Keep or Mutate.'));return;}
  d.append(knob('Interpolation',state.gen.interpolation,n=>state.gen.interpolation=n,'Move compatible values toward sibling donors; 100% reaches their midpoint.'));
  const family=element('label','setting'),select=element('select');select.id='family';
  select.add(new Option('Mixed','random'));
  for(const name of state.families)select.add(new Option(name[0].toUpperCase()+name.slice(1),name));
  select.value=state.gen.family;
  // 'random' draws donors from the whole library; any other family filters donors by filename.
  select.onchange=()=>{state.gen.family=select.value;state.gen.mode=select.value==='random'?'random':'smart';drawHeader();refresh();};
  family.append(element('span','','Family'),select);d.append(family);
  const count=field('Count','number',state.gen.count,n=>state.gen.count=Number(n),'Number of presets to generate.');count.querySelector('input').min=1;count.querySelector('input').step=1;d.append(count);
  const seed=field('Seed','number',state.gen.seed??'',n=>state.gen.seed=n===''?null:Number(n),'Optional seed for repeatable generation.');seed.querySelector('input').step=1;d.append(seed);
  d.append(field('Dry run','checkbox',state.gen.dry_run,n=>{state.gen.dry_run=n;refresh();},'Show the generation report without writing files.'));
}
