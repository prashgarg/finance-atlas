from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT.parent / "asset_pricing_theme_map/data/derived/theme_map_descriptive_v0"
OUT = ROOT / "data/site-data.json"
GRAPH_DIAGNOSTICS = ROOT / "data/analysis/graph_diagnostics_v0"
GLOBAL_CONTEXT = ROOT.parent / "asset_pricing_theme_map/data/derived/theme_map_global_context_v0"
CREDIBILITY_AUDIT = ROOT.parent / "asset_pricing_theme_map/data/derived/theme_map_credibility_audit_v0"


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
    rows = read_optional_csv(GRAPH_DIAGNOSTICS / "canonical_edge_weights.csv")[:100]
    out = []
    for row in rows:
        out.append(
            {
                "label": row["edge_pair_label"],
                "source_label": row["source_label"],
                "target_label": row["target_label"],
                "paper_count": as_int(row["paper_count"]),
                "edge_rows": as_int(row["edge_rows"]),
                "role": row["most_common_role"],
                "relationship_type": row["most_common_relationship"],
                "example_claim_text": row["example_claim_text"],
                "example_paper_id": row["example_paper_id"],
            }
        )
    return out


def build_year_counts() -> list[dict[str, Any]]:
    rows = read_csv("paper_theme_panel.csv")
    counts: dict[int, int] = {}
    for row in rows:
        year = as_int(row["publication_year"])
        if year and year <= 2023:
            counts[year] = counts.get(year, 0) + 1
    return [{"year": year, "paper_count": counts[year]} for year in sorted(counts)]


def build_slice_year_counts() -> list[dict[str, Any]]:
    rows = read_csv("paper_theme_panel.csv")
    slices = {
        "asset_pricing": "slice_asset_pricing_broad",
        "factor_investing": "slice_factor_investing",
        "market_microstructure": "slice_market_microstructure",
        "macro_state": "slice_macro_finance_states",
    }
    counts: dict[tuple[int, str], int] = {}
    denominators: dict[int, int] = {}
    for row in rows:
        year = as_int(row["publication_year"])
        if not year or year > 2023:
            continue
        denominators[year] = denominators.get(year, 0) + 1
        for label, col in slices.items():
            if as_bool(row[col]):
                counts[(year, label)] = counts.get((year, label), 0) + 1

    out = []
    for year in sorted(denominators):
        for label in slices:
            paper_count = counts.get((year, label), 0)
            out.append(
                {
                    "year": year,
                    "slice": label,
                    "paper_count": paper_count,
                    "share": paper_count / denominators[year] if denominators[year] else 0,
                }
            )
    return out


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


def read_optional_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def read_optional_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def compact_metric_row(row: dict[str, str], metric: str, count_col: str = "paper_count_2020s") -> dict[str, Any]:
    return {
        "id": row.get("onto_id", ""),
        "label": row.get("concept_display_label") or row.get("concept_label") or "",
        "field": row.get("field_primary", "") or "unknown",
        "value": as_float(row.get(metric, "0")),
        "paper_count": as_int(row.get(count_col, row.get("paper_count", "0"))),
        "share_2000s": as_float(row.get("share_2000s", "0")),
        "share_2010s": as_float(row.get("share_2010s", "0")),
        "share_2020s": as_float(row.get("share_2020s", "0")),
        "max_decade": row.get("max_decade", ""),
        "max_decade_paper_count": as_int(row.get("max_decade_paper_count", "0")),
    }


def compact_global_concept(row: dict[str, str]) -> dict[str, Any]:
    return {
        "id": row.get("onto_id", ""),
        "label": row.get("display_label") or row.get("finance_label") or row.get("global_label") or "",
        "field": row.get("finance_field_primary", "") or "unknown",
        "paper_count": as_int(row.get("finance_paper_count", "0")),
        "finance_pagerank_percentile": as_float(row.get("finance_pagerank_percentile", "0")),
        "global_pagerank_percentile": as_float(row.get("global_pagerank_percentile", "0")),
        "finance_pagerank": as_float(row.get("finance_pagerank", "0")),
        "global_pagerank": as_float(row.get("global_pagerank", "0")),
        "category": row.get("context_category", ""),
    }


