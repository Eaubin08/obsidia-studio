let META = {}, POSTS = [], CUR = null;
const $ = id => document.getElementById(id);
const api = async (url, opt = {}) => {
  const r = await fetch(url, {headers: {"Content-Type": "application/json"}, ...opt});
  if (!r.ok) { const e = await r.text(); toast("Erreur : " + e.slice(0, 200)); throw new Error(e); }
  return r.json();
};
function toast(m) { const t = $("toast"); t.textContent = m; t.style.display = "block"; clearTimeout(t._h); t._h = setTimeout(() => t.style.display = "none", 3500); }
const esc = s => (s || "").replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));

document.querySelectorAll("nav button").forEach(b => b.onclick = () => show(b.dataset.tab));
function show(tab) {
  document.querySelectorAll("nav button").forEach(x => x.classList.toggle("on", x.dataset.tab === tab));
  document.querySelectorAll(".tab").forEach(x => x.classList.toggle("on", x.id === tab));
  if (tab === "story") loadDoc();
  if (tab === "month") renderMonth();
  if (tab === "camp") loadCampaigns();
  if (tab === "journal") loadJournal();
  if (tab === "proofs") loadProofs();
  if (tab === "stats") loadStats();
  if (tab === "pilot") loadAutopilot();
}

async function init() {
  META = await api("/api/meta");
  const nets = Object.entries(META.networks).map(([k, v]) => `<option value="${k}">${v.label}</option>`).join("");
  $("fNet").innerHTML += nets; $("eNet").innerHTML = nets;
  $("eStatus").innerHTML = META.statuses.map(s => `<option>${s}</option>`).join("");
  $("iMotif").innerHTML = META.motifs.map(s => `<option>${s}</option>`).join("");
  $("fNet").onchange = render;
  $("eText").oninput = count; $("eNet").onchange = () => { count(); tplOptions(); };
  $("sDoc").onchange = loadDoc;
  $("cWeeks").oninput = cadPreview;
  cadInputs();
  TPL = await api("/api/templates");
  $("gTpl").onchange = tplInfo;
  await loadProfiles();
  $("jDate").value = iso(new Date());
  todayBar(); setInterval(() => { todayBar(); refresh(); }, 90000);
  await refresh();
}
async function refresh() { POSTS = await api("/api/posts"); render(); renderMonth(); }

function render() {
  const f = $("fNet").value;
  $("cols").innerHTML = META.statuses.map(st => {
    const cards = POSTS.filter(p => p.status === st && (!f || p.network === f)).map(p => `
      <div class="card" onclick="openPost('${p.id}')">
        ${p.image ? `<img src="/images/${p.image}" loading="lazy">` : ""}
        <span class="tag">${esc(META.networks[p.network]?.label || p.network)}</span>
        ${p.week ? `<span class="tag">S${p.week} ${esc(p.day)}</span>` : ""}
        ${p.planned ? `<span class="tag">${p.planned}</span>` : ""}
        <div class="t">${esc(p.text.split("\n")[0] || "(vide)")}</div>
      </div>`).join("");
    return `<div class="col"><h3>${st} (${POSTS.filter(p => p.status === st && (!f || p.network === f)).length})</h3>${cards}</div>`;
  }).join("");
}

