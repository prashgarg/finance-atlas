const state = {
  data: null,
  concepts: [],
  activeField: "all",
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
    <span class="detail-kicker">${concept.field_primary || "mapped concept"}</span>
    <h3>${concept.label}</h3>
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
        <span class="rising-name">${row.label}</span>
        <div class="bar-track"><div class="bar-fill" style="width: ${width}%"></div></div>
        <span class="rising-value">+${asPercent(row.rise_2020s_vs_2000s)}</span>
      </div>
    `;
  });
  document.querySelector("#rising-list").innerHTML = rows.join("");
}

function renderEdges() {
  const rows = state.data.edge_pairs.slice(0, 18).map((edge) => {
    return `
      <tr>
        <td><strong>${edge.label}</strong></td>
        <td>${formatNumber.format(edge.paper_count)}</td>
        <td>${edge.role || "mapped"}</td>
        <td>${shortText(edge.example_claim_text, 170)}</td>
      </tr>
    `;
  });
  document.querySelector("#edge-table-body").innerHTML = rows.join("");
}

function renderPapers() {
  const rows = state.data.sample_papers.slice(0, 9).map((paper) => {
    const tags = paper.tags.map((tag) => `<span class="paper-tag">${tag}</span>`).join("");
    return `
      <article class="paper-card">
        <h3>${paper.title}</h3>
        <p>${paper.year || "No year"} · ${paper.source || "Unknown source"}</p>
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
}

async function init() {
  const response = await fetch("data/site-data.json");
  if (!response.ok) {
    throw new Error("Could not load site data.");
  }
  state.data = await response.json();
  state.concepts = state.data.concepts;

  renderMetrics();
  renderConceptList();
  renderConceptDetail();
  renderRisingThemes();
  renderEdges();
  renderPapers();
  wireControls();
}

init().catch((error) => {
  document.body.innerHTML = `<main class="section"><h1>Finance Atlas</h1><p>${error.message}</p></main>`;
});
