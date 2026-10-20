# Generate

Builds new presets by replacing selected modules in a base preset with modules from library donors or one specific donor preset.

## Requirements

Configure a preset library in [Settings](./settings.md) to use **Library** donors. **Specific preset** donors work without a configured library.

## Usage

1. Choose **Generate** from the mode selector.
2. Choose a **Base preset** in the sidebar, or leave it blank / select **Use Init as base** to use the bundled Init preset.
3. Choose a donor source in the header:
   - **Library** uses the configured library and its **Family** selector. **Random / Mix** uses the entire library; **bass, lead, keys, arp, pluck** match words or abbreviations in the original filenames. If nothing matches, the family fails explicitly rather than borrowing unrelated donors.
   - **Specific preset** uses the preset selected in the sidebar as the donor for every selected module.
4. Select modules with **Replace** or **Replace + Mods** (Init base labels these **Generate** and **Generate (+ Any Modulations)**). Click the selected option again to keep the base value, or use **Keep all**.
   - With Init as the base, defaults include OSC A, Envelope 1, LFO 1, Filter 1, and every macro, with their routes.
   - With a custom base, every module starts at **Keep base**.
5. Set mutation, interpolation, count, seed, and dry run in the header. Set the output directory in the sidebar, then generate.

## Options

- **Interpolation** blends compatible values across participating donors. At 100%, a pair reaches the midpoint.
- Interpolation is available with Library donors; it has no effect when using one Specific preset donor.
- **Dry run** reports what would be generated without writing any files.
- **Base preset** supplies every unselected module and all other preset data; the source file is never modified.
- **Specific preset** uses one chosen donor for each selected module and does not require a library. Family filtering applies only to Library donors.

## Output

- Output is a directory.
- Filenames follow `generated_<family-or-random-or-custom>_<number>.SerumPreset`.
- Existing generated files require confirmation. Base, donor, and configured library inputs are protected from overwriting.

## Modulation routing

- Routes come only from each selected module's chosen donor and are copied atomically.
- Routes are deduplicated by connection identity.
- Source matching uses the bundled confirmed labels from `sources.json`. Destination matching includes oscillator subtypes.
- Unlabeled sources and unconfirmed FX-rack destinations are reported, not guessed.
- Copying routes does not transplant upstream modules. A module set to Replace without routes receives no new incoming routes.

The report lists the base, donors selected for each module, copied routes, and schema limitations.

See also: [Mutate](./mutate.md) · [Stats](./stats.md) · [Settings](./settings.md)
