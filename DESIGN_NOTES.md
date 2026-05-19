# Design Notes

Finance Atlas should feel like a research instrument and lab notebook, not a marketing page or a finished public database.

The current design rule is to make uncertainty visible. If something is unresolved, the page should say so. If a number or example is only true for the current local pass, it should be marked as provisional.

## Principles

- Keep text minimal, but make controls self-explanatory.
- Keep unresolved work visible without making caveats dominate the page.
- Mark current, sample-dependent results in restrained language.
- Lead with the academic denominator, methodology layer, and full-text boundary.
- Keep product adoption and factor performance downstream until matching is stable.
- Remove audit artifacts from main pages unless they answer a reader-facing question.
- Prefer compact controls over long explanatory copy.
- Let users move between denominators, methodology signals, and selected neighborhoods.
- Keep the site static until the research object is stable.
- Lead with diagnostics that answer a human question, not with generic chart controls.
- Be explicit that the current anchor set is a working academic denominator, not the complete strategy-source universe.
- Do not force a final product title or contribution before the research question is stable.

## Current Interface Choices

- The homepage is an orientation page, not a dashboard.
- The academic graph page carries the live denominator, methodology explorer, and PC-neighborhood explorer.
- The methods page explains the measurement stack and the de Prado visibility boundary.
- The outcomes page shows citation as the current measured outcome and keeps product adoption/factor performance outside the current evidence.
- Large headline typography has been reduced so the page feels more like a research instrument.

## Future Graph Upgrade

The current graph diagnostics are computed only within the materialized finance workspace. A stronger version should also compute centrality on the full FrontierGraph economics graph, then report whether finance concepts are central locally, globally, or both.
