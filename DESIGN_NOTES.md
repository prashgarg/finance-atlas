# Design Notes

Finance Atlas should feel like a research instrument, not a marketing page.

## Principles

- Keep text minimal, but make controls self-explanatory.
- Put time-series exploration near the top, because the main object is how the literature changes.
- Hide known audit artifacts by default, especially self-links in graph relationships.
- Keep audit artifacts available through toggles instead of deleting them.
- Prefer compact controls over long explanatory copy.
- Let users move between three views: concepts, time, and relationships.
- Keep the site static until the research object is stable.
- Lead with diagnostics that answer a human question, not with generic chart controls.
- Distinguish within-finance graph centrality from future global FrontierGraph centrality.

## Current Interface Choices

- Self-links are hidden by default in recurring relationships.
- The main time content is now diagnostic: rising themes, fading themes, new arrivals, persistent themes, and spike-like attention.
- The network section uses within-finance PageRank, approximate betweenness, bridge scores, and cross-field edge pairs.
- A smaller trend-check chart remains for raw yearly/decade context.
- The concept explorer remains the main drill-down object.
- Large headline typography has been reduced so the page feels more like a tool.

## Future Graph Upgrade

The current graph diagnostics are computed only within the materialized finance workspace. A stronger version should also compute centrality on the full FrontierGraph economics graph, then report whether finance concepts are central locally, globally, or both.