def build_global_context() -> dict[str, Any]:
    summary = read_optional_json(GLOBAL_CONTEXT / "package_summary.json")
    if not summary:
        return {"available": False}

    return {
        "available": True,
        "summary": {
            "global_concept_count": int(summary["global_concept_count"]),
            "global_edge_pair_count": int(summary["global_edge_pair_count"]),
            "finance_concept_count": int(summary["finance_concept_count"]),
            "finance_concepts_missing_from_full_graph": int(summary["finance_concepts_missing_from_full_graph"]),
            "category_counts": summary.get("category_counts", {}),
        },
        "category_summary": [
            {
                "category": row["context_category"],
                "concept_count": as_int(row["concept_count"]),
                "mean_finance_pagerank_percentile": as_float(row["mean_finance_pagerank_percentile"]),
                "mean_global_pagerank_percentile": as_float(row["mean_global_pagerank_percentile"]),
            }
            for row in read_optional_csv(GLOBAL_CONTEXT / "summary_by_category.csv")
        ],
        "local_and_global_core": [
            compact_global_concept(row)
            for row in read_optional_csv(GLOBAL_CONTEXT / "top_local_and_global_core.csv")[:40]
        ],
        "macro_finance_local_specialists": [
            compact_global_concept(row)
            for row in read_optional_csv(GLOBAL_CONTEXT / "top_macro_finance_local_specialists.csv")[:40]
        ],
        "global_macro_finance": [
            compact_global_concept(row)
            for row in read_optional_csv(GLOBAL_CONTEXT / "top_global_macro_finance_concepts.csv")[:40]
        ],
    }


def build_credibility_audit() -> dict[str, Any]:
    summary = read_optional_json(CREDIBILITY_AUDIT / "audit_summary.json")
    if not summary:
        return {"available": False}

    community_rows = read_optional_csv(CREDIBILITY_AUDIT / "community_audit.csv")
    edge_rows = read_optional_csv(CREDIBILITY_AUDIT / "edge_pair_audit.csv")
    return {
        "available": True,
        "summary": {
            "community_count": int(summary["community_count"]),
            "high_credibility_communities": int(summary["high_credibility_communities"]),
            "medium_credibility_communities": int(summary["medium_credibility_communities"]),
            "low_or_audit_first_communities": int(summary["low_or_audit_first_communities"]),
            "method_edges_in_top_100_edges": int(summary["method_edges_in_top_100_edges"]),
        },
        "communities": [
            {
                "id": as_int(row["community_id"]),
                "label": row["community_label"],
                "node_count": as_int(row["node_count"]),
                "internal_edge_weight": as_float(row["internal_edge_weight"]),
                "assessment": row["credibility_assessment"],
                "flags": row["flags"],
                "top_concepts": row["top_concepts"],
                "action": row["recommended_action"],
            }
            for row in community_rows[:24]
        ],
    }


