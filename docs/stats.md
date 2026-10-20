# Stats

Interactive charts and summaries of your configured preset library.

## Usage

Choose **Stats** from the mode selector. Hover over any chart for details. The toolbox can save a chart as PNG or show its underlying data.

## What it shows

- **Quick-glance cards** and charts for category, oscillator engine, filter type, FX usage, modulation sources and destinations, and route counts.
- A source × destination heatmap.
- A category → engine → filter sankey diagram.
- Presets added per month, and a calendar heatmap.
- Tags, authors, and unison values where stored.

## Notes

- **Categories** come from filename keywords. Presets with no match show as **Unclassified**.
- **Engine** is the oscillator sub-type that stores data beyond its defaults.
- **Dates** use file modification time, so they are approximate.
- **Caching:** results are saved in `stats-cache.json` beside `settings.json`. A file is re-read when its size or modification time changes.
- **Charts** are rendered with [Apache ECharts](https://echarts.apache.org/) 5.6.0 (Apache-2.0), vendored in `ui/vendor/echarts.min.js`.

See also: [Mutate](./mutate.md) · [Generate](./generate.md) · [Settings](./settings.md)
