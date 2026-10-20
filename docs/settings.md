# Settings

Configures the Serum preset library used by [Generate](./generate.md) and [Stats](./stats.md).

## Usage

1. Choose **Settings** from the mode selector.
2. Set your Serum preset library directory.
3. Save. The path is stored in `settings.json`.

## Notes

- Only `.SerumPreset` files directly inside the chosen folder are scanned. Subfolders are ignored, matching the generator CLI.
- Generate stays unavailable until a valid library is configured.

See also: [Mutate](./mutate.md) · [Generate](./generate.md) · [Stats](./stats.md)
