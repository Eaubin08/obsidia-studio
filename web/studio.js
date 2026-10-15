// Obsidia Studio — interface v4 : on voit d'abord le post, les réglages sont rangés.
const $ = id => document.getElementById(id);
const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"}[c]));
let META = {}, POSTS = [], TPL = [], GUIDES = {}, PROF = {};
let PAGE = "home", CUR = null, WEEK0 = mondayOf(new Date()), CALMODE = "week", HIDE = new Set();

async function api(url, opt = {}) {
  const r = await fetch(url, {headers: {"Content-Type": "application/json"}, ...opt});
  if (!r.ok) {
    let msg = await r.text();
    try { msg = JSON.parse(msg).detail; } catch (e) {}
    const err = new Error(msg); err.status = r.status; throw err;
  }
  return r.json();
}
// Informational receipt only: local session display, never a publishing permission.
function rememberCognitiveSource(postId, receipt) {
  if (!postId || !receipt || typeof receipt !== "object") return;
  try { sessionStorage.setItem("obsidia-studio-cognitive:" + postId, JSON.stringify(receipt)); } catch (_) {}
}
function cognitiveSourceCard(postId) {
  let receipt;
  try { receipt = JSON.parse(sessionStorage.getItem("obsidia-studio-cognitive:" + postId) || "null"); } catch (_) { return ""; }
  if (!receipt) return "";
  const label = receipt.source === "BRODY_NATIVE" ? "Brody seul" :
    receipt.source === "GOVERNED_MODEL_PROJECTION" ? "Brody + contribution Qwen gouvernée" :
    receipt.source === "STUDIO_DETERMINISTIC_TEMPLATE" ? "Trame locale Studio — sans IA" :
    receipt.source === "USER_SOURCE_TEXT_ONLY" ? "Texte utilisateur — sans IA" :
    receipt.source === "BRODY_DIRECT_UNVERIFIED" ? "Brody natif — contenu non vérifié" :
    "Origine cognitive non vérifiée";
  const noAi = receipt.source === "STUDIO_DETERMINISTIC_TEMPLATE" || receipt.source === "USER_SOURCE_TEXT_ONLY";
  const synthesis = noAi ? "Aucune génération cognitive effectuée" :
    receipt.brody_post_model_synthesis_proven === true ? "Synthèse post-modèle attestée" : "Synthèse Brody post-Qwen non démontrée";
  return `<div class="panel"><h3>Provenance cognitive</h3><p><b>${esc(label)}</b></p>
    <p class="muted">${esc(synthesis)} · Brouillon à valider humainement · Aucune publication autorisée par ce reçu.</p></div>`;
}
function toast(m) { const t = $("toast"); t.textContent = m; t.style.display = "block"; clearTimeout(t._h); t._h = setTimeout(() => t.style.display = "none", 3800); }
const iso = d => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
function mondayOf(d) { const x = new Date(d); x.setHours(12); x.setDate(x.getDate() - ((x.getDay() + 6) % 7)); return x; }
const addDays = (d, n) => { const x = new Date(d); x.setDate(x.getDate() + n); return x; };
const NL = k => (META.networks?.[k]?.label || k).split(" ")[0];
const NC = k => META.networks?.[k]?.color || "#8ea3c8";
const first = p => p.hook || (p.text || "").split("\n")[0] || "Idée à rédiger";
const dayLabel = d => new Date(d + "T12:00").toLocaleDateString("fr-FR", {weekday: "long", day: "numeric", month: "long"});
const short = d => new Date(d + "T12:00").toLocaleDateString("fr-FR", {weekday: "short", day: "numeric", month: "short"});
const STATE = {
  "idée": ["◌", "à rédiger", "info"], "brouillon": ["✎", "à relire", "warn"], "validé": ["✓", "prêt", "ok"],
  "programmé": ["◷", "programmé", "ok"], "publié": ["●", "publié", "muted"]
};
function badge(p) {
  if (p.check_flag && p.status !== "publié") return `<span class="st bad">✖ à corriger</span>`;
  const s = STATE[p.status] || ["", p.status, ""];
  return `<span class="st ${s[2]}">${s[0]} ${s[1]}</span>`;
}

// ============================================================ navigation
function go(page, arg) {
  PAGE = page;
  document.querySelectorAll("#nav button").forEach(b => b.classList.toggle("on", b.dataset.page === page));
  ({home: pageHome, cal: pageCal, ideas: pageIdeas, results: pageResults, settings: pageSettings, post: pagePost})[page](arg);
  window.scrollTo(0, 0);
}
document.querySelectorAll("#nav button").forEach(b => b.onclick = () => go(b.dataset.page));
async function refresh() { POSTS = await api("/api/posts"); }

// ============================================================ barre du haut
async function topBar() {
  const t = await api("/api/today");
  const one = p => `<a href="#" onclick="openPost('${p.id}');return false" style="color:${NC(p.network)}">● ${NL(p.network)} ${p.time || ""} · ${esc(first(p).slice(0, 46))}</a>`;
  const parts = [];
  if (t.late.length) parts.push(`<b class="bad">En retard</b> ${t.late.map(one).join("")}`);
  if (t.today.length) parts.push(`<b>Aujourd'hui</b> ${t.today.map(one).join("")}`);
  if (t.tomorrow.length) parts.push(`<b class="muted">Demain</b> ${t.tomorrow.map(one).join("")}`);
  $("todayBar").innerHTML = parts.join(" &nbsp; ") || `<span class="muted">${dayLabel(iso(new Date()))} · rien de prévu aujourd'hui</span>`;
  const ap = await api("/api/autopilot");
  $("pilotState").innerHTML = `<span class="dot ${ap.enabled ? "on" : ""}"></span>Pilote auto ${ap.enabled ? "actif" : "en pause"}<br><span>Rien n'est publié automatiquement.</span>`;
  window._events = t.events;
}

