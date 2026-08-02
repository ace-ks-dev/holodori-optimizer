# Holomem Board Frequency Up validation — v3.8.12

Mechanic implemented: each Frequency Up node reduces the card's **base Active Skill interval by 4%**. Therefore 0 / 1 / 2 / 3 nodes use interval multipliers **1.00 / 0.96 / 0.92 / 0.88**.

Release checks:

- **PASS — Board Off regression:** controlled v3.8.12 Board-Off result exactly matched v3.8.5 score, five cards, and Outfit (`380259.28757273004`).
- **PASS — Compare materialization:** a 17 s base interval materialized as `17 / 16.32 / 15.64 / 14.96` seconds for 0 / 1 / 2 / 3 nodes.
- **PASS — Leader exclusion:** Board-enabled Any-song and Choose-a-song searches assigned 0 nodes to the Holomem whose Outfit was used.
- **PASS — Allocation constraints:** no card exceeded 3 nodes and tested allocations stayed within the selected node budget.
- **PASS — Choose a song:** 702 bundled timelines loaded; a 6-node chart search completed with allocation `[0,2,3,0,1]`, 0 leader nodes, and no browser errors.
- **PASS — Best next card:** a 6-node acquisition search completed normally and propagated Board allocations into candidate teams.
- **PASS — performance smoke:** 31 distinct owned 5★ Holomems, Fast / Any song, completed in about 1.1 s with Board Off and 4.2 s with Board optimization in the release QC environment.
- **PASS — UI:** Off / Optimize segmented-control state and slider visibility synchronize correctly.

Scope: only Frequency Up is modeled. Board node allocation and Outfit selection are integrated into the optimizer's existing bounded heuristic search, so the output is **best found**, not a mathematical proof of the global joint team/order/Outfit/Board optimum.
