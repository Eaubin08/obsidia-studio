"""Obsidia Studio — espace local de préparation des posts (multi-réseaux).

Rien n'est publié automatiquement : le studio prépare, Étienne copie / programme / valide.
Écoute uniquement sur 127.0.0.1.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import time
import uuid
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
POSTS = DATA / "posts"
IMAGES = DATA / "images"
BACKUPS = DATA / "backups"
LINKEDIN = Path.home() / ".claude" / "linkedin"
HUMAN = Path.home() / ".claude" / "skills" / "li-human"
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
for d in (POSTS, IMAGES, BACKUPS):
    d.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(ROOT))
import visuals  # noqa: E402
import studio_ai
from studio_quality import assess as assess_editorial
from editorial_cleanup import clean_editorial_draft  # noqa: E402

# days = jours préférés (0 = lundi) : hypothèses éditoriales, modifiables, à vérifier par l'audit
NETWORKS = {
    "linkedin": {"label": "LinkedIn", "limit": 3000, "color": "#4ea1ff", "days": [1, 3, 2, 4, 0], "time": "08:30",
                 "hint": "900-1 300 caractères, lien en 1er commentaire, 3 hashtags max"},
    "facebook": {"label": "Facebook", "limit": 63206, "color": "#8b7bff", "days": [2, 4, 6, 0], "time": "12:30",
                 "hint": "plus personnel, ton direct, une question à la fin"},
    "x": {"label": "X", "limit": 280, "color": "#d6dde8", "days": [1, 3, 0, 2, 4, 5, 6], "time": "09:00",
          "hint": "une seule idée, 280 caractères, ou un fil numéroté"},
    "instagram": {"label": "Instagram", "limit": 2200, "color": "#ff6fb1", "days": [2, 4, 0, 6, 5], "time": "18:30",
                  "hint": "l'image porte le message, légende courte, hashtags en bas"},
    "youtube": {"label": "YouTube (communauté / description)", "limit": 5000, "color": "#ff5a5a", "days": [5, 2, 0], "time": "11:00",
                "hint": "annonce de vidéo ou post communauté"},
}
STATUSES = ["idée", "brouillon", "validé", "programmé", "publié"]

app = FastAPI(title="Obsidia Studio")


# ---------------------------------------------------------------- stockage
def _path(pid: str) -> Path:
    if not re.fullmatch(r"[\w-]{1,64}", pid):
        raise HTTPException(400, "identifiant invalide")
    return POSTS / f"{pid}.json"


def load(pid: str) -> dict:
    p = _path(pid)
    if not p.exists():
        raise HTTPException(404, "post introuvable")
    return json.loads(p.read_text(encoding="utf-8"))


def save(post: dict) -> dict:
    post["updated"] = datetime.now().isoformat(timespec="seconds")
    try:  # la vérification est recalculée à chaque enregistrement (pas seulement par le pilote)
        c = checklist(post)
        post["check_flag"] = "" if c["ok"] else " / ".join(i["msg"] for i in c["items"] if i["level"] == "bloquant")
    except NameError:  # au démarrage, avant la définition de checklist
        pass
    _path(post["id"]).write_text(json.dumps(post, ensure_ascii=False, indent=2), encoding="utf-8")
    return post


def seed():
    """Importe la semaine 1 validée depuis ~/.claude/linkedin si le studio est vide."""
    if any(POSTS.iterdir()):
        return
    for day, hook in (("mardi", "#1 Contrarian"), ("jeudi", "#18 Unpopular Rule")):
        txt = LINKEDIN / "drafts" / f"2026-S1-{day}.txt"
        img = LINKEDIN / "images" / f"2026-S1-{day}.png"
        if not txt.exists():
            continue
        name = f"2026-S1-{day}.png"
        if img.exists():
            shutil.copy(img, IMAGES / name)
        save({
            "id": f"s1-{day}", "network": "linkedin", "series": "Journal d'éducation d'Obsidia",
            "week": 1, "day": day, "status": "validé", "hook": hook,
            "text": txt.read_text(encoding="utf-8"), "image": name if img.exists() else "",
            "planned": "", "published": "", "notes": "Validé le 2026-10-15.",
            "created": "2026-10-15T09:00:00",
        })


seed()


# ---------------------------------------------------------------- modèles
class PostIn(BaseModel):
    network: str = "linkedin"
    series: str = "Journal d'éducation d'Obsidia"
    week: int = 0
    day: str = ""
    status: str = "idée"
    hook: str = ""
    text: str = ""
    image: str = ""
    planned: str = ""
    published: str = ""
    notes: str = ""
    campaign: str = ""
    image_idea: str = ""
    time: str = ""
    template: str = ""
    family: str = ""


class GenIn(BaseModel):
    idea: str
    network: str = "linkedin"
    source_text: str = ""
    template: str = ""


class ImageIn(BaseModel):
    line1: str
    line2: str = ""
    footer: str = ""
    motif: str = "constellation"
    format: str = "auto"


class DocIn(BaseModel):
    content: str


# ---------------------------------------------------------------- API posts
@app.get("/api/ai/status")
def ai_status():
    return {**studio_ai.status(), **studio_ai.probe()}


@app.get("/api/meta")
def meta():
    return {"networks": NETWORKS, "statuses": STATUSES, "motifs": list(visuals.MOTIFS)}


@app.get("/api/posts")
def list_posts():
    posts = [json.loads(p.read_text(encoding="utf-8")) for p in POSTS.glob("*.json")]
    return sorted(posts, key=lambda p: (p.get("week") or 999, p.get("planned") or "", p.get("created", "")))


@app.post("/api/posts")
def create_post(body: PostIn):
    post = body.model_dump()
    post["id"] = uuid.uuid4().hex[:10]
    post["created"] = datetime.now().isoformat(timespec="seconds")
    return save(post)


@app.put("/api/posts/{pid}")
def update_post(pid: str, body: PostIn, force: bool = False):
    post = load(pid)
    old_status = post.get("status")
    post.update(body.model_dump())
    # User-editable copy is not a model-verification receipt.
    post["editorial_quality"] = assess_editorial(post.get("text", ""), post.get("network", "linkedin"))
    if post["status"] in ("validé", "programmé") and old_status != post["status"] and not force:
        c = checklist(post)
        if not c["ok"]:
            raise HTTPException(409, "Vérification : " + " / ".join(i["msg"] for i in c["items"] if i["level"] == "bloquant"))
    if post["status"] == "publié" and old_status != "publié":
        post["published"] = post["published"] or datetime.now().strftime("%Y-%m-%d")
        if post["network"] == "linkedin":
            first = post["text"].strip().splitlines()[0] if post["text"].strip() else ""
            with open(LINKEDIN / "log.md", "a", encoding="utf-8") as fh:
                fh.write(f"- {post['published']} · PUBLIÉ · {post.get('hook','')} · « {first} »\n")
    return save(post)


@app.post("/api/posts/{pid}/archive")
def archive_post(pid: str):
    p = _path(pid)
    if not p.exists():
        raise HTTPException(404)
    shutil.move(str(p), BACKUPS / f"archived-{pid}-{int(time.time())}.json")
    return {"ok": True}


# ---------------------------------------------------------------- humanizer
@app.post("/api/humanize")
def humanize(body: DocIn):
    tmp = DATA / "tmp"
    tmp.mkdir(exist_ok=True)
    tag = uuid.uuid4().hex[:8]
    src, out = tmp / f"in-{tag}.txt", tmp / f"out-{tag}.txt"
    src.write_text(body.content, encoding="utf-8")
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    if not (HUMAN / "humanize.py").is_file() or not (HUMAN / "detect.py").is_file():
        src.unlink(missing_ok=True)
        return {"text": body.content, "report": "Humanizer externe absent : texte inchangé.", "score": {"status": "not_run"}}
    try:
        h = subprocess.run([sys.executable, "-I", str(HUMAN / "humanize.py"), str(src), "--lang", "fr",
                            "-o", str(out), "--report"], capture_output=True, text=True, encoding="utf-8", env=env, timeout=30)
        d = subprocess.run([sys.executable, "-I", str(HUMAN / "detect.py"), str(out), "--lang", "fr", "--json"],
                           capture_output=True, text=True, encoding="utf-8", env=env, timeout=30)
    except (OSError, subprocess.TimeoutExpired):
        src.unlink(missing_ok=True)
        out.unlink(missing_ok=True)
        return {"text": body.content, "report": "Humanizer indisponible : texte inchangé.", "score": {"status": "not_run"}}
    try:
        score = json.loads(d.stdout)
    except json.JSONDecodeError:
        score = {"error": d.stderr[-500:]}
    text = out.read_text(encoding="utf-8") if out.exists() else body.content
    src.unlink(missing_ok=True)
    out.unlink(missing_ok=True)
    return {"text": text, "report": h.stderr, "score": score}


# ---------------------------------------------------------------- génération (Brody / Obsidia)
@app.post("/api/generate")
def generate(body: GenIn):
    net = NETWORKS.get(body.network)
    if not net:
        raise HTTPException(400, "réseau inconnu")
    tpl = next((t for t in templates() if t["id"] == body.template), None)
    if body.network == "linkedin" and not body.source_text and not tpl:
        prompt = (f"Écris une publication LinkedIn en français sur : {body.idea}. "
                  "Respecte la voix fournie dans le contexte et n’invente aucun fait.")
    else:
        prompt = (f"Respecte le contexte éditorial injecté et les preuves publiques. "
                  f"Écris un post pour {net['label']} ({net['hint']}, limite {net['limit']} caractères). "
                  f"Idée : {body.idea}\n")
        if body.source_text:
            prompt += f"\nAdapte ce texte existant (même sens, ne rien inventer) :\n---\n{body.source_text}\n---\n"
        if tpl:
            prompt += (f"\nSuis le modèle « {tpl['name']} » ({tpl['when']}). Structure à respecter, "
                       f"en remplaçant chaque {{{{…}}}} par du contenu réel ou en le laissant si le fait manque :\n"
                       f"{tpl['structure']}\n")
    prompt += ("\n\nMode studio : ne pose aucune question, n'écris dans aucun fichier, ne publie rien. "
               "N'invente aucun chiffre, résultat ni anecdote : utilise {{placeholder}} si un fait manque. "
               "Réponds avec 3 accroches numérotées, puis le texte final entre les balises <POST> et </POST>, "
               "puis la liste des affirmations avec leur statut de preuve.")
    # An explicitly chosen, independent Brody-native editorial mode exists
    # for Studio. It is NOT a fallback from a denied Cognitive Ingress call.
    # The original governed ingress remains fail-closed and unchanged.
    editorial_mode = os.getenv("OBSIDIA_STUDIO_EDITORIAL_MODE", "governed_ingress")
    if editorial_mode == "studio_llamacpp":
        # Explicit local Studio mode: never a fallback after a governed HOLD.
        from studio_llamacpp import generate_llamacpp, EditorialEngineError
        try:
            draft = generate_llamacpp(
                body.idea, network=net["label"], source_text=body.source_text
            )
        except EditorialEngineError as exc:
            raise HTTPException(503, str(exc)) from exc
        cleaned = clean_editorial_draft(draft["text"])
        if not cleaned.strip():
            raise HTTPException(502, "Brouillon llama.cpp vide apres nettoyage.")
        quality = assess_editorial(cleaned, body.network)
        return {"raw": "", "text": cleaned, "quality": quality,
                "provenance": draft["provenance"], "warning": draft["warning"] + (" Vérification éditoriale : " + "; ".join(quality["issues"]) if quality["issues"] else "")}
    if editorial_mode == "studio_local_model":
        # Explicit Studio-owned editorial model route, not an automatic
        # fallback after a governed HOLD. No external repository is altered.
        from studio_editorial_engine import generate_editorial, EditorialEngineError
        try:
            draft = generate_editorial(
                body.idea, network=net["label"], source_text=body.source_text
            )
        except EditorialEngineError as exc:
            raise HTTPException(503, str(exc)) from exc
        cleaned = clean_editorial_draft(draft["text"])
        if not cleaned.strip():
            raise HTTPException(502, "Brouillon local vide apres nettoyage.")
        return {"raw": "", "text": cleaned,
                "provenance": draft["provenance"], "warning": draft["warning"]}
    if editorial_mode == "studio_template":
        from studio_editorial_contract import build_readonly_draft
        draft = build_readonly_draft(body.idea, body.source_text, net["label"])
        return {"raw": "", "text": draft["text"], "provenance": draft["provenance"], "warning": draft["warning"]}
    if editorial_mode not in ("governed_ingress", "brody_native"):
        raise HTTPException(503, "Mode éditorial Studio inconnu.")
    use_ingress = editorial_mode == "governed_ingress" and os.getenv("OBSIDIA_STUDIO_USE_INGRESS") == "1"
    if editorial_mode == "brody_native" and os.getenv("OBSIDIA_STUDIO_ALLOW_BRODY_NATIVE") != "1":
        raise HTTPException(503, "Mode Brody natif désactivé : activation explicite requise.")
    try:
        # The AMD router evaluates the *whole* request for execution intent.
        # Legacy local docs can contain historical "commit"/"push" commands;
        # they are not user instructions and must not be mixed into the
        # pre-inference routing request. Only the explicit editorial task goes
        # to the governed ingress. The old Brody path is unchanged.
        if use_ingress:
            # Keep this pre-inference request aligned with the previously
            # observed ALLOW → LOCAL_MODEL_GATE route. Generic formatting
            # instructions (notably "statut de preuve") can be classified
            # by AMD as a local status query, bypassing inference entirely.
            # Never fabricate proof claims or turn HOLD into ALLOW.
            subject = body.idea.strip()
            if not subject:
                raise HTTPException(400, "idée requise")
            from editorial_intent import explanatory_editorial_request
            routed_prompt = explanatory_editorial_request(
                subject, network=net["label"], source_text=body.source_text
            )
        else:
            routed_prompt = _studio_context() + prompt
        if use_ingress:
            out, provenance = studio_ai.generate(routed_prompt, return_receipt=True)
        else:
            out = studio_ai.generate(routed_prompt, use_ingress=False)
            provenance = {"source": "BRODY_DIRECT_UNVERIFIED", "human_approval_required": True,
                          "publication_permitted": False, "brody_post_model_synthesis_proven": False}
    except studio_ai.InferenceError as exc:
        # Never retry a blocked cognitive request through another model.
        # When actual source text was supplied by the user, Studio can still
        # offer that exact text as an explicitly non-generated review draft.
        detail = str(exc)
        if "brody_status=GOVERNANCE_BOUNDARY" in detail:
            if body.source_text.strip():
                return {
                    "raw": "",
                    "text": clean_editorial_draft(body.source_text),
                    "provenance": {
                        "source": "USER_SOURCE_TEXT_ONLY",
                        "brody_post_model_synthesis_proven": False,
                        "human_approval_required": True,
                        "publication_permitted": False,
                        "cognitive_gate": "GOVERNANCE_BOUNDARY",
                    },
                    "warning": "Génération IA bloquée par gouvernance. Texte original uniquement : aucune reformulation IA.",
                }
            raise HTTPException(409, "Génération IA retenue par la gouvernance cognitive. Aucun brouillon inventé. Ajoutez un texte source pour conserver uniquement votre texte, ou corrigez la classification d'autorité en amont.") from exc
        raise HTTPException(503, detail) from exc
    m = re.search(r"<POST>\s*(.*?)\s*</POST>", out, re.S)
    if not m or not m.group(1).strip():
        raise HTTPException(502, "Brody joignable mais aucune publication <POST> reçue. Réponse consultative non exploitable, aucun brouillon généré.")
    clean_text = clean_editorial_draft(m.group(1))
    if not clean_text:
        raise HTTPException(502, "La réponse éditoriale nettoyée est vide : brouillon refusé.")
    return {"raw": out, "text": clean_text, "provenance": provenance}


# ---------------------------------------------------------------- images
@app.post("/api/posts/{pid}/image")
def make_image(pid: str, body: ImageIn):
    post = load(pid)
    if body.motif not in visuals.MOTIFS:
        raise HTTPException(400, "motif inconnu")
    footer = body.footer or (f"{post['series'].upper()} · SEMAINE {post['week']}" if post.get("week") else (post.get("series") or "").upper())
    size = visuals.FORMATS.get(body.format) or visuals.SIZES.get(post["network"], (1080, 1350))
    post.update({"img_l1": body.line1, "img_l2": body.line2, "img_motif": body.motif})
    name = f"{pid}-{int(time.time())}.png"
    html = IMAGES / (name + ".html")
    html.write_text(visuals.render(body.motif, body.line1, body.line2, footer, size, seed=hash(pid) % 1000),
                    encoding="utf-8")
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                    "--force-device-scale-factor=1", f"--window-size={size[0]},{size[1]}",
                    f"--screenshot={IMAGES / name}", html.as_uri()], capture_output=True, timeout=60)
    html.unlink(missing_ok=True)
    if not (IMAGES / name).exists():
        raise HTTPException(500, "rendu Chrome échoué")
    post["image"] = name
    return save(post)


class VariantsIn(BaseModel):
    line1: str = ""
    line2: str = ""


VARIANT_MOTIFS = ["constellation", "frontiere", "cristal"]


def make_variants(pid, line1="", line2=""):
    """3 images au choix (motifs différents). La première devient l'image du post si aucune n'est choisie."""
    post = load(pid)
    hook = post.get("hook") or ""
    if re.match(r"\s*#\d", hook):  # « #1 Contrarian » = nom de formule, pas un texte d'image
        hook = ""
    l1 = (line1 or post.get("img_l1") or hook or post.get("text", "").split("\n")[0])[:60]
    l2 = (line2 or post.get("img_l2") or "")[:60]
    names = []
    for motif in VARIANT_MOTIFS:
        try:
            names.append(make_image(pid, ImageIn(line1=l1, line2=l2, motif=motif))["image"])
        except Exception:
            pass
    post = load(pid)
    post["variants"] = names
    if names and (not post.get("image_chosen")):
        post["image"] = names[0]
    post["img_l1"], post["img_l2"] = l1, l2
    return save(post)


@app.post("/api/posts/{pid}/variants")
def variants(pid: str, body: VariantsIn):
    return make_variants(pid, body.line1, body.line2)


class ChooseIn(BaseModel):
    image: str


@app.post("/api/posts/{pid}/choose")
def choose_image(pid: str, body: ChooseIn):
    post = load(pid)
    if not re.fullmatch(r"[\w.-]+\.png", body.image) or not (IMAGES / body.image).exists():
        raise HTTPException(400, "image inconnue")
    # Ne pas permettre d'associer l'image d'un autre post à ce post.
    allowed = set(post.get("variants") or [])
    if post.get("image"):
        allowed.add(post["image"])
    if body.image not in allowed:
        raise HTTPException(400, "image non associée à ce post")
    post["image"], post["image_chosen"] = body.image, True
    return save(post)


@app.get("/images/{name}")
def image(name: str):
    p = IMAGES / name
    if not re.fullmatch(r"[\w.-]+\.png", name) or not p.exists():
        raise HTTPException(404)
    return FileResponse(p)


# ---------------------------------------------------------------- storytelling
DOCS = {"voice": LINKEDIN / "voice.md", "plan": LINKEDIN / "plan.md", "story": DATA / "storytelling.md",
        "templates": DATA / "templates.json"}


@app.get("/api/docs/{key}")
def get_doc(key: str):
    p = DOCS.get(key)
    if not p:
        raise HTTPException(404)
    return {"content": p.read_text(encoding="utf-8") if p.exists() else ""}


@app.put("/api/docs/{key}")
def put_doc(key: str, body: DocIn):
    p = DOCS.get(key)
    if not p:
        raise HTTPException(404)
    if p.suffix == ".json":
        try:
            v = json.loads(body.content)
            assert isinstance(v, list) if key == "templates" else isinstance(v, dict)
        except Exception:
            raise HTTPException(400, f"{p.name} invalide : rien n'a été enregistré")
    if p.exists():
        shutil.copy(p, BACKUPS / f"{key}-{datetime.now():%Y%m%d-%H%M%S}.md")
    p.write_text(body.content, encoding="utf-8")
    return {"ok": True}


# ---------------------------------------------------------------- modèles et profils
def templates():
    p = DATA / "templates.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else []


@app.get("/api/templates")
def get_templates():
    return templates()


@app.get("/api/profiles")
def get_profiles():
    p = DATA / "profiles.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


@app.put("/api/profiles")
def put_profiles(body: dict):
    p = DATA / "profiles.json"
    for k, v in body.items():
        url = (v or {}).get("url", "")
        if url and not re.match(r"^https://", url):
            raise HTTPException(400, f"URL invalide pour {k}")
    if p.exists():
        shutil.copy(p, BACKUPS / f"profiles-{datetime.now():%Y%m%d-%H%M%S}.json")
    p.write_text(json.dumps(body, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"ok": True}


# ---------------------------------------------------------------- Claude Code (helper)
VOICE_RULES = (
    "Lis C:/Users/User/.claude/linkedin/voice.md et C:/Users/User/obsidia-studio/data/storytelling.md, "
    "et respecte-les strictement (voix, règle de preuve, sujets interdits). "
    "Lis aussi C:/Users/User/obsidia-studio/data/journal.md (faits réels récents notés par Étienne) et "
    "C:/Users/User/obsidia-studio/data/proofs.json (banque de preuves) : un fait n'est utilisable que s'il y figure, "
    "avec son statut exact (VISION, RÉALISÉ-DOC, TESTÉ, PROUVÉ, ACTUEL) et seulement si public=true. "
    "Respecte les règles du réseau visé dans C:/Users/User/obsidia-studio/data/guides.json. "
    "N'invente aucun chiffre, résultat, client ni anecdote : utilise {{placeholder}} si un fait manque. "
    "Oxygen est une vision, jamais présenté comme né. Aucun lien vers les dépôts, pas de maths du Millénaire. "
    "Mode studio : ne pose aucune question, n'écris dans aucun fichier, ne publie rien.\n\n")


def _studio_context():
    """Inject local docs into the model prompt, never give the model disk access."""
    parts = []
    for label, path in (("voice", DOCS["voice"]), ("story", DOCS["story"]),
                        ("journal", DATA / "journal.md"), ("guides", DATA / "guides.json"),
                        ("public_proofs", DATA / "proofs.json")):
        if not path.exists():
            continue
        try:
            content = path.read_text(encoding="utf-8")
            if label == "public_proofs":
                data = json.loads(content)
                if isinstance(data, list):
                    content = json.dumps([p for p in data if isinstance(p, dict) and p.get("public") is True], ensure_ascii=False)
                elif isinstance(data, dict):
                    content = json.dumps([p for p in data.get("items", []) if isinstance(p, dict) and p.get("public") is True], ensure_ascii=False)
                else:
                    content = "[]"
            parts.append(f"<context label={label!r}>\n{content[:12000]}\n</context>")
        except (OSError, ValueError):
            continue
    return "\n".join(parts) + "\n\n"


def claude(prompt: str, timeout: int = 600) -> str:
    """Legacy function name retained for existing call sites; routes to local stack."""
    try:
        return studio_ai.generate(_studio_context() + prompt, timeout=timeout)
    except studio_ai.InferenceError as exc:
        raise HTTPException(503, str(exc)) from exc


def claude_json(prompt: str, timeout: int = 600):
    out = claude(prompt + "\n\nRéponds UNIQUEMENT avec du JSON valide entre <JSON> et </JSON>.", timeout)
    m = re.search(r"<JSON>\s*(.*?)\s*</JSON>", out, re.S)
    try:
        return json.loads(m.group(1)) if m else None, out
    except json.JSONDecodeError:
        return None, out


def all_posts():
    return [json.loads(p.read_text(encoding="utf-8")) for p in POSTS.glob("*.json")]


# ---------------------------------------------------------------- campagnes
from datetime import date, timedelta  # noqa: E402
import threading  # noqa: E402

CAMPAIGNS = DATA / "campaigns"
CAMPAIGNS.mkdir(exist_ok=True)
JOBS: dict = {}


class CampaignIn(BaseModel):
    name: str
    goal: str = ""
    theme: str = ""
    start: str  # AAAA-MM-JJ
    weeks: int = 4
    cadence: dict = {"linkedin": 2}  # posts par semaine et par réseau


def _camp_path(cid):
    if not re.fullmatch(r"[\w-]{1,64}", cid):
        raise HTTPException(400, "identifiant invalide")
    return CAMPAIGNS / f"{cid}.json"


def load_camp(cid):
    p = _camp_path(cid)
    if not p.exists():
        raise HTTPException(404, "campagne introuvable")
    return json.loads(p.read_text(encoding="utf-8"))


def save_camp(c):
    _camp_path(c["id"]).write_text(json.dumps(c, ensure_ascii=False, indent=2), encoding="utf-8")
    return c


def slots(c):
    """Dates de publication : n posts/semaine par réseau, sur ses jours préférés."""
    start = date.fromisoformat(c["start"])
    monday = start - timedelta(days=start.weekday())
    out = []
    for w in range(c["weeks"]):
        for net, n in c["cadence"].items():
            if net not in NETWORKS or not n:
                continue
            for wd in sorted(NETWORKS[net]["days"][:min(int(n), 7)]):
                d = monday + timedelta(weeks=w, days=wd)
                if d >= start:
                    out.append({"date": d.isoformat(), "network": net, "week": w + 1,
                                "time": NETWORKS[net]["time"]})
    return sorted(out, key=lambda s: (s["date"], s["network"]))


@app.get("/api/campaigns")
def list_campaigns():
    cs = [json.loads(p.read_text(encoding="utf-8")) for p in CAMPAIGNS.glob("*.json")]
    posts = all_posts()
    for c in cs:
        mine = [p for p in posts if p.get("campaign") == c["id"]]
        c["counts"] = {s: sum(p["status"] == s for p in mine) for s in STATUSES}
        c["job"] = JOBS.get(c["id"])
    return sorted(cs, key=lambda c: c["start"], reverse=True)


@app.post("/api/campaigns")
def create_campaign(body: CampaignIn):
    c = body.model_dump()
    date.fromisoformat(c["start"])
    c["id"] = uuid.uuid4().hex[:8]
    c["created"] = datetime.now().isoformat(timespec="seconds")
    c["slots"] = len(slots(c))
    return save_camp(c)


@app.post("/api/campaigns/{cid}/plan")
def plan_campaign(cid: str):
    """Claude propose un angle par créneau ; le studio crée les posts au statut « idée »."""
    c = load_camp(cid)
    s = slots(c)
    existing = [p for p in all_posts() if p.get("campaign") == cid]
    if existing:
        raise HTTPException(409, f"cette campagne a déjà {len(existing)} posts planifiés")
    recent = [p["text"].split("\n")[0] for p in all_posts() if p["text"].strip()][:20]
    prompt = VOICE_RULES + (
        f"Campagne « {c['name']} ». Objectif : {c['goal'] or 'faire connaître le projet'}. Thème : {c['theme']}.\n"
        f"Voici {len(s)} créneaux (date, réseau, semaine) : {json.dumps(s, ensure_ascii=False)}\n"
        f"Déjà publié ou prévu (ne pas répéter) : {json.dumps(recent, ensure_ascii=False)}\n"
        "Construis un fil conducteur sur toute la campagne : une progression semaine par semaine, "
        "et adapte chaque angle au réseau. Pour un même jour sur plusieurs réseaux, garde la même idée déclinée. "
        "Pour CHAQUE créneau, dans le même ordre, donne : angle (une phrase), hook (première ligne proposée), "
        "image (idée d'image en une phrase), image_l1 et image_l2 (deux lignes courtes à écrire sur l'image), "
        "preuve (le fait réel dont le post a besoin, ou 'aucun'). "
        "Format : {\"arc\": \"le fil conducteur en 2 phrases\", \"items\": [{...}, ...]}")
    data, raw = claude_json(prompt, timeout=900)
    if not data or len(data.get("items", [])) != len(s):
        raise HTTPException(502, "réponse de Claude inexploitable :\n" + raw[-1500:])
    c["arc"] = data.get("arc", "")
    save_camp(c)
    created = 0
    for slot, it in zip(s, data["items"]):
        save({"id": uuid.uuid4().hex[:10], "network": slot["network"], "series": c["name"], "week": slot["week"],
              "day": ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"][date.fromisoformat(slot["date"]).weekday()],
              "status": "idée", "hook": it.get("hook", ""), "text": "", "image": "", "planned": slot["date"],
              "time": slot["time"],
              "published": "", "campaign": cid, "image_idea": it.get("image", ""),
              "img_l1": it.get("image_l1", ""), "img_l2": it.get("image_l2", ""),
              "notes": f"Angle : {it.get('angle','')} · Preuve nécessaire : {it.get('preuve','aucun')}",
              "created": datetime.now().isoformat(timespec="seconds")})
        created += 1
    return {"arc": c["arc"], "created": created}


def _draft_one(p, c):
    net = NETWORKS[p["network"]]
    prompt = VOICE_RULES + (
        f"Écris un post {net['label']} ({net['hint']}, limite {net['limit']} caractères) pour la campagne "
        f"« {c['name']} » (fil conducteur : {c.get('arc','')}). Semaine {p['week']}.\n"
        f"{p['notes']}\nAccroche proposée : {p['hook']}\n"
        f"Termine par la ligne « {c['name']} · Semaine {p['week']} ».\n"
        "Réponds avec le texte final entre <POST> et </POST>, puis la liste des affirmations avec leur statut de preuve.")
    out = claude(prompt)
    m = re.search(r"<POST>\s*(.*?)\s*</POST>", out, re.S)
    return m.group(1).strip() if m else ""


def _job(cid):
    c = load_camp(cid)
    todo = [p for p in all_posts() if p.get("campaign") == cid and p["status"] == "idée"]
    todo.sort(key=lambda p: p["planned"])
    JOBS[cid] = {"total": len(todo), "done": 0, "errors": 0, "running": True}
    for p in todo:
        try:
            text = _draft_one(p, c)
            if text:
                text = humanize(DocIn(content=text))["text"].strip()
                p["text"], p["status"] = text, "brouillon"
                save(p)
                try:
                    make_variants(p["id"], p.get("img_l1", ""), p.get("img_l2", ""))
                except Exception:
                    pass
            else:
                JOBS[cid]["errors"] += 1
        except Exception:
            JOBS[cid]["errors"] += 1
        JOBS[cid]["done"] += 1
    JOBS[cid]["running"] = False


@app.post("/api/campaigns/{cid}/draft")
def draft_campaign(cid: str):
    """Rédige en arrière-plan tous les posts « idée » de la campagne (texte + image). Rien n'est publié."""
    load_camp(cid)
    if JOBS.get(cid, {}).get("running"):
        raise HTTPException(409, "rédaction déjà en cours")
    threading.Thread(target=_job, args=(cid,), daemon=True).start()
    return {"started": True}


