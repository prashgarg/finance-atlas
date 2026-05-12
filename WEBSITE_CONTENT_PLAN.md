# Finance Atlas Website Content Plan

## Current Purpose

Finance Atlas is a working interface for a research project, not a finished public database. The site should help a reader see the core measurement problem quickly:

- investment products describe strategies in product language;
- academic finance describes related ideas in paper language;
- a useful bridge must say whether the two objects are the same strategy, the same mechanism, a looser shared motif, or only a keyword match.

The site should make this bridge problem concrete before it shows broad graph diagnostics.

## Visual Thesis

Calm research instrument: warm paper background, compact controls, visible uncertainty, and enough structure that the reader can inspect without feeling sold to.

## Interaction Thesis

- The homepage should orient the reader in one screen: product graphs, academic graph, bridge labels.
- The bridge explorer should be the first serious tool: choose a product family and inspect the product signature, nearest academic object, bridge label mix, and caveat.
- Older finance-graph diagnostics should remain available lower on the page, but they should not dominate the first impression.

## Page Structure

### Home

Job: explain the research object in plain language.

Content:

- title: Finance Atlas
- subtitle: mapping the research content of investment strategies
- short description of the bridge problem
- headline counts from the current local pass:
  - product documents
  - product families
  - adjudicated bridge rows
  - finance papers / academic graph size
- primary action: open bridge explorer

Tone:

- no marketing slogan;
- no claim that the result is final;
- purple language for current numbers and provisional findings;
- red placeholders only for genuinely missing pieces.

### Bridge Explorer

Job: show the core product-academic bridge object.

Data source:

- `../product_prospectus_graph/data/product_graph_systematic_all_gptoss_ovhcloud_v0/systematic_bridge_package_v0/family_bridge_cross_section.csv`
- `../product_prospectus_graph/data/product_graph_systematic_all_gptoss_ovhcloud_v0/systematic_bridge_package_v0/bridge_label_overall_summary.csv`
- optional examples from `worked_example_candidate_rows.csv`

Controls:

- product family selector
- optional bridge-type filter later

Fields to show:

- product family
- product document count
- product graph signature
- nearest academic object
- first-pass bridge label
- bridge-label distribution
- current use status
- main caveat

Bridge labels:

- `same_strategy`: the academic object studies substantially the same investment strategy or style.
- `same_mechanism`: the academic object studies a mechanism that plausibly explains the product design.
- `shared_motif`: product and paper share an instrument, market, exposure, or broad motif, but not necessarily the same strategy.
- `concept_only`: shared words or concepts are present, but the bridge is too weak for a substantive claim.
- `no_bridge`: the matched academic object is likely not useful for this product family.

### Product Families

Job: give a compact cross-section of families.

Content:

- family table or cards;
- each row: family, product signature, nearest academic object, modal bridge, caveat.

This should avoid overexplaining row-level QA. It is a map, not an audit log.

### Academic Map

Job: preserve the existing FrontierGraph finance diagnostics.

Content:

- central concepts;
- centrality change;
- communities;
- recurring relationships;
- sample papers.

This is useful context, but it is downstream of the homepage bridge question.

### Paper

Job: link the working note and show the current paper-facing exhibits.

Future content:

- embedded PDF or download link;
- compact exhibit list;
- red placeholders for missing paper figures or checks.

### Methods

Job: explain the measurement stack only as much as needed.

Content:

- product documents become product-local graphs;
- academic finance comes from FrontierGraph;
- bridges are classified by the relation between product graph and academic neighborhood;
- current numbers are provisional because family screens and bridge adjudication are still being checked.

## Homepage Implementation Scope

Use the existing static structure for now:

- keep `index.html`, `styles.css`, `app.js`, and `data/site-data.json`;
- add bridge data to `scripts/export_site_data.py`;
- replace the old “product bridge sketch” section with an interactive bridge explorer;
- keep older diagnostics below the bridge section;
- do not migrate to Astro or a larger framework yet.

## Content Rules

- Prefer concrete labels and controls over explanatory prose.
- Avoid “from X to Y” phrasing.
- Avoid pretending the site is ready for public release.
- Do not foreground tiny audit counts in the homepage copy unless they define the current data object.
- Use “current pass” or “first-pass” for temporary empirical outputs.
- Keep caveats attached to the relevant family rather than collected in a wall of limitations.