function openPost(id) {
  CUR = POSTS.find(p => p.id === id);
  $("noPost").style.display = "none"; $("editor").style.display = "grid";
  $("eNet").value = CUR.network; $("eStatus").value = CUR.status; $("eWeek").value = CUR.week || "";
  $("eDay").value = CUR.day || ""; $("eSeries").value = CUR.series || ""; $("ePlanned").value = CUR.planned || ""; $("eTime").value = CUR.time || META.networks[CUR.network]?.time || "";
  $("eHook").value = CUR.hook || ""; $("eText").value = CUR.text || ""; $("eNotes").value = CUR.notes || "";
  $("eScore").innerHTML = ""; $("gOut").style.display = "none";
  $("iL1").value = CUR.img_l1 || ""; $("iL2").value = CUR.img_l2 || "";
  if (CUR.image_idea && !CUR.text) $("gIdea").value = (CUR.hook ? CUR.hook + " — " : "") + (CUR.notes || "");
  showImg(); count(); tplOptions(); if (CUR.template) $("gTpl").value = CUR.template; tplInfo();
  $("iMotif").value = CUR.img_motif || $("iMotif").value;
  const fam = POSTS.filter(p => CUR.family && p.family === CUR.family && p.id !== CUR.id);
  $("eDecl").innerHTML = Object.entries(META.networks).filter(([k]) => k !== CUR.network && !fam.some(p => p.network === k))
    .map(([k, v]) => `<button class="b" style="border-color:${v.color}" onclick="declineTo('${k}')">→ ${v.label.split(" ")[0]}</button>`).join("");
  $("eFamily").innerHTML = fam.length ? "Versions liées : " + fam.map(p => `<a href="#" onclick="openPost('${p.id}');return false" style="color:${META.networks[p.network].color}">${META.networks[p.network].label.split(" ")[0]} (${p.status})</a>`).join(" · ") : "";
  $("eCar").innerHTML = CUR.carousel ? `<a href="/files/${CUR.carousel}" target="_blank" style="color:var(--accent)">Ouvrir le PDF</a>` : "";
  const m = CUR.metrics || {};
  $("eMetrics").innerHTML = [["impressions","Impressions"],["reactions","Réactions"],["comments","Commentaires"],["shares","Partages"],["saves","Enregistr."],["followers","Abonnés"]]
    .map(([k, l]) => `<div><label>${l}</label><input type="number" min="0" id="m-${k}" value="${m[k] || ""}"></div>`).join("");
  showCheck(); show("edit");
}
function showImg() {
  const has = !!(CUR && CUR.image);
  $("eImg").innerHTML = has ? `<img src="/images/${CUR.image}?t=${Date.now()}">` : `<p class="muted">Pas encore d'image.</p>`;
  $("dlImg").style.display = has ? "inline-block" : "none";
  if (has) { $("dlImg").href = "/images/" + CUR.image; $("dlImg").download = CUR.image; }
}
function count() {
  const n = [...$("eText").value].length, lim = META.networks[$("eNet").value]?.limit || 0;
  $("eCount").textContent = `${n} / ${lim} caractères · ${META.networks[$("eNet").value]?.hint || ""}`;
  $("eCount").classList.toggle("over", n > lim);
}
function form() {
  return {network: $("eNet").value, status: $("eStatus").value, week: +$("eWeek").value || 0, day: $("eDay").value,
    series: $("eSeries").value, planned: $("ePlanned").value, hook: $("eHook").value, text: $("eText").value,
    notes: $("eNotes").value, image: CUR.image || "", published: CUR.published || "",
    campaign: CUR.campaign || "", image_idea: CUR.image_idea || "", time: $("eTime").value,
    template: $("gTpl").value || CUR.template || "", family: CUR.family || ""};
}

// ------------------------------------------------ vue mensuelle
let MONTH = new Date(); MONTH.setDate(1);
let HIDDEN = new Set();
const MOIS = ["janvier","février","mars","avril","mai","juin","juillet","août","septembre","octobre","novembre","décembre"];
const iso = d => `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,"0")}-${String(d.getDate()).padStart(2,"0")}`;
function moveMonth(k) { if (k === 0) { MONTH = new Date(); MONTH.setDate(1); } else MONTH.setMonth(MONTH.getMonth() + k); renderMonth(); }
function renderMonth() {
  $("mTitle").textContent = `${MOIS[MONTH.getMonth()]} ${MONTH.getFullYear()}`;
  $("mNets").innerHTML = Object.entries(META.networks).map(([k, v]) =>
    `<span class="chip" onclick="toggleNet('${k}')" style="opacity:${HIDDEN.has(k) ? .35 : 1}"><i style="background:${v.color}"></i>${v.label.split(" ")[0]}</span>`).join("");
  const first = new Date(MONTH), start = new Date(first); start.setDate(1 - ((first.getDay() + 6) % 7));
  const today = iso(new Date());
  let h = ["lun","mar","mer","jeu","ven","sam","dim"].map(d => `<div class="h">${d}</div>`).join("");
  for (let i = 0; i < 42; i++) {
    const d = new Date(start); d.setDate(start.getDate() + i); const k = iso(d);
    const evs = POSTS.filter(p => (p.planned || p.published) === k && !HIDDEN.has(p.network));
    h += `<div class="day ${d.getMonth() !== MONTH.getMonth() ? "out" : ""} ${k === today ? "today" : ""}" onclick="dayClick(event,'${k}')">
      <div class="n">${d.getDate()}</div>
      ${evs.map(p => `<div class="ev st-${p.status}" style="border-color:${META.networks[p.network]?.color}" title="${esc(p.status)} · ${esc(p.hook || p.text.split("\n")[0])}" onclick="event.stopPropagation();openPost('${p.id}')">${p.time ? `<b>${p.time}</b> ` : ""}${esc(p.hook || p.text.split("\n")[0] || "(idée)")}</div>`).join("")}
    </div>`;
    if (i === 34 && d.getMonth() !== MONTH.getMonth()) break;
  }
  $("cal").innerHTML = h;
}
function toggleNet(k) { HIDDEN.has(k) ? HIDDEN.delete(k) : HIDDEN.add(k); renderMonth(); }
async function dayClick(e, k) {
  const p = await api("/api/posts", {method: "POST", body: JSON.stringify({network: "linkedin", planned: k, status: "idée"})});
  await refresh(); openPost(p.id);
}

