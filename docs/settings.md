# Settings

Configures the Serum preset library used by [Generate](./generate.md) and [Stats](./stats.md).

## Usage

1. Choose **Settings** from the mode selector.
2. Set your Serum preset library directory and save it.
3. Optionally choose and save a default output directory. It is used for new Mutate output paths and as the Generate output folder.
4. Enable or disable **Append safety limiter** for generated presets. It is enabled by default and saved when toggled.
5. Settings are stored in `settings.json`.

## Notes

- Only `.SerumPreset` files directly inside the chosen folder are scanned. Subfolders are ignored, matching the generator CLI.
- Generate stays unavailable until a valid library is configured.
- The default output directory must already exist. Clear the field and save to restore the existing output defaults.
- The safety limiter is appended after existing effects in `FXRack0` for every generated preset. Mutate exports are not affected.

See also: [Mutate](./mutate.md) · [Generate](./generate.md) · [Stats](./stats.md)
