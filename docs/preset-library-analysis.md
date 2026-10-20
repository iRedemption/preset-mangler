# Preset library classification analysis

Analysis snapshot: 2026-10-20

## Scope and method

This is a read-only analysis of the library configured in `settings.json`. It
contains 676 `.SerumPreset` files directly in the configured folder. The scan used the
project's current filename classifier (`patch_families`) and decoded each
preset container to inspect its embedded metadata and module structure. No
preset, settings, or cache files were changed.

The current classifier recognizes five filename families: bass, lead, keys,
arp, and pluck. It reports **326 classified (48.2%)** and **350 unclassified
(51.8%)**. “Unclassified” means that no current filename rule matched; it does
not mean that the preset is unreadable or lacks identifying data.

## Main findings

1. **Most unclassified files have consistent, explicit filename codes.** All
   350 use a prefix followed by ` - `; the largest groups are `PD` (69), `SY`
   (39), and `FX` (34). Many codes map clearly to instrument or sound roles.
2. **The embedded metadata is consistently present, but not consistently
   descriptive.** Every file has the same 11 metadata keys, including author,
   name, description, product/version, and tags. Descriptions are useful in
   many cases, but include blanks, URLs, short notes, and emoji.
3. **Serum tags mostly describe implementation, not musical role.** Tags such
   as `Wavetable`, `Multisample`, `Poly`, and `Mono` are valuable attributes,
   but do not replace categories such as pad, brass, or guitar.
4. **Technical characteristics can enrich classification.** Oscillator
   engines, filter types, FX chains, unison, and modulation records are
   available in the decoded data. These should be reported as attributes, not
   guessed from the preset name.
5. **A single “family” field would mix different concepts.** For example,
   `LOOP` and `SEQ` describe arrangement/behavior, `FX` describes a sound
   effect role, and `BR` describes an instrument family. Keep raw prefix,
   instrument role, and technical/style tags as separate fields.

## Unclassified inventory by filename prefix

Counts below are mutually exclusive groups based on the text before the first
` - `. Names are the exact filenames found during this scan. Suggested meaning
is a candidate mapping, not a claim about every sound in a group.

| Prefix | Count | Candidate meaning | Confidence / handling |
|---|---:|---|---|
| `PD`, `PAD` | 78 | Pad | High |
| `SY`, `SYNTH` | 45 | Synth / general synthesizer | High as a broad role; low specificity |
| `FX` | 34 | Sound effect | High |
| `SERUMFX` | 2 | SerumFX processing preset | High; keep distinct from sound-effect role |
| `SEQ` | 21 | Sequence / sequenced preset | High as a behavior tag, not an instrument family |
| `DR` | 19 | Drums / percussion | High |
| `LOOP` | 16 | Loop / loop-oriented preset | High as a behavior tag |
| `GTR` | 14 | Guitar | High |
| `OR` | 14 | Organ | High |
| `SC` | 13 | Soundscape | Tentative; validate against the source pack's naming key |
| `BR` | 12 | Brass | High |
| `STR` | 12 | Strings | High |
| `EP` | 11 | Electric piano | High |
| `VOX` | 10 | Vocal / voice | High |
| `CH` | 9 | Chord / chordal sound | Provisional; abbreviation could be ambiguous |
| `ORCH` | 8 | Orchestral | High |
| `KIT` | 6 | Kit | High as a kit/collection label; role may vary |
| `MAL` | 6 | Mallet | High |
| `BL` | 5 | Bell | High |
| `WIND` | 4 | Wind instrument | High |
| `INST` | 3 | Instrument (unspecified) | Too broad to add as an instrument family |
| `HIT` | 2 | Hit / one-shot | Provisional |
| `INIT` | 2 | Init/template or multisample source | Do not treat as a sound family |
| `MDL` | 2 | Unknown | Leave unmapped pending pack documentation |
| `HV` | 1 | Unknown | Leave unmapped |
| `PN` | 1 | Piano | High, though the sample is too small to generalize |

The inventory below keeps every prefix separate.

### Mapping recommendation