# ---------------------------------------------------------------- suggestions
@app.post("/api/suggest")
def suggest(body: DocIn):
    recent = [{"date": p.get("planned") or p.get("published"), "réseau": p["network"], "début": p["text"][:120]}
              for p in all_posts() if p["text"].strip()]
    prompt = VOICE_RULES + (
        f"Posts existants : {json.dumps(recent, ensure_ascii=False)}\n"
        f"Demande d'Étienne (peut être vide) : {body.content}\n"
        "Propose 6 idées de posts nouvelles, variées (réseaux et formats différents), qui font avancer l'histoire "
        "sans répéter l'existant. Pour chacune : network (linkedin/facebook/x/instagram/youtube), angle, hook, "
        "pourquoi (une phrase : pourquoi ça peut faire réagir), preuve (fait réel nécessaire ou 'aucun'). "
        "Format : {\"items\": [...]}")
    data, raw = claude_json(prompt)
    if not data:
        raise HTTPException(502, "réponse de Claude inexploitable :\n" + raw[-1500:])
    return data


# ================================================================ AUTOMATISATION
# Tout est automatisé SAUF la publication : le studio n'envoie jamais rien sur un réseau.
import difflib  # noqa: E402

JOURNAL = DATA / "journal.md"
PROOFS = DATA / "proofs.json"
SCHEDULE = DATA / "schedule.json"
AUTOPILOT = DATA / "autopilot.json"
FILES = DATA / "files"
FILES.mkdir(exist_ok=True)
EVENTS: list = []  # activité récente du pilote automatique


