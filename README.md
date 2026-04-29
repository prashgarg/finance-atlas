# Finance Atlas

Finance Atlas is a lightweight interactive explorer for mapped finance research themes.

The first version is static and runs on GitHub Pages. It uses small JSON exports from the local `asset_pricing_theme_map` project:

- headline corpus counts
- common canonical concepts
- rising concepts by decade
- common concept-to-concept relationships
- sample papers from selected slices

The site is intentionally simple. It is a public-facing inspection layer for the research map, not the full research database.

## Local Use

From this directory:

```bash
python3 scripts/export_site_data.py
python3 -m http.server 8000
```

Then open:

```text
http://localhost:8000
```

## Data Source

The exported data currently comes from:

```text
../asset_pricing_theme_map/data/derived/theme_map_descriptive_v0/
```

Large raw data should not be committed to this repository. Only compact website exports should live in `data/`.
