/* Shared subdivisions, file fields, tooltips, and accessible numeric controls. */
function element(tag,classes='',text='') {
  const node=document.createElement(tag); node.className=classes; node.textContent=text; return node;
}
function tooltip(node,text) { node.dataset.tooltip=text; return node; }
const tip=element('div','tooltip'); tip.id='tooltip'; tip.role='tooltip'; tip.hidden=true; document.body.append(tip);
function showTip(event) {
  const node=event.target.closest('[data-tooltip]');
  tip.hidden=!node||!node.dataset.tooltip;
  if(tip.hidden) return;
  tip.textContent=node.dataset.tooltip; node.setAttribute('aria-describedby','tooltip');
  const rect=node.getBoundingClientRect();
  tip.style.left=Math.max(8,Math.min(rect.left,innerWidth-280))+'px';
  tip.style.top=Math.min(rect.bottom+7,innerHeight-65)+'px';
}
document.addEventListener('mouseover',showTip); document.addEventListener('focusin',showTip);
document.addEventListener('mouseout',()=>tip.hidden=true); document.addEventListener('focusout',()=>tip.hidden=true);

function subdivide(parent,options,activate,classes='choices') {
  const group=element('div',classes);
  for(const [key,label,help=''] of options) {
    const button=tooltip(element('button','choice',label),help); button.type='button'; button.dataset.action=key;
    button.onclick=()=>activate(key); group.append(button);
  }
  parent.append(group); return group;
}

function pathRow(id,label,kind,changed) {
  const row=element('div','path'),input=element('input'); input.id=id; input.placeholder=label; input.setAttribute('aria-label',label);
  const browse=element('button','','Browse'); browse.type='button';
  browse.onclick=()=>run(async()=>{const path=await pywebview.api.browse(typeof kind==='function'?kind():kind); if(path) {input.value=path;input.dispatchEvent(new Event('input')); if(changed) await changed(path);}});
  const reveal=tooltip(element('button','reveal-path'),`Show ${label.toLowerCase()} in the file manager.`);
  reveal.type='button'; reveal.setAttribute('aria-label',`Show ${label.toLowerCase()} in the file manager`);
  reveal.innerHTML='<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M1.5 3.5h5l1.5 1.7h6.5v7.3h-13z"/></svg>';
  reveal.onclick=()=>run(async()=>{const result=await pywebview.api.reveal(input.value);if(result.error)throw Error(result.error);});
  input.onkeydown=e=>{if(e.key==='Enter'&&changed) run(()=>changed(input.value));};
  const text=element('label','',label); text.htmlFor=id; row.append(text,input,browse,reveal); return row;
}

function knob(label,value,change,help='') {
  const wrapper=tooltip(element('div','amount'),help),dial=element('div','dial'),needle=element('i','needle'),readout=element('span');
  dial.tabIndex=0; dial.role='slider'; dial.setAttribute('aria-label',label); dial.setAttribute('aria-valuemin',0); dial.setAttribute('aria-valuemax',100); dial.append(needle);
  const set=n=>{value=Math.max(0,Math.min(100,Math.round(n))); dial.setAttribute('aria-valuenow',value); needle.style.transform=`rotate(${value*2.7-135}deg)`; readout.textContent=value+'%'; change(value);};
  dial.onkeydown=e=>{if(['ArrowUp','ArrowRight','ArrowDown','ArrowLeft','Home','End'].includes(e.key)) {e.preventDefault();set(e.key==='Home'?0:e.key==='End'?100:value+(['ArrowUp','ArrowRight'].includes(e.key)?1:-1));}};
  dial.onwheel=e=>{e.preventDefault();if(!state.busy)set(value+(e.deltaY<0?1:-1));};
  dial.onpointerdown=e=>{if(state.busy)return; const start=e.clientY,initial=value; dial.setPointerCapture(e.pointerId);dial.onpointermove=move=>set(initial+(start-move.clientY)/2);dial.onpointerup=dial.onpointercancel=()=>dial.onpointermove=null;};
  wrapper.append(element('span','',label),dial,readout); set(value); return wrapper;
}

function field(label,type,value,change,help='') {
  const wrapper=tooltip(element('label','setting'),help),input=element('input'); input.type=type;
  if(type==='checkbox') input.checked=value; else input.value=value;
  input.oninput=()=>change(type==='checkbox'?input.checked:input.value);
  wrapper.append(element('span','',label),input); return wrapper;
}
