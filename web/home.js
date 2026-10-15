// Accueil, trimestre, audit, règles des réseaux — s'appuie sur app.js
const NETLABEL = k => (META.networks[k]?.label || k).split(" ")[0];
const NETCOLOR = k => META.networks[k]?.color || "#8ea3c8";
const todayIso = () => iso(new Date());
const upcoming = () => POSTS.filter(p => p.status !== "publié" && p.planned && p.planned >= todayIso())
  .sort((a, b) => (a.planned + (a.time || "")).localeCompare(b.planned + (b.time || "")));
const fmtDate = d => { const x = new Date(d + "T12:00"); return x.toLocaleDateString("fr-FR", {weekday: "long", day: "numeric", month: "long"}); };
const firstLine = p => esc(p.hook || (p.text || "").split("\n")[0] || "(idée à rédiger)");

// ------------------------------------------------ navigation
const _show = window.show;
window.show = function (tab) {
  _show(tab);
  if (tab === "home") renderHome();
  if (tab === "quarter") loadQuarters();
  if (tab === "journal") loadAudit();
  if (tab === "guides") renderGuides();
};
const _refresh = window.refresh;
window.refresh = async function () { await _refresh(); if ($("home").classList.contains("on")) renderHome(); };

// ------------------------------------------------ accueil
async function renderHome() {
  const next = upcoming();
  const h = next[0];
  $("hHero").innerHTML = h ? `
    <div class="txt">
      <div class="kick">Prochain post · ${NETLABEL(h.network)} · ${fmtDate(h.planned)}${h.time ? " · " + h.time : ""}</div>
      <h1>${firstLine(h)}</h1>
      <div class="meta"><span class="tag" style="color:${NETCOLOR(h.network)}">${NETLABEL(h.network)}</span><span class="tag">${esc(h.status)}</span>${h.series ? `<span class="tag">${esc(h.series)}${h.week ? " · S" + h.week : ""}</span>` : ""}</div>
      ${h.check_flag ? `<div style="color:var(--bad);font-size:13.5px">✖ ${esc(h.check_flag)}</div>` : ""}
      <div class="actions"><button class="b p" onclick="openPost('${h.id}')">Ouvrir dans l'Atelier</button>
        ${h.text ? `<button class="b" onclick="navigator.clipboard.writeText(POSTS.find(p=>p.id==='${h.id}').text);toast('Texte copié')">Copier le texte</button>` : ""}</div>
    </div>
    <div class="img" style="background-image:url('${h.image ? "/images/" + h.image : "/images/2026-S1-mardi.png"}')"></div>`
    : `<div class="txt"><div class="kick">Rien de prévu</div><h1>Ton calendrier est vide.</h1>
       <div class="meta">Lance une campagne ou un plan de trimestre, ou active le pilote automatique.</div>
       <div class="actions"><button class="b p" onclick="show('camp')">Créer une campagne</button><button class="b" onclick="show('quarter')">Plan du trimestre</button></div></div>
       <div class="img" style="background-image:url('/images/2026-S1-mardi.png')"></div>`;

  const blocked = POSTS.filter(p => p.check_flag && p.status !== "publié");
  const ideas = next.filter(p => p.status === "idée" && !(p.text || "").trim());
  const drafts = POSTS.filter(p => p.status === "brouillon");
  const undated = POSTS.filter(p => p.status === "validé" && !p.planned);
  const audit = (await api("/api/audit")).pending;
  const auditLeft = audit ? [...(audit.journal || []), ...(audit.proofs || [])].filter(x => !x.done).length : 0;
  const journal = (await api("/api/journal")).content;
  const week = new Date(Date.now() - 7 * 864e5).toISOString().slice(0, 10);
  const recentFacts = (journal.match(/^- (\d{4}-\d{2}-\d{2})/gm) || []).filter(l => l.slice(2) >= week).length;
  const tiles = [
    [blocked.length, "post(s) bloqué(s) par la vérification", "bad", "board"],
    [drafts.length, "brouillon(s) à relire", "warn", "board"],
    [ideas.length, "idée(s) à rédiger", "info", "pilot"],
    [undated.length, "post(s) validé(s) sans date", "warn", "board"],
    [auditLeft, "proposition(s) d'audit à trier", "info", "journal"],
    [recentFacts, recentFacts ? "fait(s) noté(s) cette semaine" : "fait noté cette semaine : ajoutes-en un", recentFacts ? "ok" : "bad", "journal"],
  ];
  $("hAttn").innerHTML = tiles.filter(t => t[0] || t[2] === "bad" && t[3] === "journal").map(([n, l, c, tab]) =>
    `<div class="att ${c}" onclick="show('${tab}')"><b>${n}</b>${l}</div>`).join("") || `<div class="att ok"><b>✓</b>Rien d'urgent</div>`;

  $("hNext").innerHTML = next.slice(0, 8).map(tile).join("") || `<p class="muted">Aucun post à venir.</p>`;

  const series = {};
  POSTS.forEach(p => { if (p.series) (series[p.series] ||= []).push(p); });
  $("hSeries").innerHTML = Object.entries(series).map(([s, ps]) => {
    const pub = ps.filter(p => p.status === "publié").length, val = ps.filter(p => ["validé", "programmé"].includes(p.status)).length;
    const pct = Math.round(100 * (pub + val * .6) / ps.length);
    return `<b>${esc(s)}</b><div class="prog"><span style="width:${pct}%"></span></div>
      <div class="muted">${pub} publié(s) · ${val} prêt(s) · ${ps.length - pub - val} en préparation · ${new Set(ps.map(p => p.network)).size} réseau(x)</div><br>`;
  }).join("") || `<span class="muted">Aucune série.</span>`;
}
function tile(p) {
  return `<div class="tile" onclick="openPost('${p.id}')">
    <div class="pic" style="${p.image ? `background-image:url('/images/${p.image}')` : ""}">${p.image ? "" : "◆"}</div>
    <div class="body"><span class="tag" style="color:${NETCOLOR(p.network)}">${NETLABEL(p.network)}</span><span class="tag">${p.planned ? new Date(p.planned + "T12:00").toLocaleDateString("fr-FR", {weekday: "short", day: "numeric", month: "short"}) : "sans date"}${p.time ? " " + p.time : ""}</span>
      <div class="t">${firstLine(p)}</div>
      <div class="muted" style="margin-top:6px">${esc(p.status)}${p.check_flag ? ' · <span style="color:var(--bad)">à corriger</span>' : ""}</div></div></div>`;
}

