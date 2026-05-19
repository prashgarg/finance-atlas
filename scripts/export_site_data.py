from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT.parent / "product_prospectus_graph"
OUT = ROOT / "data/site-data.json"


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def as_int(value: Any) -> int:
    try:
        if isinstance(value, str) and " of " in value:
            value = value.split(" of ", 1)[0]
        return int(float(value))
    except (TypeError, ValueError):
        return 0


def as_float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def find_metric(rows: list[dict[str, str]], name: str, default: str = "") -> str:
    for row in rows:
        if row.get("metric") == name:
            return row.get("value", default)
    return default


def metric_map(rows: list[dict[str, str]]) -> dict[str, str]:
    return {row.get("metric", ""): row.get("value", "") for row in rows}


def label_from_spec(spec_name: str) -> str:
    if spec_name.startswith("frontiergraph"):
        corpus = "FrontierGraph"
    elif spec_name.startswith("causalclaims"):
        corpus = "CausalClaims"
    else:
        corpus = "Other"

    if "concept_method" in spec_name:
        input_features = "Concepts plus method tags"
    else:
        input_features = "Concepts only"

    threshold = "title and abstract graph"
    if "eo3" in spec_name:
        threshold = "full text, edge overlap >= 3"
    elif "eo4" in spec_name:
        threshold = "full text, edge overlap >= 4"
    elif "eo5" in spec_name:
        threshold = "full text, edge overlap >= 5"

    return corpus, input_features, threshold


def bridge_label(value: str) -> str:
    labels = {
        "same_strategy": "same strategy",
        "same_mechanism_or_rationale": "mechanism or rationale",
        "shared_market_or_motif": "shared market or motif",
        "not_assigned": "not assigned",
    }
    return labels.get(value, value.replace("_", " "))


def clean_label(value: str) -> str:
    if not value or value == "NA":
        return ""
    return value.replace("_", " ")


def pc_case_label(case_id: str) -> str:
    labels = {
        "factors_returns": "Factors and returns",
        "liquidity_risk": "Liquidity and risk",
        "macro_returns": "Macro and returns",
        "methods_methods": "Methods neighborhood",
    }
    return labels.get(case_id, clean_label(case_id).title())


