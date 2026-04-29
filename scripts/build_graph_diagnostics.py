from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import networkx as nx
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT.parent / "asset_pricing_theme_map/data/derived/theme_map_descriptive_v0"
JOIN_SOURCE = ROOT.parent / "asset_pricing_theme_map/data/derived/theme_map_ontology_join_v0"
OUT = ROOT / "data/analysis/graph_diagnostics_v0"

COMPLETE_YEAR_CUTOFF = 2023
BETWEENNESS_SAMPLE_SIZE = 500
BETWEENNESS_SEED = 20260429
DECADES = [1970, 1980, 1990, 2000, 2010, 2020]


def clean(value: Any) -> str:
    if value is None or pd.isna(value):
        return ""
    text = str(value).strip()
    return "" if text.lower() in {"", "na", "nan", "none", "null"} else text


def safe_float(value: Any) -> float:
    try:
        if value is None or pd.isna(value):
            return 0.0
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def safe_int(value: Any) -> int:
    return int(round(safe_float(value)))


def write_csv(frame: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False)


def build_edge_weights(edges: pd.DataFrame) -> pd.DataFrame:
    usable = edges[
        (edges["source_onto_id"].map(clean) != "")
        & (edges["target_onto_id"].map(clean) != "")
        & (edges["source_onto_id"] != edges["target_onto_id"])
    ].copy()
    usable["edge_pair_label"] = (
        usable["source_concept_display_label"].map(clean)
        + " -> "
        + usable["target_concept_display_label"].map(clean)
    )
    grouped = (
        usable.groupby(["source_onto_id", "target_onto_id"], as_index=False)
        .agg(
            source_label=("source_concept_display_label", lambda x: x.map(clean).replace("", pd.NA).dropna().iloc[0]),
            target_label=("target_concept_display_label", lambda x: x.map(clean).replace("", pd.NA).dropna().iloc[0]),
            source_field=("source_field_primary", lambda x: x.map(clean).replace("", pd.NA).dropna().mode().iloc[0] if not x.map(clean).replace("", pd.NA).dropna().empty else ""),
            target_field=("target_field_primary", lambda x: x.map(clean).replace("", pd.NA).dropna().mode().iloc[0] if not x.map(clean).replace("", pd.NA).dropna().empty else ""),
            paper_count=("custom_id", "nunique"),
            edge_rows=("edge_id", "count"),
            most_common_role=("edge_role", lambda x: x.map(clean).replace("", pd.NA).dropna().mode().iloc[0] if not x.map(clean).replace("", pd.NA).dropna().empty else ""),
            most_common_relationship=("relationship_type", lambda x: x.map(clean).replace("", pd.NA).dropna().mode().iloc[0] if not x.map(clean).replace("", pd.NA).dropna().empty else ""),
            example_claim_text=("claim_text", lambda x: next((clean(v) for v in x if clean(v)), "")),
            example_paper_id=("custom_id", lambda x: next((clean(v) for v in x if clean(v)), "")),
        )
        .sort_values(["paper_count", "edge_rows"], ascending=[False, False])
    )
    grouped["edge_pair_label"] = grouped["source_label"] + " -> " + grouped["target_label"]
    return grouped


def graph_from_edges(edge_weights: pd.DataFrame) -> nx.DiGraph:
    graph = nx.DiGraph()
    for row in edge_weights.itertuples(index=False):
        graph.add_edge(
            row.source_onto_id,
            row.target_onto_id,
            weight=float(row.paper_count),
            edge_rows=float(row.edge_rows),
        )
    return graph