def log_event(msg):
    EVENTS.insert(0, {"at": datetime.now().strftime("%d/%m %H:%M"), "msg": msg})
    del EVENTS[60:]


def _read_json(p, default):
    try:
        return json.loads(p.read_text(encoding="utf-8")) if p.exists() else default
    except json.JSONDecodeError:
        return default


def _write_json(p, data):
    if p.exists():
        shutil.copy(p, BACKUPS / f"{p.stem}-{datetime.now():%Y%m%d-%H%M%S}{p.suffix}")
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def apply_schedule():
    for net, s in _read_json(SCHEDULE, {}).items():
        if net in NETWORKS:
            NETWORKS[net]["days"] = s.get("days", NETWORKS[net]["days"])
            NETWORKS[net]["time"] = s.get("time", NETWORKS[net]["time"])


apply_schedule()


# ---------------------------------------------------------------- journal de bord
class JournalIn(BaseModel):
    text: str
    date: str = ""


@app.get("/api/journal")
def get_journal():
    return {"content": JOURNAL.read_text(encoding="utf-8") if JOURNAL.exists() else ""}


@app.post("/api/journal")
def add_journal(body: JournalIn):
    if not body.text.strip():
        raise HTTPException(400, "entrée vide")
    d = body.date or date.today().isoformat()
    if not JOURNAL.exists():
        JOURNAL.write_text("# Journal de bord Obsidia\n\nFaits réels notés par Étienne. Source prioritaire des posts.\n\n",
                           encoding="utf-8")
    with open(JOURNAL, "a", encoding="utf-8") as fh:
        fh.write(f"- {d} · {body.text.strip()}\n")
    return get_journal()


