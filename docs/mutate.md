# Mutate

Randomly perturbs the numeric values of an existing `.SerumPreset` and saves the result as a new file.

## Usage

1. Choose **Mutate** from the mode selector.
2. Drop a `.SerumPreset` onto the window, browse for it, or type its path and press Enter.
3. Set an output **filename**.
4. Adjust the mutation knob by dragging vertically, scrolling, or using the arrow keys (Home/End select 0 and 100).
5. Hover a module and choose **Keep** or **Mutate**. Everything starts on Keep.
6. Use the envelope, LFO, and filter selectors to pick instances. Main, Bus 1, and Bus 2 select whole FX racks.
7. Click **Mangle & save** to export and view the report.

Existing output files require confirmation. The source file is never overwritten.

## How mutation works

- Each stored float is multiplied by a random factor between 0.7 and 1.3 (±30%).
- Zero stays zero. Omitted defaults stay omitted.
- Integers, strings, enums, booleans, metadata, and modulation routes are left unchanged.
- Unknown defaults and legal ranges are not inferred or clamped, so this is not full knob randomization.
- Every export starts from the loaded original, so repeated exports do not compound.

## Module mapping

- Oscillator A/B/C map to `Oscillator0`/`1`/`2`.
- Noise and Sub map to `Oscillator3`/`4`, including shared controls and nested subtype data.
- Effects are selected at rack level, including the effect chain.
- The footer, velocity, and voicing areas are decorative until implemented.

See also: [Generate](./generate.md) · [Stats](./stats.md) · [Settings](./settings.md)