def build_concept_lookup(nodes: pd.DataFrame, concept_decade: pd.DataFrame) -> pd.DataFrame:
    lookup = (
        nodes[nodes["onto_id"].map(clean) != ""]
        .groupby("onto_id", as_index=False)
        .agg(
            concept_label=("concept_display_label", lambda x: next((clean(v) for v in x if clean(v)), "")),
            field_primary=("field_primary", lambda x: x.map(clean).replace("", pd.NA).dropna().mode().iloc[0] if not x.map(clean).replace("", pd.NA).dropna().empty else ""),
            score_band=("score_band", lambda x: x.map(clean).replace("", pd.NA).dropna().mode().iloc[0] if not x.map(clean).replace("", pd.NA).dropna().empty else ""),
            node_rows=("node_id", "count"),
            paper_count=("custom_id", "nunique"),
        )
    )
    decade_summary = (
        concept_decade.groupby("onto_id", as_index=False)
        .agg(first_decade=("decade", "min"), last_decade=("decade", "max"))
    )
    return lookup.merge(decade_summary, on="onto_id", how="left")


def centrality_table(graph: nx.DiGraph, lookup: pd.DataFrame) -> pd.DataFrame:
    weighted_degree = dict(graph.degree(weight="weight"))
    weighted_in_degree = dict(graph.in_degree(weight="weight"))
    weighted_out_degree = dict(graph.out_degree(weight="weight"))
    unweighted_degree = dict(graph.degree())
    pagerank = nx.pagerank(graph, weight="weight", alpha=0.85, max_iter=200)

    undirected = graph.to_undirected()
    sample_size = min(BETWEENNESS_SAMPLE_SIZE, undirected.number_of_nodes())
    betweenness = nx.betweenness_centrality(
        undirected,
        k=sample_size,
        seed=BETWEENNESS_SEED,
        weight=None,
        normalized=True,
    )

    rows = []
    for node in graph.nodes:
        rows.append(
            {
                "onto_id": node,
                "degree_weighted": weighted_degree.get(node, 0.0),
                "in_degree_weighted": weighted_in_degree.get(node, 0.0),
                "out_degree_weighted": weighted_out_degree.get(node, 0.0),
                "degree_unweighted": unweighted_degree.get(node, 0),
                "pagerank": pagerank.get(node, 0.0),
                "betweenness_approx": betweenness.get(node, 0.0),
            }
        )
    out = pd.DataFrame(rows).merge(lookup, on="onto_id", how="left")
    out["neighbor_field_count"] = out["onto_id"].map(lambda node: neighbor_field_count(graph, node, lookup))
    out["bridge_score"] = out["betweenness_approx"] * (1 + out["neighbor_field_count"].fillna(0))
    return out.sort_values(["pagerank", "degree_weighted"], ascending=[False, False])


def neighbor_field_count(graph: nx.DiGraph, node: str, lookup: pd.DataFrame) -> int:
    field_map = lookup.set_index("onto_id")["field_primary"].to_dict()
    neighbors = set(graph.predecessors(node)) | set(graph.successors(node))
    fields = {clean(field_map.get(neighbor, "")) for neighbor in neighbors}
    fields.discard("")
    return len(fields)


def decade_centrality(edge_weights: pd.DataFrame, edges: pd.DataFrame, papers: pd.DataFrame, lookup: pd.DataFrame) -> pd.DataFrame:
    paper_decade = papers[["custom_id", "decade"]].copy()
    usable = edges[
        (edges["source_onto_id"].map(clean) != "")
        & (edges["target_onto_id"].map(clean) != "")
        & (edges["source_onto_id"] != edges["target_onto_id"])
    ].merge(paper_decade, on="custom_id", how="left", validate="many_to_one")

    rows = []
    label_map = lookup.set_index("onto_id")[["concept_label", "field_primary"]].to_dict("index")
    for decade in DECADES:
        decade_edges = usable[usable["decade"] == decade]
        grouped = (
            decade_edges.groupby(["source_onto_id", "target_onto_id"], as_index=False)
            .agg(paper_count=("custom_id", "nunique"), edge_rows=("edge_id", "count"))
        )
        if grouped.empty:
            continue
        graph = graph_from_edges(
            grouped.assign(
                source_label="",
                target_label="",
                source_field="",
                target_field="",
                most_common_role="",
                most_common_relationship="",
                example_claim_text="",
                example_paper_id="",
            )
        )
        pagerank = nx.pagerank(graph, weight="weight", alpha=0.85, max_iter=200)
        weighted_degree = dict(graph.degree(weight="weight"))
        for node in graph.nodes:
            meta = label_map.get(node, {})
            rows.append(
                {
                    "decade": decade,
                    "onto_id": node,
                    "concept_label": meta.get("concept_label", ""),
                    "field_primary": meta.get("field_primary", ""),
                    "degree_weighted": weighted_degree.get(node, 0.0),
                    "pagerank": pagerank.get(node, 0.0),
                }
            )
    return pd.DataFrame(rows).sort_values(["decade", "pagerank", "degree_weighted"], ascending=[True, False, False])