# ---------------------------------------------------------------- banque de preuves
PROOF_STATUSES = ["VISION", "RÉALISÉ-DOC", "TESTÉ", "PROUVÉ", "ACTUEL"]


class ProofIn(BaseModel):
    claim: str
    status: str = "VISION"
    source: str = ""
    date: str = ""
    scope: str = ""
    public: bool = False


@app.get("/api/proofs")
def get_proofs():
    return {"statuses": PROOF_STATUSES, "items": _read_json(PROOFS, [])}


@app.post("/api/proofs")
def add_proof(body: ProofIn):
    if body.status not in PROOF_STATUSES:
        raise HTTPException(400, "statut inconnu")
    items = _read_json(PROOFS, [])
    items.append({**body.model_dump(), "id": uuid.uuid4().hex[:8]})
    _write_json(PROOFS, items)
    return get_proofs()


@app.put("/api/proofs/{prid}")
def edit_proof(prid: str, body: ProofIn):
    items = _read_json(PROOFS, [])
    for it in items:
        if it["id"] == prid:
            it.update(body.model_dump())
    _write_json(PROOFS, items)
    return get_proofs()


@app.delete("/api/proofs/{prid}")
def del_proof(prid: str):
    _write_json(PROOFS, [it for it in _read_json(PROOFS, []) if it["id"] != prid])
    return get_proofs()


