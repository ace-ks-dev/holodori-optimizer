# Developer architecture

The distributed runtime stays as HTML + `Holodori_Chart_Data_r51.js`, but development is split so future work does not require directly editing the generated HTML.

- `src/template.html`: document structure and build placeholders.
- `src/styles.css`: presentation only.
- `src/app.js.in`: browser UI/data/orchestration; worker source is injected at build time.
- `src/search_worker.js`: scoring, comparison, and optimizer search core. Pure UI releases should leave this file byte-identical; v3.7 intentionally changes it only to express oshi search constraints and oshi Outfit selection while retaining the base PFC-v3.5.0 semantics when Board optimization is Off; v3.8.13 adds the separately versioned Frequency Up timing extension.
- `src/roster_importer.js.in`: roster screenshot import/review adapter that writes only through the existing owned-progression API.
- `src/roster_recognizer/`: generated browser recognition worker and data index; intentionally independent of scoring/search.
- `versions.json`: independent application/model/data version boundaries.
- `build.py`: deterministic standard-library build.

New mechanics should enter normalized data first, then reference/QC tests, then `search_worker.js`, and only then the user-facing UI if a control is actually needed. Chart revisions should remain data-only whenever the chart schema is unchanged.


## v3.5 scoring boundary

The scoring worker treats Score Support as an additive support pool that multiplies the effective Active Score UP. Special windows therefore enter the same conceptual support layer as Passive and Outfit support, but only during their timed window. SAR modifies activation probability separately. Search-screening proxies may approximate this interaction for candidate pruning; retained finalists are evaluated with the full selected Generic or Specific-Chart scorer.

Generic calibration constants are model-versioned. Any future change to Active overlap, Score Support, SAR, or Special semantics requires a fresh 702-chart calibration rather than reusing the v3.5 weights.


## v3.6 roster-recognition boundary

`recognizeRoster(files)` is conceptually separate from optimizer calculations. It emits card IDs plus Level/Bloom and confidence/warning evidence. The review UI is the only layer that converts those results into `setOwnedEntry()` calls. Recognition failures therefore cannot alter scoring equations or the search engine.

The recognizer registry and reference index are versioned together. At runtime the importer compares the indexed card IDs against the current optimizer registry and refuses screenshot import when they diverge. This is the future-card safety boundary.


## v3.7 player-flow boundary

The normal user path is `screenshot(s) → reviewed owned roster → goal → search → compact results`. The two first-class goals are unconstrained owned-roster search and oshi-constrained search. Manual card/progression editing, scoring-mode changes, card constraints, chart selection, and search tuning remain available through progressive disclosure rather than being removed.

Oshi selection is represented by `characterId`, not a hard-coded card ID. In automatic oshi mode the worker seeds one search for each eligible owned card belonging to that Holomem, protects the seeded slot during local polish, and returns the strongest valid team. This keeps the feature data-driven when new cards for an existing or new Holomem are appended to the registry.


## v3.8.4 acquisition scope
Best next card accepts an optional `upgradeOshiCardId`. The search worker converts that exact owned card into a required-card constraint before computing both the baseline and every candidate acquisition. This keeps marginal gains directly comparable while reusing the normal optimizer and uniqueness constraints.


## v3.8.13 Holomem Board boundary

Frequency Up is represented as integer node counts rather than percentages. A team card can receive `0..3` Member-board nodes; each node reduces the base Active interval by 4%, so the scorer derives `effectiveInterval = baseInterval * (1 - 0.04 * nodes)`. The optimizer accepts a shared `boardFrequencyNodes` budget of `0..12`.

Leader eligibility is derived from the Outfit owner's `characterId`. If the Outfit owner is one of the five team Holomems, that card is ineligible for Member-board Frequency Up. An external Outfit owner leaves all five scoring cards eligible, although the current UI budget remains capped at 12 pending a future sixth-leader/full-Board model.

The Board object/result boundary retains both node count and derived percent fields so later Member/Leader Board effects can be added without overloading Level/Bloom progression. Current modeled data is limited to Active-frequency nodes; stats and other Board bonuses are excluded.

For scalability, Board node placement is selected with a small dynamic-programming allocator over per-card Active-value estimates, then retained candidates are rescored with full overlap/SAR/chart timing at those intervals. Outfit candidates use a bounded shortlist consistent with the optimizer's existing heuristic architecture. This is therefore a best-found search result, not a formal proof of the globally optimal joint team/order/Outfit/Board allocation.