def centrality_change(decade: pd.DataFrame) -> pd.DataFrame:
    id_cols = ["onto_id", "concept_label", "field_primary"]
    page = decade.pivot_table(index=id_cols, columns="decade", values="pagerank", fill_value=0.0, aggfunc="max").reset_index()
    degree = decade.pivot_table(index=["onto_id"], columns="decade", values="degree_weighted", fill_value=0.0, aggfunc="max").reset_index()
    rename_page = {d: f"pagerank_{d}s" for d in DECADES if d in page.columns}
    rename_degree = {d: f"degree_weighted_{d}s" for d in DECADES if d in degree.columns}
    out = page.rename(columns=rename_page).merge(degree.rename(columns=rename_degree), on="onto_id", how="left")
    for decade_value in DECADES:
        if f"pagerank_{decade_value}s" not in out.columns:
            out[f"pagerank_{decade_value}s"] = 0.0
        if f"degree_weighted_{decade_value}s" not in out.columns:
            out[f"degree_weighted_{decade_value}s"] = 0.0
    out["pagerank_change_2020s_vs_2000s"] = out["pagerank_2020s"] - out["pagerank_2000s"]
    out["pagerank_change_2020s_vs_2010s"] = out["pagerank_2020s"] - out["pagerank_2010s"]
    out["degree_change_2020s_vs_2000s"] = out["degree_weighted_2020s"] - out["degree_weighted_2000s"]
    out["degree_change_2020s_vs_2010s"] = out["degree_weighted_2020s"] - out["degree_weighted_2010s"]
    out["max_pagerank"] = out[[f"pagerank_{d}s" for d in DECADES]].max(axis=1)
    out["max_degree_weighted"] = out[[f"degree_weighted_{d}s" for d in DECADES]].max(axis=1)
    return out.sort_values(["pagerank_change_2020s_vs_2000s", "pagerank_2020s"], ascending=[False, False])


def centrality_trajectories(decade: pd.DataFrame, central: pd.DataFrame, change: pd.DataFrame) -> pd.DataFrame:
    selected = set(central.head(20)["onto_id"])
    selected.update(change.head(20)["onto_id"])
    selected.update(change.sort_values("pagerank_change_2020s_vs_2000s").head(12)["onto_id"])
    selected.update(central.sort_values(["bridge_score", "pagerank"], ascending=[False, False]).head(20)["onto_id"])
    out = decade[decade["onto_id"].isin(selected)].copy()
    return out.sort_values(["onto_id", "decade"])


def undirected_graph_from_edges(edge_weights: pd.DataFrame) -> nx.Graph:
    graph = nx.Graph()
    for row in edge_weights.itertuples(index=False):
        source = row.source_onto_id
        target = row.target_onto_id
        weight = float(row.paper_count)
        if graph.has_edge(source, target):
            graph[source][target]["weight"] += weight
            graph[source][target]["edge_rows"] += float(row.edge_rows)
        else:
            graph.add_edge(source, target, weight=weight, edge_rows=float(row.edge_rows))
    return graph