# ---------------------------------------------------------------- vérification avant validation
FORBIDDEN = [(r"mill[ée]naire|riemann|navier|hodge|yang.?mills|p\s*≠\s*np|\bBSD\b", "sujet maths du Millénaire (hors limites)"),
             (r"[A-Za-z]:\\|github\.com/Eaubin08|\.claude[/\\]|worktree", "chemin de fichier / dépôt / interne"),
             (r"\bOxygen\b[^.]{0,40}\b(est n[ée]|a appris|est actif|fonctionne)", "Oxygen présenté comme déjà né / actif"),
             (r"(?i)\bindétectable|undetectable", "promesse d'indétectabilité")]


def checklist(post):
    out = []
    if post.get("status") == "idée":  # pas encore rédigé : rien à vérifier
        return {"ok": True, "items": []}
    txt = post.get("text", "")
    net = NETWORKS.get(post.get("network"), {})

    def add(level, msg):
        out.append({"level": level, "msg": msg})

    if not txt.strip():
        add("bloquant", "Texte vide")
    if "{{" in txt:
        add("bloquant", f"{txt.count('{{')} élément(s) {{{{…}}}} à remplir (fait manquant)")
    if net and len(txt) > net["limit"]:
        add("bloquant", f"Trop long : {len(txt)} / {net['limit']} caractères")
    if post.get("network") == "x" and txt and not re.match(r"^\s*1/", txt) and len(txt) > 280:
        add("bloquant", "X : plus de 280 caractères sans fil numéroté")
    for rx, label in FORBIDDEN:
        if re.search(rx, txt, re.I):
            add("bloquant", f"Contenu hors limites : {label}")
    if not post.get("image"):
        add("bloquant" if post.get("network") == "instagram" else "conseil",
            "Pas d'image" + (" (obligatoire sur Instagram)" if post.get("network") == "instagram" else ""))
    if post.get("network") == "linkedin":
        if len(re.findall(r"#\w+", txt)) > 3:
            add("conseil", "Plus de 3 hashtags")
        if re.search(r"https?://", txt):
            add("conseil", "Lien dans le texte : le mettre plutôt en premier commentaire")
        if txt and len(txt) < 400:
            add("conseil", "Moins de 400 caractères : se lit comme une pensée, pas un post")
    if not post.get("planned"):
        add("conseil", "Pas de date prévue")
    first = txt.strip()[:200].lower()
    for o in all_posts():
        if o["id"] != post["id"] and o.get("text") and o.get("network") == post.get("network"):
            if first and difflib.SequenceMatcher(None, first, o["text"].strip()[:200].lower()).ratio() > .8:
                add("conseil", f"Très proche d'un autre post ({o.get('planned') or o['id']})")
                break
    if re.search(r"\b(\d[\d\s.,]*%|\d{2,})", txt):
        add("conseil", "Contient des chiffres : vérifie qu'ils sont dans la banque de preuves")
    return {"ok": not any(c["level"] == "bloquant" for c in out), "items": out}


@app.get("/api/posts/{pid}/check")
def check_post(pid: str):
    return checklist(load(pid))


# ---------------------------------------------------------------- déclinaison multi-réseaux
class DeclineIn(BaseModel):
    networks: list


def _adapt(src, net_key):
    net = NETWORKS[net_key]
    prompt = VOICE_RULES + (
        f"Adapte ce post pour {net['label']} ({net['hint']}, limite {net['limit']} caractères). "
        "Même idée, même sens, rien d'inventé, format natif du réseau. Garde la dernière ligne de série si présente.\n"
        f"---\n{src['text']}\n---\n"
        "Réponds avec le texte final entre <POST> et </POST>.")
    m = re.search(r"<POST>\s*(.*?)\s*</POST>", claude(prompt), re.S)
    return m.group(1).strip() if m else ""