The strongest immediate candidates for normalized **role** labels are `PD` /
`PAD` → `pad`, `BR` → `brass`, `DR` → `drums`, `GTR` → `guitar`, `OR` →
`organ`, `STR` → `strings`, `EP` → `electric piano`, `VOX` → `vocal`, `BL` →
`bell`, `MAL` → `mallet`, `WIND` → `wind`, `ORCH` → `orchestral`, and `PN` →
`piano`. The `SY` / `SYNTH` mapping is valid but broad.

Represent `SEQ` and `LOOP` as behavior/format labels, not the same kind of
instrument role. Keep `FX` and `SERUMFX` distinguishable. Validate `SC`, `CH`,
`KIT`, and `HIT` before making them automatic categories. Preserve unknown
prefixes rather than silently assigning a fallback role.

These mappings should not automatically be added to the existing generation
family selector: that selector uses family matches to choose donor presets,
whereas this inventory includes roles, behaviors, and processing presets.
Use a separate normalized role/prefix taxonomy unless the donor-selection
behavior is intentionally being expanded.

## Metadata and technical characteristics

### Embedded metadata

- All 676 decoded presets contain the same 11 metadata keys: `fileType`,
  `hash`, `presetAuthor`, `presetDescription`, `presetName`, `product`,
  `productVersion`, `tags`, `url`, `vendor`, and `version`. The container
  consistently identifies the vendor as Xfer Records.
- `presetName` matches the filename stem for **661/676** files. The 15
  mismatches are listed separately below. Prefer the filename as the stable
  filesystem identity; retain the embedded name as a distinct field rather
  than silently replacing one with the other.
- Among the 350 unclassified presets, descriptions break down as **241 with
  nonblank text**, **82 blank/whitespace**, and **27 URL-like**. “Text” is
  only a useful-content candidate: descriptions can be notes, short
  instructions, emojis, or marketing copy. Examples include “Turn Mod Wheel
  For Cinematic Suspense”, “High range double bell”, and “Ring-Mod + FM
  Bells”.
- Authors are populated and useful for provenance and pack/source grouping.
  Across the full library, the most frequent values include Electric Himalaya
  (194), Steve Duda (55), loopsy.store (42), SynthHacker (37), and Level 8
  (28). Author spelling/whitespace normalization should be non-destructive.
- Product metadata identifies **674 Serum2** presets and **2 Serum2FX**
  presets. Product version is also present and can help explain pack or
  serialization differences; it is not a sound category.

### Tags

Tags overlap and counts are occurrences by preset, not mutually exclusive
categories.

| Tag | All 676 | Unclassified 350 |
|---|---:|---:|
| Preview | 616 | 325 |
| Wavetable | 577 | 281 |
| Poly | 455 | 289 |
| Mono | 221 | 61 |
| Multisample | 156 | 105 |
| Sample | 76 | 44 |
| Granular | 56 | 45 |
| Spectral | 48 | 34 |
| Embedded-Data | 37 | 11 |
| Arp | 35 | 10 |
| Clip | 27 | 22 |
| KB-Span | 17 | 12 |
| Custom-Tuning | 3 | 1 |

These are useful implementation/voice characteristics. In particular,
`Preview` is not a musical-role label, and `Wavetable`, `Multisample`,
`Granular`, and `Spectral` may describe oscillator content or available
preview data rather than an exclusive synthesis method.

### Decoded sound structure

For the 350 unclassified presets, the current extractor identifies at least
one oscillator engine of each following type in this many presets (sets can
overlap):

| Engine | Presets |
|---|---:|
| WTOsc | 301 |
| MultiSampleOsc | 107 |
| SampleOsc | 46 |
| GranularOsc | 46 |
| SpectralOsc | 34 |

The extractor sees non-empty FX module data in all **350/350** unclassified
presets.
Frequently occurring filter identifiers include `H18` (27), `LadderEMS`
(24), `MgL24` (19), `H12` (18), and `LadderMg` / `MgL6` (17 each). These are
Serum identifiers; expose them as technical values unless a validated
human-readable mapping is available.