// ============================================================ ACCUEIL
async function pageHome() {
  await refresh();
  const today = iso(new Date());
  const next = POSTS.filter(p => p.status !== "publié" && p.planned && p.planned >= today)
    .sort((a, b) => (a.planned + (a.time || "")).localeCompare(b.planned + (b.time || "")));
  const h = next[0];
  const blocked = POSTS.filter(p => p.check_flag && p.status !== "publié").length;
  const toRead = POSTS.filter(p => p.status === "brouillon" && !p.check_flag).length;
  const ready = POSTS.filter(p => ["validé", "programmé"].includes(p.status) && p.planned >= today).length;
  const ideas = next.filter(p => p.status === "idée").length;
  $("main").innerHTML = `
    ${h ? `<div class="hero" onclick="openPost('${h.id}')">
      <div class="txt"><div class="kick" style="color:${NC(h.network)}">Prochain · ${NL(h.network)} · ${dayLabel(h.planned)}${h.time ? " · " + h.time : ""}</div>
        <h1>${esc(first(h))}</h1>${badge(h)}
        <div class="actions"><button class="b p">Voir le post</button></div></div>
      <div class="img" style="${h.image ? `background-image:url('/images/${h.image}')` : ""}"></div></div>`
    : `<div class="hero empty"><div class="txt"><div class="kick">Rien de prévu</div><h1>Ton calendrier est vide.</h1>
        <div class="actions"><button class="b p" onclick="wizard()">＋ Nouveau post</button><button class="b" onclick="go('ideas','camp')">Créer une campagne</button></div></div></div>`}
    <div class="kpis">
      ${kpi(blocked, "à corriger", "bad", "cal")}${kpi(toRead, "à relire", "warn", "cal")}${kpi(ready, "prêts à publier", "ok", "cal")}${kpi(ideas, "idées à rédiger", "info", "cal")}
    </div>
    <div class="sec-row"><h2 class="sec">Les 7 prochains jours</h2><a href="#" onclick="go('cal');return false">Tout le calendrier →</a></div>
    <div class="strip">${next.filter(p => p.planned <= iso(addDays(new Date(), 7))).map(card).join("") || `<p class="muted">Rien sur les 7 prochains jours.</p>`}</div>
    <div class="two">
      <div><h2 class="sec">Ta série</h2><div class="soft">${seriesBlock()}</div></div>
      <div><h2 class="sec">Ce que le pilote a fait</h2><div class="soft">${(window._events || []).slice(0, 8).map(e => `<div class="muted">${e.at} · ${esc(e.msg)}</div>`).join("") || `<span class="muted">Rien pour l'instant.</span>`}</div></div>
    </div>`;
}
const kpi = (n, l, c, page) => `<div class="kpi ${c}" onclick="go('${page}')"><b>${n}</b><span>${l}</span></div>`;
function seriesBlock() {
  const s = {};
  POSTS.forEach(p => { if (p.series) (s[p.series] ||= []).push(p); });
  return Object.entries(s).map(([name, ps]) => {
    const pub = ps.filter(p => p.status === "publié").length, ok = ps.filter(p => ["validé", "programmé"].includes(p.status)).length;
    return `<b>${esc(name)}</b><div class="prog"><span style="width:${Math.round(100 * (pub + ok) / ps.length)}%"></span></div>
      <div class="muted">${pub} publiés · ${ok} prêts · ${ps.length - pub - ok} en préparation</div>`;
  }).join("<br>") || `<span class="muted">Aucune série.</span>`;
}
function card(p) {
  return `<div class="pcard" onclick="openPost('${p.id}')">
    <div class="pic" style="${p.image ? `background-image:url('/images/${p.image}')` : ""}">${p.image ? "" : "◆"}</div>
    <div class="pbody"><div class="net" style="color:${NC(p.network)}">● ${NL(p.network)} <span class="muted">${p.planned ? short(p.planned) : ""} ${p.time || ""}</span></div>
      <div class="ttl">${esc(first(p))}</div>${badge(p)}</div></div>`;
}

// ============================================================ CALENDRIER
async function pageCal() {
  await refresh();
  const legend = Object.keys(META.networks).map(k => `<span class="chip ${HIDE.has(k) ? "off" : ""}" onclick="toggleNet('${k}')"><i style="background:${NC(k)}"></i>${NL(k)}</span>`).join("");
  const head = CALMODE === "week"
    ? `Semaine du ${WEEK0.toLocaleDateString("fr-FR", {day: "numeric", month: "long"})}`
    : WEEK0.toLocaleDateString("fr-FR", {month: "long", year: "numeric"});
  $("main").innerHTML = `
    <div class="page-head row-head"><div><h1>${head}</h1><p class="muted">Clique sur un post pour le voir, sur ＋ pour en créer un.</p></div>
      <div><button class="b" onclick="moveCal(-1)">‹</button><button class="b" onclick="moveCal(0)">Aujourd'hui</button><button class="b" onclick="moveCal(1)">›</button>
        <span class="seg"><button class="${CALMODE === "week" ? "on" : ""}" onclick="CALMODE='week';pageCal()">Semaine</button><button class="${CALMODE === "month" ? "on" : ""}" onclick="CALMODE='month';WEEK0=new Date(WEEK0.getFullYear(),WEEK0.getMonth(),1,12);pageCal()">Mois</button></span></div></div>
    <div class="legend">${legend}</div>
    ${CALMODE === "week" ? weekView() : monthView()}`;
}
const visible = () => POSTS.filter(p => !HIDE.has(p.network));
function weekView() {
  const today = iso(new Date());
  return `<div class="week">${[0, 1, 2, 3, 4, 5, 6].map(i => {
    const d = iso(addDays(WEEK0, i));
    const ps = visible().filter(p => (p.planned || p.published) === d).sort((a, b) => (a.time || "").localeCompare(b.time || ""));
    return `<div class="wday ${d === today ? "today" : ""}"><div class="wh"><b>${new Date(d + "T12:00").toLocaleDateString("fr-FR", {weekday: "short"})}</b> ${new Date(d + "T12:00").getDate()}</div>
      ${ps.map(card).join("")}<button class="add" onclick="wizard('${d}')">＋</button></div>`;
  }).join("")}</div>`;
}
function monthView() {
  const m = WEEK0.getMonth(), start = mondayOf(new Date(WEEK0.getFullYear(), m, 1, 12)), today = iso(new Date());
  let h = ["lun", "mar", "mer", "jeu", "ven", "sam", "dim"].map(d => `<div class="mh">${d}</div>`).join("");
  for (let i = 0; i < 42; i++) {
    const dd = addDays(start, i), d = iso(dd);
    if (i >= 35 && dd.getMonth() !== m) break;
    const ps = visible().filter(p => (p.planned || p.published) === d);
    h += `<div class="mday ${dd.getMonth() !== m ? "out" : ""} ${d === today ? "today" : ""}" onclick="WEEK0=mondayOf(new Date('${d}T12:00'));CALMODE='week';pageCal()">
      <span class="n">${dd.getDate()}</span><div class="thumbs">${ps.map(p => `<div class="th" title="${esc(first(p))}" style="border-color:${NC(p.network)};${p.image ? `background-image:url('/images/${p.image}')` : ""}"></div>`).join("")}</div></div>`;
  }
  return `<div class="month">${h}</div><p class="muted">Clique sur un jour pour voir sa semaine en détail.</p>`;
}
function moveCal(k) {
  if (k === 0) WEEK0 = CALMODE === "week" ? mondayOf(new Date()) : new Date(new Date().getFullYear(), new Date().getMonth(), 1, 12);
  else if (CALMODE === "week") WEEK0 = addDays(WEEK0, 7 * k);
  else WEEK0 = new Date(WEEK0.getFullYear(), WEEK0.getMonth() + k, 1, 12);
  pageCal();
}
function toggleNet(k) { HIDE.has(k) ? HIDE.delete(k) : HIDE.add(k); pageCal(); }

// ============================================================ POST (aperçu)
async function openPost(id) { await refresh(); CUR = POSTS.find(p => p.id === id); go("post"); }
let EDITING = false;
async function pagePost() {
  if (!CUR) return go("home");
  const p = CUR, prof = PROF[p.network] || {}, check = await api(`/api/posts/${p.id}/check`);
  const blocking = check.items.filter(i => i.level === "bloquant"), tips = check.items.filter(i => i.level !== "bloquant");
  const fam = POSTS.filter(x => p.family && x.family === p.family && x.id !== p.id);
  const g = GUIDES[p.network] || {};
  const imgs = (p.variants || []).filter(Boolean);
  $("main").innerHTML = `
    <div class="crumb"><a href="#" onclick="go('cal');return false">← Calendrier</a></div>
    <div class="postview">
      <div class="phone">
        <div class="ph-head"><div class="av">${esc((prof.name || "É")[0])}</div><div><b>${esc(prof.name || "Étienne Aubin")}</b><div class="muted">${NL(p.network)} · ${p.planned ? short(p.planned) : "sans date"} ${p.time || ""}</div></div>
          <span class="netdot" style="background:${NC(p.network)}"></span></div>
        ${EDITING
          ? `<textarea id="edText" class="edit">${esc(p.text)}</textarea><div class="count" id="edCount"></div>
             <div class="actions"><button class="b p" onclick="saveText()">Enregistrer</button><button class="b" onclick="EDITING=false;pagePost()">Annuler</button><button class="b ghost" onclick="cleanText()">Nettoyer le style</button></div>`
          : `<div class="ph-text">${p.text ? esc(p.text) : `<span class="muted">Ce post n'est pas encore rédigé.</span>`}</div>`}
        ${p.image ? `<img class="ph-img" src="/images/${p.image}">` : `<div class="ph-noimg">Pas encore d'image</div>`}
      </div>
      <div class="side-panel">
        <div class="status-card ${blocking.length ? "s-bad" : p.status === "validé" || p.status === "programmé" ? "s-ok" : "s-warn"}">
          ${badge(p)}<h2>${esc(first(p))}</h2>
          ${blocking.length ? `<ul class="bad">${blocking.map(i => `<li>${esc(i.msg)}</li>`).join("")}</ul>` : ""}
          ${tips.length ? `<details class="tips"><summary>${tips.length} conseil(s)</summary><ul>${tips.map(i => `<li>${esc(i.msg)}</li>`).join("")}</ul></details>` : ""}
        </div>
        ${cognitiveSourceCard(p.id)}
        <div class="big-actions">
          ${!p.text ? `<button class="b p xl" onclick="writeIt(this)">✎ Faire rédiger par Obsidia</button><button class="b xl" onclick="EDITING=true;pagePost()">Rédiger manuellement (sans quota)</button><p class="muted">La rédaction de posts utilise Obsidia / Brody → Qwen local. D'autres outils du Studio utilisent encore Claude Code. Les images du Studio sont rendues localement par Chrome.</p>` : `
          <button class="b p xl" onclick="copyText()">Copier le texte</button>
          <button class="b xl" onclick="copyImg()" ${p.image ? "" : "disabled"}>Copier l'image</button>
          <button class="b xl" onclick="EDITING=true;pagePost()">Modifier le texte</button>
          ${["validé", "programmé"].includes(p.status)
            ? `<button class="b ok xl" onclick="setStatus('publié')">● Marquer comme publié</button>`
            : p.status === "publié" ? "" : `<button class="b ok xl" onclick="setStatus('validé')">✓ Valider</button>`}`}
        </div>
        <div class="panel">
          <div class="row-head"><h3>Image</h3><button class="b small" onclick="newImages(this)">Nouvelles images</button></div>
          <div class="variants">${imgs.length ? imgs.map(n => `<img src="/images/${n}" class="${n === p.image ? "on" : ""}" onclick="chooseImg('${n}')">`).join("")
            : `<span class="muted">Clique sur « Nouvelles images » pour en obtenir 3 au choix.</span>`}</div>
          <details><summary>Changer le texte de l'image</summary>
            <div class="row"><input id="vL1" value="${esc(p.img_l1 || "")}" placeholder="Ligne 1"><input id="vL2" value="${esc(p.img_l2 || "")}" placeholder="Ligne 2"></div>
            <button class="b small" onclick="newImages(this)">Refaire les images</button></details>
        </div>
        ${g.format ? `<div class="panel rules"><h3 style="color:${NC(p.network)}">Règles ${NL(p.network)}</h3><div class="muted">${esc(g.format)}</div></div>` : ""}
        <details class="panel more"><summary>Plus d'options</summary>
          <h4>Réglages du post</h4>
          <div class="row"><select id="oNet">${Object.keys(META.networks).map(k => `<option value="${k}" ${k === p.network ? "selected" : ""}>${NL(k)}</option>`).join("")}</select>
            <input id="oDate" type="date" value="${p.planned || ""}"><input id="oTime" type="time" value="${p.time || ""}"></div>
          <div class="row"><select id="oStatus">${META.statuses.map(s => `<option ${s === p.status ? "selected" : ""}>${s}</option>`).join("")}</select>
            <input id="oSeries" value="${esc(p.series || "")}" placeholder="Série"></div>
          <input id="oNotes" value="${esc(p.notes || "")}" placeholder="Notes, sources, à confirmer">
          <button class="b small" onclick="saveOptions()">Enregistrer les réglages</button>
          <h4>Réécrire avec Obsidia</h4>
          <div class="row"><select id="oTpl"><option value="">Sans modèle</option>${TPL.map(t => `<option value="${t.id}" ${t.id === p.template ? "selected" : ""}>${esc(t.name)}</option>`).join("")}</select>
            <input id="oIdea" placeholder="Ce que tu veux changer ou ajouter"></div>
          <button class="b small" onclick="rewrite(this)">Réécrire</button>
          <h4>Décliner vers</h4>
          <div>${Object.keys(META.networks).filter(k => k !== p.network && !fam.some(x => x.network === k)).map(k => `<button class="b small" style="border-color:${NC(k)}" onclick="declineTo('${k}')">${NL(k)}</button>`).join("")}</div>
          ${fam.length ? `<div class="muted">Versions liées : ${fam.map(x => `<a href="#" onclick="openPost('${x.id}');return false" style="color:${NC(x.network)}">${NL(x.network)}</a>`).join(" · ")}</div>` : ""}
          <h4>Carrousel PDF</h4>
          <button class="b small" onclick="makeCarousel()">Générer le PDF</button> ${p.carousel ? `<a href="/files/${p.carousel}" target="_blank">Ouvrir le PDF</a>` : ""}
          <h4>Statistiques (après publication)</h4>
          <div class="row">${[["impressions", "Impressions"], ["reactions", "Réactions"], ["comments", "Comment."], ["shares", "Partages"], ["followers", "Abonnés"]].map(([k, l]) => `<input id="m-${k}" type="number" min="0" placeholder="${l}" value="${p.metrics?.[k] || ""}">`).join("")}</div>
          <button class="b small" onclick="saveMetrics()">Enregistrer</button>
          <h4>Supprimer</h4><button class="b small ghost" onclick="archive()">Archiver ce post</button>
        </details>
      </div>
    </div>`;
  if (EDITING) { const t = $("edText"); const c = () => { const n = [...t.value].length, lim = META.networks[p.network].limit; $("edCount").textContent = `${n} / ${lim}`; $("edCount").classList.toggle("over", n > lim); }; t.oninput = c; c(); t.focus(); }
}
async function putPost(changes, force) {
  const body = {...CUR, ...changes};
  try { CUR = await api(`/api/posts/${CUR.id}${force ? "?force=true" : ""}`, {method: "PUT", body: JSON.stringify(body)}); return true; }
  catch (e) {
    if (e.status === 409) {
      if (await askModal("La vérification bloque", esc(e.message).replaceAll(" / ", "<br>"), "Valider quand même")) return putPost(changes, true);
      return false;
    }
    toast("Erreur : " + e.message); return false;
  }
}
async function saveText() { const text = $("edText").value; if (await putPost({text, status: text.trim() && CUR.status === "idée" ? "brouillon" : CUR.status})) { EDITING = false; toast("Brouillon enregistré"); pagePost(); } }
async function cleanText() { const r = await api("/api/humanize", {method: "POST", body: JSON.stringify({content: $("edText").value})}); $("edText").value = r.text.trim(); $("edText").oninput(); toast("Style nettoyé (mêmes idées, moins de tics)"); }
async function setStatus(s) { if (await putPost({status: s})) { toast(s === "validé" ? "Validé ✓" : "Marqué comme publié"); pagePost(); topBar(); } }
async function copyText() { await navigator.clipboard.writeText(CUR.text); toast("Texte copié : colle-le sur " + NL(CUR.network)); }
async function copyImg() { const b = await (await fetch("/images/" + CUR.image)).blob(); await navigator.clipboard.write([new ClipboardItem({"image/png": b})]); toast("Image copiée"); }
async function chooseImg(n) { CUR = await api(`/api/posts/${CUR.id}/choose`, {method: "POST", body: JSON.stringify({image: n})}); pagePost(); }
async function newImages(btn) {
  btn.disabled = true; btn.textContent = "Création des images…";
  try { CUR = await api(`/api/posts/${CUR.id}/variants`, {method: "POST", body: JSON.stringify({line1: $("vL1")?.value || "", line2: $("vL2")?.value || ""})}); }
  catch (e) { toast("Images : " + e.message); }
  pagePost();
}
async function saveOptions() {
  if (await putPost({network: $("oNet").value, planned: $("oDate").value, time: $("oTime").value, status: $("oStatus").value, series: $("oSeries").value, notes: $("oNotes").value})) { toast("Réglages enregistrés"); pagePost(); }
}
async function writeIt(btn, idea, template) {
  btn.disabled = true; btn.textContent = "Brody rédige (Qwen si nécessaire)…";
  try {
    const r = await api("/api/generate", {method: "POST", body: JSON.stringify({idea: idea || [CUR.hook, CUR.notes].filter(Boolean).join(" — ") || "post", network: CUR.network, template: template || CUR.template || ""})});
    if (!r.text) { toast("Obsidia n'a pas rendu de texte exploitable"); return pagePost(); }
    rememberCognitiveSource(CUR.id, r.provenance);
    if (r.warning) toast(r.warning);
    const cleaned = (await api("/api/humanize", {method: "POST", body: JSON.stringify({content: r.text})})).text.trim();
    await putPost({text: cleaned, status: CUR.status === "idée" ? "brouillon" : CUR.status});
    if (r.provenance?.source !== "STUDIO_DETERMINISTIC_TEMPLATE") {
      btn.textContent = "Création des images…";
      CUR = await api(`/api/posts/${CUR.id}/variants`, {method: "POST", body: JSON.stringify({})});
    }
  } catch (e) { toast("Erreur : " + e.message); }
  pagePost();
}
async function rewrite(btn) {
  btn.disabled = true; btn.textContent = "Brody réécrit (Qwen si nécessaire)…";
  try {
    const r = await api("/api/generate", {method: "POST", body: JSON.stringify({idea: $("oIdea").value || "améliorer ce post", network: CUR.network, source_text: CUR.text, template: $("oTpl").value})});
    if (r.text) { rememberCognitiveSource(CUR.id, r.provenance); if (r.warning) toast(r.warning); await putPost({text: (await api("/api/humanize", {method: "POST", body: JSON.stringify({content: r.text})})).text.trim(), template: $("oTpl").value}); toast("Réécrit"); }
  } catch (e) { toast("Erreur : " + e.message); }
  pagePost();
}
async function declineTo(k) { await api(`/api/posts/${CUR.id}/decline`, {method: "POST", body: JSON.stringify({networks: [k]})}); toast(`Version ${NL(k)} en préparation (1 à 2 min) : elle apparaîtra dans le calendrier`); }
async function makeCarousel() { try { const r = await api(`/api/posts/${CUR.id}/carousel`, {method: "POST"}); window.open("/files/" + r.file); } catch (e) { toast(e.message); } }
async function saveMetrics() {
  const b = {}; ["impressions", "reactions", "comments", "shares", "followers"].forEach(k => b[k] = +$("m-" + k).value || 0);
  CUR = await api(`/api/posts/${CUR.id}/metrics`, {method: "PUT", body: JSON.stringify(b)}); toast("Statistiques enregistrées");
}
async function archive() { if (await askModal("Archiver ce post ?", "Il disparaît du calendrier (une copie est gardée dans data/backups).", "Archiver")) { await api(`/api/posts/${CUR.id}/archive`, {method: "POST"}); CUR = null; go("cal"); } }

// ============================================================ fenêtre (modale)
function closeModal() { $("modal").classList.remove("on"); }
function askModal(title, html, okLabel) {
  return new Promise(res => {
    $("sheet").innerHTML = `<h2>${title}</h2><div>${html}</div><div class="actions"><button class="b p" id="mOk">${okLabel}</button><button class="b" id="mNo">Annuler</button></div>`;
    $("modal").classList.add("on");
    $("mOk").onclick = () => { closeModal(); res(true); };
    $("mNo").onclick = () => { closeModal(); res(false); };
  });
}

// ============================================================ NOUVEAU POST (3 étapes)
let WZ = {};
function wizard(date) {
  WZ = {date: date || iso(addDays(new Date(), 1)), network: "linkedin", template: ""};
  $("sheet").innerHTML = `<div class="steps"><b>1</b> Type de post · <span>2 Idée</span> · <span>3 Rédaction</span></div>
    <h2>Quel type de post ?</h2>
    <div class="tpls">${[{id: "", name: "Libre", when: "Pas de structure imposée : Claude choisit la meilleure forme."}, ...TPL].map(t => `
      <div class="tpl" onclick="WZ.template='${t.id}';wizard2()"><div class="tpl-ico">${tplIcon(t.id)}</div><b>${esc(t.name)}</b><span>${esc(t.when)}</span>
      ${t.networks ? `<div>${t.networks.map(n => `<i style="background:${NC(n)}"></i>`).join("")}</div>` : ""}</div>`).join("")}</div>`;
  $("modal").classList.add("on");
}
const tplIcon = id => ({position: "⚑", journal: "✍", correction: "⟲", mecanisme: "⚙", question: "?", citation: "❝", fil: "≡", carrousel: "▤", video: "▶", parcours: "⛰"}[id] || "◆");
async function wizard2() {
  const t = TPL.find(x => x.id === WZ.template);
  const journal = (await api("/api/journal")).content.split("\n").filter(l => l.startsWith("- ")).slice(-6).reverse();
  $("sheet").innerHTML = `<div class="steps"><span>1 Type</span> · <b>2</b> Idée · <span>3 Rédaction</span></div>
    <h2>${t ? esc(t.name) : "Post libre"}</h2>
    <label>Réseau</label><div class="netpick">${Object.keys(META.networks).map(k => `<button class="np ${k === WZ.network ? "on" : ""}" style="--c:${NC(k)}" onclick="WZ.network='${k}';this.parentNode.querySelectorAll('.np').forEach(b=>b.classList.remove('on'));this.classList.add('on')">${NL(k)}</button>`).join("")}</div>
    <div class="row"><div><label>Date</label><input type="date" id="wDate" value="${WZ.date}"></div></div>
    <label>Ton idée, ou ce qui s'est passé</label><textarea id="wIdea" class="short" placeholder="ex. Brody fusionnait deux hypothèses : j'ai ajouté une règle pour qu'il les garde séparées"></textarea>
    ${journal.length ? `<label>Ou pars d'un fait récent de ton journal</label><div class="facts">${journal.map(l => `<button class="fact" onclick="$('wIdea').value=this.textContent">${esc(l.replace(/^- /, ""))}</button>`).join("")}</div>` : ""}
    <div class="actions"><button class="b p" onclick="wizard3(this)">Faire rédiger par Obsidia</button><button class="b" onclick="wizardSaveIdea(this)">Enregistrer l'idée seule</button><button class="b" onclick="wizard()">← Retour</button></div>`;
}
// Le mode brouillon manuel ne consomme aucun quota Claude et conserve l'idée localement.
async function wizardSaveIdea(btn) {
  const idea = $("wIdea")?.value.trim() || "";
  if (!idea) return toast("Écris une idée, même en quelques mots");
  WZ.date = $("wDate").value;
  btn.disabled = true;
  try {
    const p = await api("/api/posts", {method: "POST", body: JSON.stringify({
      network: WZ.network, planned: WZ.date, time: META.networks[WZ.network].time,
      status: "idée", hook: idea.slice(0, 120), notes: idea, template: WZ.template,
      series: "Journal d'éducation d'Obsidia"
    })});
    closeModal();
    EDITING = false;
    await openPost(p.id);
    toast("Idée enregistrée — aucune génération IA lancée");
  } catch (e) {
    btn.disabled = false;
    toast("Impossible d'enregistrer : " + e.message);
  }
}
async function wizard3(btn) {
  const idea = $("wIdea").value.trim();
  if (!idea) return toast("Écris une idée, même en quelques mots");
  WZ.date = $("wDate").value;
  btn.disabled = true;
  $("sheet").innerHTML = `<div class="steps"><span>1 Type</span> · <span>2 Idée</span> · <b>3</b> Rédaction</div><div class="writing"><div class="spin"></div><h2>Brody rédige (Qwen si nécessaire) ton post…</h2><p class="muted">Puis le nettoie et crée 3 images. Compte 1 à 3 minutes.</p></div>`;
  try {
    const p = await api("/api/posts", {method: "POST", body: JSON.stringify({network: WZ.network, planned: WZ.date, time: META.networks[WZ.network].time, status: "idée", hook: idea.slice(0, 120), template: WZ.template, series: "Journal d'éducation d'Obsidia"})});
    await refresh(); CUR = POSTS.find(x => x.id === p.id);
    const r = await api("/api/generate", {method: "POST", body: JSON.stringify({idea, network: WZ.network, template: WZ.template})});
    if (r.text) {
      rememberCognitiveSource(p.id, r.provenance);
      if (r.warning) toast(r.warning);
      const cleaned = (await api("/api/humanize", {method: "POST", body: JSON.stringify({content: r.text})})).text.trim();
      await putPost({text: cleaned, status: "brouillon", hook: cleaned.split("\n")[0].slice(0, 120)});
      if (r.provenance?.source !== "STUDIO_DETERMINISTIC_TEMPLATE") {
        CUR = await api(`/api/posts/${p.id}/variants`, {method: "POST", body: JSON.stringify({})});
      }
    } else toast("Obsidia n'a pas rendu de texte : réessaie depuis le post");
  } catch (e) { toast("Erreur : " + e.message); }
  closeModal(); EDITING = false; go("post");
}

// ============================================================ IDÉES (suggestions, journal, campagnes, trimestre)
let IDEATAB = "atelier";
let ATELIER_FILTER = {network: "", search: ""};
const ATELIER_SELECTED = new Set();
async function pageIdeas(tab) {
  if (tab) IDEATAB = tab;
  $("main").innerHTML = `<div class="page-head"><h1>Idées</h1><p class="muted">Ce qui nourrit tes posts : des idées, des faits réels, des campagnes.</p></div>
    <div class="tabs">${[["atelier", "Atelier"], ["sugg", "Suggestions"], ["journal", "Journal & audit"], ["camp", "Campagnes"], ["quarter", "Trimestre"]].map(([k, l]) => `<button class="${k === IDEATAB ? "on" : ""}" onclick="pageIdeas('${k}')">${l}</button>`).join("")}</div>
    <div id="ideaBody"></div>`;
  ({atelier: ideasAtelier, sugg: ideasSugg, journal: ideasJournal, camp: ideasCamp, quarter: ideasQuarter})[IDEATAB]();
}
// Tableau éditorial : filtre réseau/texte et changement de statut avec contrôles du serveur.
async function ideasAtelier() {
  await refresh();
  const status = ["idée", "brouillon", "validé", "programmé", "publié"];
  $("ideaBody").innerHTML = `
    <div class="panel atelier-tools">
      <div class="row">
        <input id="atelierSearch" placeholder="Rechercher un post, un sujet ou une série…" value="${esc(ATELIER_FILTER.search)}" oninput="filterAtelier()">
        <select id="atelierNetwork" onchange="filterAtelier()">
          <option value="">Tous les réseaux</option>
          ${Object.keys(META.networks).map(k => `<option value="${k}" ${k === ATELIER_FILTER.network ? "selected" : ""}>${esc(NL(k))}</option>`).join("")}
        </select>
        <button class="b p" style="flex:0 0 auto" onclick="wizard()">＋ Nouveau post</button>
      </div>
      <p class="muted">Glisse une carte entre les colonnes, ou sélectionne des cartes pour une action groupée. Aucun post ne sera publié automatiquement.</p><div class="atelier-bulk"><span id="atelierCount">0 sélectionné</span><button class="b small" onclick="atelierSelectAll()">Tout sélectionner (filtré)</button><button class="b small" onclick="atelierClear()">Effacer</button><select id="atelierDestination"><option value="">Déplacer vers…</option><option value="idée">Idée</option><option value="brouillon">Brouillon</option><option value="validé">Validé</option><option value="programmé">Programmé</option></select><button class="b p small" onclick="atelierBatch()">Appliquer</button></div>
    </div>
    <div class="atelier-board" id="atelierBoard"></div>`;
  renderAtelier(status);
}
function filterAtelier() {
  ATELIER_FILTER = {network: $("atelierNetwork").value, search: $("atelierSearch").value};
  renderAtelier();
}
function renderAtelier() {
  const board = $("atelierBoard"); if (!board) return;
  const q = ATELIER_FILTER.search.toLocaleLowerCase("fr");
  const matches = POSTS.filter(p => (!ATELIER_FILTER.network || p.network === ATELIER_FILTER.network) &&
    (!q || [p.hook, p.text, p.series, p.notes].some(v => String(v || "").toLocaleLowerCase("fr").includes(q))));
  const status = ["idée", "brouillon", "validé", "programmé", "publié"];
  board.innerHTML = status.map(st => {
    const ps = matches.filter(p => p.status === st).sort((a,b) => (a.planned || "9999").localeCompare(b.planned || "9999"));
    return `<section class="atelier-col" ondragover="atelierDragOver(event)" ondragleave="atelierDragLeave(event)" ondrop="atelierDrop(event, this.dataset.status)" data-status="${st}"><h3>${esc(st)} <span class="tag">${ps.length}</span></h3>
      ${ps.map(p => `<article class="atelier-card" draggable="true" ondragstart="atelierDragStart(event, this.dataset.id)" ondragend="atelierDragEnd(event)" data-id="${p.id}">
        <div class="net" style="color:${NC(p.network)}">● ${esc(NL(p.network))} ${p.planned ? "· " + esc(p.planned) : "· sans date"}</div>
        <label class="atelier-check"><input type="checkbox" ${ATELIER_SELECTED.has(p.id) ? "checked" : ""} onchange="atelierToggle(\'${p.id}\',this.checked)"> Sélectionner</label><button class="atelier-title" onclick="openPost('${p.id}')">${esc(first(p))}</button>
        ${p.check_flag ? `<div class="bad" style="font-size:12px">À corriger : ${esc(p.check_flag)}</div>` : ""}
        <div class="atelier-actions"><button class="b small" onclick="openPost('${p.id}')">Ouvrir</button>
          <select aria-label="Changer le statut" onchange="atelierSetStatus('${p.id}',this)">
            ${status.map(x => `<option value="${x}" ${x === st ? "selected" : ""}>${esc(x)}</option>`).join("")}
          </select></div>
      </article>`).join("") || '<p class="muted">Aucun post.</p>'}</section>`;
  }).join("");
  atelierUpdateSelectedCount();
}
async function atelierSetStatus(id, select) {
  const p = POSTS.find(x => x.id === id); if (!p) return;
  const next = select.value;
  select.disabled = true;
  // Un post ne doit pas être déclaré publié par un changement rapide de colonne.
  if (next === "publié" && p.status !== "publié") {
    select.value = p.status;
    select.disabled = false;
    toast("Ouvre le post et utilise « Marquer comme publié » après publication réelle.");
    return;
  }
  if (next === p.status) { select.disabled = false; return; }
  try {
    await api(`/api/posts/${id}`, {method: "PUT", body: JSON.stringify({...p, status: next})});
    await refresh();
    renderAtelier();
    toast("Statut modifié : " + next);
  } catch (e) {
    select.value = p.status;
    select.disabled = false;
    toast("Statut inchangé : " + e.message);
  }
}
function atelierUpdateSelectedCount() { const el = $("atelierCount"); if (el) el.textContent = ATELIER_SELECTED.size + " sélectionné(s)"; }
function atelierToggle(id, value) { if(value) ATELIER_SELECTED.add(id); else ATELIER_SELECTED.delete(id); atelierUpdateSelectedCount(); }
function atelierClear() { ATELIER_SELECTED.clear(); renderAtelier(); }
function atelierSelectAll() {
 const q = ATELIER_FILTER.search.toLocaleLowerCase("fr");
 POSTS.filter(p => (!ATELIER_FILTER.network || p.network === ATELIER_FILTER.network) && (!q || [p.hook,p.text,p.series,p.notes].some(v => String(v || "").toLocaleLowerCase("fr").includes(q)))).forEach(p => ATELIER_SELECTED.add(p.id));
 renderAtelier();
}
function atelierDragStart(e,id) { e.dataTransfer.setData("text/plain",id); e.dataTransfer.effectAllowed="move"; e.currentTarget.classList.add("dragging"); }
function atelierDragEnd(e) { e.currentTarget.classList.remove("dragging"); document.querySelectorAll(".atelier-col").forEach(el=>el.classList.remove("drop-target")); }
function atelierDragOver(e) { e.preventDefault(); e.currentTarget.classList.add("drop-target"); }
function atelierDragLeave(e) { if(!e.currentTarget.contains(e.relatedTarget)) e.currentTarget.classList.remove("drop-target"); }
async function atelierDrop(e,status) {
 e.preventDefault(); e.currentTarget.classList.remove("drop-target");
 const id=e.dataTransfer.getData("text/plain"), p=POSTS.find(x=>x.id===id);
 if(!p || p.status===status) return;
 if(status==="publié") return toast("Ouvre le post pour confirmer une publication réelle.");
 try { await api("/api/posts/"+id,{method:"PUT",body:JSON.stringify({...p,status})}); await refresh(); renderAtelier(); toast("Post déplacé"); }
 catch(err) { toast("Déplacement bloqué : "+err.message); }
}
async function atelierBatch() {
 const status=$("atelierDestination").value, ids=[...ATELIER_SELECTED];
 if(!status || !ids.length) return toast("Choisis une destination et au moins un post.");
 const confirmed=await askModal("Déplacer "+ids.length+" posts ?", "Les contrôles restent appliqués à chaque publication. Aucune publication automatique.", "Confirmer");
 if(!confirmed) return;
 let done=0, fail=0;
 for(const id of ids) { const p=POSTS.find(x=>x.id===id); if(!p) continue;
  if(p.status===status) {ATELIER_SELECTED.delete(id);continue;}
  try {await api("/api/posts/"+id,{method:"PUT",body:JSON.stringify({...p,status})});ATELIER_SELECTED.delete(id);done++;}
  catch(e){fail++;}
 }
 await refresh();renderAtelier();toast(done+" modifié(s), "+fail+" bloqué(s).");
}
function ideasSugg() {
  $("ideaBody").innerHTML = `<div class="panel"><div class="row"><input id="sAsk" placeholder="Un angle particulier ? (facultatif) ex. des idées Instagram autour de Brody"><button class="b p" style="flex:0 0 auto" onclick="suggest(this)">Proposer 6 idées</button></div></div><div class="ideas" id="sOut"></div>`;
}
let SUGG = [];
async function suggest(btn) {
  btn.disabled = true; $("sOut").innerHTML = `<div class="writing"><div class="spin"></div><p class="muted">Claude réfléchit (1 à 3 min)…</p></div>`;
  try { SUGG = (await api("/api/suggest", {method: "POST", body: JSON.stringify({content: $("sAsk").value})})).items || []; } catch (e) { toast(e.message); }
  btn.disabled = false;
  $("sOut").innerHTML = SUGG.map((s, i) => `<div class="idea" style="border-top-color:${NC(s.network)}"><div class="net" style="color:${NC(s.network)}">● ${NL(s.network)}</div>
    <h3>${esc(s.hook)}</h3><p>${esc(s.angle)}</p><div class="muted">Pourquoi : ${esc(s.pourquoi)}</div><div class="muted">Fait nécessaire : ${esc(s.preuve)}</div>
    <button class="b small" onclick="adopt(${i},this)">Ajouter au calendrier</button></div>`).join("");
}
async function adopt(i, btn) {
  const s = SUGG[i], net = META.networks[s.network] ? s.network : "linkedin";
  await api("/api/posts", {method: "POST", body: JSON.stringify({network: net, status: "idée", hook: s.hook, planned: iso(addDays(new Date(), 2)), time: META.networks[net].time, notes: `Angle : ${s.angle} · Fait nécessaire : ${s.preuve}`, series: "Journal d'éducation d'Obsidia"})});
  btn.textContent = "Ajouté ✓"; btn.disabled = true;
}
async function ideasJournal() {
  const a = await api("/api/audit"), j = (await api("/api/journal")).content;
  const p = a.pending;
  const left = p ? [...(p.journal || []).map((x, i) => ({...x, kind: "journal", i})), ...(p.proofs || []).map((x, i) => ({...x, kind: "proof", i}))].filter(x => !x.done) : [];
  $("ideaBody").innerHTML = `<div class="two">
    <div><div class="panel"><h3>Noter un fait réel</h3><p class="muted">Ce qui s'est passé dans Obsidia. C'est la matière première des posts : Claude ne cite que des faits notés ici.</p>
      <div class="row"><input id="jText" placeholder="ex. la mémoire est branchée en lecture seule sur la cognition"><button class="b p" style="flex:0 0 auto" onclick="addFact()">Ajouter</button></div></div>
      <div class="panel"><h3>Mon journal</h3><div class="journal">${j.split("\n").filter(l => l.startsWith("- ")).reverse().map(l => `<div>${esc(l.slice(2))}</div>`).join("") || `<span class="muted">Vide.</span>`}</div></div></div>
    <div><div class="panel"><h3>Audit de mes avancées</h3><p class="muted">Claude lit l'historique git de ton PC et de GitHub (sans rien modifier) et te propose des faits. Les preuves arrivent en privé.</p>
      <button class="b p" onclick="runAudit(this)" ${a.job.running ? "disabled" : ""}>${a.job.running ? "Audit en cours…" : "Lancer l'audit"}</button> <span class="muted">${esc(a.job.msg || "")}</span>
      ${p ? `<p>${esc(p.summary || "")}</p>` : ""}
      ${left.map(x => `<div class="fact-row"><span class="tag">${x.kind === "journal" ? "fait" : esc(x.status)}</span>${esc(x.text || x.claim)}<button class="b small" onclick="acceptA('${x.kind}',${x.i})">Garder</button></div>`).join("")}
      ${p && !left.length ? `<p class="muted">Tout est trié ✓</p>` : ""}
      ${p?.sensible?.length ? `<details><summary class="warn">${p.sensible.length} point(s) à ne pas publier tel quel</summary><ul>${p.sensible.map(s => `<li>${esc(s)}</li>`).join("")}</ul></details>` : ""}</div></div></div>`;
  if (a.job.running) setTimeout(() => IDEATAB === "journal" && PAGE === "ideas" && ideasJournal(), 6000);
}
async function addFact() { if (!$("jText").value.trim()) return; await api("/api/journal", {method: "POST", body: JSON.stringify({text: $("jText").value})}); toast("Fait ajouté"); ideasJournal(); }
async function runAudit() { try { await api("/api/audit", {method: "POST", body: JSON.stringify({})}); } catch (e) { toast(e.message); } ideasJournal(); }
async function acceptA(kind, index) { await api("/api/audit/accept", {method: "POST", body: JSON.stringify({kind, index})}); ideasJournal(); }
async function ideasCamp() {
  const cs = await api("/api/campaigns");
  $("ideaBody").innerHTML = `<div class="two"><div class="panel"><h3>Nouvelle campagne</h3>
      <input id="cName" value="Journal d'éducation d'Obsidia" placeholder="Nom">
      <input id="cGoal" placeholder="Objectif" style="margin-top:8px"><input id="cTheme" placeholder="Thème / fil conducteur" style="margin-top:8px">
      <div class="row" style="margin-top:8px"><input id="cStart" type="date" value="${iso(addDays(new Date(), 1))}"><input id="cWeeks" type="number" value="4" min="1" max="12" title="semaines"></div>
      <label>Posts par semaine</label><div class="row">${Object.keys(META.networks).map(k => `<label class="mini-num"><span style="color:${NC(k)}">${NL(k)}</span><input type="number" min="0" max="7" id="cad-${k}" value="${k === "linkedin" ? 2 : 0}"></label>`).join("")}</div>
      <button class="b p" onclick="newCamp()">Créer</button></div>
    <div>${cs.map(c => {
      const n = Object.values(c.counts).reduce((a, b) => a + b, 0), j = c.job;
      return `<div class="panel"><h3>${esc(c.name)}</h3><div class="muted">Début ${c.start} · ${c.weeks} semaines · ${c.slots} posts</div>
        ${c.arc ? `<p>${esc(c.arc)}</p>` : ""}<div class="prog"><span style="width:${n ? Math.round(100 * (n - c.counts["idée"]) / n) : 0}%"></span></div>
        <div class="muted">${META.statuses.map(s => `${c.counts[s]} ${s}`).join(" · ")}${j ? ` · rédaction ${j.done}/${j.total}${j.running ? " en cours…" : ""}` : ""}</div>
        <div class="actions">${!n ? `<button class="b p small" onclick="planCamp('${c.id}',this)">Planifier avec Claude</button>` : ""}
        ${c.counts["idée"] && !(j && j.running) ? `<button class="b small" onclick="draftCamp('${c.id}')">Tout rédiger</button>` : ""}</div></div>`;
    }).join("") || `<p class="muted">Aucune campagne.</p>`}</div></div>`;
  if (cs.some(c => c.job?.running)) setTimeout(() => IDEATAB === "camp" && PAGE === "ideas" && ideasCamp(), 10000);
}
async function newCamp() {
  const cadence = {}; Object.keys(META.networks).forEach(k => { const v = +$("cad-" + k).value; if (v) cadence[k] = v; });
  await api("/api/campaigns", {method: "POST", body: JSON.stringify({name: $("cName").value, goal: $("cGoal").value, theme: $("cTheme").value, start: $("cStart").value, weeks: +$("cWeeks").value, cadence})});
  ideasCamp();
}
async function planCamp(id, btn) { btn.disabled = true; btn.textContent = "Claude planifie…"; try { await api(`/api/campaigns/${id}/plan`, {method: "POST"}); } catch (e) { toast(e.message); } ideasCamp(); }
async function draftCamp(id) { await api(`/api/campaigns/${id}/draft`, {method: "POST"}); toast("Rédaction lancée en arrière-plan"); ideasCamp(); }
async function ideasQuarter() {
  const qs = await api("/api/quarters"), d = new Date();
  $("ideaBody").innerHTML = `<div class="panel"><div class="row"><input id="qId" value="${d.getFullYear()}-T${Math.floor(d.getMonth() / 3) + 1}" style="flex:0 0 140px"><input id="qGoal" placeholder="Objectif du trimestre"><button class="b p" style="flex:0 0 auto" onclick="makeQ(this)">Construire le plan</button></div></div>
    ${qs.map(q => `<div class="panel"><div class="row-head"><h2>${esc(q.quarter)}</h2>${q.campaigns.length ? `<button class="b p small" onclick="qCamps('${q.quarter}')">Créer les ${q.campaigns.length} campagnes</button>` : ""}</div><div class="md">${esc(q.content)}</div></div>`).join("")}`;
}
async function makeQ(btn) { btn.disabled = true; btn.textContent = "Claude construit le plan…"; try { await api("/api/quarters", {method: "POST", body: JSON.stringify({quarter: $("qId").value, goal: $("qGoal").value})}); } catch (e) { toast(e.message); } ideasQuarter(); }
async function qCamps(q) { const r = await api(`/api/quarters/${q}/campaigns`, {method: "POST"}); toast(`${r.created.length} campagne(s) créée(s)`); pageIdeas("camp"); }

// ============================================================ RÉSULTATS
async function pageResults() {
  const s = await api("/api/stats");
  const J = ["lun", "mar", "mer", "jeu", "ven", "sam", "dim"];
  const bars = (rows, key, fmt) => { const mx = Math.max(...rows.map(r => r.er), 1); return rows.sort((a, b) => b.er - a.er).map(r => `<div class="bar"><span class="bl">${NL(r.network)} · ${fmt(r[key])}</span><span class="bt"><span style="width:${100 * r.er / mx}%;background:${NC(r.network)}"></span></span><b>${r.er} %</b><span class="muted">n=${r.n}</span></div>`).join(""); };
  $("main").innerHTML = `<div class="page-head row-head"><div><h1>Résultats</h1><p class="muted">Saisis les chiffres d'un post publié dans « Plus d'options » du post. Le reste se calcule.</p></div>
      <button class="b" onclick="adjust(this)">Ajuster mes horaires d'après mes chiffres</button></div>
    ${!s.n ? `<div class="hero empty"><div class="txt"><div class="kick">Pas encore de chiffres</div><h1>Publie, puis note tes statistiques.</h1><p class="muted">Impressions, réactions, commentaires : 30 secondes par post, et ici tu verras ce qui marche vraiment pour toi.</p></div></div>` : `
    <div class="kpis">${kpi(s.n, "posts mesurés", "info", "results")}${kpi((100 * s.posts.reduce((a, p) => a + p.er, 0) / s.n).toFixed(1) + " %", "engagement moyen", "ok", "results")}${kpi(s.posts.reduce((a, p) => a + p.impressions, 0), "impressions", "info", "results")}</div>
    <div class="two"><div class="panel"><h3>Par jour</h3>${bars(s.by_weekday, "weekday", d => J[d])}</div><div class="panel"><h3>Par heure</h3>${bars(s.by_hour, "hour", h => (h || "?") + " h")}</div></div>
    <div class="two"><div class="panel"><h3>Par type de post</h3>${bars(s.by_template, "template", t => esc(TPL.find(x => x.id === t)?.name || t))}</div>
      <div class="panel"><h3>Meilleurs posts</h3>${s.posts.slice(0, 6).map(p => `<div class="bar"><span class="bl" style="color:${NC(p.network)}">${NL(p.network)}</span><span class="tt">${esc(p.first)}</span><b>${(100 * p.er).toFixed(1)} %</b></div>`).join("")}</div></div>
    <p class="muted">Moins de ${s.min_for_adjust} posts par réseau : ce sont des tendances, pas des certitudes.</p>`}
    <pre id="adj" style="display:none"></pre>`;
}
async function adjust() { const r = await api("/api/stats/adjust", {method: "POST"}); $("adj").style.display = "block"; $("adj").textContent = r.changes.join("\n"); META = await api("/api/meta"); }

// ============================================================ RÉGLAGES
let SETTAB = "pilot";
function pageSettings(tab) {
  if (tab) SETTAB = tab;
  $("main").innerHTML = `<div class="page-head"><h1>Réglages</h1></div>
    <div class="tabs">${[["pilot", "Pilote auto"], ["rules", "Règles des réseaux"], ["tpl", "Types de posts"], ["proofs", "Preuves"], ["voice", "Ma voix & histoire"], ["nets", "Mes réseaux"]].map(([k, l]) => `<button class="${k === SETTAB ? "on" : ""}" onclick="pageSettings('${k}')">${l}</button>`).join("")}</div>
    <div id="setBody"></div>`;
  ({pilot: setPilot, rules: setRules, tpl: setTpl, proofs: setProofs, voice: setVoice, nets: setNets})[SETTAB]();
}
async function setPilot() {
  const c = await api("/api/autopilot");
  const chk = (id, on, label) => `<label class="switch"><input type="checkbox" id="${id}" ${on ? "checked" : ""}><span></span>${label}</label>`;
  const nets = (g, sel, ex) => Object.keys(META.networks).filter(k => k !== ex).map(k => `<label class="chip"><input type="checkbox" data-g="${g}" value="${k}" ${sel.includes(k) ? "checked" : ""}> ${NL(k)}</label>`).join("");
  $("setBody").innerHTML = `<div class="two"><div class="panel">
    ${chk("apEnabled", c.enabled, "<b>Pilote automatique</b>")}
    <div class="sub">Il prépare tout en arrière-plan tant que le studio est ouvert. <b>Il ne publie jamais.</b></div>
    ${chk("apDraft", c.auto_draft, `Rédiger les idées des <input id="apH" type="number" class="mini" value="${c.draft_horizon_days}"> prochains jours (texte + 3 images)`)}
    ${chk("apRefill", c.auto_refill, `Garder au moins <input id="apMin" type="number" class="mini" value="${c.min_planned_14d}"> posts prévus sur 14 jours`)}
    <div class="sub">${nets("refill", c.refill_networks)}</div>
    ${chk("apDecline", c.auto_decline, "Décliner chaque post LinkedIn validé vers :")}
    <div class="sub">${nets("decl", c.decline_to, "linkedin")}</div>
    ${chk("apCheck", c.auto_check, "Vérifier en continu tous les brouillons")}
    ${chk("apAudit", c.auto_audit, "Auditer mes avancées GitHub + PC chaque semaine")}
    <button class="b p" onclick="savePilot()">Enregistrer</button></div>
    <div class="panel"><h3>Activité récente</h3>${(window._events || []).map(e => `<div class="muted">${e.at} · ${esc(e.msg)}</div>`).join("") || `<span class="muted">Rien pour l'instant.</span>`}
    <p class="muted" style="margin-top:14px">Chaque rédaction utilise ton quota Claude Code.</p></div></div>`;
}
async function savePilot() {
  const pick = g => [...document.querySelectorAll(`input[data-g="${g}"]:checked`)].map(x => x.value);
  await api("/api/autopilot", {method: "PUT", body: JSON.stringify({enabled: $("apEnabled").checked, auto_draft: $("apDraft").checked, draft_horizon_days: +$("apH").value,
    auto_refill: $("apRefill").checked, min_planned_14d: +$("apMin").value, refill_networks: pick("refill"), auto_decline: $("apDecline").checked,
    decline_to: pick("decl"), auto_check: $("apCheck").checked, auto_audit: $("apAudit").checked})});
  toast("Enregistré"); topBar();
}
function setRules() {
  $("setBody").innerHTML = `<div class="rules-grid">${Object.entries(GUIDES).filter(([k]) => !k.startsWith("_")).map(([k, g]) => `
    <div class="guide" style="border-top-color:${NC(k)}"><h3 style="color:${NC(k)}">${NL(k)}</h3><p>${esc(g.role)}</p>
      <div class="k">Ton</div><div>${esc(g.ton)}</div><div class="k">Format</div><div>${esc(g.format)}</div>
      <div class="k">À faire</div><ul>${(g.faire || []).map(x => `<li>${esc(x)}</li>`).join("")}</ul>
      <div class="k">À éviter</div><ul>${(g.eviter || []).map(x => `<li>${esc(x)}</li>`).join("")}</ul>
      <div class="k">Rythme · heure</div><div>${esc(g.rythme)} · ${META.networks[k]?.time || ""}</div></div>`).join("")}</div>
    ${docEditor("guides", "Modifier les règles (format JSON)")}`;
}
function setTpl() {
  $("setBody").innerHTML = `<div class="tpls">${TPL.map(t => `<div class="tpl"><div class="tpl-ico">${tplIcon(t.id)}</div><b>${esc(t.name)}</b><span>${esc(t.when)}</span>
      <div>${t.networks.map(n => `<i style="background:${NC(n)}"></i>`).join("")}</div><pre>${esc(t.structure)}</pre></div>`).join("")}</div>
    ${docEditor("templates", "Modifier les types de posts (format JSON)")}`;
}
async function setProofs() {
  const d = await api("/api/proofs");
  $("setBody").innerHTML = `<div class="two"><div class="panel"><h3>Ajouter une preuve</h3>
      <input id="pClaim" placeholder="Affirmation"><div class="row" style="margin-top:8px"><select id="pStatus">${d.statuses.map(s => `<option>${s}</option>`).join("")}</select><input id="pDate" type="date"></div>
      <input id="pSource" placeholder="Source (document, commit, rapport)" style="margin-top:8px"><input id="pScope" placeholder="Périmètre / hypothèses" style="margin-top:8px">
      <label class="switch"><input type="checkbox" id="pPublic"><span></span>Publiable</label><button class="b p" onclick="addProof()">Ajouter</button>
      <p class="muted">VISION = objectif · RÉALISÉ-DOC = fait et documenté · TESTÉ = test avec périmètre · PROUVÉ = preuve formelle · ACTUEL = vérifié récemment.</p></div>
    <div>${d.items.map(p => `<div class="panel proof"><span class="tag">${esc(p.status)}</span><span class="tag ${p.public ? "ok" : "warn"}">${p.public ? "publiable" : "privé"}</span>
      <b>${esc(p.claim)}</b><div class="muted">${esc(p.source)} ${esc(p.date)} ${p.scope ? "· " + esc(p.scope) : ""}</div>
      <div class="actions"><button class="b small" onclick="togglePublic('${p.id}')">${p.public ? "Rendre privé" : "Rendre publiable"}</button><button class="b small ghost" onclick="delProof('${p.id}')">Supprimer</button></div></div>`).join("") || `<p class="muted">Aucune preuve. L'audit (Idées → Journal & audit) en propose.</p>`}</div></div>`;
  window._proofs = d.items;
}
async function addProof() { await api("/api/proofs", {method: "POST", body: JSON.stringify({claim: $("pClaim").value, status: $("pStatus").value, source: $("pSource").value, date: $("pDate").value, scope: $("pScope").value, public: $("pPublic").checked})}); setProofs(); }
async function togglePublic(id) { const p = window._proofs.find(x => x.id === id); await api(`/api/proofs/${id}`, {method: "PUT", body: JSON.stringify({...p, public: !p.public})}); setProofs(); }
async function delProof(id) { if (await askModal("Supprimer cette preuve ?", "", "Supprimer")) { await api(`/api/proofs/${id}`, {method: "DELETE"}); setProofs(); } }
function setVoice() {
  $("setBody").innerHTML = `<div class="tabs small">${[["story", "Mon histoire"], ["voice", "Ma voix"], ["plan", "Plan de la série"], ["sources", "Sources de l'audit"]].map(([k, l]) => `<button onclick="loadDocInto('${k}')">${l}</button>`).join("")}</div><div id="docBox"></div>`;
  loadDocInto("story");
}
function docEditor(key, label) { setTimeout(() => loadDocInto(key, "docBox2"), 0); return `<details class="panel"><summary>${label}</summary><div id="docBox2"></div></details>`; }
async function loadDocInto(key, box = "docBox") {
  const c = (await api("/api/docs/" + key)).content;
  $(box).innerHTML = `<textarea class="doc" id="doc-${key}">${esc(c)}</textarea><button class="b p" onclick="saveDocK('${key}')">Enregistrer</button>`;
}
async function saveDocK(key) {
  try { await api("/api/docs/" + key, {method: "PUT", body: JSON.stringify({content: $("doc-" + key).value})}); toast("Enregistré (sauvegarde faite)"); await loadRefs(); }
  catch (e) { toast(e.message); }
}
function setNets() {
  $("setBody").innerHTML = `<div class="panel narrow">${Object.entries(PROF).map(([k, v]) => `<div class="row" style="align-items:center;margin-bottom:8px"><b style="flex:0 0 120px;color:${NC(k)}">${esc(META.networks[k] ? NL(k) : k)}</b><input data-k="${k}" class="purl" value="${esc(v.url)}" placeholder="https://…"><input data-n="${k}" class="pname" value="${esc(v.name)}" placeholder="Nom affiché"></div>`).join("")}
    <button class="b p" onclick="saveNets()">Enregistrer</button></div>`;
}
async function saveNets() {
  const d = {}; document.querySelectorAll(".purl").forEach(i => d[i.dataset.k] = {url: i.value.trim(), name: document.querySelector(`.pname[data-n="${i.dataset.k}"]`).value});
  try { await api("/api/profiles", {method: "PUT", body: JSON.stringify(d)}); await loadRefs(); toast("Réseaux enregistrés"); } catch (e) { toast(e.message); }
}

// ============================================================ démarrage
async function loadRefs() {
  [META, TPL, GUIDES, PROF] = await Promise.all([api("/api/meta"), api("/api/templates"), api("/api/guides"), api("/api/profiles")]);
  $("profLinks").innerHTML = Object.entries(PROF).filter(([, v]) => v.url).map(([k, v]) => `<a href="${esc(v.url)}" target="_blank" rel="noopener" class="chip"><i style="background:${NC(k)}"></i>${META.networks[k] ? NL(k) : esc(k)}</a>`).join("");
}
(async () => {
  await loadRefs(); await topBar();
  go("home");
  setInterval(async () => { await topBar(); if (["home", "cal"].includes(PAGE)) { PAGE === "home" ? pageHome() : pageCal(); } }, 60000);
})();
