# Best next card performance — v3.8.12

The acquisition calculator still screens every eligible unowned card, then refines the strongest 12 (5★ pool) or 16 (All cards). In v3.8.12, those repeated candidate-constrained refinements use the dedicated bounded `upgrade` search profile instead of rerunning the full Fast/Balanced/Thorough Best Team profile for every candidate.

Normal Best Team search effort is unchanged. Scoring equations, Holomem Board interval rules, Outfit/Oshi constraints, and candidate-at-max-Level/Bloom-0 semantics are unchanged.
