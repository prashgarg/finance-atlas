const state = {
  data: null,
  concepts: [],
  activeField: "all",
  activeTimeView: "volume",
  edgeRole: "all",
  includeSelfLinks: false,
  query: "",
  selectedConceptId: null,
};

const formatNumber = new Intl.NumberFormat("en-US");
const formatPercent = new Intl.NumberFormat("en-US", {
  maximumFractionDigits: 1,
  minimumFractionDigits: 0,
});

function asPercent(value) {
  return `${formatPercent.format(value * 100)}%`;
}

function shortText(value, length = 150) {
  if (!value) return "";
  return value.length > length ? `${value.slice(0, length - 1)}...` : value;
}

function metricCard(value, label) {
  return `<article class="metric"><strong>${value}</strong><span>${label}</span></article>`;
}

function niceLabel(value) {
  return String(value || "")
    .replaceAll("_", " ")
    .replace(/\b\w/g, (match) => match.toUpperCase());
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function renderMetrics() {
  const summary = state.data.summary;
  const grid = document.querySelector("#metric-grid");
  grid.innerHTML = [
    metricCard(formatNumber.format(summary.paper_count), "papers"),
    metricCard(formatNumber.format(summary.unique_concepts), "concepts"),
    metricCard(formatNumber.format(summary.unique_canonical_edge_pairs), "edge pairs"),
    metricCard(formatNumber.format(summary.factor_investing_count), "factor papers"),
  ].join("");
}

function filteredConcepts() {
  const query = state.query.trim().toLowerCase();
  return state.concepts.filter((concept) => {
    const matchesField = state.activeField === "all" || concept.field_primary === state.activeField;
    const matchesQuery =
      !query ||
      concept.label.toLowerCase().includes(query) ||
      concept.field_primary.toLowerCase().includes(query);
    return matchesField && matchesQuery;
  });
}

function renderConceptList() {
  const concepts = filteredConcepts().slice(0, 80);
  const count = document.querySelector("#concept-count");
  const list = document.querySelector("#concept-list");
  count.textContent = `${formatNumber.format(concepts.length)} shown`;

  if (!state.selectedConceptId && concepts.length) {
    state.selectedConceptId = concepts[0].id;
  }

  list.innerHTML = concepts
    .map((concept) => {
      const active = concept.id === state.selectedConceptId ? " active" : "";
      return `
        <button class="concept-row${active}" data-concept-id="${concept.id}">
          <strong>${concept.label}</strong>
          <span>${formatNumber.format(concept.paper_count)} papers · ${concept.field_primary}</span>
        </button>
      `;
    })
    .join("");

  list.querySelectorAll("[data-concept-id]").forEach((button) => {
    button.addEventListener("click", () => {
      state.selectedConceptId = button.dataset.conceptId;
      renderConceptList();
      renderConceptDetail();
    });
  });
}

function renderConceptDetail() {
  const panel = document.querySelector("#concept-detail");
  const concept =
    state.concepts.find((item) => item.id === state.selectedConceptId) || filteredConcepts()[0] || state.concepts[0];

  if (!concept) {
    panel.innerHTML = "<p>No concept selected.</p>";
    return;
  }

  state.selectedConceptId = concept.id;
  const maxShare = Math.max(...concept.decades.map((row) => row.share), 0.01);
  const decadeRows = concept.decades
    .map((row) => {
      const width = Math.max(2, (row.share / maxShare) * 100);
      return `
        <div class="decade-row">
          <span>${row.decade}s</span>
          <div class="bar-track"><div class="bar-fill" style="width: ${width}%"></div></div>
          <span>${asPercent(row.share)}</span>
        </div>
      `;
    })
    .join("");

  panel.innerHTML = `
    <span class="detail-kicker">${escapeHtml(concept.field_primary || "mapped concept")}</span>
    <h3>${escapeHtml(concept.label)}</h3>
    <div class="detail-stats">
      <div class="detail-stat"><strong>${formatNumber.format(concept.paper_count)}</strong><span>papers</span></div>
      <div class="detail-stat"><strong>${formatNumber.format(concept.node_rows)}</strong><span>node rows</span></div>
      <div class="detail-stat"><strong>${concept.score_band || "mapped"}</strong><span>mapping band</span></div>
    </div>
    <div class="mini-chart">${decadeRows}</div>
  `;
}

function renderRisingThemes() {
  const maxRise = Math.max(...state.data.rising_concepts.map((row) => row.rise_2020s_vs_2000s), 0.01);
  const rows = state.data.rising_concepts.slice(0, 18).map((row) => {
    const width = Math.max(2, (row.rise_2020s_vs_2000s / maxRise) * 100);
    return `
      <div class="rising-row">
        <span class="rising-name">${escapeHtml(row.label)}</span>
        <div class="bar-track"><div class="bar-fill" style="width: ${width}%"></div></div>
        <span class="rising-value">+${asPercent(row.rise_2020s_vs_2000s)}</span>
      </div>
    `;
  });
  document.querySelector("#rising-list").innerHTML = rows.join("");
}

function scalePoints(series, width, height, padding) {
  const xs = series.flatMap((line) => line.points.map((point) => point.x));
  const ys = series.flatMap((line) => line.points.map((point) => point.y));
  const minX = Math.min(...xs);
  const maxX = Math.max(...xs);
  const maxY = Math.max(...ys, 1);
  const usableWidth = width - padding.left - padding.right;
  const usableHeight = height - padding.top - padding.bottom;

  return {
    minX,
    maxX,
    maxY,
    xScale: (x) => padding.left + ((x - minX) / Math.max(1, maxX - minX)) * usableWidth,
    yScale: (y) => padding.top + usableHeight - (y / maxY) * usableHeight,
  };
}

function renderLineChart({ series, yFormatter = formatNumber.format, xTicks, yLabel }) {
  const width = 920;
  const height = 360;
  const padding = { top: 24, right: 28, bottom: 42, left: 64 };
  const colors = ["#2f6f4e", "#4e668f", "#c58d2d", "#8a5a44", "#7a5a9e", "#537a7a"];
  const scales = scalePoints(series, width, height, padding);
  const yTicks = [0, 0.25, 0.5, 0.75, 1].map((share) => scales.maxY * share);
  const ticks = xTicks || series[0].points.filter((_, index) => index % 8 === 0).map((point) => point.x);

  const grid = yTicks
    .map((tick) => {
      const y = scales.yScale(tick);
      return `<line x1="${padding.left}" y1="${y}" x2="${width - padding.right}" y2="${y}" class="grid-line"></line>
        <text x="${padding.left - 10}" y="${y + 4}" text-anchor="end" class="axis-label">${yFormatter(tick)}</text>`;
    })
    .join("");

  const xAxis = ticks
    .map((tick) => {
      const x = scales.xScale(tick);
      return `<text x="${x}" y="${height - 13}" text-anchor="middle" class="axis-label">${tick}</text>`;
    })
    .join("");

  const paths = series
    .map((line, index) => {
      const d = line.points
        .map((point, pointIndex) => {
          const x = scales.xScale(point.x).toFixed(2);
          const y = scales.yScale(point.y).toFixed(2);
          return `${pointIndex === 0 ? "M" : "L"}${x},${y}`;
        })
        .join(" ");
      return `<path d="${d}" fill="none" stroke="${colors[index % colors.length]}" stroke-width="3" stroke-linecap="round"></path>`;
    })
    .join("");

  return `
    <svg viewBox="0 0 ${width} ${height}" class="svg-chart" aria-hidden="true">
      <text x="${padding.left}" y="16" class="chart-y-label">${escapeHtml(yLabel)}</text>
      ${grid}
      ${paths}
      <line x1="${padding.left}" y1="${height - padding.bottom}" x2="${width - padding.right}" y2="${height - padding.bottom}" class="axis-line"></line>
      ${xAxis}
    </svg>
  `;
}

function renderTimeChart() {
  const chart = document.querySelector("#time-chart");
  const legend = document.querySelector("#time-legend");
  let series = [];
  let yFormatter = formatNumber.format;
  let yLabel = "Papers";

  if (state.activeTimeView === "volume") {
    series = [
      {
        name: "Papers",
        points: state.data.year_counts.map((row) => ({ x: row.year, y: row.paper_count })),
      },
    ];
  }

  if (state.activeTimeView === "fields") {
    const keep = ["finance", "macro", "micro", "methods", "public", "environment"];
    series = keep.map((field) => ({
      name: niceLabel(field),
      points: state.data.field_decades
        .filter((row) => row.field === field)
        .map((row) => ({ x: row.decade, y: row.share })),
    }));
    yFormatter = asPercent;
    yLabel = "Share of papers";
  }

  if (state.activeTimeView === "slices") {
    const keep = ["asset_pricing", "factor_investing", "market_microstructure", "macro_state"];
    series = keep.map((slice) => ({
      name: niceLabel(slice),
      points: state.data.slice_year_counts
        .filter((row) => row.slice === slice)
        .map((row) => ({ x: row.year, y: row.share })),
    }));
    yFormatter = asPercent;
    yLabel = "Share of papers";
  }

  chart.innerHTML = renderLineChart({ series, yFormatter, yLabel });
  legend.innerHTML = series.map((line, index) => `<span><i style="--i:${index}"></i>${line.name}</span>`).join("");
}

function renderEdges() {
  const edges = state.data.edge_pairs
    .filter((edge) => state.includeSelfLinks || !edge.is_self_loop)
    .filter((edge) => state.edgeRole === "all" || edge.role === state.edgeRole)
    .slice(0, 18);

  const rows = edges.map((edge) => {
    return `
      <tr>
        <td><strong>${escapeHtml(edge.label)}</strong></td>
        <td>${formatNumber.format(edge.paper_count)}</td>
        <td>${escapeHtml(edge.role || "mapped")}</td>
        <td>${escapeHtml(shortText(edge.example_claim_text, 170))}</td>
      </tr>
    `;
  });
  document.querySelector("#edge-table-body").innerHTML = rows.join("");
}

function populateEdgeRoles() {
  const select = document.querySelector("#edge-role-select");
  const roles = [...new Set(state.data.edge_pairs.map((edge) => edge.role).filter(Boolean))].sort();
  select.innerHTML = `<option value="all">All roles</option>${roles
    .map((role) => `<option value="${escapeHtml(role)}">${escapeHtml(niceLabel(role))}</option>`)
    .join("")}`;
}

function renderPapers() {
  const rows = state.data.sample_papers.slice(0, 9).map((paper) => {
    const tags = paper.tags.map((tag) => `<span class="paper-tag">${escapeHtml(tag)}</span>`).join("");
    return `
      <article class="paper-card">
        <h3>${escapeHtml(paper.title)}</h3>
        <p>${paper.year || "No year"} · ${escapeHtml(paper.source || "Unknown source")}</p>
        <div class="paper-tags">${tags}</div>
      </article>
    `;
  });
  document.querySelector("#paper-grid").innerHTML = rows.join("");
}

function wireControls() {
  const search = document.querySelector("#concept-search");
  search.addEventListener("input", (event) => {
    state.query = event.target.value;
    state.selectedConceptId = null;
    renderConceptList();
    renderConceptDetail();
  });

  document.querySelectorAll(".chip").forEach((chip) => {
    chip.addEventListener("click", () => {
      document.querySelectorAll(".chip").forEach((item) => item.classList.remove("active"));
      chip.classList.add("active");
      state.activeField = chip.dataset.field;
      state.selectedConceptId = null;
      renderConceptList();
      renderConceptDetail();
    });
  });

  document.querySelector("#time-view-select").addEventListener("change", (event) => {
    state.activeTimeView = event.target.value;
    renderTimeChart();
  });

  document.querySelector("#edge-role-select").addEventListener("change", (event) => {
    state.edgeRole = event.target.value;
    renderEdges();
  });

  document.querySelector("#include-self-links").addEventListener("change", (event) => {
    state.includeSelfLinks = event.target.checked;
    renderEdges();
  });
}

async function init() {
  const response = await fetch("data/site-data.json");
  if (!response.ok) {
    throw new Error("Could not load site data.");
  }
  state.data = await response.json();
  state.concepts = state.data.concepts;

  renderMetrics();
  renderTimeChart();
  renderConceptList();
  renderConceptDetail();
  renderRisingThemes();
  populateEdgeRoles();
  renderEdges();
  renderPapers();
  wireControls();
}

init().catch((error) => {
  document.body.innerHTML = `<main class="section"><h1>Finance Atlas</h1><p>${error.message}</p></main>`;
});
