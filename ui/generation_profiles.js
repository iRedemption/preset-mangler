const GENERATION_PROFILES = [
  {
    id: 'default',
    label: 'Default',
    baseKeys: ['Oscillator0', 'Env0', 'LFO0', 'VoiceFilter0'],
    initPrefixes: ['Macro'],
    action: 'modulations',
  },
  {
    id: 'modulators',
    label: 'Modulators',
    basePrefixes: ['Env', 'LFO'],
    action: 'generate',
  },
  {
    id: 'osc-b-c-noise',
    label: 'OSC B + C + Noise',
    baseKeys: ['Oscillator1', 'Oscillator2', 'Oscillator3'],
    action: 'generate',
  },
  {
    id: 'fx',
    label: 'FX only',
    basePrefixes: ['FXRack'],
    action: 'generate',
  },
  {
    id: 'filters-fx',
    label: 'Filters + FX',
    basePrefixes: ['VoiceFilter', 'FXRack'],
    action: 'generate',
  },
  {
    id: 'macros',
    label: 'Macros only',
    initPrefixes: ['Macro'],
    action: 'generate',
  },
];
