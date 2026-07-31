Holodori Team Optimizer v1.2.2
=================================

Concept, game-rule decisions, testing, and project direction by ace_ks on Discord.
Application code generated with ChatGPT by OpenAI under ace_ks's direction and review.

CONTRIBUTORS
------------
- AiO (Discord): key game-mechanics information, including H/M/L base activation probabilities, plus testing and interpretation support.
- falconx578 (Discord): testing and help understanding game mechanics.
- xyzeex (Discord): contributions to community discussions and game-mechanics interpretation.
- luckyluck.u (Discord): contributions to community discussions and game-mechanics interpretation.
- CroXz_123 (Reddit): testing and help understanding game mechanics.
- pathtobalance (Discord): original 5-star card database spreadsheet.
- Hololive Dreams Discord server: broader community discussion, testing feedback, and help interpreting game mechanics.

FILES
-----
- Holodori_Optimizer_v1.2.2.html: the offline optimizer.
- Holodori_Card_Database_HML_SAR.csv: editable/importable 5-star card database.

HOW TO USE
----------
1. Open the HTML file in a modern browser.
2. Choose “Find best team for my oshi” or the unrestricted global search.
3. For a personal result, enable “Use only cards I own” and check your exact card variants.
4. Select the oshi, Outfit mode, song length, Special model and result count.
5. Run the optimizer.

RESPONSIBLE USE AND DISCLAIMER
------------------------------
This is an unofficial fan-made planning tool. It is not affiliated with, endorsed by, or operated by the game developer, publisher, hololive production, or COVER Corporation.

This optimizer covers 5-star cards only. 4-star and 3-star cards are not included in its database or search results.

This optimizer does not currently take into account Holomem Board Bonuses, Memory Bonuses, or Member Power-Up Bonuses. These account-specific bonuses can materially change actual in-game power and rankings.

Card parameters are modeled as max-bloomed, level 80 5-star cards. Actual in-game values will be lower for cards below that investment level. Relative team comparisons are most meaningful when the compared cards have similar bloom and level investment; uneven investment can change the ranking.

Results are estimates based on incomplete information, simplified formulas, and documented assumptions. Actual in-game performance may differ because of song and chart design, difficulty, account progression, hidden rounding, balance changes, and mechanics that are not fully understood.

Do not use this tool as the sole basis for buying currency, pulling on banners, or making other financial decisions. Gacha outcomes are random and the optimizer cannot guarantee that spending will produce a specific unit or result. Spend only within limits you are comfortable with, and prioritize the characters and playstyles you enjoy.

The tool, creator, contributors, and code-generation provider make no warranties about accuracy, completeness, availability, or fitness for a particular purpose. Users are responsible for their own gameplay and spending decisions. This notice is informational and is not legal or financial advice.

OWNED-CARD SEARCH
-----------------
- The selected oshi is automatically included.
- At least five cards from five different holomems are required.
- Normal and Summer versions of the same holomem cannot coexist.
- In “Best outfit from any card” or “Use a specific outfit” mode, an external Outfit card must also be marked as owned.
- The owned roster is stored locally in the browser. It is not uploaded anywhere.

DATABASE UPDATES
----------------
Use “Export current database CSV”, add cards with the same normalized columns, then import the CSV. Imported data is stored locally by the browser. New mechanics still require a code update.



MATHEMATICAL MODEL SUMMARY
--------------------------
The HTML now contains a full methodology, glossary and exact mathematical notation for every results-table term. Core equations are summarized here.

For card i:
  BaseTotal_i = Performance_i + Technique_i + Sense_i

Passive-adjusted Team Stat:
  Stat_passive = sum_i [P_i(1+b_i,P+b_i,All) + T_i(1+b_i,T+b_i,All) + S_i(1+b_i,S+b_i,All)]

Triggered Outfit stat addition:
  OutfitStat = (o_P+o_All)sum_i P_i + (o_T+o_All)sum_i T_i + (o_S+o_All)sum_i S_i
  TeamStat = Stat_passive + OutfitTriggered * OutfitStat

