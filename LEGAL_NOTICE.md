# Holodori Team Optimizer — Disclaimers & Attribution

**Version 3.8.16 — 2 August 2026**

This notice is intended to make the project's unofficial status, third-party-content use, network/build behavior, attribution, and limitations clear. It is not legal advice and does not create permission where permission is otherwise required.

## 1. Unofficial, non-commercial fan project

Holodori Team Optimizer is an independent, non-commercial fan-made analytical/planning tool. It is **not affiliated with, sponsored by, approved by, endorsed by, or operated by** COVER Corp., hololive production, QualiArts, Inc., HolodoriDB, or any of their affiliates, licensors, partners, or talent.

The optimizer is not an official game calculator and does not provide financial, investment, gambling, or spending advice.

## 2. Third-party intellectual property

`hololive`, `hololive production`, `hololive Dreams`, character/game names, logos, card artwork, illustrations, chart content, and other associated materials may be protected by copyright, trademark, and other rights owned by COVER Corp., QualiArts, Inc., their licensors, artists, or other rights holders.

The project **does not claim ownership of those materials and does not grant rights in them**. Their appearance or analytical representation in the optimizer is for identification/reference in an unofficial fan-made tool and does not imply endorsement or affiliation. Any license that may apply to original optimizer code does not extend to third-party artwork, game content, names, trademarks, chart content, or data unless the applicable rights holder expressly says otherwise.

## 3. Card artwork

Card artwork is presentation-only. The distributed optimizer does **not package the card-image files**. When artwork is enabled, the user's browser constructs remote image URLs from the HolodoriDB card `assetId`. The primary portrait uses the `img_card_vert_{assetId}` asset under:

`https://api.holodori.best/api/asset/assetbundles/`

The portrait presentation also requests small HolodoriDB-hosted UI assets for the rarity banner, rarity stars, and Happy/Pure/Cute attribute badge under:

`https://api.holodori.best/manual_assets/`

If a vertical portrait is unavailable, the application may retry the existing `img_card_full_{assetId}` artwork endpoint as a visual fallback.

Artwork can be disabled and never affects calculations or search. The artwork remains the property of its applicable rights holders. The project does not guarantee continued third-party availability.

## 4. HolodoriDB data and service

Structured card/master data is derived from **HolodoriDB / holodori.best**, credited by the project and used with permission. HolodoriDB is a separate third-party project and does not operate or endorse this optimizer unless it expressly states otherwise.

Use of HolodoriDB-hosted resources remains subject to applicable permissions, provider rules, technical limits, and availability.

## 5. Chart timing and developer tooling

v3 can consume a normalized Perfect-Full-Combo timing snapshot for chart-specific analysis. The public browser runtime:

- does **not** contact the game asset CDN for chart data;
- does **not** download/decrypt game resources;
- does **not** require or bundle raw `.sus` chart files; and
- operates only on normalized timing/weight data supplied in `Holodori_Chart_Timelines.json`.

An optional developer helper can invoke separately installed third-party asset tooling as one possible **offline build-time** source of chart resources. That helper is not required for browser use, and this project does not claim that technical accessibility of a resource creates copyright, redistribution, or other legal permission. Underlying chart/game content remains subject to the applicable rights holders' rights and terms.

The chart-provider boundary is intentionally replaceable so an authorized HolodoriDB/rights-holder timing feed can be substituted without changing browser scoring logic.

## 6. Privacy and network requests

The optimizer has no built-in user account system or analytics. Owned-card and progression preferences are stored in browser local storage.

The public application may make these third-party requests:

- **Card artwork and portrait UI assets:** direct image requests to `api.holodori.best` when artwork is enabled, including vertical card portraits, rarity banners/stars, and attribute badges. Image elements use `referrerpolicy="no-referrer"`, although the remote service may still receive ordinary request metadata such as IP address, user agent, timestamp, and path.
- **Card-database update checks:** requests to GitHub-hosted HolodoriDB raw data.

Specific-chart timing is loaded from the bundled/imported snapshot and does not require the browser to contact the game asset service.

The project does not control third-party infrastructure, logging, retention, privacy, or availability.

## 7. Accuracy, randomness, purchases, and reliance

The optimizer is an analytical model. Results may be incomplete, outdated, inaccurate, or affected by undocumented mechanics, future balance changes, database/chart errors, assumptions, omitted account systems, hidden rounding, or random Active-skill outcomes.

The current model is limited to Perfect Full Combo and reports a comparative expected index rather than an official literal game score. It models Holomem Board **Frequency Up** nodes for eligible Member cards, but does not yet model other Member Board bonuses, Leader Board bonuses, Memory, Member Power-Up, Fever, hidden rounding, or other undocumented account systems.

Do not use optimizer output as the sole basis for spending money, pulling gacha, disposing of items, or making account decisions. Gacha outcomes are random and optimizer output does not guarantee future performance or value.

## 8. No warranty

**TO THE MAXIMUM EXTENT PERMITTED BY APPLICABLE LAW, THE TOOL IS PROVIDED “AS IS” AND “AS AVAILABLE,” WITHOUT WARRANTIES OF ANY KIND**, express or implied, including warranties of accuracy, completeness, availability, merchantability, fitness for a particular purpose, non-infringement, reliability, or compatibility with future game/database versions.

## 9. Limitation of liability

To the maximum extent permitted by applicable law, the maintainer and contributors shall not be liable for indirect, incidental, special, exemplary, punitive, or consequential loss or damage arising out of or related to use of or inability to use the optimizer; reliance on rankings/scores/data; gameplay/account/gacha/spending decisions; inaccurate/incomplete/delayed data; local-data loss; or outages/acts of third-party services.

**Nothing in this notice excludes, limits, or waives liability or user rights that cannot legally be excluded, limited, or waived under applicable law.**

## 10. Rights-holder and takedown requests

The project is intended to respect rights holders. If you represent a rights holder and believe artwork display, chart-data handling, data access, attribution, naming, or other material should be changed or removed, contact the project maintainer **ace_ks** through the project's public GitHub/Discord contact channel. Good-faith rights-holder requests can be addressed by removing or disabling the affected integration.

## 11. Relevant official terms

Users and contributors should consult the current versions of:

- [hololive production Derivative Works Guidelines](https://hololivepro.com/en/terms/)
- [hololive Dreams EULA](https://store.steampowered.com/eula/4282500_eula_0)

External terms may change and take precedence over any project summary with respect to the applicable rights holder's content.