The current stats extractor finds stored modulation-slot records in
**349/350** unclassified presets. This is a count of records with non-empty
`plainParams`, not a verified count of audible/enabled connections. A robust
future “active routes” statistic should validate amount, source, destination,
and enabled/bypass state before labeling a route active. Similarly, an FX
module being stored does not establish that it is audible or enabled.

### Name/metadata discrepancies

These 15 embedded `presetName` values differ from the matching filename stem:

| Filename | Embedded `presetName` |
|---|---|
| `BA - Analog Classics 6.SerumPreset` | `BA - Analog Classics 7` |
| `Bass - Super Freak.SerumPreset` | `BASS - Super Freak` |
| `Bass - Yazoo.SerumPreset` | `- Init - Yazoo` |
| `GTR - 70's Funk Guitar.SerumPreset` | `GT - 70's Funk Guitar` |
| `GTR - Solo Electric Guitar 1.SerumPreset` | `GTR - Solo Electric Guitar 2` |
| `GTR - Solo Electric Guitar 2.SerumPreset` | `GTR - Solo Electric Guitar 3` |
| `Pad - Vangelis 1.SerumPreset` | `Pad - Vagelis 1` |
| `PD - Brass 'n' Plucks.SerumPreset` | `PAD - Brass 'n' Plucks` |
| `PD - Sinessss.SerumPreset` | `PD Sinessss` |
| `PL - Harp Wire.SerumPreset` | `PL - Harp` |
| `Pluck - Eurythmics.SerumPreset` | `Pluck Eurythmics` |
| `Pluck - Ploinky.SerumPreset` | `Pluck - Ploinky (BAD)` |
| `SC - Birds.SerumPreset` | `SC - Birds v2` |
| `SEQ - Funky Acid.SerumPreset` | `BA - Funky Acid` |
| `Synth - Lead Retrospective.SerumPreset` | `Synth - Warm Nostalgia 2` |

These mismatches are also a warning against relying on embedded names as a
classification source without reconciliation.

## Complete list: the 350 currently unclassified presets

The names below are grouped by their filename prefix. Prefix counts are the
same ones used in the inventory table.

### `PD` — 69

```text
PD - 1970s String Machine.SerumPreset
PD - Airy Chant.SerumPreset
PD - Amazon Souls.SerumPreset
PD - Amorphic.SerumPreset
PD - Analog Butter.SerumPreset
PD - Analog Silk Sweep.SerumPreset
PD - Analog Soft Cotton.SerumPreset
PD - Analog Soundtrack.SerumPreset
PD - Analogous.SerumPreset
PD - Artificial.SerumPreset
PD - Astralink.SerumPreset
PD - Bamboo Forest Reflections.SerumPreset
PD - Beach Butterfly.SerumPreset
PD - Belladonna.SerumPreset
PD - Big Analog Pad.SerumPreset
PD - Blessings of Peace.SerumPreset
PD - Bright Laser Pad.SerumPreset
PD - Butterbrot.SerumPreset
PD - Cal's Chimes.SerumPreset
PD - Classic Analog.SerumPreset
PD - Cooked.SerumPreset
PD - Cosmic Aura.SerumPreset
PD - CreepySoundscapePad.SerumPreset
PD - Crushed Chord.SerumPreset
PD - Crystal Strings.SerumPreset
PD - Dark Shuffle Motion.SerumPreset
PD - Dark Space.SerumPreset
PD - Digital Movements.SerumPreset
PD - Distant Desolation.SerumPreset
PD - Early Morning Sunrays .SerumPreset
PD - Emotions.SerumPreset
PD - Ether.SerumPreset
PD - Euphoric.SerumPreset
PD - Gargantua.SerumPreset
PD - Ghost Voices.SerumPreset
PD - Granular Ambience.SerumPreset
PD - Heart Chakra Emotion.SerumPreset
PD - Heaven Grains.SerumPreset
PD - Illuminous.SerumPreset
PD - Interstellar.SerumPreset
PD - Liminal Autumn .SerumPreset
PD - Lost Carrier.SerumPreset
PD - Lush Band-Pass Sweep.SerumPreset
PD - Lush Chorus.SerumPreset
PD - Melancholy Sparkles.SerumPreset
PD - Midnight.SerumPreset
PD - Morning Clouds.SerumPreset
PD - Morphorama.SerumPreset
PD - Motion Tech.SerumPreset
PD - Octavian.SerumPreset
PD - Octopus Underwater PingPong.SerumPreset
PD - Pacific Rain.SerumPreset
PD - Phase Mistress.SerumPreset
PD - Quantize.SerumPreset
PD - Replicant.SerumPreset
PD - Safari.SerumPreset
PD - Score.SerumPreset
PD - Sinessss.SerumPreset
PD - Space Choir.SerumPreset
PD - Space Coin.SerumPreset
PD - String Machine - Serilina.SerumPreset
PD - Synthestra.SerumPreset
PD - Textured Aura.SerumPreset
PD - The Sine.SerumPreset
PD - The Swarm.SerumPreset
PD - Violins + Flute Grains.SerumPreset
PD - Vocaloid.SerumPreset
PD - Voyager.SerumPreset
PD - Warm Room.SerumPreset
```

