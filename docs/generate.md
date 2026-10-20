# Generate

Builds new presets by replacing selected modules in a base preset with modules from library donors or one specific donor preset.

## Requirements

Configure a preset library in [Settings](./settings.md) to use **Library** donors. **Specific preset** donors work without a configured library.

## Usage

1. Choose **Generate** from the mode selector.
2. Choose a **Base preset** in the sidebar, or drag a `.SerumPreset` file onto the window while Generate is active. Leave the field blank / select **Use Init as base** to use the bundled Init preset.
3. Choose a **Profile** in the header to set a starting module selection. Profiles can be fine-tuned with each module's Replace / Keep controls:
   - **Default** restores the existing OSC A, Envelope 1, LFO 1, Filter 1, and all-macros selection, with matching donor routes.
   - **Modulators** replaces all available envelopes and LFOs. Velocity and Note are modulation sources, not standalone replaceable modules.
   - **OSC B + C + Noise**, **FX only**, and **Filters + FX** replace only those module groups.
   - **Macros only** replaces all macro modules without copying routes, so it does not select any non-macro modules. If the base has no macro entries, supported macro modules are added from donors. A macro missing from the donors is reported and not fabricated.
4. Choose a donor source in the header:
   - **Library** uses the configured library and its **Family** selector. **Random / Mix** uses the entire library; **bass, lead, keys, arp, pluck** match words or abbreviations in the original filenames. If nothing matches, the family fails explicitly rather than borrowing unrelated donors.
   - **Specific preset** uses the preset selected in the sidebar as the donor for every selected module.
5. Select modules with **Replace** or **Replace + Mods** (Init base labels these **Generate** and **Generate (+ Any Modulations)**). Click the selected option again to keep the base value, or use **Keep all**.
   - With Init as the base, defaults include OSC A, Envelope 1, LFO 1, Filter 1, and every macro, with their routes.
   - With a custom base, no modules are selected initially; a macro missing from the base stays absent unless a profile or module action adds it.
6. Set mutation, interpolation, count, seed, and dry run in the header. Set the output directory in the sidebar, then generate.

## Options

- **Interpolation** blends compatible values across participating donors. At 100%, a pair reaches the midpoint.
- Interpolation is available with Library donors; it has no effect when using one Specific preset donor.
- **Dry run** reports what would be generated without writing any files.
- **Append safety limiter** is enabled by default in Settings. When enabled, the compressor effect from the bundled `Init_Safety_Limiter.SerumPreset` is added at the end of `FXRack0` for each generated preset, after any existing effects; no existing effect is replaced.
- **Base preset** supplies every unselected module and all other preset data; the source file is never modified.
- Generation profiles only set the selected module groups; donor source, family, and the configured safety limiter remain independent. **Macros only** does not copy donor routes.
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