// ------------------------------------------------ campagnes
function cadInputs() {
  $("cCad").innerHTML = Object.entries(META.networks).map(([k, v]) =>
    `<div><label style="color:${v.color}">${v.label.split(" ")[0]}</label><input type="number" min="0" max="7" id="cad-${k}" value="${k === "linkedin" ? 2 : 0}" oninput="cadPreview()"></div>`).join("");
  $("cStart").value = iso(new Date(Date.now() + 86400000)); cadPreview();
}
function cadPreview() {
  const n = Object.keys(META.networks).reduce((s, k) => s + (+$("cad-" + k).value || 0), 0) * (+$("cWeeks").value || 0);
  $("cPreview").textContent = `≈ ${n} posts sur ${$("cWeeks").value} semaines.`;
}
async function createCampaign() {
  const cadence = {}; Object.keys(META.networks).forEach(k => { const v = +$("cad-" + k).value; if (v) cadence[k] = v; });
  if (!Object.keys(cadence).length) return toast("Choisis au moins un réseau");
  await api("/api/campaigns", {method: "POST", body: JSON.stringify({name: $("cName").value, goal: $("cGoal").value,
    theme: $("cTheme").value, start: $("cStart").value, weeks: +$("cWeeks").value, cadence})});
  toast("Campagne créée"); loadCampaigns();
}
let POLL = null;
async function loadCampaigns() {
  const cs = await api("/api/campaigns");
  $("cList").innerHTML = cs.length ? cs.map(c => {
    const nb = Object.values(c.counts).reduce((a, b) => a + b, 0), j = c.job;
    return `<div class="camp"><b>${esc(c.name)}</b> <span class="muted">· début ${c.start} · ${c.weeks} sem. · ${c.slots} créneaux</span>
      <div class="muted">${Object.entries(c.cadence).map(([k, v]) => `${META.networks[k].label.split(" ")[0]} ${v}/sem`).join(" · ")}</div>
      ${c.arc ? `<p style="margin:6px 0">${esc(c.arc)}</p>` : ""}
      <div class="muted">${META.statuses.map(s => `${s} ${c.counts[s]}`).join(" · ")}</div>
      ${j ? `<div class="muted">Rédaction : ${j.done}/${j.total}${j.errors ? ` · ${j.errors} échec(s)` : ""}${j.running ? " · en cours…" : " · terminé"}</div>` : ""}
      <button class="b" ${nb ? "disabled" : ""} onclick="planCampaign('${c.id}',this)">1. Planifier avec Claude</button>
      <button class="b" ${c.counts["idée"] && !(j && j.running) ? "" : "disabled"} onclick="draftCampaign('${c.id}')">2. Tout rédiger</button>
    </div>`;
  }).join("") : `<p class="muted">Aucune campagne.</p>`;
  const running = cs.some(c => c.job && c.job.running);
  clearTimeout(POLL); if (running) POLL = setTimeout(async () => { await loadCampaigns(); await refresh(); }, 8000);
}
async function planCampaign(id, btn) {
  btn.disabled = true; btn.textContent = "Claude planifie… (quelques minutes)";
  try { const r = await api(`/api/campaigns/${id}/plan`, {method: "POST"}); toast(`${r.created} posts planifiés`); }
  finally { await refresh(); loadCampaigns(); }
}
async function draftCampaign(id) { await api(`/api/campaigns/${id}/draft`, {method: "POST"}); toast("Rédaction lancée en arrière-plan"); loadCampaigns(); }