### `SY` — 39

```text
SY - Action Hero.SerumPreset
SY - Air of Nostalgia.SerumPreset
SY - Analog VCO Poly.SerumPreset
SY - Analog WT Poly.SerumPreset
SY - Butter Smooth Poly.SerumPreset
SY - Capella.SerumPreset
SY - Chronos Purity.SerumPreset
SY - Dotted Flicker.SerumPreset
SY - Dual PWM Poly.SerumPreset
SY - Dual Shyness.SerumPreset
SY - Dubba.SerumPreset
SY - EMS Poly.SerumPreset
SY - Env LPF Seq.SerumPreset
SY - Etherium Plux.SerumPreset
SY - Fire Glow.SerumPreset
SY - Heavy Motion Synth.SerumPreset
SY - Hybrid Synthwave Poly 2.SerumPreset
SY - Hybrid Synthwave Poly.SerumPreset
SY - IDM Chords.SerumPreset
SY - Interesting Sines.SerumPreset
SY - Interrupted Confessions.SerumPreset
SY - Jupiter Duality.SerumPreset
SY - Liquid Square Poly.SerumPreset
SY - Magnetic.SerumPreset
SY - Motion Sync.SerumPreset
SY - Neon Streets Poly.SerumPreset
SY - Nils Type Beat.SerumPreset
SY - Over The Dune.SerumPreset
SY - Plastic Player.SerumPreset
SY - Ring-Modulated Line.SerumPreset
SY - Rolling Plains.SerumPreset
SY - Rubber Echoes.SerumPreset
SY - Salute.SerumPreset
SY - Smooth Dubs.SerumPreset
SY - Tetris.SerumPreset
SY - Tomb Beneath Petra.SerumPreset
SY - TwisteeSaws.SerumPreset
SY - Vibey Jive.SerumPreset
SY - Whispers.SerumPreset
```

### `FX` — 34

```text
FX - Atmospheric Boom.SerumPreset
FX - Bent Mod Launch.SerumPreset
FX - BHouse Glide - 04.SerumPreset
FX - Church.SerumPreset
FX - Creepy CB Radio Chatter.SerumPreset
FX - Demon Woosh.SerumPreset
FX - Didn't Hit Me.SerumPreset
FX - Drop Sweep - Alien.SerumPreset
FX - Drop Sweep - Cyborg.SerumPreset
FX - Drop Sweep - Dual.SerumPreset
FX - Drop Sweep - Linear.SerumPreset
FX - Drop Sweep - Shaker.SerumPreset
FX - Drop Sweep - Square.SerumPreset
FX - Drop Sweep - Wiggle.SerumPreset
FX - Duga - 3 Woodpecker.SerumPreset
FX - FM Bubble Sweep.SerumPreset
FX - FM explosions.SerumPreset
FX - Hands Up.SerumPreset
FX - Laser Generator.SerumPreset
FX - Meow.SerumPreset
FX - Noise Sweep 1.SerumPreset
FX - Noise Sweep 2.SerumPreset
FX - Noise Sweep 3.SerumPreset
FX - Office Telephone.SerumPreset
FX - Radioactive Microwave.SerumPreset
FX - Rise Sweep - Digi.SerumPreset
FX - Rise Sweep - Overcooked.SerumPreset
FX - Rise Sweep - Sinusoid.SerumPreset
FX - Techno Siren.SerumPreset
FX - Torture Sweep.SerumPreset
FX - Wander Blips.SerumPreset
FX - Wasp Whistle Sweep.SerumPreset
FX - What goes up.SerumPreset
FX - Wind Tunnel.SerumPreset
```

