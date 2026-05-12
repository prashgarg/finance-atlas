# Design Notes

Finance Atlas should feel like a research instrument and lab notebook, not a marketing page or a finished public database.

The current design rule is to make uncertainty visible. If something is unresolved, the page should say so. If a number or example is only true for the current local pass, it should be marked as provisional.

## Principles

- Keep text minimal, but make controls self-explanatory.
- Keep unresolved work visible through red placeholders.
- Mark current, sample-dependent results in purple/provisional language.
- Put the product-academic bridge near the top, because it is the current research object.
- Keep the public relationship view focused on economically interpretable source-target pairs.
- Keep audit artifacts available through toggles instead of deleting them.
- Prefer compact controls over long explanatory copy.
- Let users move between bridge examples, concepts, time, and relationships.
- Keep the site static until the research object is stable.
- Lead with diagnostics that answer a human question, not with generic chart controls.
- Distinguish within-finance graph centrality from future global FrontierGraph centrality.
- Be explicit that the current map is an FWCI-selected extracted graph workspace, not the complete strategy-source universe.
- Do not force a final product title or contribution before the research question is stable.

## Current Interface Choices

- Recurring relationships should show interpretable source-target pairs.
- The main time content is now diagnostic: rising themes, fading themes, new arrivals, persistent themes, and spike-like attention.
- The network section uses within-finance PageRank, approximate betweenness, bridge scores, and cross-field edge pairs.
- A smaller trend-check chart remains for raw yearly/decade context.
- The concept explorer remains the main drill-down object.
- Large headline typography has been reduced so the page feels more like a tool.
- Practitioner strategy sources are mentioned only as a coverage boundary, not as extracted graph content.
- The product-bridge section is now the main first-pass tool. It should read as a structured measurement prototype, not as a final claim about the product universe.

## Future Graph Upgrade

The current graph diagnostics are computed only within the materialized finance workspace. A stronger version should also compute centrality on the full FrontierGraph economics graph, then report whether finance concepts are central locally, globally, or both.