// ------------------------------------------------ vérification, déclinaison, carrousel, stats
async function showCheck() {
  if (!CUR) return;
  const c = await api(`/api/posts/${CUR.id}/check`);
  $("eCheck").innerHTML = c.items.length ? c.items.map(i => `<div style="font-size:13px;color:${i.level === "bloquant" ? "#ff8a8a" : "var(--warn)"}">${i.level === "bloquant" ? "✖" : "•"} ${esc(i.msg)}</div>`).join("")
    : `<div style="font-size:13px;color:var(--ok)">✔ Vérification OK</div>`;
}
async function declineTo(net) {
  await savePost();
  await api(`/api/posts/${CUR.id}/decline`, {method: "POST", body: JSON.stringify({networks: [net]})});
  toast(`Claude prépare la version ${META.networks[net].label.split(" ")[0]} (1-2 min, elle apparaîtra dans le calendrier)`);
  setTimeout(refresh, 60000); setTimeout(refresh, 120000);
}
async function makeCarousel() {
  await savePost();
  const r = await api(`/api/posts/${CUR.id}/carousel`, {method: "POST"});
  CUR.carousel = r.file; $("eCar").innerHTML = `<a href="/files/${r.file}" target="_blank" style="color:var(--accent)">Ouvrir le PDF (${r.slides} slides)</a>`;
}
async function saveMetrics() {
  const b = {}; ["impressions","reactions","comments","shares","saves","followers"].forEach(k => b[k] = +$("m-" + k).value || 0);
  CUR = await api(`/api/posts/${CUR.id}/metrics`, {method: "PUT", body: JSON.stringify(b)}); toast("Statistiques enregistrées");
}

// ------------------------------------------------ aujourd'hui
async function todayBar() {
  const t = await api("/api/today");
  const line = p => `<a href="#" onclick="openPost('${p.id}');return false" style="color:${META.networks[p.network]?.color};margin-right:14px">${META.networks[p.network]?.label.split(" ")[0]} ${p.time || ""} · ${esc((p.hook || p.text.split("\n")[0] || "(idée)").slice(0, 60))} <span class="muted">(${p.status})</span></a>`;
  const parts = [];
  if (t.late.length) parts.push(`<b style="color:#ff8a8a">En retard :</b> ${t.late.map(line).join("")}`);
  if (t.today.length) parts.push(`<b>Aujourd'hui :</b> ${t.today.map(line).join("")}`);
  if (t.tomorrow.length) parts.push(`<b>Demain :</b> ${t.tomorrow.map(line).join("")}`);
  $("todayBar").style.display = parts.length ? "block" : "none";
  $("todayBar").innerHTML = parts.join("<br>");
  $("apEvents").innerHTML = t.events.length ? t.events.map(e => `<div>${e.at} · ${esc(e.msg)}</div>`).join("") : "Rien pour l'instant.";
}

// ------------------------------------------------ journal
async function loadJournal() { $("jOut").textContent = (await api("/api/journal")).content || "Journal vide."; }
async function addJournal() {
  if (!$("jText").value.trim()) return;
  $("jOut").textContent = (await api("/api/journal", {method: "POST", body: JSON.stringify({text: $("jText").value, date: $("jDate").value})})).content;
  $("jText").value = ""; toast("Ajouté au journal");
}