Fixed base Active rates:
  H = 0.55, M = 0.46, L = 0.37

Duration-weighted SAR approximation:
  SARmult = 1 + sum_k [SAR_k * min(Duration_k, SongLength) / SongLength]
  p_i = min(1, BaseProbability_i * SARmult)

At second t, with a_i(t) indicating card i's scheduled Active window and H_i the cards with higher Active priority:
  WinnerProbability_i(t) = a_i(t)p_i * product_{j in H_i}[1-a_j(t)p_j]

  RawActive = (1/L) sum_t sum_i ActiveMagnitude_i * WinnerProbability_i(t)
  Coverage = (1/L) sum_t {1-product_i[1-a_i(t)p_i]}
  PassiveSupportedActive = (1/L) sum_t sum_i ActiveMagnitude_i(1+Support_i)WinnerProbability_i(t)
  AdjustedActive = PassiveSupportedActive + OutfitTriggered * OutfitSupport * RawActive
  SupportUplift = AdjustedActive - RawActive

Ordinary direct Special model:
  Special_i = SpecialMagnitude_i * SpecialDuration_i * SlotWeight_i / SongLength
  Slot weights in combo-biased mode = 0.92, 0.96, 1.00, 1.04, 1.08
  SpecialBonus = sum_i Special_i

Final comparative objective:
  TotalBonus = AdjustedActive + SpecialBonus + OtherScoreBonus
  StatXScore = TeamStat * (1 + TotalBonus/100)

Outfit penalty and row gap:
  OutfitPenalty = max(0, (BestPermittedIndex-UsedIndex)/BestPermittedIndex)
  Gap = (Rank1Index-RowIndex)/Rank1Index

SEARCH LIMITATION
-----------------
The browser enumerates every valid composition, but global mode uses a quick-score shortlist before the full exact timing and all 120 orders are applied. This makes the search practical, but the result is not a formal proof of the mathematical global optimum. The full details and shortlist-size equations are documented inside the HTML.

MODEL SCOPE
-----------
The optimizer currently includes only 5-star cards. The Stat × Score output is a comparative model, not the game’s literal Unit Score. Board, memory, member power-up and exact chart note/combo scoring are excluded. Review the full assumptions section inside the HTML. Rankings are estimates, not guarantees; small gaps should be treated as uncertain.

CHANGELOG
---------
v1.2.2 — 31 July 2026
- Added a prominent max-bloomed, level 80 card assumption and clarified the effect of uneven investment.
- Added Discord contributors xyzeex and luckyluck.u.

v1.2.1 — 31 July 2026
- Re-rendered division expressions as vertically stacked fractions in the HTML methodology section.
- Added a community credit for the Hololive Dreams Discord server.

v1.2.0 — 31 July 2026
- Added a complete methodology and mathematical definitions section for every result column and major model component.
- Documented exact stat, targeting, Active overlap, coverage, Score Support, Special, SAR, Outfit penalty, gap and Stat x Score equations.
- Disclosed the multi-stage shortlist search and its optimality limitation.

v1.1.3 — 31 July 2026
- Simplified the introductory subtitle.
- Added a prominent disclaimer that Holomem Board, Memory, and Member Power-Up Bonuses are not modeled.

v1.1.2 — 31 July 2026
- Clarified prominently that only 5-star cards are included; 4-star and 3-star cards are excluded.
- Expanded credits for AiO, falconx578, CroXz_123, and pathtobalance.

v1.1.1 — 31 July 2026
- Added a prominent responsible-use and gacha-spending disclaimer.
- Clarified that model results may differ from in-game performance and are not purchase advice or guarantees.
- Added transparent attribution that the application code was generated with ChatGPT by OpenAI under ace_ks's direction and review.

v1.1.0 — 31 July 2026
- Added optional personal owned-card roster filtering for oshi searches.
- Restricted external/specific outfits to owned cards in personal searches.
- Added searchable ownership checkboxes, validation and browser persistence.

v1.0.0 — 31 July 2026
- First formally versioned release.
- Fixed H/M/L rates, ordinary Specials, approximate multiplicative SAR, external outfits, global search and importable database.
