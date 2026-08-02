# Holodori Optimizer — empirical game validation plan

## Current status

The optimizer has strong internal software/data QC and now has targeted live-game evidence for several timing/mechanic assumptions, but it has **not** yet been validated against a sufficiently large set of observed final game scores. Generic-vs-Specific-Chart deviation is an internal model comparison and must not be interpreted as live-game score error.

## Live-game evidence already obtained

### Active timing / chart origin

A recorded `you&aIzu · Expert` run was aligned to the chart's fixed Special triggers (22.67 / 52.00 / 73.33 / 105.33 / 121.33 s). Observed Active procs for Summer Watame / Summer Flare / Towa / Summer Noel / Nene fell on the predicted interval grids within recording precision, supporting the model assumption that Active timing starts from chart/song t=0 with no additional intro lockout.

### Board Active frequency

Summer Watame's 35 s base Active matched approximately 31.25 s checks with +12% Board activation frequency, supporting `effective interval = base interval / 1.12` rather than subtracting 12% directly from cooldown.

### Score Support semantics

Observed HUD behavior is consistent with Score Support sources adding and multiplying Active Score UP. A 95% Active showed roughly `95 + 24%` with 25% support and roughly `95 + 129%` when an additional 110% Special Score Support was active. v3.5 implements this relationship; display rounding itself is not assumed to be the game's internal scoring rounding.

## Recommended validation ladder

1. **Card/stat sanity checks** — compare imported Level/Bloom P/T/S values against the game UI for a stratified card sample.
2. **Deterministic team-stat checks** — isolate Passive and Outfit effects and compare relative team-stat changes while holding account bonuses fixed.
3. **More chart/timing checks** — validate additional songs, Active intervals, Special triggers, SAR windows, and Board frequency levels.
4. **Same-chart team tests** — use one fixed chart and mechanically contrasting teams (Active-heavy, support-heavy, SAR-heavy, stat-heavy). Compare observed mean score ratios and rankings against predictions.
5. **Cross-chart tests** — repeat selected teams on charts from low/high Generic-vs-Specific deviation regions to test chart-specific timing predictions.

## What to record

For every run record app/game version, chart + difficulty, exact ordered team, card Level/Bloom, Outfit, Board/Memory/Power-Up state, FC/Perfect status, final score, and—if observable—Active proc events. Keep progression/account bonuses fixed within a comparison block.

## Statistical targets

- Primary: predicted vs observed **team score ratios** on the same chart.
- Ranking: Spearman correlation and whether predicted best teams are best on average.
- Calibration: regress observed normalized score against predicted index; inspect slope/intercept, R², and residual bias by mechanic/chart.
- Proc variance: compare observed run-to-run SD with Comparison's modeled SD.

If individual Active proc events can be logged, conditioning a validation calculation on the observed proc sequence is especially valuable because it removes much of the stochastic noise.

## Suggested first score experiment

Start with 6 mechanically different teams × 3 Expert charts × enough clean PFC repetitions to estimate a stable mean. Choose one chart near the Generic average and two charts from opposite ends of the measured Generic-vs-Specific deviation distribution.
