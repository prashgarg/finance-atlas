# Finance Atlas

Finance Atlas is a beta research instrument.

The site is static and runs on GitHub Pages. It organizes graph-based finance-literature diagnostics and product-design bridge evidence while the research object is still being refined.

Current content includes:

- materialized finance graph diagnostics
- common canonical concepts and relationships
- time/change diagnostics for the current graph workspace
- an interactive bridge explorer for product families and academic finance neighborhoods
- worked examples for clean, mechanism-level, and noisy bridge cases
- provenance for the current product-graph and bridge package
- explicit current-pass markers for counts and examples that may change

The site should be described as a beta research instrument, not a finished product or public database.

## Local Use

From this directory:

```bash
python3 scripts/export_site_data.py
python3 scripts/refresh_paper_asset.py
python3 -m http.server 8000
```

Then open:

```text
http://localhost:8000
```

## Data Source

The older exported graph data currently comes from:

```text
../asset_pricing_theme_map/data/derived/theme_map_descriptive_v0/
```

Large raw data should not be committed to this repository. Only compact website exports should live in `data/`.

The working note PDF is copied into the static site with:

```bash
python3 scripts/refresh_paper_asset.py
```

The newer product-bridge evidence currently lives outside this repo in:

```text
../product_prospectus_graph/
```

The static site exports only compact JSON summaries from those research outputs. Until the research object stabilizes, full product graph outputs and raw package files should remain outside this repository.

## Graph Diagnostics

The local graph-diagnostics package can be rebuilt with:

```bash
python3 scripts/build_graph_diagnostics.py
python3 scripts/export_site_data.py
```

The diagnostics are computed within the materialized finance workspace. Later versions can add global FrontierGraph centrality measures.

## Coverage Boundary

The broader source registry includes strategy-facing outlets such as `Financial Analysts Journal` and `The Journal of Portfolio Management`. These outlets are tracked as a future graph-extraction boundary. The local audit is in:

```text
../asset_pricing_theme_map/data/derived/strategy_source_coverage_audit_v0/
```