### `SEQ` — 21

```text
SEQ - A Hint of Retro.SerumPreset
SEQ - Almost A Guitar.SerumPreset
SEQ - American Beauty.SerumPreset
SEQ - Broken 80s Tape.SerumPreset
SEQ - Chug-A-Luggin.SerumPreset
SEQ - Fifth DMension.SerumPreset
SEQ - Funky Acid.SerumPreset
SEQ - Introducing.SerumPreset
SEQ - LOW Freqz.SerumPreset
SEQ - Night Raider.SerumPreset
SEQ - Perc Jam Loop Offsets.SerumPreset
SEQ - Perc-O-Lator.SerumPreset
SEQ - Pixel Storm.SerumPreset
SEQ - Pluxis.SerumPreset
SEQ - Psychedelic Dulcimer.SerumPreset
SEQ - Running down the Hill.SerumPreset
SEQ - Stressed Acid.SerumPreset
SEQ - Trance in the Pance.SerumPreset
SEQ - Trons Echolot.SerumPreset
SEQ - Vocal Circuit.SerumPreset
SEQ - What The Future Holds.SerumPreset
```

### `DR` — 19

```text
DR - 909 Snare.SerumPreset
DR - Clap Machine.SerumPreset
DR - Hats Velocity Sensitive.SerumPreset
DR - IDM Beat.SerumPreset
DR - Kick Designer.SerumPreset
DR - Kick Generator.SerumPreset
DR - Kick Heavy.SerumPreset
DR - Kick Hype.SerumPreset
DR - Kick Minimal.SerumPreset
DR - Kick Synth 1.SerumPreset
DR - Kick Synth 2.SerumPreset
DR - Rim.SerumPreset
DR - Shake.SerumPreset
DR - Snare Fill.SerumPreset
DR - Snare Old Metal.SerumPreset
DR - Snare Roll.SerumPreset
DR - Snared.SerumPreset
DR - Taiko Sunrise Set.SerumPreset
DR - Tom Simm.SerumPreset
```

### `LOOP` — 16

```text
LOOP - Ancient Breakdown.SerumPreset
LOOP - Apollo's Aria.SerumPreset
LOOP - Auto Scratch.SerumPreset
LOOP - Balafon Dreams.SerumPreset
LOOP - Balcan Trap.SerumPreset
LOOP - Breakwave.SerumPreset
LOOP - BSOD Big Convolver.SerumPreset
LOOP - Downtempo Cave.SerumPreset
LOOP - Easy House Beat.SerumPreset
LOOP - Elec Simple Vintage.SerumPreset
LOOP - Funk Practice.SerumPreset
LOOP - New Dawn.SerumPreset
LOOP - On The Couch.SerumPreset
LOOP - Perc Movie Action.SerumPreset
LOOP - Synth Tech Drums.SerumPreset
LOOP - Techno Loop.SerumPreset
```

### `GTR` — 14

```text
GTR - 100 Nights in Marocco.SerumPreset
GTR - 70's Funk Guitar.SerumPreset
GTR - Acoustic Guitar Duo.SerumPreset
GTR - Acoustic Guitar in a Room.SerumPreset
GTR - Amped Monoriff.SerumPreset
GTR - Campfire Stomper.SerumPreset
GTR - Classic Nylon Guitar.SerumPreset
GTR - Dawn Strum.SerumPreset
GTR - Disto Rush.SerumPreset
GTR - Future Punk Powercords.SerumPreset
GTR - Mariachi Guitar.SerumPreset
GTR - Solo Electric Guitar 1.SerumPreset
GTR - Solo Electric Guitar 2.SerumPreset
GTR - Twelve String Guitar.SerumPreset
```

### `OR` — 14