// ------------------------------------------------ barre du jour (compacte)
window.todayBar = async function () {
  const t = await api("/api/today");
  const one = p => `<a href="#" onclick="openPost('${p.id}');return false" style="color:${NETCOLOR(p.network)}">● ${NETLABEL(p.network)} ${p.time || ""} ${firstLine(p).slice(0, 48)}</a>`;
  const parts = [];
  if (t.late.length) parts.push(`<b style="color:var(--bad)">En retard</b> ${t.late.map(one).join("")}`);
  if (t.today.length) parts.push(`<b>Aujourd'hui</b> ${t.today.map(one).join("")}`);
  if (t.tomorrow.length) parts.push(`<b class="muted">Demain</b> ${t.tomorrow.map(one).join("")}`);
  $("todayBar").innerHTML = parts.join(" &nbsp; ") || `<span class="muted">${new Date().toLocaleDateString("fr-FR", {weekday: "long", day: "numeric", month: "long"})} · rien de prévu aujourd'hui</span>`;
  $("apEvents").innerHTML = t.events.length ? t.events.map(e => `<div class="muted">${e.at} · ${esc(e.msg)}</div>`).join("") : "Rien pour l'instant.";
};

// ------------------------------------------------ règles des réseaux
let GUIDES = {};
async function renderGuides() {
  GUIDES = await api("/api/guides");
  $("gList").innerHTML = Object.entries(GUIDES).filter(([k]) => !k.startsWith("_")).map(([k, g]) => `
    <div class="guide" style="border-top-color:${NETCOLOR(k)}">
      <h3 style="color:${NETCOLOR(k)}">${esc(META.networks[k]?.label || k)}</h3>
      <div>${esc(g.role)}</div>
      <div class="k">Ton</div><div>${esc(g.ton)}</div>
      <div class="k">Format</div><div>${esc(g.format)}</div>
      <div class="k">À faire</div><ul>${(g.faire || []).map(x => `<li>${esc(x)}</li>`).join("")}</ul>
      <div class="k">À éviter</div><ul>${(g.eviter || []).map(x => `<li>${esc(x)}</li>`).join("")}</ul>
      <div class="k">Rythme · horaire de départ</div><div>${esc(g.rythme)} · ${META.networks[k]?.time || ""}</div>
    </div>`).join("") + `<p class="muted">${esc(GUIDES._note || "")} Modifiable dans Storytelling → Règles des réseaux.</p>`;
}
async function showRules() {
  if (!Object.keys(GUIDES).length) GUIDES = await api("/api/guides");
  const g = GUIDES[$("eNet").value];
  $("eRules").innerHTML = g ? `<h3>Règles ${esc(NETLABEL($("eNet").value))}</h3><div class="muted">${esc(g.format)}</div>
    <ul>${(g.faire || []).slice(0, 3).map(x => `<li>${esc(x)}</li>`).join("")}</ul>
    <div class="muted">À éviter : ${esc((g.eviter || []).slice(0, 3).join(" · "))}</div>` : "";
}
const _openPost = window.openPost;
window.openPost = function (id) { _openPost(id); showRules(); };