// ------------------------------------------------ preuves
async function loadProofs(data) {
  const d = data || await api("/api/proofs");
  $("pStatus").innerHTML = d.statuses.map(s => `<option>${s}</option>`).join("");
  $("pList").innerHTML = d.items.length ? d.items.map(p => `<div class="sug"><span class="tag">${p.status}</span>${p.public ? '<span class="tag" style="color:var(--ok)">publiable</span>' : '<span class="tag" style="color:var(--warn)">privé</span>'}
    <b>${esc(p.claim)}</b><div class="muted">${esc(p.source)} ${p.date ? "· " + p.date : ""} ${p.scope ? "· " + esc(p.scope) : ""}</div>
    <button class="b" onclick="delProof('${p.id}')">Supprimer</button></div>`).join("") : `<p class="muted">Aucune preuve. Ajoute tes faits vérifiés : Claude ne pourra citer que ceux-là.</p>`;
}
async function addProof() {
  if (!$("pClaim").value.trim()) return;
  loadProofs(await api("/api/proofs", {method: "POST", body: JSON.stringify({claim: $("pClaim").value, status: $("pStatus").value,
    source: $("pSource").value, date: $("pDate").value, scope: $("pScope").value, public: $("pPublic").checked})}));
  ["pClaim","pSource","pScope"].forEach(k => $(k).value = ""); toast("Preuve ajoutée");
}
async function delProof(id) { loadProofs(await api(`/api/proofs/${id}`, {method: "DELETE"})); }

// ------------------------------------------------ bilan
const JOURS = ["lun","mar","mer","jeu","ven","sam","dim"];
async function loadStats() {
  const s = await api("/api/stats");
  if (!s.n) { $("stOut").innerHTML = `<p class="muted">Aucune statistique saisie pour l'instant.</p>`; return; }
  const tbl = (rows, key, fmt) => `<table style="border-collapse:collapse;margin:6px 0 16px">${rows.sort((a, b) => b.er - a.er).map(r =>
    `<tr><td style="padding:3px 10px;color:${META.networks[r.network]?.color}">${META.networks[r.network]?.label.split(" ")[0]}</td><td style="padding:3px 10px">${fmt(r[key])}</td><td style="padding:3px 10px"><b>${r.er} %</b></td><td class="muted" style="padding:3px 10px">n=${r.n}</td></tr>`).join("")}</table>`;
  $("stOut").innerHTML = `<h3>${s.n} posts mesurés</h3>
    <h4>Meilleurs posts</h4>${s.posts.slice(0, 8).map(p => `<div><span style="color:${META.networks[p.network]?.color}">●</span> <b>${(100 * p.er).toFixed(1)} %</b> · ${esc(p.first)} <span class="muted">(${p.impressions} imp.)</span></div>`).join("")}
    <h4>Par jour</h4>${tbl(s.by_weekday, "weekday", d => JOURS[d])}
    <h4>Par heure</h4>${tbl(s.by_hour, "hour", h => h ? h + " h" : "?")}
    <h4>Par modèle</h4>${tbl(s.by_template, "template", t => esc(TPL.find(x => x.id === t)?.name || t))}
    <p class="muted">Avec moins de ${s.min_for_adjust} posts par réseau, les écarts ne veulent rien dire : ce sont des tendances, pas des certitudes.</p>`;
}
async function adjustSchedule() {
  const r = await api("/api/stats/adjust", {method: "POST"});
  $("adjOut").style.display = "block"; $("adjOut").textContent = r.changes.join("\n"); META = await api("/api/meta");
}

// ------------------------------------------------ pilote
async function loadAutopilot() {
  const c = await api("/api/autopilot");
  $("apEnabled").checked = c.enabled; $("apDraft").checked = c.auto_draft; $("apHorizon").value = c.draft_horizon_days;
  $("apRefill").checked = c.auto_refill; $("apMin").value = c.min_planned_14d; $("apDecline").checked = c.auto_decline; $("apCheck").checked = c.auto_check;
  const boxes = (id, sel, excl) => $(id).innerHTML = Object.entries(META.networks).filter(([k]) => k !== excl).map(([k, v]) =>
    `<label class="chip"><input type="checkbox" data-g="${id}" value="${k}" ${sel.includes(k) ? "checked" : ""} style="width:auto"> ${v.label.split(" ")[0]}</label>`).join("");
  boxes("apRefillNets", c.refill_networks); boxes("apDeclNets", c.decline_to, "linkedin");
  todayBar();
}
async function saveAutopilot() {
  const pick = id => [...document.querySelectorAll(`input[data-g="${id}"]:checked`)].map(x => x.value);
  await api("/api/autopilot", {method: "PUT", body: JSON.stringify({enabled: $("apEnabled").checked, auto_draft: $("apDraft").checked,
    draft_horizon_days: +$("apHorizon").value, auto_refill: $("apRefill").checked, min_planned_14d: +$("apMin").value,
    auto_decline: $("apDecline").checked, decline_to: pick("apDeclNets"), refill_networks: pick("apRefillNets"), auto_check: $("apCheck").checked})});
  toast($("apEnabled").checked ? "Pilote automatique actif (il ne publie jamais)" : "Pilote automatique désactivé"); todayBar();
}

