from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT.parent / "asset_pricing_theme_map/data/derived/theme_map_descriptive_v0"
OUT = ROOT / "data/site-data.json"


def read_csv(name: str) -> list[dict[str, str]]:
    path = SOURCE / name
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def as_int(value: str) -> int:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return 0


def as_float(value: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def as_bool(value: str) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def compact_title(value: str, limit: int = 116) -> str:
    text = " ".join(str(value or "").split())
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "..."


def build_summary(summary_raw: dict[str, Any]) -> dict[str, Any]:
    return {
        "paper_count": int(summary_raw["paper_count"]),
        "unique_concepts": int(summary_raw["unique_concepts"]),
        "unique_canonical_edge_pairs": int(summary_raw["unique_canonical_edge_pairs"]),
        "asset_pricing_broad_count": int(summary_raw["asset_pricing_broad_count"]),
        "factor_investing_count": int(summary_raw["factor_investing_count"]),
        "market_microstructure_count": int(summary_raw["market_microstructure_count"]),
        "macro_finance_states_count": int(summary_raw["macro_finance_states_count"]),
        "paper_count_figure_year_cutoff": int(summary_raw.get("paper_count_figure_year_cutoff", 2023)),
    }


def build_concepts() -> list[dict[str, Any]]:
    top = read_csv("top_canonical_concepts_overall.csv")[:120]
    decade_rows = read_csv("concept_decade_panel.csv")
    by_concept: dict[str, list[dict[str, Any]]] = {}
    for row in decade_rows:
        concept_id = row["onto_id"]
        by_concept.setdefault(concept_id, []).append(
            {
                "decade": as_int(row["decade"]),
                "paper_count": as_int(row["paper_count"]),
                "share": as_float(row["paper_share_in_decade"]),
            }
        )

    concepts = []
    for row in top:
        concept_id = row["onto_id"]
        decades = sorted(by_concept.get(concept_id, []), key=lambda item: item["decade"])
        concepts.append(
            {
                "id": concept_id,
                "label": row["concept_display_label"],
                "paper_count": as_int(row["paper_count"]),
                "node_rows": as_int(row["node_rows"]),
                "field_primary": row["field_primary"] or "unknown",
                "score_band": row["score_band_mode"] or "",
                "first_decade": as_int(row["first_decade"]),
                "last_decade": as_int(row["last_decade"]),
                "decades": decades,
            }
        )
    return concepts


def build_rising() -> list[dict[str, Any]]:
    rows = read_csv("rising_concepts.csv")[:80]
    return [
        {
            "id": row["onto_id"],
            "label": row["concept_display_label"],
            "field_primary": row["field_primary"] or "unknown",
            "paper_count_2020s": as_int(row["paper_count_2020s"]),
            "rise_2020s_vs_2000s": as_float(row["rise_2020s_vs_2000s"]),
            "rise_2020s_vs_2010s": as_float(row["rise_2020s_vs_2010s"]),
        }
        for row in rows
    ]


def build_edges() -> list[dict[str, Any]]:
    rows = read_csv("top_canonical_edge_pairs_overall.csv")[:100]
    return [
        {
            "label": row["canonical_edge_pair_label"],
            "paper_count": as_int(row["paper_count"]),
            "edge_rows": as_int(row["edge_rows"]),
            "role": row["most_common_edge_role"],
            "relationship_type": row["most_common_relationship_type"],
            "example_claim_text": row["example_claim_text"],
            "example_paper_id": row["example_paper_id"],
        }
        for row in rows
    ]


def build_year_counts() -> list[dict[str, Any]]:
    rows = read_csv("paper_theme_panel.csv")
    counts: dict[int, int] = {}
    for row in rows:
        year = as_int(row["publication_year"])
        if year and year <= 2023:
            counts[year] = counts.get(year, 0) + 1
    return [{"year": year, "paper_count": counts[year]} for year in sorted(counts)]


def build_field_decades() -> list[dict[str, Any]]:
    rows = read_csv("field_decade_panel.csv")
    keep = {"finance", "macro", "micro", "methods", "public", "io", "environment", "trade"}
    return [
        {
            "decade": as_int(row["decade"]),
            "field": row["field_label"],
            "paper_count": as_int(row["paper_count"]),
            "share": as_float(row["paper_share_in_decade"]),
        }
        for row in rows
        if row["field_label"] in keep
    ]


def build_sample_papers() -> list[dict[str, Any]]:
    rows = read_csv("paper_theme_panel.csv")
    selected = []
    for row in rows:
        tags = []
        if as_bool(row["slice_factor_investing"]):
            tags.append("factor")
        if as_bool(row["slice_asset_pricing_broad"]):
            tags.append("asset pricing")
        if as_bool(row["slice_market_microstructure"]):
            tags.append("microstructure")
        if as_bool(row["slice_macro_finance_states"]):
            tags.append("macro/state")
        if not tags:
            continue
        year = as_int(row["publication_year"])
        if year < 2010:
            continue
        selected.append(
            {
                "id": row["custom_id"],
                "title": compact_title(row["title"]),
                "year": year,
                "source": row["source_display_name"],
                "node_count": as_int(row["node_count"]),
                "edge_count": as_int(row["edge_count"]),
                "tags": tags[:4],
            }
        )
    selected.sort(key=lambda item: (len(item["tags"]), item["year"], item["node_count"]), reverse=True)
    return selected[:36]


def main() -> None:
    with (SOURCE / "package_summary.json").open(encoding="utf-8") as handle:
        summary_raw = json.load(handle)

    data = {
        "summary": build_summary(summary_raw),
        "concepts": build_concepts(),
        "rising_concepts": build_rising(),
        "edge_pairs": build_edges(),
        "year_counts": build_year_counts(),
        "field_decades": build_field_decades(),
        "sample_papers": build_sample_papers(),
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