```text
OR - Clip Organ.SerumPreset
OR - Fantasia Organ.SerumPreset
OR - Happy Phantom.SerumPreset
OR - House Organ.SerumPreset
OR - Jazz FM organ.SerumPreset
OR - Leslie Organ.SerumPreset
OR - Memory Organ .SerumPreset
OR - Organ Also.SerumPreset
OR - Organ Flute.SerumPreset
OR - Organica.SerumPreset
OR - Pipe Dream.SerumPreset
OR - Rotorgana Model A.SerumPreset
OR - Rotorgana Model B.SerumPreset
OR - Thermite.SerumPreset
```

### `SC` — 13

```text
SC - Astral Projection.SerumPreset
SC - Birds.SerumPreset
SC - Cascades of Spectral Lights.SerumPreset
SC - Chaos Theory.SerumPreset
SC - Dark Waterphone.SerumPreset
SC - Fictional Ambience.SerumPreset
SC - Hybrid Colors.SerumPreset
SC - Memories of Etheric Lights.SerumPreset
SC - Quantum Abyss.SerumPreset
SC - Sitar in the Mist.SerumPreset
SC - Stars on a cold night.SerumPreset
SC - The Numbers Experiment.SerumPreset
SC - Zancovic.SerumPreset
```

### `BR` — 12

```text
BR - Brass Hype.SerumPreset
BR - Brass Wall.SerumPreset
BR - Bright Octaves Synth Brass.SerumPreset
BR - Cinema Brass Trio.SerumPreset
BR - Hybrid Brass.SerumPreset
BR - Little Brassy Breakdown.SerumPreset
BR - Slow Synth Brass.SerumPreset
BR - Synth Trumpet Ensemble .SerumPreset
BR - Tight and Punchy.SerumPreset
BR - Trombone.SerumPreset
BR - Trombones Attack Blast.SerumPreset
BR - Warm Hybrid Brass.SerumPreset
```

### `STR` — 12

```text
STR - Classic Syn Strings.SerumPreset
STR - Early Memories.SerumPreset
STR - French Shimmer.SerumPreset
STR - Hybrid Strings.SerumPreset
STR - Motion Solina.SerumPreset
STR - Pedal Chords.SerumPreset
STR - String Layer.SerumPreset
STR - Strings Ensemble - Elegy.SerumPreset
STR - Strings Ensemble - Hybrid 2.SerumPreset
STR - Strings Ensemble - Hybrid.SerumPreset
STR - Strings.SerumPreset
STR - Vector Broken Fanfare.SerumPreset
```

### `EP` — 11

```text
EP - Ballad FM EP.SerumPreset
EP - Ethereal Pianet.SerumPreset
EP - FM Edge Suitcase.SerumPreset
EP - INST Pianet.SerumPreset
EP - INST Winding Roads.SerumPreset
EP - Lo-Fi Tremolo EP.SerumPreset
EP - Mark1 Stage.SerumPreset
EP - Moody FM EP.SerumPreset
EP - Sad LoFI Pianet.SerumPreset
EP - Time Capsule.SerumPreset
EP - Wurli Phaser.SerumPreset
```

### `VOX` — 10

```text
VOX - Alto Vox + Strings.SerumPreset
VOX - Choir Ascension.SerumPreset
VOX - Choir.SerumPreset
VOX - Granular Voices.SerumPreset
VOX - I Talk.SerumPreset
VOX - In Between Nights.SerumPreset
VOX - Peaceful Choir.SerumPreset
VOX - String Vocal Follower.SerumPreset
VOX - Synth Pop Choir.SerumPreset
VOX - Voices in a hurry.SerumPreset
```

### `CH` — 9

```text
CH - Band Stabber.SerumPreset
CH - Beach Club.SerumPreset
CH - Dub Vibes 1000.SerumPreset
CH - Dubtron.SerumPreset
CH - Happy Raver.SerumPreset
CH - Heavy SQ.SerumPreset
CH - High and Low.SerumPreset
CH - The Abnoxious One.SerumPreset
CH - Vintage Spread.SerumPreset
```

### `PAD` — 9