// ------------------------------------------------ modèles
let TPL = [];
function tplOptions() {
  const net = $("eNet").value;
  const opts = TPL.filter(t => t.networks.includes(net)).concat(TPL.filter(t => !t.networks.includes(net)));
  $("gTpl").innerHTML = `<option value="">Libre (sans modèle)</option>` +
    opts.map(t => `<option value="${t.id}">${esc(t.name)}${t.networks.includes(net) ? "" : " (autre réseau)"}</option>`).join("");
  tplInfo();
}
function tplInfo() {
  const t = TPL.find(x => x.id === $("gTpl").value);
  $("gTplWhen").textContent = t ? `${t.when} · Motif d'image conseillé : ${t.motif}` : "";
  if (t) $("iMotif").value = t.motif;
}
function insertTpl() {
  const t = TPL.find(x => x.id === $("gTpl").value); if (!t) return toast("Choisis un modèle");
  if ($("eText").value.trim() && !confirmReplace()) return;
  $("eText").value = t.structure; count();
}
function confirmReplace() { toast("Le texte n'est pas vide : vide-le d'abord pour insérer le squelette."); return false; }

// ------------------------------------------------ profils
let PROF = {};
async function loadProfiles() {
  PROF = await api("/api/profiles");
  $("profLinks").innerHTML = Object.entries(PROF).map(([k, v]) => v.url
    ? `<a href="${esc(v.url)}" target="_blank" rel="noopener" class="chip" style="color:${META.networks[k]?.color || "var(--muted)"};text-decoration:none"><i style="background:${META.networks[k]?.color || "#8ea3c8"}"></i>${esc((META.networks[k]?.label || k).split(" ")[0])}</a>`
    : `<span class="chip muted" title="profil non renseigné">${esc((META.networks[k]?.label || k).split(" ")[0])} ?</span>`).join("");
}
function editProfiles() {
  show("story"); $("sDoc").value = "profiles";
  $("sText").value = JSON.stringify(PROF, null, 2);
  toast("Modifie les URL puis clique sur Enregistrer");
}

// ------------------------------------------------ suggestions
let SUGG = [];
async function suggest() {
  $("sOut").innerHTML = `<p class="muted">Claude réfléchit… (1 à 3 minutes)</p>`;
  const r = await api("/api/suggest", {method: "POST", body: JSON.stringify({content: $("sAsk").value})});
  SUGG = r.items || [];
  $("sOut").innerHTML = SUGG.map((s, i) => `<div class="sug">
    <span class="tag" style="color:${META.networks[s.network]?.color}">${esc(META.networks[s.network]?.label || s.network)}</span>
    <b>${esc(s.hook)}</b><div>${esc(s.angle)}</div>
    <div class="muted">Pourquoi : ${esc(s.pourquoi)} · Preuve : ${esc(s.preuve)}</div>
    <button class="b" onclick="adoptSugg(${i})">Ajouter comme idée</button></div>`).join("");
}
async function adoptSugg(i) {
  const s = SUGG[i];
  await api("/api/posts", {method: "POST", body: JSON.stringify({network: META.networks[s.network] ? s.network : "linkedin",
    status: "idée", hook: s.hook, notes: `Angle : ${s.angle} · Preuve nécessaire : ${s.preuve}`, series: ""})});
  await refresh(); toast("Ajouté aux idées (sans date : donne-lui une date dans l'Atelier)");
}
async function savePost(force) {
  const r = await fetch(`/api/posts/${CUR.id}${force === true ? "?force=true" : ""}`, {method: "PUT", headers: {"Content-Type": "application/json"}, body: JSON.stringify(form())});
  if (r.status === 409) {
    const msg = (await r.json()).detail;
    $("eCheck").innerHTML = `<div style="border:1px solid #ff7a7a;border-radius:8px;padding:8px">${esc(msg)}<br>
      <button class="b" onclick="savePost(true)">Valider quand même</button></div>`;
    return toast("Validation bloquée par la vérification");
  }
  if (!r.ok) return toast("Erreur : " + (await r.text()).slice(0, 200));
  CUR = await r.json(); await refresh(); await showCheck(); toast("Enregistré");
}
async function newPost() {
  const p = await api("/api/posts", {method: "POST", body: JSON.stringify({network: $("fNet").value || "linkedin"})});
  await refresh(); openPost(p.id);
}
async function markPublished() { $("eStatus").value = "publié"; await savePost(); toast("Marqué comme publié"); }
async function archivePost() { await api(`/api/posts/${CUR.id}/archive`, {method: "POST"}); CUR = null; $("editor").style.display = "none"; $("noPost").style.display = "block"; await refresh(); show("board"); }
async function copyText() { await navigator.clipboard.writeText($("eText").value); toast("Texte copié"); }

