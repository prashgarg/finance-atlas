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
BRIDGE_PACKAGE = (
    ROOT.parent
    / "product_prospectus_graph/data/product_graph_systematic_all_gptoss_ovhcloud_v0/systematic_bridge_package_v0"
)
PRODUCT_GRAPH_PACKAGE = BRIDGE_PACKAGE.parent
SOURCE_AUDIT = PRODUCT_GRAPH_PACKAGE / "source_evidence_audit_v0"

NEAREST_ACADEMIC_OBJECT = {
    "broad allocation inflation sensitive": "inflation hedging and asset allocation under inflation",
    "crypto futures exposure": "bitcoin futures, futures price discovery, and crypto market structure",
    "crypto spot or reference exposure": "crypto assets, bitcoin exposure, and cross-market spillovers",
    "esg climate sustainable screen": "ESG investing, sustainable screens, and climate-risk pricing",
    "managed futures trend following core": "time-series momentum and trend-following strategies",
    "multifactor smart beta": "factor investing, smart beta, and multifactor portfolio design",
    "real asset inflation hedge": "real assets, commodities, REITs, and inflation hedging",
    "volatility exposure or control unsplit": "volatility risk premium, variance risk, and volatility-managed exposure",
    "tips or real return inflation protection": "inflation-indexed bonds and real-return protection",
    "quality growth stock selection": "quality factor, earnings quality, and growth-stock selection",
    "managed volatility overlay": "target-volatility rules, risk control, and volatility management",
    "low volatility or multifactor lowvol": "low-beta, low-volatility, and minimum-variance strategies",
}

BRIDGE_CAVEATS = {
    "broad allocation inflation sensitive": "Mechanism bridge: the product protects against inflation, but the academic object may study the hedge channel rather than the product rule.",
    "crypto futures exposure": "Mostly market or instrument bridge: futures products and papers share the crypto-futures object, but product design can differ from the academic question.",
    "crypto spot or reference exposure": "Shared motif bridge: crypto exposure is common to both sides, but the academic object may study prices or spillovers rather than an investable wrapper.",
    "esg climate sustainable screen": "Same-strategy candidate: screens and exclusions are close, but ESG labels can combine preference, risk, and disclosure motives.",
    "managed futures trend following core": "Same-strategy candidate: trend-following products map naturally to time-series momentum, pending source-text checks.",
    "multifactor smart beta": "Same-strategy candidate: academic factor investing and product factor sleeves are close, but implementation details can differ.",
    "real asset inflation hedge": "Mechanism bridge: products hold real assets; papers often study the inflation-hedging channel rather than the fund design.",
    "volatility exposure or control unsplit": "Mechanism bridge: volatility is central, but exposure products, risk-control products, and volatility-risk-premium papers are not one object.",
    "tips or real return inflation protection": "Shared market bridge: TIPS products and inflation-indexed bond papers are close, but the product wrapper adds maturity and allocation choices.",
    "quality growth stock selection": "Boundary case: quality, growth, credit quality, and generic quality language are easy to confuse.",
    "managed volatility overlay": "Boundary case: volatility control can be a strategy rule, a risk disclosure, or incidental language.",
    "low volatility or multifactor lowvol": "Boundary case: low-volatility products can mix low-beta, minimum-variance, multifactor, and defensive-equity ideas.",
}

BRIDGE_LABEL_ORDER = ["same_strategy", "same_mechanism", "shared_motif", "concept_only", "no_bridge"]

FAMILY_DISPLAY_NAME = {
    "managed futures trend following core": "Managed futures / trend following",
    "multifactor smart beta": "Multifactor smart beta",
    "esg climate sustainable screen": "ESG / sustainable screens",
    "volatility exposure or control unsplit": "Volatility exposure / control",
    "broad allocation inflation sensitive": "Inflation-sensitive allocation",
    "real asset inflation hedge": "Real-asset inflation hedge",
    "tips or real return inflation protection": "TIPS / real-return protection",
    "crypto futures exposure": "Crypto futures exposure",
    "crypto spot or reference exposure": "Crypto spot / reference exposure",
    "quality growth stock selection": "Quality / growth stock selection",
    "managed volatility overlay": "Managed-volatility overlay",
    "low volatility or multifactor lowvol": "Low-volatility / low-beta",
}