```text
Pad - Analog Strings.SerumPreset
Pad - Enya.SerumPreset
Pad - Lost at Sea.SerumPreset
Pad - Mysterious Pad.SerumPreset
Pad - Slow Dreamy Pad.SerumPreset
Pad - Static.SerumPreset
Pad - Vangelis 1.SerumPreset
Pad - Vangelis 2.SerumPreset
Pad - Vertigo.SerumPreset
```

### `ORCH` — 8

```text
ORCH - Choir and Strings.SerumPreset
ORCH - Cinematic Brass .SerumPreset
ORCH - Cinematic Good Byes.SerumPreset
ORCH - Cinematic Longing.SerumPreset
ORCH - Cinematic Salut To The Hero.SerumPreset
ORCH - Cinematic Summer Solstice.SerumPreset
ORCH - Iberian Folk.SerumPreset
ORCH - Warrior in Heart.SerumPreset
```

### `KIT` — 6

```text
KIT - Auxillary Kit.SerumPreset
KIT - GrittyKitCommittee.SerumPreset
KIT - Machine Basic Kit.SerumPreset
KIT - Mental.SerumPreset
KIT - Pitched Up Layer Kit.SerumPreset
KIT - VTL Heavy Drums.SerumPreset
```

### `MAL` — 6

```text
MAL - Deep Sea Shell Mallet.SerumPreset
MAL - Handpan for the Heart.SerumPreset
MAL - Hybrid Balafon.SerumPreset
MAL - Rustic Wires.SerumPreset
MAL - Spectral Tropicana.SerumPreset
MAL - Tropical Wood.SerumPreset
```

### `SYNTH` — 6

```text
Synth - Billie Jean.SerumPreset
Synth - In The Air Tonight.SerumPreset
Synth - Jackson Fever.SerumPreset
Synth - Miami Vice.SerumPreset
Synth - Stranger Things.SerumPreset
Synth - Sweet Dreams.SerumPreset
```

### `BL` — 5

```text
BL - Ambient Ice Cave Bell Pad.SerumPreset
BL - Kinderjoy.SerumPreset
BL - Sweet Ring-Mod Bell.SerumPreset
BL - Wudang Mountain.SerumPreset
BL - Zenatrope 02.SerumPreset
```

### `WIND` — 4

```text
WIND - Alto Sax.SerumPreset
WIND - Flute.SerumPreset
WIND - Lo-Fi Fluterton.SerumPreset
WIND - Pan Flute.SerumPreset
```

### `INST` — 3

```text
INST - Acoustic Modelled Waterphorium.SerumPreset
INST - Doors To the Secret Garden.SerumPreset
INST - Strings and Horns Ensemble.SerumPreset
```

### `HIT` — 2

```text
HIT - Nova Surge.SerumPreset
HIT - Zombie Orch Stab.SerumPreset
```

### `INIT` — 2

```text
INIT - Brass Multisample.SerumPreset
INIT - Strings Multisample.SerumPreset
```

### `MDL` — 2

```text
MDL - Slimy Swaying.SerumPreset
MDL - Slippery Snake.SerumPreset
```

### `SERUMFX` — 2

```text
SerumFX - Input Filter.SerumPreset
SerumFX - Vocoder.SerumPreset
```

### `HV` — 1

```text
HV - Whomever.SerumPreset
```

### `PN` — 1

```text
PN - Emotional Upright.SerumPreset
```

## Suggested next steps

1. Add a prefix parser that recognizes only a bounded leading code before the
   separator, preserves the original code, and maps known codes to a separate
   role/behavior field.
2. Keep high-confidence mappings separate from tentative mappings, and add
   tests for every alias and unknown-prefix behavior before changing stats or
   generation donor selection.
3. Add embedded tags, author, description, engine, filter, FX types, and
   validated modulation details as facets. Keep raw values available so future
   schema mappings remain reversible.
4. Review the 15 embedded-name mismatches and the ambiguous prefixes against
   the original preset pack documentation or by listening in Serum before
   treating them as canonical classifications.
5. Treat genre, mood, and sound-design adjectives inferred from names or
   descriptions as suggestions unless they are explicitly tagged or reviewed.
