# Holodori Optimizer v3.14.0-beta.22

## Skill timeline readability

- Replaced the long Skill timing & value paragraph with a compact four-item legend shared verbatim by Optimizer and Compare.
- The legend keeps the important mappings visible: position/width = timing, brighter = stronger Effective Active Score UP, the shared Special lane contains five fixed party-order windows, SAR raises normal Active proc chance inside its fixed Special window, and bottom bars represent Expected Active value.
- Full score-term definitions remain available in the existing expandable glossary instead of being duplicated above the chart.

## Default Outfit artwork

- Fixed synthetic Default Outfit entries rendering initials in Compare/Outfit previews because their synthetic IDs do not exist in the local artwork manifest.
- Default Outfits now resolve their representative bundled portrait through `displayCardId`.
- Representative Default Outfit portraits suppress rarity/attribute/group chrome so the art identifies the member without implying the Default Outfit has the representative card's rarity or attribute.

Scoring, search, Board, chart, and canonical mechanics are unchanged from beta.21.

## Included data

- Cards: **169**
- Songs: **182**
- Exact chart pack: **r53**
- Chart metadata rows: **728**
- Exact timelines: **722**
- Packed note events: **416,423**

## Integrity

Standalone HTML SHA-256: `6298eac6669f543f6980c2b97a8fbab235a8c3107fd1909b58e561c2a4eb42a3`
