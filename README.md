# Holodori Team Optimizer v3.5.0

## Start here

Extract the **entire ZIP** into one folder, then open `Holodori_Optimizer_v3.5.0.html` in a modern browser. Keep `Holodori_Chart_Data_r51.js` beside the HTML file.

No Python installation, Node.js, local server, game-CDN connection, or manual chart import is required for normal use. If the chart companion is missing, the app fails safely to Generic scoring rather than silently claiming exact chart timing.

## v3.5.0 scoring correction

v3.5.0 corrects how **Score Support Effect** is modeled.

Special Skills that grant Score Support are **not standalone direct score bonuses**. Passive, Outfit, and concurrently active Special Score Support percentages add together, and that total multiplies the currently effective Active Score UP:

```text
Supported Active = Active Score UP × (1 + Passive Support + Outfit Support + active Special Support)
```

A Special Score Support window therefore contributes no score when no Active is effective. Skill Activation Rate (SAR) remains separate: it changes Active proc probability only for checks inside the relevant SAR window.

Specific Chart mode evaluates the support pool on the actual chart timeline, including exact note-weight segments, Active overlap, Special windows, combo state, and SAR/check alignment. Multiple concurrent Score Support sources add before multiplying the Active.

This behavior is consistent with observed in-game HUD examples such as a 95% Active receiving approximately +24% from 25% Score Support, and approximately +129% when an additional 110% Special Score Support is concurrently active.

## Generic recalibration

Because the old Generic calibration had been fitted to the previous direct-Special interpretation, v3.5.0 recalibrates Generic from scratch against all **702 validated non-tutorial r51 charts**.

Fitted Special-position exposure multipliers:

```text
0.894342 / 1.191239 / 1.410406 / 1.516521 / 1.062967
```

Internal Generic-vs-Specific-Chart validation on 30 mechanically varied teams × 702 charts (21,060 team/chart cases):

- mean absolute deviation: **2.90%**
- mean bias: **−0.12%**
- chart-level median average deviation: **2.65%**
- chart-level 95th percentile average deviation: **4.96%**
- largest individual case in that sample: **15.46%**

A separate fit on 20 teams evaluated on a held-out 10-team subset produced **2.86%** mean absolute deviation and **+0.35%** mean bias.

These are comparisons against the optimizer's own corrected exact-chart model, **not measured live-game score error**. Use Specific Chart whenever the song/difficulty is known.

## Production chart scoring

The release ships **702 validated live revision-51 Perfect-FC timelines**, representing **405,194 scoring notes** and **3,510 chart-defined Special trigger timestamps**.

From the current 708 song+difficulty metadata rows:

- 702 non-tutorial rows have validated exact timelines.
- `Rebellion · Normal` (`m0158:2`) is unavailable because its SUS resource is absent from live r51.
- `save our hearts · Easy` (`m0161:1`) is unavailable for the same reason.
- four `m9999` tutorial difficulties are not used because their charts expose two Skill/Special triggers instead of the five-slot normal-live model.

## Comparison Board timing

Comparison optionally models per-member Holomem Board Active Skill activation frequency at **0 / +4 / +8 / +12%** using:

```text
effective interval = base interval / (1 + frequency bonus)
```

This is based on gameplay timing evidence, including a 35 s Active matching a 31.25 s grid at +12%. Optimizer search remains Board-neutral.

## Search behavior

The all-rarity distinct-Holomem space contains **893,166,556** valid five-card compositions before order. Global optimization therefore uses bounded beam search, structured synergy/diversity rescue, local swap polish, exact finalist refinement, and exhaustive 5! order verification for retained finalists. **Balanced** is the recommended default.

Search is best-found heuristic rather than a formal proof of the global optimum. v3.5 QC includes a tractable exhaustive regression where production Balanced search reproduced the literal Top 10 with zero score drift in both Generic and Specific Chart modes.

## Deliberate exclusions

Optimizer search still excludes Holomem Board bonuses, Memories, Member Power-Up, other Skill Tree/Board score effects, Fever/multiplayer mechanics, player judgement errors, and undocumented account/game constants. Comparison can optionally model only the experimentally supported Board Active-frequency nodes.

The output is an **expected comparative index**, not the game's literal displayed score.

## Files

- `Holodori_Optimizer_v3.5.0.html` — browser application and normalized card/master metadata.
- `Holodori_Chart_Data_r51.js` — compact lossless exact-chart companion, decoded lazily.
- `CHART_DATA_GUIDE.md` — chart format/provenance notes.
- `GAME_VALIDATION_PLAN.md` — recommended empirical validation protocol and current evidence.
- `QC_REPORT.txt` — release diagnostics.
- `RELEASE_MANIFEST.json` — release hashes/version boundaries.
- `LEGAL_NOTICE.md` — attribution/legal notice.

## Artwork and network behavior

Card portraits and song jackets may be requested from `api.holodori.best`. Artwork is presentation-only and never changes scoring. Exact chart data is local; the browser does not fetch/decrypt game chart resources at runtime. No analytics are included.

## Attribution

This is an unofficial fan-made analytical tool and is not affiliated with or endorsed by COVER Corp., hololive production, QualiArts, Inc., the hololive Dreams game team, or HolodoriDB. See `LEGAL_NOTICE.md` and the in-app Disclaimers tab.