// ------------------------------------------------ trimestre
function currentQuarter() { const d = new Date(); return `${d.getFullYear()}-T${Math.floor(d.getMonth() / 3) + 1}`; }
async function loadQuarters() {
  if (!$("qId").value) $("qId").value = currentQuarter();
  const qs = await api("/api/quarters");
  $("qOut").innerHTML = qs.map(q => `<div class="quarter"><div class="row-head"><h2 style="margin:0">${esc(q.quarter)}</h2>
      ${q.campaigns.length ? `<button class="b p" onclick="quarterCampaigns('${q.quarter}')">Créer les ${q.campaigns.length} campagnes du trimestre</button>` : ""}</div>
      <div class="md">${esc(q.content)}</div>
      ${q.campaigns.length ? `<h3>Campagnes proposées</h3>${q.campaigns.map(c => `<div class="muted">• <b>${esc(c.name)}</b> · début ${esc(c.start)} · ${c.weeks} sem. · ${esc(Object.entries(c.cadence || {}).map(([k, v]) => NETLABEL(k) + " " + v + "/sem").join(", "))}</div>`).join("")}` : ""}
    </div>`).join("") || `<p class="muted">Aucun plan pour l'instant.</p>`;
}
async function makeQuarter(btn) {
  btn.disabled = true; btn.textContent = "Claude construit le plan… (quelques minutes)";
  try { await api("/api/quarters", {method: "POST", body: JSON.stringify({quarter: $("qId").value, goal: $("qGoal").value})}); toast("Plan du trimestre prêt"); }
  finally { btn.disabled = false; btn.textContent = "Construire le plan avec Claude"; loadQuarters(); }
}
async function quarterCampaigns(q) {
  const r = await api(`/api/quarters/${q}/campaigns`, {method: "POST"});
  toast(`${r.created.length} campagne(s) créée(s) : va dans Campagnes pour les planifier`); show("camp");
}

// ------------------------------------------------ audit
let AUDIT_POLL = null;
async function loadAudit() {
  const a = await api("/api/audit");
  if (!$("aSince").value) $("aSince").value = new Date(Date.now() - 14 * 864e5).toISOString().slice(0, 10);
  $("aState").textContent = a.job.msg || "";
  const p = a.pending;
  $("aOut").innerHTML = p ? `
    <p><b>Audit du ${esc(p.at || "")}</b> <span class="muted">depuis le ${esc(p.since)} · ${p.counts?.local || 0} dépôt(s) local(aux), ${p.counts?.github || 0} sur GitHub</span></p>
    <p>${esc(p.summary || "")}</p>
    <h3>Faits pour le journal</h3>
    ${(p.journal || []).map((j, i) => `<div class="sug">${esc(j.date || "")} · ${esc(j.text)} ${j.done ? '<span class="tag" style="color:var(--ok)">ajouté</span>' : `<button class="b" onclick="acceptAudit('journal',${i})">Ajouter au journal</button>`}</div>`).join("") || '<p class="muted">Aucun.</p>'}
    <h3>Preuves proposées (arrivent en « privé »)</h3>
    ${(p.proofs || []).map((j, i) => `<div class="sug"><span class="tag">${esc(j.status)}</span><b>${esc(j.claim)}</b><div class="muted">${esc(j.source || "")} · ${esc(j.date || "")} ${j.scope ? "· " + esc(j.scope) : ""}</div>
      ${j.done ? '<span class="tag" style="color:var(--ok)">ajoutée</span>' : `<button class="b" onclick="acceptAudit('proof',${i})">Ajouter aux preuves</button>`}</div>`).join("") || '<p class="muted">Aucune.</p>'}
    ${(p.sensible || []).length ? `<h3 style="color:var(--warn)">À ne pas publier tel quel</h3><ul>${p.sensible.map(s => `<li>${esc(s)}</li>`).join("")}</ul>` : ""}` : "";
  clearTimeout(AUDIT_POLL);
  if (a.job.running) AUDIT_POLL = setTimeout(loadAudit, 6000);
  loadJournal();
}
async function runAudit() {
  try { await api("/api/audit", {method: "POST", body: JSON.stringify({since: $("aSince").value})}); toast("Audit lancé (2 à 5 minutes)"); } catch (e) {}
  loadAudit();
}
async function acceptAudit(kind, index) { await api("/api/audit/accept", {method: "POST", body: JSON.stringify({kind, index})}); loadAudit(); }

// ------------------------------------------------ pilote : audit hebdo
const _loadAP = window.loadAutopilot;
window.loadAutopilot = async function () { await _loadAP(); $("apAudit").checked = !!(await api("/api/autopilot")).auto_audit; };
const _saveAP = window.saveAutopilot;
window.saveAutopilot = async function () { await _saveAP(); await api("/api/autopilot", {method: "PUT", body: JSON.stringify({auto_audit: $("apAudit").checked})}); };

// ------------------------------------------------ démarrage
(async () => {
  await init();
  $("eNet").addEventListener("change", showRules);
  show("home");
})();