def decline_post(pid, networks):
    src = load(pid)
    fam = src.get("family") or src["id"]
    if not src.get("family"):
        src["family"] = fam
        save(src)
    existing = {p["network"] for p in all_posts() if p.get("family") == fam}
    made = 0
    for net in networks:
        if net not in NETWORKS or net in existing:
            continue
        text = _adapt(src, net)
        if not text:
            log_event(f"Déclinaison {net} échouée pour « {src['text'][:40]} »")
            continue
        text = humanize(DocIn(content=text))["text"].strip()
        p = save({**{k: src.get(k, "") for k in ("series", "week", "day", "planned", "campaign", "template", "hook")},
                  "id": uuid.uuid4().hex[:10], "network": net, "status": "brouillon", "text": text, "image": "",
                  "time": NETWORKS[net]["time"], "family": fam, "published": "",
                  "notes": f"Décliné automatiquement depuis le post {src['network']} {src['id']}",
                  "created": datetime.now().isoformat(timespec="seconds")})
        try:
            make_variants(p["id"], src.get("img_l1", ""), src.get("img_l2", ""))
        except Exception:
            pass
        made += 1
        log_event(f"Version {NETWORKS[net]['label']} créée pour « {src['text'][:40]}… »")
    return made


@app.post("/api/posts/{pid}/decline")
def decline(pid: str, body: DeclineIn):
    load(pid)
    threading.Thread(target=decline_post, args=(pid, body.networks), daemon=True).start()
    return {"started": True}


# ---------------------------------------------------------------- carrousel PDF
def parse_slides(text):
    slides = []
    for line in text.splitlines():
        m = re.match(r"\s*Slide\s*\d+[^:]*:\s*(.+)", line, re.I)
        if m:
            t, _, b = m.group(1).partition(" — ")
            if not b:
                t, _, b = m.group(1).partition(". ")
            slides.append((t.strip(), b.strip()))
    if not slides:
        blocks = [b.strip() for b in text.split("\n\n") if b.strip()]
        slides = [(b.split("\n")[0], " ".join(b.split("\n")[1:])) for b in blocks]
    return slides[:12]


@app.post("/api/posts/{pid}/carousel")
def make_carousel(pid: str):
    post = load(pid)
    slides = parse_slides(post["text"])
    if len(slides) < 3:
        raise HTTPException(400, "Il faut au moins 3 slides (lignes « Slide 1 : … » ou paragraphes)")
    handle = get_profiles().get(post["network"], {}).get("name", "Obsidia")
    html = FILES / f"{pid}.html"
    html.write_text(visuals.carousel(slides, handle), encoding="utf-8")
    pdf = FILES / f"{pid}-carrousel.pdf"
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={pdf}", html.as_uri()], capture_output=True, timeout=90)
    html.unlink(missing_ok=True)
    if not pdf.exists():
        raise HTTPException(500, "génération PDF échouée")
    post["carousel"] = pdf.name
    save(post)
    return {"file": pdf.name, "slides": len(slides)}


@app.get("/files/{name}")
def get_file(name: str):
    p = FILES / name
    if not re.fullmatch(r"[\w.-]+\.pdf", name) or not p.exists():
        raise HTTPException(404)
    return FileResponse(p)


# ---------------------------------------------------------------- aujourd'hui
@app.get("/api/today")
def today():
    t, tm = date.today().isoformat(), (date.today() + timedelta(days=1)).isoformat()
    ps = [p for p in all_posts() if p["status"] in ("validé", "programmé") and p.get("planned")]
    return {"today": [p for p in ps if p["planned"] == t],
            "tomorrow": [p for p in ps if p["planned"] == tm],
            "late": [p for p in ps if p["planned"] < t and p["status"] in ("validé", "programmé")],
            "events": EVENTS[:15]}


# ---------------------------------------------------------------- bilan
class MetricsIn(BaseModel):
    impressions: int = 0
    reactions: int = 0
    comments: int = 0
    shares: int = 0
    saves: int = 0
    clicks: int = 0
    followers: int = 0


@app.put("/api/posts/{pid}/metrics")
def set_metrics(pid: str, body: MetricsIn):
    post = load(pid)
    post["metrics"] = {**body.model_dump(), "at": date.today().isoformat()}
    return save(post)


def _er(m):
    return (m["reactions"] + m["comments"] + m["shares"] + m.get("saves", 0)) / m["impressions"] if m.get("impressions") else None


@app.get("/api/stats")
def stats():
    rows = []
    for p in all_posts():
        m = p.get("metrics")
        if not m or not m.get("impressions") or not (p.get("published") or p.get("planned")):
            continue
        d = date.fromisoformat((p.get("published") or p["planned"])[:10])
        rows.append({"network": p["network"], "er": _er(m), "comment_ratio": m["comments"] / max(m["reactions"], 1),
                     "reach": m["impressions"] / m["followers"] if m.get("followers") else None,
                     "weekday": d.weekday(), "hour": (p.get("time") or "")[:2], "template": p.get("template") or "libre",
                     "first": p["text"].strip().split("\n")[0][:80], "impressions": m["impressions"]})

    def group(key):
        g = {}
        for r in rows:
            g.setdefault((r["network"], r[key]), []).append(r["er"])
        return [{"network": k[0], key: k[1], "n": len(v), "er": round(100 * sum(v) / len(v), 2)} for k, v in g.items()]

    return {"n": len(rows), "posts": sorted(rows, key=lambda r: -r["er"]),
            "by_weekday": group("weekday"), "by_hour": group("hour"), "by_template": group("template"),
            "min_for_adjust": 8}


@app.post("/api/stats/adjust")
def adjust_schedule():
    """Ajuste jours/heures d'un réseau quand il a au moins 8 posts mesurés."""
    st = stats()
    sched, changes = _read_json(SCHEDULE, {}), []
    for net in NETWORKS:
        days = sorted([g for g in st["by_weekday"] if g["network"] == net], key=lambda g: -g["er"])
        n = sum(g["n"] for g in days)
        if n < st["min_for_adjust"]:
            changes.append(f"{NETWORKS[net]['label']} : {n} post(s) mesuré(s), il en faut {st['min_for_adjust']} — inchangé")
            continue
        best = [g["weekday"] for g in days] + [d for d in NETWORKS[net]["days"] if d not in [g["weekday"] for g in days]]
        hours = sorted([g for g in st["by_hour"] if g["network"] == net and g["hour"]], key=lambda g: -g["er"])
        new = {"days": best, "time": (hours[0]["hour"] + ":" + NETWORKS[net]["time"][3:]) if hours else NETWORKS[net]["time"]}
        sched[net] = new
        changes.append(f"{NETWORKS[net]['label']} : jours {new['days'][:3]} à {new['time']} (sur {n} posts)")
    _write_json(SCHEDULE, sched)
    apply_schedule()
    return {"changes": changes}


# ---------------------------------------------------------------- pilote automatique
DEFAULT_AUTOPILOT = {"enabled": False, "auto_draft": True, "draft_horizon_days": 10,
                     "auto_decline": True, "decline_to": ["facebook", "instagram"],
                     "auto_refill": True, "min_planned_14d": 6, "refill_networks": ["linkedin"],
                     "auto_check": True}


@app.get("/api/autopilot")
def get_autopilot():
    return {**DEFAULT_AUTOPILOT, **_read_json(AUTOPILOT, {})}


@app.put("/api/autopilot")
def put_autopilot(body: dict):
    cfg = {**get_autopilot(), **{k: v for k, v in body.items() if k in DEFAULT_AUTOPILOT}}
    _write_json(AUTOPILOT, cfg)
    log_event("Réglages du pilote automatique modifiés")
    return cfg


def _free_slots(networks, horizon=14, n=6):
    taken = {(p.get("planned"), p["network"]) for p in all_posts()}
    out, d0 = [], date.today() + timedelta(days=1)
    for i in range(horizon):
        d = d0 + timedelta(days=i)
        for net in networks:
            if net in NETWORKS and d.weekday() in NETWORKS[net]["days"][:2] and (d.isoformat(), net) not in taken:
                out.append((d.isoformat(), net))
    return out[:n]


