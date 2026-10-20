"""Run the actual desktop renderer hidden and check bridge/layout interactions."""

from pathlib import Path
import base64
import json
import shutil
import sys
import tempfile
import time
import traceback

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import webview
from ui.assets import application
from ui.bridge import Bridge
from backend.preset import load_preset
import backend.settings as settings

root = Path(__file__).resolve().parents[1]
if not (root / "testing/presets-for-tests").is_dir():
    root = root.parent / "serum-preset-mutator"
source = root / "testing/presets-for-tests/interpolationA.SerumPreset"
temporary = tempfile.TemporaryDirectory()
settings.CONFIG = Path(temporary.name) / "settings.json"
library = Path(temporary.name) / "library"
library.mkdir()
shutil.copyfile(source, library / "BS - Test.SerumPreset")
api = Bridge()
window = api._window = webview.create_window("Preset Mangler smoke check", application(), js_api=api, hidden=True)
failures = []


def check():
    try:
        window.events.loaded.wait(15)
        for _ in range(100):
            if window.evaluate_js("state.ready && !state.busy"):
                break
            time.sleep(.1)
        else:
            raise AssertionError(window.evaluate_js("$('status').textContent"))
        assert window.evaluate_js("$('stage').hidden && document.querySelectorAll('#modes .mode-options>.choice').length===4")
        assert window.evaluate_js("state.settings.safety_limiter===true")
        assert window.evaluate_js("$('generate-mode').getAttribute('aria-disabled')==='false';")
        assert window.evaluate_js("chooseMode('generate'); state.mode==='generate'")
        assert window.evaluate_js("chooseMode('mutate'); $('stage').hidden && !$('empty').hidden && !!document.querySelector('.drop-icon')")
        window.evaluate_js("run(()=>load(" + json.dumps(str(source)) + "))")
        for _ in range(100):
            if window.evaluate_js("state.loaded && !state.busy && $('under').complete && $('under').naturalWidth>0"):
                break
            time.sleep(.1)
        assert window.evaluate_js("$('stage').offsetWidth===1190 && $('stage').offsetHeight===740")
        assert window.evaluate_js("getComputedStyle($('under')).opacity === '0.5'")
        assert window.evaluate_js("state.mutated.size===0 && document.querySelector('[data-module=lfo] select').options.length===10")
        assert window.evaluate_js("document.querySelector('[data-module=Oscillator0] [data-action=Mutate]').click(); state.mutated.has('Oscillator0')")
        assert window.evaluate_js("S.main='fx'; drawTop(); S.fx=1; drawTop(); document.querySelector('[data-module=fx] [data-action=Mutate]').click(); state.mutated.has('FXRack1')")
        for _ in range(50):
            if window.evaluate_js("$('under').complete && $('under').naturalWidth>0"):
                break
            time.sleep(.1)
        assert window.evaluate_js("$('under').naturalWidth>0 && $('under').src.endsWith('serum2ui_FX.png')")
        assert window.evaluate_js("S.main='osc'; drawTop(); state.mutated.has('Oscillator0') && state.mutated.has('FXRack1')")
        assert window.evaluate_js("$('reset').click(); state.mutated.size===0")
        encoded = base64.b64encode(source.read_bytes()).decode()
        window.evaluate_js('const transfer=new DataTransfer(); transfer.items.add(new File([Uint8Array.from(atob('
                           + json.dumps(encoded) + '),c=>c.charCodeAt(0))],"Dropped.SerumPreset")); '
                           'document.dispatchEvent(new DragEvent("drop",{dataTransfer:transfer}));')
        for _ in range(100):
            if window.evaluate_js("!state.busy && $('input').value==='Dropped.SerumPreset'"):
                break
            time.sleep(.1)
        assert window.evaluate_js("$('input').value==='Dropped.SerumPreset' && state.mutated.size===0")
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "Smoke.SerumPreset"
            window.evaluate_js("document.querySelector('[data-module=Oscillator0] [data-action=Mutate]').click(); "
                               "$('output').value=" + json.dumps(str(destination)) + "; $('export').click();")
            for _ in range(100):
                if window.evaluate_js("!state.busy && $('report').open"):
                    break
                time.sleep(.1)
            assert destination.exists(), window.evaluate_js("$('status').textContent")
            output, original = load_preset(destination), load_preset(source)
            assert output["data"]["Oscillator0"] != original["data"]["Oscillator0"]
            assert all(output["data"][k] == v for k, v in original["data"].items() if k != "Oscillator0")
        window.evaluate_js("$('report').close(); chooseMode('settings');")
        assert window.evaluate_js("$('stage').hidden && !$('settings-page').hidden")
        window.evaluate_js("$('library').value=" + json.dumps(str(library)) + "; $('save-library').click();")
        for _ in range(100):
            if window.evaluate_js("!state.busy && state.settings.valid"):
                break
            time.sleep(.1)
        assert window.evaluate_js("$('generate-mode').getAttribute('aria-disabled')==='false'")
        window.evaluate_js("document.querySelector('#settings-page input[type=checkbox]').click();")
        for _ in range(100):
            if not window.evaluate_js("state.busy"):
                break
            time.sleep(.1)
        assert window.evaluate_js("state.settings.safety_limiter===false")
        window.evaluate_js("document.querySelector('#settings-page input[type=checkbox]').click();")
        for _ in range(100):
            if not window.evaluate_js("state.busy"):
                break
            time.sleep(.1)
        assert window.evaluate_js("state.settings.safety_limiter===true")
        default_output = Path(temporary.name) / "default-output"
        default_output.mkdir()
        window.evaluate_js("$('output-directory').value=" + json.dumps(str(default_output)) +
                           "; $('save-output-directory').click();")
        for _ in range(100):
            if not window.evaluate_js("state.busy"):
                break
            time.sleep(.1)
        assert window.evaluate_js("state.settings.output_directory===" + json.dumps(str(default_output.resolve())) +
                                  " && state.gen.output===" + json.dumps(str(default_output.resolve())))
        assert window.evaluate_js("chooseMode('generate'); ! $('stage').hidden && state.generated.size===12")
        assert window.evaluate_js("['base-path','output'].every(id=>{const row=$(id).parentElement;const button=row.querySelector('.reveal-path');return button&&button.getAttribute('aria-label')&&button.querySelector('svg')})")
        assert window.evaluate_js("['Oscillator0','Env0','LFO0','VoiceFilter0','Macro7'].every(k=>state.generated.get(k)==='modulations')")
        assert window.evaluate_js("document.querySelector('[data-module=Oscillator1] [data-action=generate]').click(); state.generated.get('Oscillator1')==='generate'")
        assert window.evaluate_js("$('family').value='bass'; $('family').dispatchEvent(new Event('change')); state.gen.mode==='smart' && state.gen.family==='bass' && !$('family').disabled")
        assert window.evaluate_js("$('family').value='random'; $('family').dispatchEvent(new Event('change')); state.gen.mode==='random'")
        target = Path(temporary.name) / "generated"
        window.evaluate_js("$('output').value=" + json.dumps(str(target)) + "; $('export').click();")
        for _ in range(100):
            if window.evaluate_js("!state.busy && $('report').open"):
                break
            time.sleep(.1)
        generated = target / "generated_random_001.SerumPreset"
        assert generated.exists(), window.evaluate_js("$('status').textContent")
        generated_preset = load_preset(generated)
        assert generated_preset['data']['Oscillator1'] == original['data']['Oscillator1']
        base = load_preset(settings.ASSETS / "Init.SerumPreset")
        assert generated_preset['data']['Oscillator2'] == base['data']['Oscillator2']
        limiter = load_preset(settings.ASSETS / "Init_Safety_Limiter.SerumPreset")['data']['FXRack0']['FX'][0]
        assert generated_preset['data']['FXRack0']['FX'] == [limiter]
        custom_base_path = root / "testing/presets-for-tests/Init_mod_cutoff.SerumPreset"
        custom_base = load_preset(custom_base_path)
        window.evaluate_js("$('report').close(); state.gen.donorSource='preset'; drawSidebar(); drawHeader(); "
                           "$('donor-path').value=" + json.dumps(str(source)) + "; "
                           "$('donor-path').dispatchEvent(new Event('input'));")
        expected_base = str(custom_base_path.resolve())
        window.evaluate_js("$('base-path').value=" + json.dumps(str(custom_base_path)) + ";")
        window.evaluate_js("run(()=>selectBase(" + json.dumps(str(custom_base_path)) + "))")
        for _ in range(100):
            if window.evaluate_js("!state.busy && state.gen.basePath===" + json.dumps(expected_base)):
                break
            time.sleep(.1)
        assert window.evaluate_js("state.gen.basePath===" + json.dumps(expected_base) +
                                  " && state.generated.size===0 && state.baseModules.length>0 && "
                                  "document.querySelector('[data-module=Oscillator1] [data-action=generate]').textContent==='Replace'")
        custom_target = Path(temporary.name) / "custom-generated"
        window.evaluate_js("$('output').value=" + json.dumps(str(custom_target)) + "; "
                           "document.querySelector('[data-module=Oscillator1] [data-action=generate]').click(); $('export').click();")
        for _ in range(100):
            if window.evaluate_js("!state.busy && $('report').open"):
                break
            time.sleep(.1)
        custom_output_path = custom_target / "generated_custom_001.SerumPreset"
        assert custom_output_path.exists(), window.evaluate_js(
            "JSON.stringify({status:$('status').textContent, donor:state.gen.donorPath, base:state.gen.basePath, "
            "selected:Object.fromEntries(state.generated), busy:state.busy})")
        custom_output = load_preset(custom_output_path)
        donor = load_preset(source)
        assert custom_output['data']['Oscillator1'] == donor['data']['Oscillator1']
        assert all(custom_output['data'][key] == value for key, value in custom_base['data'].items()
                   if key not in ('Oscillator1', 'FXRack0'))
        assert custom_output['data']['FXRack0']['FX'] == custom_base['data']['FXRack0']['FX'] + [limiter]
        assert window.evaluate_js("$('report').querySelector('pre').textContent.includes('Base: Init_mod_cutoff.SerumPreset') && "
                                  "$('report').querySelector('pre').textContent.includes('interpolationA.SerumPreset')")
        dropped_base = base64.b64encode(custom_base_path.read_bytes()).decode()
        window.evaluate_js("$('report').close(); run(()=>selectBase(''));")
        for _ in range(100):
            if window.evaluate_js("!state.busy && state.gen.basePath===''"):
                break
            time.sleep(.1)
        window.evaluate_js('const baseTransfer=new DataTransfer(); baseTransfer.items.add(new File([Uint8Array.from(atob('
                           + json.dumps(dropped_base) + '),c=>c.charCodeAt(0))],"DroppedBase.SerumPreset")); '
                           'document.dispatchEvent(new DragEvent("drop",{dataTransfer:baseTransfer}));')
        for _ in range(100):
            if window.evaluate_js("!state.busy && state.gen.baseToken"):
                break
            time.sleep(.1)
        assert window.evaluate_js("state.gen.baseName==='DroppedBase.SerumPreset' && "
                                  "$('base-path').value==='DroppedBase.SerumPreset' && state.generated.size===0")
        dropped_target = Path(temporary.name) / "dropped-base-generated"
        window.evaluate_js("$('output').value=" + json.dumps(str(dropped_target)) + "; "
                           "document.querySelector('[data-module=Oscillator1] [data-action=generate]').click(); $('export').click();")
        for _ in range(100):
            if window.evaluate_js("!state.busy && $('report').open"):
                break
            time.sleep(.1)
        dropped_output = load_preset(dropped_target / "generated_custom_001.SerumPreset")
        assert dropped_output['data']['Oscillator2'] == custom_base['data']['Oscillator2']
        assert window.evaluate_js("$('report').querySelector('pre').textContent.includes('Base: DroppedBase.SerumPreset')")
        assert window.evaluate_js("$('report').close(); chooseMode('mutate'); ! $('stage').hidden && state.amount===30 && state.mutated.has('Oscillator0')")
        window.evaluate_js("$('report').close(); chooseMode('stats');")
        for _ in range(100):
            if window.evaluate_js("document.querySelectorAll('#stats-page .chart-box').length>=10"):
                break
            time.sleep(.1)
        assert window.evaluate_js("!$('stats-page').hidden && document.querySelectorAll('#stats-page .chart-box').length>=10 && document.querySelectorAll('#stats-page .stat-card').length>=4"), window.evaluate_js("$('status').textContent")
        assert window.evaluate_js("chooseMode('mutate'); $('stats-page').hidden")
        print("PASS: mode access, mutation drop/export, library settings, Init/custom-base generation, dropped-base generation, specific donors, preservation and mode switching.")
    except Exception:
        failures.append(traceback.format_exc())
    finally:
        window.destroy()


webview.start(check)
temporary.cleanup()
if failures:
    raise SystemExit("UI smoke check failed: " + "; ".join(failures))
