# Generate

Builds new presets by combining modules from donor presets in your Serum library, starting from the bundled Init preset.

## Requirements

A valid preset library must be configured in [Settings](./settings.md). Generate stays unavailable until one is set.

## Usage

1. Choose **Generate** from the mode selector.
2. Pick a **Family**:
   - **Random / Mix** uses the entire library.
   - **bass, lead, keys, arp, pluck** select donors by matching words or abbreviations in the original filenames. If nothing matches, the family fails explicitly rather than borrowing unrelated donors.
3. Select modules with **Generate** or **Generate (+ Any Modulations)**. Click the selected option again to restore Keep Init, or use **Keep all**.
   - Defaults include OSC A, Envelope 1, LFO 1, Filter 1, and every macro, with their routes.
   - Other modules stay exactly at Init.
4. Set the header options: mutation, interpolation, family, count, seed, and dry run.
5. Set the source and output fields in the sidebar, then click the action button.

## Options

- **Interpolation** blends compatible values across participating donors. At 100%, a pair reaches the midpoint.
- **Dry run** reports what would be generated without writing any files.

## Output

- Output is a directory.
- Filenames follow `generated_<family-or-random>_<number>.SerumPreset`.
- Existing generated files require confirmation. Library inputs are protected from overwriting.

## Modulation routing

- Routes come only from each selected module's chosen donor and are copied atomically.
- Routes are deduplicated by connection identity.
- Source matching uses the bundled confirmed labels from `sources.json`. Destination matching includes oscillator subtypes.
- Unlabeled sources and unconfirmed FX-rack destinations are reported, not guessed.
- Copying routes does not transplant upstream modules. A module set to Generate without routes receives no new incoming routes.

The report lists donors, copied routes, and schema limitations.

See also: [Mutate](./mutate.md) · [Stats](./stats.md) · [Settings](./settings.md)
