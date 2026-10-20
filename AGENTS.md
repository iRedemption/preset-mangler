# Preset Mangler instructions

These instructions apply to this directory and its descendants. Follow the
repository-level `AGENTS.md` as well. Before preset or schema work, read
`../../.github/copilot-instructions.md`; for Python that manipulates presets,
also read `../../.github/instructions/preset-scripts.instructions.md`.
Read `README.md` for the current tool behaviour.

## Priorities

1. Preserve preset integrity and the user's source files.
2. Keep the code modular, reusable, and standalone.
3. Preserve the supplied UI geometry and clear, consistent interactions.
4. Keep implementations as compact, efficient, succinct, and easy to maintain as possible.

Prefer the smallest clear implementation. Low line count must not come at the
expense of correctness, readable names, explicit errors, or useful module boundaries.
Avoid dense one-liners, speculative frameworks, unnecessary dependencies, and
abstractions that do not remove meaningful duplication.

## Structure and reuse

- Keep `mangler.py` as the single launcher; put feature implementation elsewhere.
- Keep UI layout, reusable UI components, interactions, and desktop integration
  in `ui/`. Keep preset operations and configuration logic in `backend/`.
- Keep backend operations usable without launching a desktop window. The bridge
  coordinates dialogs and backend calls; it must not duplicate preset algorithms.
- Reuse subdivisions, path fields, knobs, and tooltips from `ui/components.js`.
  Represent variable choices with data rather than separate hard-coded renderers.
- Reuse the shared container, mutation, selection, and interpolation helpers.
  Both modes must use the same mutation implementation.
- Reuse relevant logic from `../preset-generator/` and `../cli/` when adding
  features, but keep required helpers and assets bundled locally. Runtime use
  must not depend on sibling tools or the repository schema directory.
- Maintain a single local implementation of each algorithm. When adapting a
  bundled helper, document its origin and intentional differences; check its
  consumers instead of creating another slightly different copy.
- Resolve bundled assets relative to the tool, not the working directory.
  Keep dependencies in `requirements.txt`; keep local settings and caches out of Git.

## UI contract

- Preserve the supplied 1190 x 740 stage and inclusive rectangle coordinates in
  `ui/layout.js`. Scale the stage and underlay together to maintain exact alignment.
- Keep OSC and FX screenshots in `assets/` beneath the rectangles at 50% opacity.
  Leave unimplemented tabs inactive until their layout and behaviour are supplied.
- On launch, show the three sidebar options: Generate, Mutate, and Settings
  with a gear icon. Hide the layout until a mode is chosen. Mutate without a
  source shows the drag-and-drop/browse prompt.
- Generate has no sub-modes; donor selection is set by the Family dropdown
  (Random / Mix or a specific family). Disable Generate until a valid
  preset library is configured, and explain the requirement in a tooltip.
- Keep source/output fields and the action button at the bottom of the sidebar.
  Put mode parameters in the measured header controls area. Settings replaces
  the layout with a settings page.
- Keep mutation and generation selections/settings separate. Preserve selections
  across tab and mode changes; loading a new mutation source resets its selections.
- Reuse tooltips for brief explanations. Support keyboard interaction, labelled
  controls, visible focus, busy feedback, and readable errors. Avoid exposing
  implementation details in ordinary controls.
- Keep native window objects and internal state private to the desktop bridge;
  expose only the small API needed by the interface.

## Preset operations

- Mutate defaults to Keep for every module. Only modules marked Mutate change.
  Each export starts from the original loaded preset, never a previous output.
- Preserve current float-only percentage mutation. Do not infer missing defaults,
  enum choices, or parameter ranges. Preserve integers, booleans, strings,
  metadata, and modulation routes in mutation mode.
- Generate always starts from the bundled `assets/Init.SerumPreset`. Replace
  only selected module subtrees; unselected modules retain their Init values.
- Default Generate (+ Any Modulations) selections are OSC A, Envelope 1, LFO 1,
  Filter 1, and all macros. Clicking an already selected generation option
  deselects it and keeps Init.
- Family "Random / Mix" chooses donors from the configured library. Any other
  family reuses the generator's filename words and abbreviations for bass, lead,
  keys, arp, and pluck. If no filenames match, fail clearly rather than falling
  back to unrelated donors.
- Scan directly contained `.SerumPreset` files, as the generator does. Changing
  scanning or matching semantics must be an intentional, documented feature change.
- Copy oscillator wrappers with their nested subtype data and FX racks with
  their complete chains/order. Do not guess subtype or individual-effect mappings.
- Copy modulation records atomically from each selected module's chosen donor,
  deduplicate connection identities, and allocate only confirmed free slots.
  Check oscillator subtype destinations as well as wrapper destinations.
- Source-side route matching uses confirmed labels only. Report unlabeled sources,
  unsupported FX mappings, missing donor modules, and slot-capacity failures.
  Do not silently infer upstream modules or transplant unselected source modules.
- Generate without modulation copying receives no new incoming routes. Preserve
  route identity during interpolation; reuse the established interpolation logic.
- Protect mutation sources and library inputs from overwriting. Confirm replacing
  existing output files. Dry runs must not create output files or directories.
- Return useful reports that distinguish performed operations, assumptions, and
  work omitted because schema knowledge is incomplete.

## Verification and maintenance

Use real Serum-exported fixtures for container/generation checks; do not invent
schema facts or fabricate exports to claim Serum compatibility. Test preservation
of sources, unselected modules, route records, and seeded behaviour when changing
preset logic. Test relevant desktop interactions when changing UI behaviour.
Keep tests proportional to the change; documentation-only edits need no test run.

From the repository root:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s src/preset-mangler/tests -v
.\.venv\Scripts\python.exe src/preset-mangler/tests/smoke_ui.py
```

The desktop smoke check opens a hidden window and uses temporary settings,
libraries, and outputs; it must not modify the user's real settings or presets.
Update `README.md` when behaviour, setup, controls, or limitations change.