FAMILY_DISPLAY_ORDER = {
    "managed futures trend following core": 1,
    "multifactor smart beta": 2,
    "esg climate sustainable screen": 3,
    "volatility exposure or control unsplit": 4,
    "broad allocation inflation sensitive": 5,
    "real asset inflation hedge": 6,
    "tips or real return inflation protection": 7,
    "crypto futures exposure": 8,
    "crypto spot or reference exposure": 9,
    "quality growth stock selection": 10,
    "managed volatility overlay": 11,
    "low volatility or multifactor lowvol": 12,
}

FEATURED_EXAMPLE_SPECS = [
    {
        "family": "managed futures trend following core",
        "preferred_label": "same_strategy",
        "lesson": "Clean same-strategy bridge: product trend following maps naturally to academic time-series momentum.",
    },
    {
        "family": "multifactor smart beta",
        "preferred_label": "same_strategy",
        "lesson": "Another same-strategy bridge: product factor sleeves and academic factor-investing papers are close objects.",
    },
    {
        "family": "volatility exposure or control unsplit",
        "preferred_label": "same_mechanism",
        "lesson": "Mechanism bridge: products use volatility exposure or control, while papers often study VIX or variance-risk-premium mechanisms.",
    },
    {
        "family": "broad allocation inflation sensitive",
        "preferred_label": "same_mechanism",
        "lesson": "Mechanism bridge: products seek inflation protection, while papers study inflation-hedging channels across assets.",
    },
    {
        "family": "quality growth stock selection",
        "preferred_label": "no_bridge",
        "lesson": "Boundary case: quality in product language can collide with earnings quality or generic quality in academic language.",
    },
]

TYPOLOGY_TABLE_SPECS = [
    {
        "family": "managed futures trend following core",
        "product_graph_signature_text": "Futures-based rules; trend-following strategy; asset-class rotation",
        "bridge_type": "Same strategy",
        "main_caveat": "Need source-text check that the product rule is genuinely trend-following, not broad managed-futures branding.",
    },
    {
        "family": "multifactor smart beta",
        "product_graph_signature_text": "Factor/style targeting; index-like rules; portfolio construction",
        "bridge_type": "Same strategy",
        "main_caveat": "Academic work may study factor construction more generally than investable index implementation.",
    },
    {
        "family": "volatility exposure or control unsplit",
        "product_graph_signature_text": "Volatility-linked instruments; exposure rules; VIX or variance-risk terms",
        "bridge_type": "Mechanism / rationale",
        "main_caveat": "Academic mechanisms may explain volatility-risk pricing rather than the product wrapper.",
    },
    {
        "family": "broad allocation inflation sensitive",
        "product_graph_signature_text": "Real assets; allocation rules; inflation-risk exposure",
        "bridge_type": "Mechanism / rationale",
        "main_caveat": "The bridge may be through inflation-hedging rationale, not a single named strategy.",
    },
    {
        "family": "crypto futures exposure",
        "product_graph_signature_text": "Futures contracts; bitcoin exposure; roll or term-structure language",
        "bridge_type": "Shared market / motif",
        "main_caveat": "Academic work may study the market or instrument, not the product strategy.",
    },
    {
        "family": "quality growth stock selection",
        "product_graph_signature_text": "Stock-selection rules; quality or growth language; fundamentals",
        "bridge_type": "Boundary / noisy",
        "main_caveat": "Retrieval often confuses investment quality with accounting earnings quality or generic quality language.",
    },
    {
        "family": "low volatility or multifactor lowvol",
        "product_graph_signature_text": "Factor/style targeting; defensive equity; index rules",
        "bridge_type": "Boundary / noisy",
        "main_caveat": "Retrieval can drift to volatility of flows or mathematical minimum-variance problems.",
    },
]


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


def slugify(value: str) -> str:
    return (
        str(value or "")
        .strip()
        .lower()
        .replace("&", "and")
        .replace("/", " ")
        .replace("-", " ")
        .replace(",", " ")
        .replace("  ", " ")
        .replace(" ", "-")
    )


def split_signature(value: str, limit: int = 4) -> list[str]:
    parts = [part.strip() for part in str(value or "").split(";") if part.strip()]
    return parts[:limit]


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


