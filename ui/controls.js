/* Mode navigation and settings; shared controls also populate the measured header. */
function drawNavigation() {
  $('modes').replaceChildren();
  const group=subdivide($('modes'),[
    ['generate','Generate','Build from Init or a chosen base preset, using library donors or one specific preset.'],
    ['mutate','Mutate','Vary selected modules in a source preset.'],
    ['stats','▦ Stats','Charts and quick-glance insights for your library.'],
    ['settings','⚙ Settings','Set your Serum preset library directory.'],
  ],chooseMode,'mode-options');
  const generate=group.children[0]; generate.id='generate-mode'; generate.setAttribute('aria-disabled',String(!state.ready));
  group.children[3].classList.add('settings-mode');
  [...group.children].forEach(b=>b.classList.toggle('selected',b.dataset.action===state.mode));
}

function chooseMode(mode) {
  if(state.busy||mode==='generate'&&!state.ready)return;
  state.mode=mode;
  state.modules=mode==='generate'?generationModules(state.baseModules):new Set(state.sourceModules);
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
  } else {
    const base=pathRow('base-path','Base preset (blank = Init)','input',selectBase);
    $('io').append(base);$('base-path').value=state.gen.basePath;
    $('io').append(element('p','library-note','Or drop a .SerumPreset in Generate mode to use it as the base.'));
    const useInit=element('button','','Use Init as base');useInit.type='button';
    useInit.onclick=()=>run(async()=>{await selectBase('');$('base-path').value='';});
    $('io').append(useInit);
    if(state.gen.donorSource==='preset') {
      const donor=pathRow('donor-path','Specific donor preset','input',path=>{state.gen.donorPath=path.trim();refresh();});
      $('io').append(donor);$('donor-path').value=state.gen.donorPath;
      $('donor-path').oninput=()=>{state.gen.donorPath=$('donor-path').value.trim();refresh();};
    } else {
      $('io').append(tooltip(element('p','library-note',state.settings.library||'Set a library in Settings to use library donors.'),
        'Library donors require a valid preset library configured in Settings.'));
    }
  }
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
  $('settings-page').append(element('h2','','Default output directory'));
  const output=pathRow('output-directory','Output directory','directory');$('settings-page').append(output);
  $('output-directory').value=state.settings.output_directory||'';
  const saveOutput=element('button','','Save output directory');saveOutput.id='save-output-directory';
  saveOutput.onclick=()=>run(async()=>{
    const result=await pywebview.api.output_directory($('output-directory').value.trim());
    if(result.error)throw Error(result.error);
    state.settings=result;state.gen.output=result.output_directory||'preset-generations';
    if(state.loaded&&result.output_directory) {
      const filename=state.output.split(/[\\/]/).pop();
      const separator=result.output_directory.includes('\\')?'\\':'/';
      state.output=result.output_directory.replace(/[\\/]+$/,'')+separator+filename;
    }
    if(state.mode==='generate')$('output').value=state.gen.output;
    else if(state.mode==='mutate'&&state.loaded)$('output').value=state.output;
    status(`Default output directory saved · ${result.output_directory}`);
  });
  $('settings-page').append(saveOutput);
  $('settings-page').append(element('h2','','Generated preset safety limiter'));
  const limiter=field('Append safety limiter','checkbox',state.settings.safety_limiter,enabled=>enabled,
    'Append the standard digital limiter after the existing effects in FXRack0 for each generated preset.');
  limiter.querySelector('input').onchange=()=>run(async()=>{
    const input=limiter.querySelector('input');
    const result=await pywebview.api.safety_limiter(input.checked);
    if(result.error){input.checked=state.settings.safety_limiter;throw Error(result.error);}
    state.settings=result;status(`Safety limiter ${result.safety_limiter?'enabled':'disabled'} for generated presets.`);
  });
  $('settings-page').append(limiter);
}

function makeControls(d) {d.classList.add('controls');d.id='header-controls';d.replaceChildren();fillHeader(d);}
function drawHeader() {if($('header-controls'))fillHeader($('header-controls'));}
function fillHeader(d) {
  d.replaceChildren();
  const generating=state.mode==='generate';
  d.append(knob('Mutation',generating?state.gen.mutation:state.amount,n=>{if(generating)state.gen.mutation=n;else state.amount=n;refresh();},'Vary stored floats by ± the selected percentage.'));
  if(!generating) {d.append(element('span','hint','Hover a module to choose Keep or Mutate.'));return;}
  const profile=tooltip(element('label','setting profile-setting'),
    'Apply a starting module selection, then fine-tune individual modules. Modulators replaces available envelopes and LFOs; Velocity and Note are not separate replaceable modules.');
  const profileSelect=element('select');profileSelect.id='generation-profile';
  const activeProfile=activeGenerationProfile();
  const customOption=new Option('Custom','custom',false,activeProfile==='custom');customOption.disabled=true;
  profileSelect.add(customOption);
  for(const item of GENERATION_PROFILES)profileSelect.add(new Option(item.label,item.id,false,activeProfile===item.id));
  profileSelect.setAttribute('aria-label','Generation profile');
  profileSelect.onchange=()=>applyGenerationProfile(profileSelect.value);
  profile.append(element('span','','Profile'),profileSelect);d.append(profile);
  const donor=element('label','setting'),source=element('select');source.id='donor-source';
  source.add(new Option('Library','library'));source.add(new Option('Specific preset','preset'));
  source.value=state.gen.donorSource;
  source.onchange=()=>{state.gen.donorSource=source.value;drawSidebar();drawHeader();refresh();};
  donor.append(element('span','','Donors'),source);d.append(donor);
  if(state.gen.donorSource==='preset') {
    d.append(tooltip(element('span','hint','One donor'),'Selected modules come from the specific preset in the sidebar.'));
  } else {
    d.append(knob('Interpolation',state.gen.interpolation,n=>state.gen.interpolation=n,'Move compatible values toward sibling donors; 100% reaches their midpoint.'));
    const family=element('label','setting'),select=element('select');select.id='family';
    select.add(new Option('Mixed','random'));
    for(const name of state.families)select.add(new Option(name[0].toUpperCase()+name.slice(1),name));
    select.value=state.gen.family;
    // 'random' draws donors from the whole library; any other family filters donors by filename.
    select.onchange=()=>{state.gen.family=select.value;state.gen.mode=select.value==='random'?'random':'smart';drawHeader();refresh();};
    family.append(element('span','','Family'),select);d.append(family);
  }
  const count=field('Count','number',state.gen.count,n=>state.gen.count=Number(n),'Number of presets to generate.');count.querySelector('input').min=1;count.querySelector('input').step=1;d.append(count);
  const seed=field('Seed','number',state.gen.seed??'',n=>state.gen.seed=n===''?null:Number(n),'Optional seed for repeatable generation.');seed.querySelector('input').step=1;d.append(seed);
  d.append(field('Dry run','checkbox',state.gen.dry_run,n=>{state.gen.dry_run=n;refresh();},'Show the generation report without writing files.'));
}