def refill():
    cfg = get_autopilot()
    horizon = (date.today() + timedelta(days=14)).isoformat()
    planned = [p for p in all_posts() if p.get("planned") and date.today().isoformat() <= p["planned"] <= horizon]
    missing = cfg["min_planned_14d"] - len(planned)
    if missing <= 0:
        return
    free = _free_slots(cfg["refill_networks"], n=missing)
    if not free:
        return
    data = suggest(DocIn(content=f"Propose exactement {len(free)} idées pour ces créneaux, dans cet ordre : "
                                  f"{json.dumps(free)}. Continue le fil conducteur de la série en cours."))
    for (d, net), it in zip(free, data.get("items", [])):
        save({"id": uuid.uuid4().hex[:10], "network": net, "status": "idée", "series": "Journal d'éducation d'Obsidia",
              "planned": d, "time": NETWORKS[net]["time"], "hook": it.get("hook", ""), "text": "", "image": "",
              "notes": f"Angle : {it.get('angle','')} · Preuve nécessaire : {it.get('preuve','aucun')} · (idée automatique)",
              "created": datetime.now().isoformat(timespec="seconds"), "published": ""})
    log_event(f"{min(len(free), len(data.get('items', [])))} idée(s) ajoutée(s) automatiquement au calendrier")


def auto_draft_one():
    cfg = get_autopilot()
    horizon = (date.today() + timedelta(days=cfg["draft_horizon_days"])).isoformat()
    # uniquement des idées SANS texte, à venir : le pilote n'écrase jamais un texte existant
    todo = sorted([p for p in all_posts() if p["status"] == "idée" and not p.get("text", "").strip()
                   and p.get("planned") and date.today().isoformat() <= p["planned"] <= horizon],
                  key=lambda p: p["planned"])
    if not todo:
        return False
    p = todo[0]
    net = NETWORKS[p["network"]]
    prompt = VOICE_RULES + (
        f"Écris un post {net['label']} ({net['hint']}, limite {net['limit']} caractères) pour la série "
        f"« {p.get('series','')} », semaine {p.get('week') or '?'}.\n{p.get('notes','')}\nAccroche proposée : {p.get('hook','')}\n"
        "Donne aussi deux lignes courtes pour l'image. Format : texte entre <POST></POST>, puis <IMG1>…</IMG1><IMG2>…</IMG2>.")
    out = claude(prompt)
    m = re.search(r"<POST>\s*(.*?)\s*</POST>", out, re.S)
    if not m:
        p["notes"] = (p.get("notes", "") + " · rédaction auto échouée").strip(" ·")
        p["status"] = "brouillon"
        save(p)
        log_event(f"Rédaction automatique échouée ({p['planned']} {net['label']})")
        return True
    if load(p["id"]).get("text", "").strip():  # modifié par Étienne pendant la rédaction : on n'écrase pas
        log_event(f"Rédaction ignorée : le post du {p['planned']} a été modifié entre-temps")
        return True
    p["text"] = humanize(DocIn(content=m.group(1).strip()))["text"].strip()
    p["status"] = "brouillon"
    save(p)
    l1 = re.search(r"<IMG1>(.*?)</IMG1>", out, re.S)
    l2 = re.search(r"<IMG2>(.*?)</IMG2>", out, re.S)
    line1 = (l1.group(1).strip() if l1 else (p.get("hook") or p["text"].split("\n")[0]))[:60]
    try:
        make_variants(p["id"], line1, l2.group(1).strip()[:60] if l2 else "")
    except Exception as e:
        log_event(f"Image non générée ({p['planned']}) : {str(e)[:80]}")
    log_event(f"Brouillon rédigé : {p['planned']} {net['label']} « {p['text'][:40]}… »")
    return True


def auto_decline_validated():
    cfg = get_autopilot()
    for p in all_posts():
        if p["network"] == "linkedin" and p["status"] in ("validé", "programmé") and not p.get("declined"):
            p["declined"] = True
            save(p)
            decline_post(p["id"], cfg["decline_to"])
            return True
    return False


def auto_check():
    for p in all_posts():
        if p["status"] in ("brouillon", "validé", "programmé"):
            c = checklist(p)
            flag = "" if c["ok"] else " / ".join(i["msg"] for i in c["items"] if i["level"] == "bloquant")
            if p.get("check_flag", "") != flag:
                p["check_flag"] = flag
                save(p)


AUTO_STATE = {"last_refill": 0.0, "busy": False}


def autopilot_loop():
    while True:
        time.sleep(60)
        cfg = get_autopilot()
        if not cfg["enabled"] or AUTO_STATE["busy"]:
            continue
        AUTO_STATE["busy"] = True
        try:
            if cfg["auto_check"]:
                auto_check()
            weekly_audit_tick()
            if cfg["auto_refill"] and time.time() - AUTO_STATE["last_refill"] > 6 * 3600:
                AUTO_STATE["last_refill"] = time.time()
                refill()
            if cfg["auto_draft"] and auto_draft_one():
                continue
            if cfg["auto_decline"]:
                auto_decline_validated()
        except Exception as e:  # le pilote ne doit jamais tuer le serveur
            log_event(f"Erreur du pilote : {str(e)[:120]}")
        finally:
            AUTO_STATE["busy"] = False


# ---------------------------------------------------------------- guides par réseau
GUIDES = DATA / "guides.json"
DOCS["guides"] = GUIDES


@app.get("/api/guides")
def get_guides():
    return _read_json(GUIDES, {})


# ---------------------------------------------------------------- plan trimestriel
QUARTERS = DATA / "quarters"
QUARTERS.mkdir(exist_ok=True)


class QuarterIn(BaseModel):
    quarter: str  # ex. 2026-T4
    goal: str = ""


def _quarter_months(q):
    m = re.fullmatch(r"(\d{4})-T([1-4])", q)
    if not m:
        raise HTTPException(400, "format attendu : 2026-T4")
    y, t = int(m.group(1)), int(m.group(2))
    return y, [3 * (t - 1) + i for i in (1, 2, 3)]


@app.get("/api/quarters")
def list_quarters():
    return [{"quarter": p.stem, "content": p.read_text(encoding="utf-8"),
             "campaigns": _read_json(QUARTERS / f"{p.stem}.json", [])} for p in sorted(QUARTERS.glob("*.md"), reverse=True)]


@app.post("/api/quarters")
def make_quarter(body: QuarterIn):
    y, months = _quarter_months(body.quarter)
    names = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre",
             "novembre", "décembre"]
    prompt = VOICE_RULES + (
        f"Construis le plan marketing et storytelling d'Étienne pour le trimestre {body.quarter} "
        f"({', '.join(names[m - 1] for m in months)} {y}). Objectif d'Étienne : {body.goal or 'faire parler du projet Obsidia'}.\n"
        "Lis aussi C:/Users/User/.claude/linkedin/plan.md et le journal. Réseaux : LinkedIn, Facebook, Instagram, YouTube "
        "(X n'existe pas encore).\n"
        "Contenu en markdown : 1) le message central du trimestre en une phrase ; 2) l'arc narratif mois par mois "
        "(où en est l'histoire au début, au milieu, à la fin) ; 3) le rôle de chaque réseau ce trimestre ; "
        "4) les temps forts possibles (vidéos, jalons du projet À CONFIRMER par Étienne, jamais inventés) ; "
        "5) ce qu'on mesure et le seuil qui ferait changer de cap (hypothèses, pas des promesses) ; "
        "6) les faits à collecter dans le journal pour nourrir le trimestre.\n"
        "Réponds avec le markdown entre <PLAN></PLAN>, puis entre <JSON></JSON> une liste de 3 campagnes "
        "(une par mois) : [{\"name\",\"goal\",\"theme\",\"start\":\"AAAA-MM-JJ\",\"weeks\",\"cadence\":{\"linkedin\":2,...}}].")
    out = claude(prompt, timeout=900)
    plan = re.search(r"<PLAN>\s*(.*?)\s*</PLAN>", out, re.S)
    camps = re.search(r"<JSON>\s*(.*?)\s*</JSON>", out, re.S)
    if not plan:
        raise HTTPException(502, "réponse de Claude inexploitable :\n" + out[-1500:])
    (QUARTERS / f"{body.quarter}.md").write_text(plan.group(1), encoding="utf-8")
    try:
        cs = json.loads(camps.group(1)) if camps else []
    except json.JSONDecodeError:
        cs = []
    _write_json(QUARTERS / f"{body.quarter}.json", cs)
    log_event(f"Plan du trimestre {body.quarter} rédigé")
    return {"quarter": body.quarter, "content": plan.group(1), "campaigns": cs}