def build_site_data() -> dict[str, Any]:
    post_summary_rows = read_csv(PROJECT / "data/academic_analysis_graph_post_recall_anchor_v1/package_summary_v1.csv")
    post_summary = metric_map(post_summary_rows)
    anchor_summary = read_json(PROJECT / "data/anchor_denominator_validation_v1/package_summary.json")
    recall_summary = read_json(PROJECT / "data/anchor_recall_validation_v1/package_summary.json")
    graph_nodes = read_csv(
        PROJECT / "data/academic_analysis_graph_post_recall_anchor_v1/post_recall_anchor_node_role_summary_v1.csv"
    )
    graph_edges = read_csv(
        PROJECT / "data/academic_analysis_graph_post_recall_anchor_v1/post_recall_anchor_edge_role_summary_v1.csv"
    )
    methodology = read_csv(
        PROJECT
        / "data/analysis_graph_methodology_layer_post_recall_anchor_v1/post_recall_methodology_feature_summary_by_role_v1.csv"
    )
    methodology_panel = read_csv(
        PROJECT
        / "data/analysis_graph_methodology_layer_post_recall_anchor_v1/post_recall_methodology_panel_v1.csv"
    )
    pc_specs = read_csv(PROJECT / "data/targeted_pc_specs_v0/targeted_pc_specs_summary_v0.csv")
    semantic_summary = read_json(PROJECT / "data/pc_semantic_ontology_overlap_v0/package_summary.json")
    semantic_examples = read_csv(
        PROJECT / "data/pc_semantic_ontology_overlap_v0/pc_cross_corpus_semantic_ontology_overlap_v0.csv"
    )
    pc_case_crosswalk = read_csv(
        PROJECT / "data/pc_family_neighborhoods_v0/pc_family_case_study_crosswalk_v0.csv"
    )
    pc_audit = read_csv(PROJECT / "data/pc_family_neighborhoods_v0/pc_case_study_manual_audit_summary_v0.csv")
    full_text_summary = read_csv(PROJECT / "data/full_text_feasibility_v0/package_summary_v0.csv")
    full_text_rows = read_csv(PROJECT / "data/full_text_feasibility_v0/full_text_hf_gptoss_summary_v0.csv")
    citation_summary = read_csv(PROJECT / "data/citation_benchmark_post_recall_v1/citation_benchmark_post_recall_summary_v1.csv")
    citation_regression = read_csv(PROJECT / "data/citation_benchmark_post_recall_v1/citation_regression_summary_post_recall_v1.csv")
    citation_features = read_csv(
        PROJECT / "data/citation_benchmark_post_recall_v1/citation_selected_feature_associations_post_recall_v1.csv"
    )
    bridge_families = read_csv(PROJECT / "data/cross_sectional_bridge_dataset_v0/bridge_family_dataset.csv")
    bridge_summary = read_csv(PROJECT / "data/cross_sectional_bridge_dataset_v0/bridge_type_summary.csv")

    node_counts = {row["final_analysis_role"]: as_int(row.get("nodes")) for row in graph_nodes}
    edge_counts = {row["final_analysis_role"]: as_int(row.get("edges")) for row in graph_edges}
    strict = as_int(post_summary.get("strict_anchor_papers", 908))
    high_promoted = as_int(post_summary.get("high_priority_review_promoted_anchor_papers", 40))
    medium_clean = as_int(post_summary.get("medium_recall_clean_promoted_anchor_papers", 20))
    medium_orthodox = as_int(post_summary.get("medium_recall_orthodox_promoted_anchor_papers", 44))
    medium_extended = as_int(post_summary.get("medium_recall_extended_promoted_anchor_papers", 6))
    medium_promoted = medium_clean + medium_orthodox
    pre_recall = as_int(post_summary.get("pre_recall_anchor_papers", strict + high_promoted))
    anchors = as_int(post_summary.get("conservative_post_recall_anchor_papers", strict + high_promoted + medium_promoted))
    sensitivity = as_int(post_summary.get("broader_post_recall_anchor_papers", anchors + medium_extended))
    sensitivity_additions = max(0, sensitivity - anchors)
    context_papers = as_int(post_summary.get("context_papers", 1109))
    active_graph = as_int(post_summary.get("active_papers", anchors + context_papers))

    denominators = [
        {
            "name": "Strict anchors",
            "count": strict,
            "description": "Papers that pass the strongest factor-investing screen.",
            "use": "High-precision starting target set.",
        },
        {
            "name": "High-priority promoted anchors",
            "count": high_promoted,
            "description": "Reviewed target papers recovered from the first neighborhood review.",
            "use": "Adds clear misses while preserving labels.",
        },
        {
            "name": "Medium-recall promoted anchors",
            "count": medium_promoted,
            "description": "Additional target papers recovered from the medium-priority recall review.",
            "use": "Newest recall additions inside the main denominator.",
        },
        {
            "name": "Conservative post-recall anchors",
            "count": anchors,
            "description": "Strict anchors plus high-priority and medium-recall promoted anchors.",
            "use": "Main denominator for methodology and citation work.",
        },
        {
            "name": "Sensitivity-only additions",
            "count": sensitivity_additions,
            "description": "Borderline medium-recall additions kept outside the main denominator.",
            "use": "Appendix or sensitivity checks.",
        },
        {
            "name": "Context papers",
            "count": context_papers,
            "description": "Nearby graph papers used for interpretation.",
            "use": "Neighborhood context, not counted as target papers.",
        },
        {
            "name": "Active graph",
            "count": active_graph,
            "description": "Main anchors, sensitivity additions, and context papers used in the current graph layer.",
            "use": "Input frame for PC-style neighborhood discovery.",
        },
    ]

    graph_layers = [
        {
            "role": "Strict anchor core",
            "nodes": node_counts.get("anchor_strict_core", 0),
            "edges": edge_counts.get("anchor_strict_core", 0),
            "description": "Concepts and relationships inside the strongest target-paper set.",
        },
        {
            "role": "High-priority promoted",
            "nodes": node_counts.get("anchor_review_promoted", 0),
            "edges": edge_counts.get("anchor_review_promoted", 0),
            "description": "Target papers recovered by the first review after the strict screen.",
        },
        {
            "role": "Medium-recall additions",
            "nodes": node_counts.get("anchor_recall_promoted_clean", 0)
            + node_counts.get("anchor_recall_promoted_orthodox", 0),
            "edges": edge_counts.get("anchor_recall_promoted_clean", 0)
            + edge_counts.get("anchor_recall_promoted_orthodox", 0),
            "description": "Newest target papers recovered by recall review.",
        },
        {
            "role": "Graph neighborhood",
            "nodes": node_counts.get("graph_neighborhood", 0),
            "edges": edge_counts.get("graph_neighborhood", 0),
            "description": "Nearby concepts that help interpret the target literature.",
        },
        {
            "role": "Close context",
            "nodes": node_counts.get("graph_context_close", 0),
            "edges": edge_counts.get("graph_context_close", 0),
            "description": "Close but non-target papers kept for context.",
        },
    ]

    strict_methodology = [
        {
            "feature_name": row.get("feature_name", ""),
            "feature": row["feature_label"],
            "layer": row["measurement_layer"],
            "de_prado_link": row["de_prado_link"],
            "interpretation": row.get(
                "interpretation",
                "Current graph-derived signal; interpretation is documented in the paper methods.",
            ),
            "papers": as_int(row["papers"]),
            "count": as_int(row["paper_count"]),
            "share": as_float(row["paper_share"]),
        }
        for row in methodology
        if row.get("analysis_role") == "combined_conservative_post_recall_anchor"
    ]
    strict_methodology.sort(key=lambda row: row["share"], reverse=True)

    def truthy(row: dict[str, str], key: str) -> bool:
        return str(row.get(key, "")).lower() in {"true", "1", "yes"}

    conservative_methodology_rows = [
        row for row in methodology_panel if truthy(row, "anchor_in_conservative_post_recall")
    ]

    def count_any(keys: list[str]) -> int:
        return sum(any(truthy(row, key) for key in keys) for row in conservative_methodology_rows)

    def crosswalk_row(
        item: str,
        status: str,
        proxy: str,
        keys: list[str] | None,
        boundary: str,
    ) -> dict[str, Any]:
        count = count_any(keys) if keys else None
        denominator = len(conservative_methodology_rows)
        return {
            "item": item,
            "status": status,
            "proxy": proxy,
            "papers": count,
            "share": None if count is None or denominator == 0 else count / denominator,
            "boundary": boundary,
        }

    deprado_crosswalk = [
        crosswalk_row(
            "Causal framing / mechanisms",
            "Graph-visible",
            "Causal-presentation and mechanism edge attributes",
            ["has_causal_presentation", "has_mechanism_edge"],
            "Useful for claim mapping; not proof of formal causal discovery.",
        ),
        crosswalk_row(
            "Identification / adjustment",
            "Partly visible",
            "Identification-design, exogenous-variation, and adjustment text",
            [
                "has_identification_design_visible",
                "has_exogenous_variation_visible",
                "textsupp_controls_adjustment",
            ],
            "Exact adjustment sets usually need full text.",
        ),
        crosswalk_row(
            "Predictive validation",
            "Partly visible",
            "Forecasting, robustness, and validation-text signals",
            ["has_forecasting_edge", "has_robustness_edge", "textsupp_validation"],
            "Broad validation is visible; design details need full text.",
        ),
        crosswalk_row(
            "Variable selection",
            "Full-text target",
            "Variable and feature-selection text",
            ["textsupp_variable_selection"],
            "Usually a methods-section, table, or appendix detail.",
        ),
        crosswalk_row(
            "Portfolio construction",
            "Mostly full text",
            "Portfolio-implementation text",
            ["textsupp_portfolio_implementation"],
            "Abstract-level evidence is thin.",
        ),
        crosswalk_row(
            "Backtesting methodology",
            "Full-text target",
            "Backtest, historical-simulation, and stress-test text",
            ["textsupp_backtesting"],
            "Abstract graph strongly undercounts this central due-diligence object.",
        ),
        crosswalk_row(
            "Multiple-testing adjustment",
            "Full-text target",
            "Multiple-testing, data-snooping, FDR, and false-discovery text",
            ["textsupp_multiple_testing"],
            "Abstract graph strongly undercounts this central factor-testing object.",
        ),
        crosswalk_row(
            "Transparency / reproducibility",
            "Not measured yet",
            "No stable current field",
            None,
            "Needs code, data, appendix, or replication-material evidence.",
        ),
    ]

    def methodology_examples(feature_name: str, limit: int = 6) -> list[dict[str, Any]]:
        matched = [
            row
            for row in conservative_methodology_rows
            if truthy(row, feature_name)
        ]
        matched.sort(
            key=lambda row: (
                as_int(row.get("methodology_signal_count")),
                as_int(row.get("publication_year")),
                row.get("title", ""),
            ),
            reverse=True,
        )
        return [
            {
                "title": row.get("title"),
                "year": as_int(row.get("publication_year")),
                "source": row.get("source_display_name"),
                "role": row.get("final_analysis_role") or row.get("analysis_role"),
                "family": clean_label(row.get("anchor_family"))
                or clean_label(row.get("strict_family"))
                or clean_label(row.get("final_analysis_role"))
                or clean_label(row.get("analysis_role")),
                "signal_count": as_int(row.get("methodology_signal_count")),
            }
            for row in matched[:limit]
        ]

    methodology_explorer = [
        {
            "feature_name": row["feature_name"],
            "feature": row["feature"],
            "layer": row["layer"],
            "de_prado_link": row["de_prado_link"],
            "papers": row["count"],
            "share": row["share"],
            "examples": methodology_examples(row["feature_name"]),
        }
        for row in strict_methodology
    ]
    methodology_order = {
        "has_causal_presentation": 0,
        "has_conditioning_scope_signal": 1,
        "has_mechanism_edge": 2,
        "has_empirical_design_visible": 3,
        "has_identification_design_visible": 4,
        "has_robustness_edge": 5,
        "has_forecasting_edge": 6,
        "textsupp_portfolio_implementation": 7,
        "textsupp_backtesting": 8,
        "textsupp_multiple_testing": 9,
        "textsupp_variable_selection": 10,
        "textsupp_controls_adjustment": 11,
        "textsupp_validation": 12,
        "has_statistical_significance_visible": 13,
    }
    methodology_explorer.sort(
        key=lambda row: (methodology_order.get(row.get("feature_name", ""), 99), -row.get("share", 0))
    )

    source_comparison = [
        {
            "source": "FrontierGraph",
            "gives": "Broad paper discovery and title/abstract research graphs.",
            "boundary": "Too thin for many methods-section and appendix details.",
        },
        {
            "source": "Causal Claims in Economics",
            "gives": "Smaller full-text graph source for comparison and replication.",
            "boundary": "CEPR/NBER working-paper universe, not the published-paper target corpus.",
        },
        {
            "source": "New target-paper PDFs",
            "gives": "Future high-resolution measurement of methodology and implementation details.",
            "boundary": "Best source, but costly to acquire and process at scale.",
        },
    ]

    pc_runs = []
    for row in pc_specs:
        corpus, features, threshold = label_from_spec(row.get("spec_name", ""))
        pc_runs.append(
            {
                "spec": row.get("spec_name"),
                "corpus": corpus,
                "features": features,
                "threshold": threshold,
                "observations": as_int(row.get("observations")),
                "selected_variables": as_int(row.get("selected_variables")),
                "edges": as_int(row.get("pc_edges")),
                "directed_edges": as_int(row.get("directed_or_partly_directed_edges")),
                "use": "Neighborhood discovery, not causal proof.",
            }
        )

    both_semantic = [
        {
            "pair": row.get("semantic_pair"),
            "frontiergraph_edges": as_int(row.get("frontiergraph_edges")),
            "causalclaims_edges": as_int(row.get("causalclaims_edges")),
            "status": row.get("overlap_status"),
        }
        for row in semantic_examples
        if row.get("overlap_status") == "both_corpora"
    ][:6]

    pc_audit_by_case: dict[str, dict[str, Any]] = {}
    for row in pc_audit:
        case_id = row.get("case_id", "")
        corpus = row.get("corpus", "")
        if not case_id or not corpus:
            continue
        slot = pc_audit_by_case.setdefault(case_id, {})
        corpus_slot = slot.setdefault(
            corpus,
            {"strong_examples": 0, "candidates": 0, "not_yet": 0, "background_only": 0, "judgments": []},
        )
        corpus_slot["strong_examples"] += as_int(row.get("strong_examples"))
        corpus_slot["candidates"] += as_int(row.get("candidates"))
        corpus_slot["not_yet"] += as_int(row.get("not_yet"))
        corpus_slot["background_only"] += as_int(row.get("background_only"))
        corpus_slot["judgments"].append(row.get("audit_judgment"))

    pc_neighborhoods = []
    for row in pc_case_crosswalk:
        case_id = row.get("case_id", "")
        pc_neighborhoods.append(
            {
                "case_id": case_id,
                "label": pc_case_label(case_id),
                "family_pair": row.get("family_pair", "").replace("_", " "),
                "frontiergraph_edges": as_int(row.get("FrontierGraph")),
                "causalclaims_edges": as_int(row.get("CausalClaims")),
                "frontiergraph_audit": pc_audit_by_case.get(case_id, {}).get("FrontierGraph", {}),
                "causalclaims_audit": pc_audit_by_case.get(case_id, {}).get("CausalClaims", {}),
            }
        )
    pc_case_order = {
        "liquidity_risk": 0,
        "macro_returns": 1,
        "factors_returns": 2,
        "methods_methods": 3,
    }
    pc_neighborhoods.sort(key=lambda row: pc_case_order.get(row.get("case_id", ""), 99))

    full_text = {
        "sample_n": as_int(find_metric(full_text_summary, "sample_n", "50")),
        "downloaded": as_int(find_metric(full_text_summary, "pdf_status_downloaded_n", "30")),
        "scored": as_int(find_metric(full_text_summary, "scoring_status_scored_hf_gptoss_v0_n", "30")),
        "reveals_missed": as_int(find_metric(full_text_summary, "full_text_added_value_reveals_missed_signal_n", "20")),
        "refines": as_int(find_metric(full_text_summary, "full_text_added_value_refines_abstract_signal_n", "9")),
        "none": as_int(find_metric(full_text_summary, "full_text_added_value_none_n", "1")),
        "estimated_cost_usd": as_float(find_metric(full_text_summary, "hf_gptoss_estimated_cost_usd", "0.032")),
        "examples": [
            {
                "title": row.get("title"),
                "source": row.get("source_display_name"),
                "added_value": row.get("full_text_added_value", "").replace("_", " "),
                "substantive_fields": as_int(row.get("substantive_signal_fields")),
                "confidence": row.get("overall_confidence"),
            }
            for row in full_text_rows[:6]
        ],
    }

    citation_row = next(
        (row for row in citation_summary if row.get("denominator") == "conservative_post_recall_1012"),
        citation_summary[0] if citation_summary else {},
    )
    regression = {
        row.get("model"): row
        for row in citation_regression
        if row.get("denominator") == "conservative_post_recall_1012"
    }
    citation = {
        "anchors": as_int(citation_row.get("papers", anchors)),
        "matched": as_int(citation_row.get("openalex_matches", 0)),
        "median_citations": as_float(citation_row.get("median_citations", 0)),
        "mean_citations": as_float(citation_row.get("mean_citations", 0)),
        "median_per_year": as_float(citation_row.get("median_citations_per_year", 0)),
        "baseline_r2": as_float(regression.get("Baseline: age + graph size + anchor layer", {}).get("adj_r_squared", 0)),
        "methodology_r2": as_float(regression.get("Add methodology-signal count", {}).get("adj_r_squared", 0)),
        "domain_r2": as_float(regression.get("Add methodology-domain indicators", {}).get("adj_r_squared", 0)),
    }
    citation["feature_associations"] = [
        {
            "feature": row.get("feature_label"),
            "papers": as_int(row.get("papers_with_feature")),
            "median_with": as_float(row.get("median_cpy_with")),
            "median_without": as_float(row.get("median_cpy_without")),
            "adjusted_percent": as_float(row.get("approx_percent_difference")),
            "p_value": as_float(row.get("adjusted_p_value")),
        }
        for row in citation_features
        if row.get("denominator") == "conservative_post_recall_1012"
    ]

    family_rows = []
    for row in bridge_families:
        family_rows.append(
            {
                "family": row.get("product_family_label"),
                "status": clean_label(row.get("current_status")),
                "status_raw": row.get("current_status"),
                "rows": as_int(row.get("product_rows")),
                "coherent_rows": as_int(row.get("coherent_rows")),
                "coherent_share": as_float(row.get("coherent_share")),
                "product_evidence": row.get("product_side_evidence"),
                "academic_evidence": row.get("academic_side_evidence"),
                "nearest_academic_object": "" if row.get("nearest_academic_object") == "NA" else row.get("nearest_academic_object"),
                "bridge_type": bridge_label(row.get("bridge_type", "")),
                "reason": row.get("bridge_reason"),
                "caveat": row.get("main_caveat"),
                "confidence": clean_label(row.get("confidence_from_source")),
            }
        )

    product_bridge = {
        "summary": [
            {
                "bridge_type": bridge_label(row.get("bridge_type", "")),
                "status": row.get("current_status"),
                "families": as_int(row.get("families")),
            }
            for row in bridge_summary
        ],
        "families": family_rows,
    }

    home_metrics = [
        {"value": f"{anchors:,}", "label": "anchor papers"},
        {"value": f"{active_graph:,}", "label": "active graph papers"},
        {"value": f"{citation['matched']:,}", "label": "OpenAlex citation matches"},
        {"value": f"{full_text['scored']:,}", "label": "scored PDFs"},
    ]

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "snapshot": {
            "title": "Finance Atlas",
            "subtitle": "Graph-first map of factor-investing research, current denominators, and downstream outcome modules.",
            "anchors": anchors,
            "strict_anchors": strict,
            "pre_recall_anchors": pre_recall,
            "high_priority_promoted_anchors": high_promoted,
            "medium_recall_promoted_anchors": medium_promoted,
            "sensitivity_additions": sensitivity_additions,
            "broader_post_recall_anchors": sensitivity,
            "active_graph": active_graph,
        },
        "home_metrics": home_metrics,
        "denominators": denominators,
        "graph_layers": graph_layers,
        "methodology": strict_methodology,
        "methodology_explorer": methodology_explorer,
        "deprado_crosswalk": deprado_crosswalk,
        "source_comparison": source_comparison,
        "pc_runs": pc_runs,
        "pc_audit": pc_audit,
        "pc_neighborhoods": pc_neighborhoods,
        "semantic_overlap": {
            "summary": semantic_summary,
            "examples": both_semantic,
        },
        "recall": {
            "known_papers": as_int(recall_summary.get("known_papers", 20)),
            "known_covered_as_anchor": as_int(recall_summary.get("known_covered_as_anchor", 8)),
            "known_found_outside_anchor": as_int(recall_summary.get("known_found_outside_anchor", 7)),
            "known_not_found": as_int(recall_summary.get("known_not_found", 5)),
            "medium_priority_review_queue": as_int(recall_summary.get("medium_priority_review_queue", 404)),
            "context_heavy_review_queue": as_int(recall_summary.get("context_heavy_review_queue", 1179)),
        },
        "validation": {
            "reviewed_anchor_evidence": as_int(anchor_summary.get("manually_reviewed_anchor_evidence", 60)),
            "reviewed_anchor_targets": as_int(anchor_summary.get("manually_reviewed_anchor_targets", 59)),
            "reviewed_anchor_false_positive": as_int(anchor_summary.get("manually_reviewed_anchor_false_positive", 0)),
        },
        "full_text": full_text,
        "citation": citation,
        "product_bridge": product_bridge,
        "outcome_modules": [
            {
                "name": "Citation benchmark",
                "status": "available",
                "description": "Low-friction external outcome for the current anchor set.",
            },
            {
                "name": "Product adoption",
                "status": "designed, not scaled",
                "description": "Uses SEC product graphs and bridge types. Current evidence is a design pilot.",
            },
            {
                "name": "Factor performance",
                "status": "parked",
                "description": "Needs audited paper-to-factor and paper-to-state links before it can be a main result.",
            },
        ],
    }


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(build_site_data(), indent=2), encoding="utf-8")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
