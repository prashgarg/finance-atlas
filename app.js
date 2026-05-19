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
      ["Full-text boundary", "A PDF sample tests which de Prado-style details abstracts miss."],
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

}

function renderAcademic() {
  const denomSummary = document.querySelector("[data-denominator-summary]");
  if (denomSummary) {
    const keep = new Set(["Conservative post-recall anchors", "Context papers", "Active graph"]);
    denomSummary.innerHTML = table(
      ["Object", "Papers", "Use"],
      state.data.denominators
        .filter((row) => keep.has(row.name))
        .map(
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

  const explorer = document.querySelector("[data-methodology-explorer]");
  if (explorer) renderMethodologyExplorer(explorer);

  const pcExplorer = document.querySelector("[data-pc-explorer]");
  if (pcExplorer) renderPcExplorer(pcExplorer);
}

function auditLine(audit) {
  if (!audit || !Object.keys(audit).length) return "No manual audit row.";
  const bits = [];
  if (audit.strong_examples) bits.push(`${fmt(audit.strong_examples)} strong`);
  if (audit.candidates) bits.push(`${fmt(audit.candidates)} candidate`);
  if (audit.not_yet) bits.push(`${fmt(audit.not_yet)} needs source`);
  if (audit.background_only) bits.push(`${fmt(audit.background_only)} background`);
  return bits.join(" · ") || "No retained examples.";
}

function renderPcExplorer(target) {
  const cases = state.data.pc_neighborhoods || [];
  if (!cases.length) return;

  function draw(caseId) {
    const selected = cases.find((row) => row.case_id === caseId) || cases[0];
    target.querySelector("[data-pc-detail]").innerHTML = `
      <div class="explorer-summary">
        <div>
          <p class="eyebrow">${esc(selected.family_pair)}</p>
          <h3>${esc(selected.label)}</h3>
          <p>PC-retained neighborhoods are used as discovery maps. The comparison asks whether similar economic neighborhoods appear in the title/abstract graph and the full-text CausalClaims graph.</p>
        </div>
        <div class="metric-stack">
          ${metric(fmt(selected.frontiergraph_edges), "FrontierGraph edges")}
          ${metric(fmt(selected.causalclaims_edges), "CausalClaims edges")}
        </div>
      </div>
      <div class="paper-card-grid two">
        <article class="paper-card">
          <strong>FrontierGraph audit</strong>
          <p>${esc(auditLine(selected.frontiergraph_audit))}</p>
          <span>${esc((selected.frontiergraph_audit?.judgments || []).join(", "))}</span>
        </article>
        <article class="paper-card">
          <strong>CausalClaims audit</strong>
          <p>${esc(auditLine(selected.causalclaims_audit))}</p>
          <span>${esc((selected.causalclaims_audit?.judgments || []).join(", "))}</span>
        </article>
      </div>
    `;
  }

  target.innerHTML = `
    <div class="explorer-panel">
      <label class="field-control">
        <span>Neighborhood</span>
        <select data-pc-select>
          ${cases.map((row) => `<option value="${esc(row.case_id)}">${esc(row.label)}</option>`).join("")}
        </select>
      </label>
      <div data-pc-detail></div>
    </div>
  `;

  const select = target.querySelector("[data-pc-select]");
  select.addEventListener("change", () => draw(select.value));
  draw(select.value);
}

function renderMethodologyExplorer(target) {
  const features = state.data.methodology_explorer || [];
  if (!features.length) return;

  function draw(featureName) {
    const selected = features.find((row) => row.feature_name === featureName) || features[0];
    target.querySelector("[data-methodology-detail]").innerHTML = `
      <div class="explorer-summary">
        <div>
          <p class="eyebrow">${esc(selected.layer)}</p>
          <h3>${esc(selected.feature)}</h3>
          <p>${esc(selected.de_prado_link)}</p>
        </div>
        <div class="metric-stack">
          ${metric(fmt(selected.papers), "papers")}
          ${metric(pct(selected.share), "of anchor set")}
        </div>
      </div>
      <div class="paper-card-grid">
        ${selected.examples
          .map(
            (row) => `
              <article class="paper-card">
                <strong>${esc(row.title)}</strong>
                <p>${esc(row.source)}${row.year ? `, ${esc(row.year)}` : ""}</p>
                <span>${esc(row.family || row.role || "anchor paper")} · ${fmt(row.signal_count)} signals</span>
              </article>
            `,
          )
          .join("")}
      </div>
    `;
  }

  target.innerHTML = `
    <div class="explorer-panel">
      <label class="field-control">
        <span>Methodology signal</span>
        <select data-methodology-select>
          ${features
            .map((row) => `<option value="${esc(row.feature_name)}">${esc(row.feature)}</option>`)
            .join("")}
        </select>
      </label>
      <div data-methodology-detail></div>
    </div>
  `;

  const select = target.querySelector("[data-methodology-select]");
  select.addEventListener("change", () => draw(select.value));
  draw(select.value);
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
          The PDF sample asks whether full text changes practitioner-methodology measurement.
          The answer is yes often enough that backtesting, multiple testing, implementation,
          and variable-selection fields should not be inferred from abstracts alone.
        </div>
      </div>
    `;
  }
}

function renderOutcomes() {
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

  const citationFeatures = document.querySelector("[data-citation-features]");
  if (citationFeatures) {
    const rows = state.data.citation.feature_associations || [];
    const max = Math.max(...rows.map((row) => Math.abs(row.adjusted_percent)), 1);
    citationFeatures.innerHTML = rows
      .map((row) =>
        barRow(
          row.feature,
          Math.abs(row.adjusted_percent),
          max,
          `${row.adjusted_percent >= 0 ? "+" : ""}${row.adjusted_percent.toFixed(1)}%`,
          `${fmt(row.papers)} papers · p=${row.p_value.toFixed(2)}`,
        ),
      )
      .join("");
  }
}

async function init() {
  const response = await fetch("data/site-data.json");
  state.data = await response.json();
  const page = document.body.dataset.page;
  if (page === "home") renderHome();
  if (page === "academic") renderAcademic();
  if (page === "methods") renderMethods();
  if (page === "outcomes") renderOutcomes();
}

init().catch((error) => {
  console.error(error);
});