def community_tables(edge_weights: pd.DataFrame, central: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    graph = undirected_graph_from_edges(edge_weights)
    communities = nx.algorithms.community.louvain_communities(
        graph,
        weight="weight",
        seed=BETWEENNESS_SEED,
        resolution=1.0,
    )
    central_lookup = central.set_index("onto_id").to_dict("index")
    assignments = {}
    raw_summaries = []
    for raw_id, nodes_in_community in enumerate(communities):
        nodes = list(nodes_in_community)
        subgraph = graph.subgraph(nodes)
        members = []
        field_counts: dict[str, int] = {}
        for node in nodes:
            meta = central_lookup.get(node, {})
            field = clean(meta.get("field_primary", "")) or "unknown"
            field_counts[field] = field_counts.get(field, 0) + 1
            members.append(
                {
                    "onto_id": node,
                    "concept_label": clean(meta.get("concept_label", "")),
                    "field_primary": field,
                    "paper_count": safe_int(meta.get("paper_count", 0)),
                    "pagerank": safe_float(meta.get("pagerank", 0)),
                    "degree_weighted": safe_float(meta.get("degree_weighted", 0)),
                    "bridge_score": safe_float(meta.get("bridge_score", 0)),
                }
            )
        members_sorted = sorted(members, key=lambda x: (x["pagerank"], x["degree_weighted"], x["paper_count"]), reverse=True)
        internal_weight = sum(data.get("weight", 0.0) for _, _, data in subgraph.edges(data=True))
        total_papers = sum(member["paper_count"] for member in members)
        raw_summaries.append(
            {
                "raw_community_id": raw_id,
                "node_count": len(nodes),
                "internal_edge_count": subgraph.number_of_edges(),
                "internal_edge_weight": internal_weight,
                "member_paper_count_sum": total_papers,
                "top_concepts": members_sorted[:10],
                "field_counts": field_counts,
            }
        )

    ranked = sorted(raw_summaries, key=lambda x: (x["internal_edge_weight"], x["node_count"]), reverse=True)
    community_id_map = {item["raw_community_id"]: rank + 1 for rank, item in enumerate(ranked)}
    rows = []
    member_rows = []
    for item in ranked:
        community_id = community_id_map[item["raw_community_id"]]
        top_concepts = item["top_concepts"]
        top_labels = [member["concept_label"] for member in top_concepts if member["concept_label"]]
        field_counts = sorted(item["field_counts"].items(), key=lambda kv: kv[1], reverse=True)
        rows.append(
            {
                "community_id": community_id,
                "community_label": " / ".join(top_labels[:3]),
                "node_count": item["node_count"],
                "internal_edge_count": item["internal_edge_count"],
                "internal_edge_weight": item["internal_edge_weight"],
                "member_paper_count_sum": item["member_paper_count_sum"],
                "top_field": field_counts[0][0] if field_counts else "",
                "top_fields_json": json.dumps([{"field": field, "count": count} for field, count in field_counts[:6]], ensure_ascii=False),
                "top_concepts_json": json.dumps(top_concepts[:8], ensure_ascii=False),
            }
        )
        for member in top_concepts:
            member_rows.append({"community_id": community_id, **member})

    return pd.DataFrame(rows), pd.DataFrame(member_rows)


def field_bridge_edges(edge_weights: pd.DataFrame) -> pd.DataFrame:
    bridges = edge_weights[
        (edge_weights["source_field"].map(clean) != "")
        & (edge_weights["target_field"].map(clean) != "")
        & (edge_weights["source_field"] != edge_weights["target_field"])
    ].copy()
    bridges["field_pair"] = bridges["source_field"] + " -> " + bridges["target_field"]
    return bridges.sort_values(["paper_count", "edge_rows"], ascending=[False, False])


def field_bridge_summary(bridge_edges: pd.DataFrame) -> pd.DataFrame:
    return (
        bridge_edges.groupby("field_pair", as_index=False)
        .agg(
            edge_pair_count=("edge_pair_label", "nunique"),
            paper_count=("paper_count", "sum"),
            edge_rows=("edge_rows", "sum"),
            top_edge_pair=("edge_pair_label", lambda x: next(iter(x), "")),
        )
        .sort_values(["paper_count", "edge_pair_count"], ascending=[False, False])
    )


def concept_change_buckets(concept_decade: pd.DataFrame) -> dict[str, pd.DataFrame]:
    pivot = concept_decade.pivot_table(
        index=["onto_id", "concept_display_label", "field_primary"],
        columns="decade",
        values="paper_share_in_decade",
        fill_value=0.0,
        aggfunc="max",
    ).reset_index()
    counts = concept_decade.pivot_table(
        index="onto_id",
        columns="decade",
        values="paper_count",
        fill_value=0,
        aggfunc="max",
    ).reset_index()
    for decade in DECADES:
        if decade not in pivot.columns:
            pivot[decade] = 0.0
        if decade not in counts.columns:
            counts[decade] = 0
    out = pivot.merge(counts, on="onto_id", suffixes=("_share", "_count"))
    rename = {}
    for col in out.columns:
        if isinstance(col, (int, float)) and int(col) in DECADES:
            rename[col] = f"share_{int(col)}s"
        text = str(col)
        if text.endswith("_share") and text.split("_", 1)[0].isdigit():
            rename[col] = f"share_{text.split('_', 1)[0]}s"
        if text.endswith("_count") and text.split("_", 1)[0].isdigit():
            rename[col] = f"paper_count_{text.split('_', 1)[0]}s"
    out = out.rename(columns=rename)

    for decade in DECADES:
        if f"share_{decade}s" not in out.columns:
            out[f"share_{decade}s"] = 0.0
        if f"paper_count_{decade}s" not in out.columns:
            out[f"paper_count_{decade}s"] = 0
    out["rise_2020s_vs_2000s"] = out["share_2020s"] - out["share_2000s"]
    out["fall_2020s_vs_2000s"] = out["share_2000s"] - out["share_2020s"]
    out["max_share"] = out[[f"share_{d}s" for d in DECADES]].max(axis=1)
    out["mean_share"] = out[[f"share_{d}s" for d in DECADES]].mean(axis=1)
    count_cols = [f"paper_count_{d}s" for d in DECADES]
    out["max_decade_paper_count"] = out[count_cols].max(axis=1)
    out["max_decade"] = out[[f"share_{d}s" for d in DECADES]].idxmax(axis=1).str.extract(r"(\d{4})")[0]
    out["spike_score"] = out["max_share"] / out["mean_share"].replace(0, math.nan)
    out["pre_2010_max_share"] = out[["share_1970s", "share_1980s", "share_1990s", "share_2000s"]].max(axis=1)
    out["post_2010_max_share"] = out[["share_2010s", "share_2020s"]].max(axis=1)
    out["min_1990_onward_share"] = out[["share_1990s", "share_2000s", "share_2010s", "share_2020s"]].min(axis=1)

    rising = out[out["paper_count_2020s"] >= 20].sort_values(
        ["rise_2020s_vs_2000s", "paper_count_2020s"], ascending=[False, False]
    )
    falling = out[out["paper_count_2000s"] >= 20].sort_values(
        ["fall_2020s_vs_2000s", "paper_count_2000s"], ascending=[False, False]
    )
    new_arrivals = out[(out["pre_2010_max_share"] <= 0.005) & (out["share_2020s"] >= 0.01)].sort_values(
        ["share_2020s", "paper_count_2020s"], ascending=[False, False]
    )
    persistent = out[(out["min_1990_onward_share"] >= 0.02) & (out["paper_count_2020s"] >= 30)].sort_values(
        ["mean_share", "paper_count_2020s"], ascending=[False, False]
    )
    spiky = out[(out["max_share"] >= 0.015) & (out["max_decade_paper_count"] >= 20) & (out["spike_score"] >= 2.2)].sort_values(
        ["spike_score", "max_share"], ascending=[False, False]
    )
    return {
        "rising": rising,
        "falling": falling,
        "new_arrivals": new_arrivals,
        "persistent": persistent,
        "spiky": spiky,
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    edges = pd.read_parquet(JOIN_SOURCE / "edge_ontology_join.parquet")
    nodes = pd.read_parquet(JOIN_SOURCE / "node_ontology_join.parquet")
    papers = pd.read_csv(JOIN_SOURCE / "paper_ontology_panel.csv", keep_default_na=False)
    papers["publication_year"] = pd.to_numeric(papers["publication_year"], errors="coerce").astype("Int64")
    papers = papers[papers["publication_year"].notna()].copy()
    papers["decade"] = (papers["publication_year"] // 10 * 10).astype("Int64")
    concept_decade = pd.read_csv(SOURCE / "concept_decade_panel.csv")

    edge_weights = build_edge_weights(edges)
    lookup = build_concept_lookup(nodes, concept_decade)
    graph = graph_from_edges(edge_weights)
    central = centrality_table(graph, lookup)
    decade = decade_centrality(edge_weights, edges, papers, lookup)
    change = centrality_change(decade)
    trajectories = centrality_trajectories(decade, central, change)
    community_summary, community_members = community_tables(edge_weights, central)
    bridges = field_bridge_edges(edge_weights)
    bridge_summary = field_bridge_summary(bridges)
    buckets = concept_change_buckets(concept_decade)

    write_csv(edge_weights, OUT / "canonical_edge_weights.csv")
    write_csv(central, OUT / "concept_centrality_overall.csv")
    write_csv(decade, OUT / "concept_centrality_by_decade.csv")
    write_csv(change, OUT / "concept_centrality_change.csv")
    write_csv(trajectories, OUT / "concept_centrality_trajectories.csv")
    write_csv(community_summary, OUT / "community_summary.csv")
    write_csv(community_members, OUT / "community_members_top.csv")
    write_csv(bridges, OUT / "field_bridge_edges.csv")
    write_csv(bridge_summary, OUT / "field_bridge_summary.csv")
    for name, frame in buckets.items():
        write_csv(frame, OUT / f"theme_{name}.csv")

    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": "within_materialized_finance_workspace",
        "graph_nodes": graph.number_of_nodes(),
        "graph_edges_non_self": graph.number_of_edges(),
        "input_edge_rows": int(edges.shape[0]),
        "non_self_canonical_edge_pairs": int(edge_weights.shape[0]),
        "community_count": int(community_summary.shape[0]),
        "betweenness_sample_size": min(BETWEENNESS_SAMPLE_SIZE, graph.number_of_nodes()),
        "betweenness_seed": BETWEENNESS_SEED,
        "top_pagerank": central[["concept_label", "field_primary", "pagerank", "degree_weighted"]].head(12).to_dict("records"),
        "top_bridges": central.sort_values(["bridge_score", "pagerank"], ascending=[False, False])[
            ["concept_label", "field_primary", "bridge_score", "betweenness_approx", "neighbor_field_count"]
        ]
        .head(12)
        .to_dict("records"),
    }
    (OUT / "package_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (OUT / "README.md").write_text(
        "\n".join(
            [
                "# Graph Diagnostics v0",
                "",
                "Within-finance graph diagnostics for Finance Atlas.",
                "",
                "This package uses the materialized finance workspace only. It does not yet compute global FrontierGraph centrality.",
                "",
                "Main outputs:",
                "",
                "- `concept_centrality_overall.csv`: weighted degree, in/out degree, PageRank, approximate betweenness, and bridge score.",
                "- `concept_centrality_by_decade.csv`: within-decade weighted degree and PageRank.",
                "- `concept_centrality_change.csv`: changes in PageRank and weighted degree across decades.",
                "- `concept_centrality_trajectories.csv`: decade centrality trajectories for selected important concepts.",
                "- `community_summary.csv`: Louvain communities in the within-finance concept graph.",
                "- `community_members_top.csv`: top concepts in each community.",
                "- `canonical_edge_weights.csv`: non-self canonical edge-pair weights.",
                "- `field_bridge_edges.csv`: cross-field canonical edge pairs.",
                "- `field_bridge_summary.csv`: cross-field field-pair summaries.",
                "- `theme_rising.csv`, `theme_falling.csv`, `theme_new_arrivals.csv`, `theme_persistent.csv`, `theme_spiky.csv`: concept-change diagnostics.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