def build_graph_diagnostics() -> dict[str, Any]:
    summary_path = GRAPH_DIAGNOSTICS / "package_summary.json"
    if not summary_path.exists():
        return {"available": False}

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    central = read_optional_csv(GRAPH_DIAGNOSTICS / "concept_centrality_overall.csv")
    decade = read_optional_csv(GRAPH_DIAGNOSTICS / "concept_centrality_by_decade.csv")
    field_bridges = read_optional_csv(GRAPH_DIAGNOSTICS / "field_bridge_edges.csv")
    field_bridge_summary = read_optional_csv(GRAPH_DIAGNOSTICS / "field_bridge_summary.csv")
    centrality_change = read_optional_csv(GRAPH_DIAGNOSTICS / "concept_centrality_change.csv")
    centrality_trajectories = read_optional_csv(GRAPH_DIAGNOSTICS / "concept_centrality_trajectories.csv")
    community_summary = read_optional_csv(GRAPH_DIAGNOSTICS / "community_summary.csv")

    top_central = [
        {
            "id": row["onto_id"],
            "label": row["concept_label"],
            "field": row["field_primary"] or "unknown",
            "pagerank": as_float(row["pagerank"]),
            "degree_weighted": as_float(row["degree_weighted"]),
            "in_degree_weighted": as_float(row["in_degree_weighted"]),
            "out_degree_weighted": as_float(row["out_degree_weighted"]),
            "betweenness_approx": as_float(row["betweenness_approx"]),
            "bridge_score": as_float(row["bridge_score"]),
        }
        for row in central[:40]
    ]

    bridge_concepts = sorted(
        top_central,
        key=lambda row: (row["bridge_score"], row["betweenness_approx"], row["pagerank"]),
        reverse=True,
    )[:30]

    top_by_decade: dict[str, list[dict[str, Any]]] = {}
    for row in decade:
        decade_key = str(as_int(row["decade"]))
        top_by_decade.setdefault(decade_key, [])
        if len(top_by_decade[decade_key]) < 10:
            top_by_decade[decade_key].append(
                {
                    "id": row["onto_id"],
                    "label": row["concept_label"],
                    "field": row["field_primary"] or "unknown",
                    "pagerank": as_float(row["pagerank"]),
                    "degree_weighted": as_float(row["degree_weighted"]),
                }
            )

    centrality_risers = [
        {
            "id": row["onto_id"],
            "label": row["concept_label"],
            "field": row.get("field_primary", "") or "unknown",
            "pagerank_2000s": as_float(row.get("pagerank_2000s", "0")),
            "pagerank_2020s": as_float(row.get("pagerank_2020s", "0")),
            "pagerank_change": as_float(row.get("pagerank_change_2020s_vs_2000s", "0")),
            "degree_change": as_float(row.get("degree_change_2020s_vs_2000s", "0")),
        }
        for row in centrality_change
        if as_float(row.get("pagerank_change_2020s_vs_2000s", "0")) > 0
    ][:35]

    centrality_fallers = [
        {
            "id": row["onto_id"],
            "label": row["concept_label"],
            "field": row.get("field_primary", "") or "unknown",
            "pagerank_2000s": as_float(row.get("pagerank_2000s", "0")),
            "pagerank_2020s": as_float(row.get("pagerank_2020s", "0")),
            "pagerank_change": as_float(row.get("pagerank_change_2020s_vs_2000s", "0")),
            "degree_change": as_float(row.get("degree_change_2020s_vs_2000s", "0")),
        }
        for row in sorted(
            centrality_change,
            key=lambda x: as_float(x.get("pagerank_change_2020s_vs_2000s", "0")),
        )
        if as_float(row.get("pagerank_change_2020s_vs_2000s", "0")) < 0
    ][:25]

    trajectory_map: dict[str, dict[str, Any]] = {}
    for row in centrality_trajectories:
        concept_id = row["onto_id"]
        item = trajectory_map.setdefault(
            concept_id,
            {
                "id": concept_id,
                "label": row["concept_label"],
                "field": row.get("field_primary", "") or "unknown",
                "points": [],
            },
        )
        item["points"].append(
            {
                "decade": as_int(row["decade"]),
                "pagerank": as_float(row["pagerank"]),
                "degree_weighted": as_float(row["degree_weighted"]),
            }
        )

    communities = []
    for row in community_summary[:18]:
        try:
            top_concepts = json.loads(row.get("top_concepts_json", "[]"))
        except json.JSONDecodeError:
            top_concepts = []
        try:
            top_fields = json.loads(row.get("top_fields_json", "[]"))
        except json.JSONDecodeError:
            top_fields = []
        communities.append(
            {
                "community_id": as_int(row["community_id"]),
                "label": row["community_label"],
                "node_count": as_int(row["node_count"]),
                "internal_edge_weight": as_float(row["internal_edge_weight"]),
                "top_field": row.get("top_field", "") or "unknown",
                "top_concepts": [
                    {
                        "label": concept.get("concept_label", ""),
                        "field": concept.get("field_primary", "") or "unknown",
                        "pagerank": as_float(concept.get("pagerank", 0)),
                        "paper_count": as_int(concept.get("paper_count", 0)),
                    }
                    for concept in top_concepts[:6]
                ],
                "top_fields": top_fields[:5],
            }
        )

    buckets = {}
    bucket_specs = {
        "rising": ("theme_rising.csv", "rise_2020s_vs_2000s"),
        "falling": ("theme_falling.csv", "fall_2020s_vs_2000s"),
        "new_arrivals": ("theme_new_arrivals.csv", "share_2020s"),
        "persistent": ("theme_persistent.csv", "mean_share"),
        "spiky": ("theme_spiky.csv", "spike_score"),
    }
    for name, (filename, metric) in bucket_specs.items():
        buckets[name] = [
            compact_metric_row(row, metric)
            for row in read_optional_csv(GRAPH_DIAGNOSTICS / filename)[:30]
        ]

    return {
        "available": True,
        "summary": {
            "scope": summary["scope"],
            "graph_nodes": summary["graph_nodes"],
            "graph_relationship_pairs": summary["graph_edges_non_self"],
            "community_count": summary.get("community_count", 0),
            "betweenness_sample_size": summary["betweenness_sample_size"],
        },
        "top_central": top_central,
        "bridge_concepts": bridge_concepts,
        "centrality_by_decade": top_by_decade,
        "centrality_risers": centrality_risers,
        "centrality_fallers": centrality_fallers,
        "centrality_trajectories": list(trajectory_map.values())[:50],
        "communities": communities,
        "theme_buckets": buckets,
        "field_bridge_edges": [
            {
                "label": row["edge_pair_label"],
                "field_pair": row["field_pair"],
                "paper_count": as_int(row["paper_count"]),
                "role": row["most_common_role"],
                "example_claim_text": row["example_claim_text"],
            }
            for row in field_bridges[:40]
        ],
        "field_bridge_summary": [
            {
                "field_pair": row["field_pair"],
                "paper_count": as_int(row["paper_count"]),
                "edge_pair_count": as_int(row["edge_pair_count"]),
                "top_edge_pair": row["top_edge_pair"],
            }
            for row in field_bridge_summary[:20]
        ],
        "global_context": build_global_context(),
        "credibility_audit": build_credibility_audit(),
    }


def main() -> None:
    with (SOURCE / "package_summary.json").open(encoding="utf-8") as handle:
        summary_raw = json.load(handle)

    data = {
        "summary": build_summary(summary_raw),
        "concepts": build_concepts(),
        "rising_concepts": build_rising(),
        "edge_pairs": build_edges(),
        "year_counts": build_year_counts(),
        "slice_year_counts": build_slice_year_counts(),
        "field_decades": build_field_decades(),
        "sample_papers": build_sample_papers(),
        "graph_diagnostics": build_graph_diagnostics(),
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
