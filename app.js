const state = { data: null };

const number = new Intl.NumberFormat("en-US");
const percent = new Intl.NumberFormat("en-US", { maximumFractionDigits: 1 });

function esc(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function fmt(value) {
  return number.format(Number(value || 0));
}

function pct(value) {
  return `${percent.format(Number(value || 0) * 100)}%`;
}

function compact(value) {
  const num = Number(value || 0);
  if (num >= 1000) return `${percent.format(num / 1000)}k`;
  return fmt(num);
}

function term(label, tip) {
  return `<span class="term" tabindex="0" data-tip="${esc(tip)}">${esc(label)}</span>`;
}

function metric(value, label) {
  return `<div class="metric-line"><b>${esc(value)}</b><span>${esc(label)}</span></div>`;
}

function barRow(label, value, max, right, note = "") {
  const width = max > 0 ? Math.max(3, (Number(value || 0) / max) * 100) : 0;
  return `
    <div class="bar-row">
      <div class="bar-label">
        <strong>${esc(label)}</strong>
        ${note ? `<span>${esc(note)}</span>` : ""}
      </div>
      <div class="bar-track"><div class="bar-fill" style="width:${width}%"></div></div>
      <b>${esc(right ?? fmt(value))}</b>
    </div>
  `;
}

function table(headers, rows) {
  return `
    <div class="table-wrap">
      <table>
        <thead><tr>${headers.map((h) => `<th>${esc(h)}</th>`).join("")}</tr></thead>
        <tbody>${rows.join("")}</tbody>
      </table>
    </div>
  `;
}

function renderMetrics() {
  const el = document.querySelector("[data-home-metrics]");
  if (!el) return;
  el.innerHTML = state.data.home_metrics.map((m) => metric(m.value, m.label)).join("");
}

function renderHome() {
  renderMetrics();
  const d = state.data;
  const workflow = document.querySelector("[data-home-workflow]");
  if (workflow) {
    workflow.innerHTML = [
      ["Discovery frame", "FrontierGraph supplies a broad title-and-abstract research graph."],
      ["Main denominator", `The current target set is ${fmt(d.snapshot.anchors)} conservative post-recall anchor papers.`],
      ["Methodology layer", "Graph fields measure causal framing, mechanisms, scope conditions, and related signals."],
      ["Full-text boundary", "A PDF pilot tests which de Prado-style details abstracts miss."],
    ]
      .map(
        ([title, body], idx) => `
          <li>
            <span>${String(idx + 1).padStart(2, "0")}</span>
            <strong>${esc(title)}</strong>
            <p>${esc(body)}</p>
          </li>
        `,
      )
      .join("");
  }

  const findings = document.querySelector("[data-home-findings]");
  if (findings) {
    const ft = d.full_text;
    findings.innerHTML = [
      {
        label: "Main denominator",
        value: fmt(d.snapshot.anchors),
        text: "conservative post-recall anchor papers define the current target literature.",
      },
      {
        label: "Sensitivity only",
        value: fmt(d.snapshot.sensitivity_additions),
        text: "extended medium-recall cases are outside the main denominator.",
      },
      {
        label: "Full text",
        value: fmt(ft.reveals_missed + ft.refines),
        text: "of 30 scored PDFs reveal or refine signals relative to abstracts.",
      },
    ]
      .map(
        (item) => `
          <article class="finding">
            <span>${esc(item.label)}</span>
            <b>${esc(item.value)}</b>
            <p>${esc(item.text)}</p>
          </article>
        `,
      )
      .join("");
  }

  const methods = document.querySelector("[data-methodology-mini]");
  if (methods) {
    const rows = state.data.methodology.slice(0, 6);
    methods.innerHTML = rows
      .map((row) => barRow(row.feature, row.share, 1, pct(row.share), row.de_prado_link))
      .join("");
  }

  const outcomes = document.querySelector("[data-outcome-modules]");
  if (outcomes) renderOutcomeModules(outcomes);
}

function renderAcademic() {
  const denom = document.querySelector("[data-denominators]");
  if (denom) {
    denom.innerHTML = table(
      ["Object", "Papers", "What it is for", "What not to infer"],
      state.data.denominators.map(
        (row) => `
          <tr>
            <td><strong>${esc(row.name)}</strong><p>${esc(row.description)}</p></td>
            <td>${fmt(row.count)}</td>
            <td>${esc(row.use)}</td>
            <td>${row.name.includes("Context") ? "Target-paper status." : row.name.includes("Active") ? "A final corpus denominator." : row.name.includes("Sensitivity") ? "Main-denominator status." : "Recall completeness."}</td>
          </tr>
        `,
      ),
    );
  }

  const graph = document.querySelector("[data-graph-layers]");
  if (graph) {
    const max = Math.max(...state.data.graph_layers.map((row) => row.nodes));
    graph.innerHTML = state.data.graph_layers
      .map((row) => barRow(row.role, row.nodes, max, `${fmt(row.nodes)} nodes · ${fmt(row.edges)} edges`, row.description))
      .join("");
  }

  const meth = document.querySelector("[data-methodology-bars]");
  if (meth) {
    meth.innerHTML = state.data.methodology
      .slice(0, 10)
      .map((row) => barRow(row.feature, row.share, 1, pct(row.share), row.de_prado_link))
      .join("");
  }

  const pc = document.querySelector("[data-pc-runs]");
  if (pc) {
    pc.innerHTML = table(
      ["Corpus", "Text basis", "PC input", "Edges", "Current use"],
      state.data.pc_runs.map(
        (row) => `
          <tr>
            <td>${esc(row.corpus)}</td>
            <td>${esc(row.threshold)}</td>
            <td>${esc(row.features)}<p>${fmt(row.selected_variables)} variables, ${fmt(row.observations)} observations</p></td>
            <td>${fmt(row.edges)}</td>
            <td>${esc(row.use)}</td>
          </tr>
        `,
      ),
    );
  }

  const semantic = document.querySelector("[data-semantic-overlap]");
  if (semantic) {
    const s = state.data.semantic_overlap.summary;
    semantic.innerHTML = `
      <div class="split-panel">
        <div>
          ${metric(fmt(s.semantic_overlap_pairs_both_corpora), "semantic pairs in both corpora")}
          ${metric(fmt(s.family_overlap_pairs_both_corpora), "family-level overlaps")}
        </div>
        <ul class="quiet-list">
          ${state.data.semantic_overlap.examples
            .map((row) => `<li><strong>${esc(row.pair)}</strong><span>${fmt(row.frontiergraph_edges)} FG edges, ${fmt(row.causalclaims_edges)} CausalClaims edges</span></li>`)
            .join("")}
        </ul>
      </div>
    `;
  }
}

function renderMethods() {
  const sources = document.querySelector("[data-source-comparison]");
  if (sources) {
    sources.innerHTML = table(
      ["Source", "What it gives us", "Boundary"],
      state.data.source_comparison.map(
        (row) => `
          <tr>
            <td><strong>${esc(row.source)}</strong></td>
            <td>${esc(row.gives)}</td>
            <td>${esc(row.boundary)}</td>
          </tr>
        `,
      ),
    );
  }

  const objects = document.querySelector("[data-objects-table]");
  if (objects) {
    objects.innerHTML = table(
      ["Object", "Denominator", "Role"],
      state.data.denominators.map(
        (row) => `
          <tr>
            <td><strong>${esc(row.name)}</strong><p>${esc(row.description)}</p></td>
            <td>${fmt(row.count)}</td>
            <td>${esc(row.use)}</td>
          </tr>
        `,
      ),
    );
  }

  const visibility = document.querySelector("[data-visibility-table]");
  if (visibility) {
    visibility.innerHTML = table(
      ["Methodology object", "Status", "Current proxy", "Papers", "Boundary"],
      state.data.deprado_crosswalk.map(
        (row) => `
          <tr>
            <td><strong>${esc(row.item)}</strong></td>
            <td>${esc(row.status)}</td>
            <td>${esc(row.proxy)}</td>
            <td>${row.papers === null ? "—" : `${fmt(row.papers)}<p>${pct(row.share)}</p>`}</td>
            <td>${esc(row.boundary)}</td>
          </tr>
        `,
      ),
    );
  }

  const fullText = document.querySelector("[data-full-text-boundary]");
  if (fullText) {
    const ft = state.data.full_text;
    fullText.innerHTML = `
      <div class="split-panel">
        <div class="metric-stack">
          ${metric(fmt(ft.sample_n), "sample papers")}
          ${metric(fmt(ft.scored), "scored PDFs")}
          ${metric(fmt(ft.reveals_missed), "reveal missed signals")}
          ${metric(fmt(ft.refines), "refine abstract signals")}
        </div>
        <div class="note-block">
          The pilot asks whether full text changes practitioner-methodology measurement.
          The answer is yes often enough that backtesting, multiple testing, implementation,
          and variable-selection fields should not be inferred from abstracts alone.
        </div>
      </div>
    `;
  }
}

function renderOutcomeModules(target) {
  const modules = state.data.outcome_modules;
  target.innerHTML = modules
    .map(
      (row) => `
        <article class="module-row">
          <div>
            <strong>${esc(row.name)}</strong>
            <p>${esc(row.description)}</p>
          </div>
          <span>${esc(row.status)}</span>
        </article>
      `,
    )
    .join("");
}

function renderOutcomes() {
  const modules = document.querySelector("[data-outcome-modules]");
  if (modules) renderOutcomeModules(modules);

  const citation = document.querySelector("[data-citation]");
  if (citation) {
    const c = state.data.citation;
    citation.innerHTML = `
      <div class="metric-stack">
        ${metric(fmt(c.anchors), "anchor papers")}
        ${metric(fmt(c.matched), "citation matches")}
        ${metric(String(c.median_citations), "median citations")}
      </div>
      <div class="note-block">
        On the ${fmt(c.anchors)}-paper anchor denominator, baseline adjusted R² is ${c.baseline_r2.toFixed(3)}. Adding graph-visible methodology counts changes it to ${c.methodology_r2.toFixed(3)}; adding method-domain indicators changes it to ${c.domain_r2.toFixed(3)}.
      </div>
    `;
  }

  const products = document.querySelector("[data-product-bridge]");
  if (products) {
    const rows = state.data.product_bridge.families
      .slice()
      .sort((a, b) => {
        const status = String(a.status).localeCompare(String(b.status));
        return status || String(a.family).localeCompare(String(b.family));
      })
      .map(
        (row) => `
          <tr>
            <td><strong>${esc(row.family)}</strong><p>${esc(row.status)}</p></td>
            <td>${esc(row.product_evidence)}</td>
            <td>${esc(row.nearest_academic_object)}</td>
            <td>${esc(row.bridge_type)}<p>${esc(row.confidence)} confidence</p></td>
            <td>${esc(row.caveat)}</td>
          </tr>
        `,
      );
    products.innerHTML = table(
      ["Product family", "Product graph signature", "Nearest academic object", "Bridge type", "Main caveat"],
      rows,
    );
  }

  const factor = document.querySelector("[data-factor-contract]");
  if (factor) {
    const items = [
      "stable factor-investing denominator",
      "audited paper-to-factor links",
      "condition-type classification",
      "state proxy library",
      "harmonized return panel",
      "signal-month design",
    ];
    factor.innerHTML = `<ul class="compact-checklist">${items.map((x) => `<li>${esc(x)}</li>`).join("")}</ul>`;
  }
}

function renderPaper() {
  const paper = document.querySelector("[data-paper-status]");
  if (!paper) return;
  paper.innerHTML = `
    <div class="note-block">
      The paper draft is being reorganized around three empirical questions: corpus discovery, graph-visible methodology, and full-text added value. The public site will link the PDF once those pieces are stable enough to read without internal caveats.
    </div>
  `;
}

async function init() {
  const response = await fetch("data/site-data.json");
  state.data = await response.json();
  const page = document.body.dataset.page;
  if (page === "home") renderHome();
  if (page === "academic") renderAcademic();
  if (page === "methods") renderMethods();
  if (page === "outcomes") renderOutcomes();
  if (page === "paper") renderPaper();
}

init().catch((error) => {
  console.error(error);
});