@app.post("/api/quarters/{q}/campaigns")
def quarter_campaigns(q: str):
    _quarter_months(q)
    made = []
    for c in _read_json(QUARTERS / f"{q}.json", []):
        try:
            made.append(create_campaign(CampaignIn(**{k: c[k] for k in ("name", "goal", "theme", "start", "weeks", "cadence") if k in c}))["name"])
        except Exception as e:
            log_event(f"Campagne du trimestre ignorée : {str(e)[:80]}")
    return {"created": made}


# ---------------------------------------------------------------- audit des avancées (GitHub + PC)
SOURCES = DATA / "sources.json"
AUDIT_PENDING = DATA / "audit-pending.json"
DOCS["sources"] = SOURCES
AUDIT_JOB = {"running": False, "msg": ""}


def _git(d, *args):
    r = subprocess.run(["git", "-C", str(d), *args], capture_output=True, text=True, encoding="utf-8",
                       errors="replace", timeout=30)
    return r.stdout.strip()


def gather_progress(since):
    src = _read_json(SOURCES, {})
    seen, local = set(), []
    for root in src.get("local_roots", []):
        rp = Path(root)
        if not rp.exists():
            continue
        for d in [rp] + [x for x in rp.iterdir() if x.is_dir()]:
            if not (d / ".git").exists():
                continue
            log = _git(d, "log", "--all", f"--since={since}", "--date=short", "--format=%h|%ad|%D|%s", "-n", "60")
            rows = [l for l in log.splitlines() if l and l.split("|")[0] not in seen]
            seen.update(l.split("|")[0] for l in rows)
            if rows:
                local.append(f"## {d.name} (local)\n" + "\n".join(rows))
    remote = []
    user = src.get("github_user")
    if user:
        import urllib.request
        try:
            with urllib.request.urlopen(f"https://api.github.com/users/{user}/repos?sort=pushed&per_page=30", timeout=20) as r:
                repos = json.loads(r.read().decode("utf-8"))
            for repo in repos:
                if repo["pushed_at"][:10] < since:
                    continue
                with urllib.request.urlopen(f"https://api.github.com/repos/{user}/{repo['name']}/commits?since={since}T00:00:00Z&per_page=40", timeout=20) as r:
                    cs = json.loads(r.read().decode("utf-8"))
                rows = [f"{c['sha'][:7]}|{c['commit']['author']['date'][:10]}|{c['commit']['message'].splitlines()[0]}" for c in cs if c['sha'][:7] not in seen]
                if rows:
                    remote.append(f"## {repo['name']} (GitHub public, branche par défaut)\n" + "\n".join(rows))
        except Exception as e:
            remote.append(f"(GitHub inaccessible : {str(e)[:80]})")
    return local, remote


def run_audit(since):
    AUDIT_JOB.update(running=True, msg="Lecture de l'historique git…")
    try:
        local, remote = gather_progress(since)
        digest = ("\n\n".join(local))[:14000] + "\n\n" + ("\n\n".join(remote))[:6000]
        if not local and not remote:
            AUDIT_JOB.update(running=False, msg=f"Aucune activité depuis le {since}")
            return
        AUDIT_JOB["msg"] = f"Claude analyse {len(local)} dépôt(s) local(aux) et {len(remote)} dépôt(s) GitHub…"
        prompt = VOICE_RULES + (
            f"Voici l'historique git d'Étienne depuis le {since} (format hash|date|refs|message), sur son PC et sur GitHub :\n"
            f"{digest}\n\n"
            "Fais un audit de ses avancées pour nourrir sa communication. Règles strictes :\n"
            "- Ne déduis que ce que les messages de commit disent. Un message de commit n'est PAS une preuve de résultat.\n"
            "- journal : 3 à 10 faits en français simple, datés, compréhensibles par un non-développeur.\n"
            "- proofs : seulement des faits vérifiables, statut RÉALISÉ-DOC (travail commité) ou TESTÉ (si le commit parle de tests, "
            "avec le périmètre). Jamais PROUVÉ ni ACTUEL. Source = dépôt + hash.\n"
            "- sensible : liste ce qui ne doit PAS être publié tel quel (noms internes, chemins, sujets privés).\n"
            "- Distingue ce qui est seulement local de ce qui est sur GitHub.\n"
            "Format : {\"summary\": \"3 phrases\", \"journal\": [{\"date\",\"text\"}], "
            "\"proofs\": [{\"claim\",\"status\",\"source\",\"date\",\"scope\"}], \"sensible\": [\"...\"]}")
        data, raw = claude_json(prompt, timeout=900)
        if not data:
            AUDIT_JOB.update(running=False, msg="Réponse de Claude inexploitable")
            return
        data["since"], data["at"] = since, datetime.now().isoformat(timespec="minutes")
        data["counts"] = {"local": len(local), "github": len(remote)}
        _write_json(AUDIT_PENDING, data)
        src = _read_json(SOURCES, {})
        src["last_audit"] = date.today().isoformat()
        _write_json(SOURCES, src)
        AUDIT_JOB.update(running=False, msg="Audit terminé : à relire")
        log_event(f"Audit des avancées : {len(data.get('journal', []))} faits, {len(data.get('proofs', []))} preuves proposées")
    except Exception as e:
        AUDIT_JOB.update(running=False, msg=f"Erreur : {str(e)[:120]}")


class AuditIn(BaseModel):
    since: str = ""


@app.post("/api/audit")
def start_audit(body: AuditIn):
    if AUDIT_JOB["running"]:
        raise HTTPException(409, "audit déjà en cours")
    since = body.since or _read_json(SOURCES, {}).get("last_audit") or (date.today() - timedelta(days=14)).isoformat()
    date.fromisoformat(since)
    threading.Thread(target=run_audit, args=(since,), daemon=True).start()
    return {"started": True, "since": since}


@app.get("/api/audit")
def audit_state():
    return {"job": AUDIT_JOB, "pending": _read_json(AUDIT_PENDING, None)}


class AcceptIn(BaseModel):
    kind: str  # journal | proof
    index: int


@app.post("/api/audit/accept")
def audit_accept(body: AcceptIn):
    pend = _read_json(AUDIT_PENDING, None)
    if not pend:
        raise HTTPException(404, "rien à accepter")
    key = "journal" if body.kind == "journal" else "proofs"
    items = pend.get(key, [])
    if not 0 <= body.index < len(items) or items[body.index].get("done"):
        raise HTTPException(400, "élément invalide")
    it = items[body.index]
    if key == "journal":
        add_journal(JournalIn(text=it["text"], date=it.get("date", "")))
    else:
        st = it.get("status") if it.get("status") in PROOF_STATUSES else "RÉALISÉ-DOC"
        add_proof(ProofIn(claim=it["claim"], status=st, source=it.get("source", ""), date=it.get("date", ""),
                          scope=it.get("scope", ""), public=False))  # jamais publiable par défaut
    it["done"] = True
    _write_json(AUDIT_PENDING, pend)
    return pend


DEFAULT_AUTOPILOT["auto_audit"] = False  # audit hebdomadaire automatique


def weekly_audit_tick():
    cfg = get_autopilot()
    last = _read_json(SOURCES, {}).get("last_audit") or "2000-01-01"
    if cfg.get("auto_audit") and not AUDIT_JOB["running"] and (date.today() - date.fromisoformat(last)).days >= 7:
        run_audit(last)


threading.Thread(target=autopilot_loop, daemon=True).start()


app.mount("/", StaticFiles(directory=ROOT / "web", html=True), name="web")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8108)