async function humanize() {
  $("eScore").textContent = "Nettoyage…";
  const r = await api("/api/humanize", {method: "POST", body: JSON.stringify({content: $("eText").value})});
  const changed = r.text.trim() !== $("eText").value.trim();
  $("eText").value = r.text.trim(); count();
  const s = r.score.human_score !== undefined ? `Score lisibilité <b>${r.score.human_score}</b> (${r.score.verdict}) · ` : "";
  $("eScore").innerHTML = `${s}${changed ? "texte modifié" : "aucune modification"} — <span class="muted">heuristique locale, pas une garantie</span><pre>${esc(r.report)}</pre>`;
}
async function generate(adapt) {
  const idea = $("gIdea").value.trim();
  if (!idea && !adapt) return toast("Écris d'abord une idée");
  $("gOut").style.display = "block"; $("gOut").textContent = "Brody prépare le brouillon (Qwen si nécessaire)…";
  const r = await api("/api/generate", {method: "POST", body: JSON.stringify({idea: idea || "adapter ce post", network: $("eNet").value, source_text: adapt ? $("eText").value : "", template: $("gTpl").value})});
  $("gOut").textContent = r.raw;
  if (r.text) { $("eText").value = r.text; count(); toast("Brouillon placé dans l'éditeur (non enregistré)"); }
}
async function makeImage() {
  if (!$("iL1").value) return toast("Ligne 1 vide");
  await savePost();
  CUR = await api(`/api/posts/${CUR.id}/image`, {method: "POST", body: JSON.stringify({line1: $("iL1").value, line2: $("iL2").value, footer: $("iFoot").value, motif: $("iMotif").value, format: $("iFormat").value})});
  showImg(); await refresh(); toast("Image générée");
}
async function copyImage() {
  if (!CUR.image) return;
  const blob = await (await fetch("/images/" + CUR.image)).blob();
  await navigator.clipboard.write([new ClipboardItem({"image/png": blob})]); toast("Image copiée");
}
async function loadDoc() {
  if ($("sDoc").value === "profiles") { $("sText").value = JSON.stringify(PROF, null, 2); return; }
  $("sText").value = (await api("/api/docs/" + $("sDoc").value)).content;
}
async function saveDoc() {
  if ($("sDoc").value === "profiles") {
    let data; try { data = JSON.parse($("sText").value); } catch { return toast("Format invalide : rien n'a été enregistré"); }
    await api("/api/profiles", {method: "PUT", body: JSON.stringify(data)}); await loadProfiles(); return toast("Réseaux enregistrés");
  }
  await api("/api/docs/" + $("sDoc").value, {method: "PUT", body: JSON.stringify({content: $("sText").value})});
  if ($("sDoc").value === "templates") TPL = await api("/api/templates");
  toast("Enregistré (sauvegarde faite)");
}
// init() est appelé par home.js