def build_product_bridge() -> dict[str, Any]:
    family_rows = read_optional_csv(BRIDGE_PACKAGE / "family_bridge_cross_section.csv")
    label_rows = read_optional_csv(BRIDGE_PACKAGE / "bridge_label_overall_summary.csv")
    example_rows = read_optional_csv(BRIDGE_PACKAGE / "worked_example_candidate_rows.csv")
    source_audit_rows = read_optional_csv(SOURCE_AUDIT / "bridge_typology_source_audit.csv")
    product_evidence_rows = read_optional_csv(SOURCE_AUDIT / "bridge_typology_product_evidence_long.csv")
    academic_evidence_rows = read_optional_csv(SOURCE_AUDIT / "bridge_typology_academic_evidence_long.csv")
    package_summary = read_optional_json(PRODUCT_GRAPH_PACKAGE / "package_summary.json")

    if not family_rows:
        return {"available": False}

    examples_by_family: dict[str, list[dict[str, Any]]] = {}
    for row in example_rows:
        family = row.get("product_family", "")
        if not family:
            continue
        examples_by_family.setdefault(family, [])
        if len(examples_by_family[family]) >= 3:
            continue
        examples_by_family[family].append(
            {
                "academic_year": as_int(row.get("academic_year", "")),
                "academic_title": compact_title(row.get("academic_title", ""), 96),
                "academic_venue": row.get("academic_venue", ""),
                "matched_terms": row.get("matched_terms", ""),
                "bridge_label": row.get("adjudicated_bridge_label", ""),
                "confidence": row.get("adjudication_confidence", ""),
            }
        )

    product_evidence_by_display: dict[str, list[dict[str, Any]]] = {}
    for row in product_evidence_rows:
        family = row.get("product_family", "")
        if not family:
            continue
        product_evidence_by_display.setdefault(family, []).append(
            {
                "slot": as_int(row.get("slot", "0")),
                "field_group": row.get("field_group", ""),
                "edge_or_node_type": row.get("edge_or_node_type", ""),
                "quote": row.get("quote", ""),
            }
        )

    academic_evidence_by_display: dict[str, list[dict[str, Any]]] = {}
    for row in academic_evidence_rows:
        family = row.get("product_family", "")
        if not family:
            continue
        academic_evidence_by_display.setdefault(family, []).append(
            {
                "slot": as_int(row.get("slot", "0")),
                "title": compact_title(row.get("title", ""), 110),
                "year": as_int(row.get("year", "")),
                "venue": row.get("venue", ""),
                "matched_terms": row.get("matched_terms", ""),
                "frontiergraph_edge": row.get("frontiergraph_edge", ""),
            }
        )

    audit_by_family: dict[str, dict[str, Any]] = {}
    for row in source_audit_rows:
        family = row.get("product_family", "")
        family_id = row.get("primary_subfamily", "")
        if not family_id:
            continue
        audit_by_family[family_id] = {
            "survives": row.get("bridge_label_survives_source_evidence", ""),
            "reason": row.get("audit_reason", ""),
            "caveat_after_audit": row.get("main_caveat_after_audit", ""),
            "product_evidence_count": as_int(row.get("product_evidence_count", "0")),
            "academic_evidence_count": as_int(row.get("academic_evidence_count", "0")),
            "product_excerpts": product_evidence_by_display.get(family, []),
            "academic_evidence": academic_evidence_by_display.get(family, []),
        }

    families = []
    for row in family_rows:
        family = row["product_family"]
        label_counts = {label: as_int(row.get(label, "0")) for label in BRIDGE_LABEL_ORDER}
        bridge_review_rows = as_int(row.get("bridge_review_rows", "0"))
        modal_label = row.get("modal_first_pass_bridge", "")
        display_name = FAMILY_DISPLAY_NAME.get(family, family.replace(" or ", " / ").title())
        families.append(
            {
                "id": slugify(family),
                "product_family": family,
                "display_name": display_name,
                "documents": as_int(row.get("documents", "0")),
                "mean_nodes": as_float(row.get("mean_nodes", "0")),
                "mean_edges": as_float(row.get("mean_edges", "0")),
                "product_graph_signature": split_signature(row.get("top_edge_signature", "")),
                "product_node_signature": split_signature(row.get("top_node_signature", "")),
                "nearest_academic_object": NEAREST_ACADEMIC_OBJECT.get(family, "academic finance neighborhood"),
                "plausible_state_documents": as_int(row.get("plausible_state_documents", "0")),
                "plausible_state_share": as_float(row.get("plausible_state_share", "0")),
                "interpretation": row.get("interpretation", ""),
                "label_counts": label_counts,
                "modal_first_pass_bridge": modal_label,
                "modal_first_pass_bridge_share": as_float(row.get("modal_first_pass_bridge_share", "0")),
                "substantive_bridge_rows": as_int(row.get("substantive_bridge_rows", "0")),
                "weak_or_rejected_rows": as_int(row.get("weak_or_rejected_rows", "0")),
                "bridge_review_rows": bridge_review_rows,
                "substantive_bridge_share": as_float(row.get("substantive_bridge_share", "0")),
                "current_use_status": row.get("current_use_status", ""),
                "main_caveat": BRIDGE_CAVEATS.get(family, "Needs source-text review before stronger claims."),
                "examples": examples_by_family.get(family, []),
                "source_audit": audit_by_family.get(family.replace(" ", "_"), {}),
            }
        )

    families.sort(key=lambda item: FAMILY_DISPLAY_ORDER.get(item["product_family"], 999))
    family_by_name = {item["product_family"]: item for item in families}

    featured_examples = []
    for spec in FEATURED_EXAMPLE_SPECS:
        family = spec["family"]
        preferred_label = spec["preferred_label"]
        candidates = [row for row in example_rows if row.get("product_family") == family]
        chosen = next((row for row in candidates if row.get("adjudicated_bridge_label") == preferred_label), None)
        chosen = chosen or (candidates[0] if candidates else None)
        family_item = family_by_name.get(family, {})
        if not chosen:
            continue
        featured_examples.append(
            {
                "family_id": slugify(family),
                "product_family": family,
                "display_name": FAMILY_DISPLAY_NAME.get(family, family.replace(" or ", " / ").title()),
                "bridge_label": chosen.get("adjudicated_bridge_label", preferred_label),
                "lesson": spec["lesson"],
                "product_graph_signature": family_item.get("product_graph_signature", []),
                "nearest_academic_object": family_item.get("nearest_academic_object", ""),
                "academic_year": as_int(chosen.get("academic_year", "")),
                "academic_title": compact_title(chosen.get("academic_title", ""), 118),
                "academic_venue": chosen.get("academic_venue", ""),
                "matched_terms": chosen.get("matched_terms", ""),
                "confidence": chosen.get("adjudication_confidence", ""),
                "main_caveat": family_item.get("main_caveat", ""),
            }
        )

    typology_rows = []
    for spec in TYPOLOGY_TABLE_SPECS:
        family = spec["family"]
        family_item = family_by_name.get(family, {})
        typology_rows.append(
            {
                "family_id": slugify(family),
                "product_family": family,
                "display_name": FAMILY_DISPLAY_NAME.get(family, family.replace(" or ", " / ").title()),
                "product_graph_signature_text": spec["product_graph_signature_text"],
                "nearest_academic_object": family_item.get("nearest_academic_object", NEAREST_ACADEMIC_OBJECT.get(family, "")),
                "bridge_type": spec["bridge_type"],
                "modal_first_pass_bridge": family_item.get("modal_first_pass_bridge", ""),
                "main_caveat": spec["main_caveat"],
                "source_audit": family_item.get("source_audit", {}),
            }
        )

    label_summary = [
        {
            "label": row.get("adjudicated_bridge_label", ""),
            "rows": as_int(row.get("rows", "0")),
            "share": as_float(row.get("share", "0")),
        }
        for row in label_rows
    ]

    return {
        "available": True,
        "summary": {
            "product_documents": int(package_summary.get("product_document_count", 0) or package_summary.get("documents", 0)),
            "product_families": len(families),
            "bridge_review_rows": sum(item["bridge_review_rows"] for item in families),
            "substantive_bridge_rows": sum(item["substantive_bridge_rows"] for item in families),
            "weak_or_rejected_rows": sum(item["weak_or_rejected_rows"] for item in families),
            "same_strategy_rows": sum(item["label_counts"]["same_strategy"] for item in families),
            "same_mechanism_rows": sum(item["label_counts"]["same_mechanism"] for item in families),
            "shared_motif_rows": sum(item["label_counts"]["shared_motif"] for item in families),
        },
        "provenance": {
            "product_graph_package": str(PRODUCT_GRAPH_PACKAGE.relative_to(ROOT.parent)),
            "bridge_package": str(BRIDGE_PACKAGE.relative_to(ROOT.parent)),
            "model": package_summary.get("model", ""),
            "provider": package_summary.get("provider", ""),
            "estimated_cost_usd": as_float(package_summary.get("estimated_cost_usd", 0)),
            "parsed_ok": as_int(package_summary.get("parsed_ok", 0)),
            "parse_errors": as_int(package_summary.get("parse_errors", 0)),
            "created_at": package_summary.get("created_at", ""),
        },
        "label_summary": label_summary,
        "families": families,
        "featured_examples": featured_examples,
        "typology_rows": typology_rows,
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
        "product_bridge": build_product_bridge(),
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
