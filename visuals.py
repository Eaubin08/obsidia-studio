"""Visuels Obsidia (style bannière : bleu nuit, cristaux). Rendu HTML/SVG -> PNG via Chrome."""
import html as H
import math
import random

SIZES = {"linkedin": (1080, 1350), "facebook": (1080, 1350), "instagram": (1080, 1350),
         "x": (1600, 900), "youtube": (1080, 1080)}
FORMATS = {"auto": None, "portrait": (1080, 1350), "carre": (1080, 1080), "story": (1080, 1920),
           "paysage": (1600, 900), "miniature-youtube": (1280, 720)}


def carousel(slides, handle, size=(1080, 1350)):
    """Une page HTML par slide (impression PDF). slides = [(titre, texte), ...]"""
    w, h = size
    pages = []
    n = len(slides)
    for i, (title, body) in enumerate(slides, 1):
        motif = constellation(w, h) if i == 1 else ""
        big = i == 1
        pages.append(f"""<section><svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg">
<rect width="100%" height="100%" fill="url(#bg)"/>{_dust(w, h, i)}<g opacity="{.45 if big else .0}">{motif}</g>
<foreignObject x="90" y="{h*.62 if big else h*.2:.0f}" width="{w-180}" height="{h*.6:.0f}">
<div xmlns="http://www.w3.org/1999/xhtml" style="font-family:Segoe UI,Arial,sans-serif;color:#eaf4ff">
<div style="font-size:{86 if big else 64}px;font-weight:700;line-height:1.1;color:{'#eaf4ff' if big else '#7cc8ff'}">{H.escape(title)}</div>
<div style="font-size:40px;line-height:1.35;margin-top:36px;color:#d8e6fb">{H.escape(body)}</div></div></foreignObject>
<text x="90" y="{h-70}" font-family="Segoe UI" font-size="28" fill="#8aa6cf">{H.escape(handle)}</text>
<text x="{w-90}" y="{h-70}" text-anchor="end" font-family="Segoe UI" font-size="28" fill="#8aa6cf">{i}/{n}</text>
</svg></section>""")
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
@page{{size:{w}px {h}px;margin:0}}html,body{{margin:0;background:#050b1c}}section{{width:{w}px;height:{h}px;page-break-after:always;overflow:hidden}}
svg{{display:block}}</style></head><body>
<svg width="0" height="0" style="position:absolute"><defs>
<radialGradient id="bg" cx="50%" cy="42%" r="75%"><stop offset="0" stop-color="#0d2350"/><stop offset=".55" stop-color="#071431"/><stop offset="1" stop-color="#03070f"/></radialGradient>
<linearGradient id="cr" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#7fc4ff" stop-opacity=".55"/><stop offset="1" stop-color="#1a4f9c" stop-opacity=".15"/></linearGradient>
<radialGradient id="glow"><stop offset="0" stop-color="#e8f6ff"/><stop offset=".25" stop-color="#7cc8ff" stop-opacity=".9"/><stop offset="1" stop-color="#2a7fff" stop-opacity="0"/></radialGradient>
</defs></svg>{''.join(pages)}</body></html>"""


def _crystal(cx, cy, s, rot=0, op=1.0, lit=False):
    pts = [(0, -1.6), (.7, -.5), (.55, 1.0), (0, 1.5), (-.55, 1.0), (-.7, -.5)]
    a = math.radians(rot)
    P = [(cx + s * (x * math.cos(a) - y * math.sin(a)), cy + s * (x * math.sin(a) + y * math.cos(a))) for x, y in pts]
    poly = " ".join(f"{x:.1f},{y:.1f}" for x, y in P)
    stroke = "#bfe3ff" if lit else "#4f8fd8"
    return (f'<g opacity="{op}"><polygon points="{poly}" fill="url(#cr)" stroke="{stroke}" stroke-width="2.5"/>'
            f'<line x1="{P[0][0]:.1f}" y1="{P[0][1]:.1f}" x2="{P[3][0]:.1f}" y2="{P[3][1]:.1f}" '
            f'stroke="{stroke}" stroke-opacity=".5" stroke-width="1.5"/></g>')


def constellation(w, h):
    """Corps cristallin formé, une lumière qui s'allume au centre."""
    cx, cy, k = w / 2, h * 0.41, min(w, h) / 1080
    raw = [(0, -300, 46), (-200, -150, 40), (200, -150, 40), (-240, 90, 36), (240, 90, 36),
           (-120, 290, 34), (120, 290, 34)]
    nodes = [(cx + x * k, cy + y * k, r * k) for x, y, r in raw]
    c = (cx, cy + 40 * k)
    links = [(0, 1), (0, 2), (1, 3), (2, 4), (3, 5), (4, 6), (5, 6)]
    s = "".join(f'<line x1="{nodes[a][0]:.0f}" y1="{nodes[a][1]:.0f}" x2="{nodes[b][0]:.0f}" y2="{nodes[b][1]:.0f}" '
                f'stroke="#3d6fb5" stroke-opacity=".45" stroke-width="2"/>' for a, b in links)
    s += "".join(f'<line x1="{x:.0f}" y1="{y:.0f}" x2="{c[0]:.0f}" y2="{c[1]:.0f}" stroke="#3d6fb5" '
                 f'stroke-opacity=".45" stroke-width="2"/>' for x, y, _ in nodes)
    for i, (x, y, r) in enumerate(nodes):
        s += _crystal(x, y, r, rot=(i * 23) % 40 - 20, op=.75)
    s += f'<circle cx="{c[0]:.0f}" cy="{c[1]:.0f}" r="{150*k:.0f}" fill="url(#glow)" opacity=".55"/>'
    s += f'<circle cx="{c[0]:.0f}" cy="{c[1]:.0f}" r="{60*k:.0f}" fill="url(#glow)"/>'
    return s + _crystal(*c, 30 * k, lit=True)


def frontiere(w, h):
    """Une autorité isolée au-dessus d'une frontière, des agents identiques en dessous."""
    k = min(w, h) / 1080
    s = f'<circle cx="{w/2}" cy="{h*.245}" r="{190*k:.0f}" fill="url(#glow)" opacity=".35"/>'
    s += _crystal(w / 2, h * .245, 95 * k, lit=True)
    s += (f'<line x1="{w*.13}" y1="{h*.415}" x2="{w*.87}" y2="{h*.415}" stroke="#7cc8ff" stroke-opacity=".7" '
          f'stroke-width="3" stroke-dasharray="14 12"/>')
    n = 7
    step = w * .74 / (n - 1)
    for row in range(2):
        for i in range(n - row):
            s += _crystal(w * .13 + i * step + (step / 2 if row else 0), h * .51 + row * 150 * k, 32 * k, op=.85)
    return s


def cristal(w, h):
    """Un seul cristal lumineux, sobre."""
    k = min(w, h) / 1080
    return (f'<circle cx="{w/2}" cy="{h*.36}" r="{240*k:.0f}" fill="url(#glow)" opacity=".4"/>'
            + _crystal(w / 2, h * .36, 120 * k, lit=True))


def texte(w, h):
    """Aucun dessin : la phrase seule."""
    return ""


MOTIFS = {"constellation": constellation, "frontiere": frontiere, "cristal": cristal, "texte": texte}


def _dust(w, h, seed):
    r = random.Random(seed)
    return "".join(f'<circle cx="{r.randint(0,w)}" cy="{r.randint(0,h)}" r="{r.choice([1,1,1.5,2])}" '
                   f'fill="#9cc9ff" opacity="{r.uniform(.15,.5):.2f}"/>' for _ in range(int(w * h / 9000)))


def _fit(text, w, base):
    # Segoe UI gras ~0.55 em par caractère
    return min(base, int(w * 0.88 / max(len(text), 1) / 0.55))


def render(motif, line1, line2, footer, size=(1080, 1350), seed=1):
    w, h = size
    art = MOTIFS[motif](w, h)
    k = min(w, h) / 1080
    only_text = motif == "texte"
    y1 = h * (0.45 if only_text else 0.82)
    f1, f2 = _fit(line1, w, int(64 * k)), _fit(line2, w, int(64 * k))
    gap = max(f1, f2) * 1.45
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
html,body{{margin:0;width:{w}px;height:{h}px;overflow:hidden;background:#050b1c}}svg{{display:block}}</style></head><body>
<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg"><defs>
<radialGradient id="bg" cx="50%" cy="42%" r="75%"><stop offset="0" stop-color="#0d2350"/><stop offset=".55" stop-color="#071431"/><stop offset="1" stop-color="#03070f"/></radialGradient>
<linearGradient id="cr" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#7fc4ff" stop-opacity=".55"/><stop offset="1" stop-color="#1a4f9c" stop-opacity=".15"/></linearGradient>
<radialGradient id="glow"><stop offset="0" stop-color="#e8f6ff"/><stop offset=".25" stop-color="#7cc8ff" stop-opacity=".9"/><stop offset="1" stop-color="#2a7fff" stop-opacity="0"/></radialGradient>
</defs><rect width="100%" height="100%" fill="url(#bg)"/>{_dust(w, h, seed)}{art}
<g font-family="Segoe UI, Arial, sans-serif" font-weight="700" text-anchor="middle">
<text x="{w/2}" y="{y1:.0f}" font-size="{f1}" fill="#eaf4ff">{H.escape(line1)}</text>
<text x="{w/2}" y="{y1+gap:.0f}" font-size="{f2}" fill="#7cc8ff">{H.escape(line2)}</text></g>
<text x="{w/2}" y="{h-60*k:.0f}" text-anchor="middle" font-family="Segoe UI, Arial, sans-serif" font-size="{int(26*k)}"
 letter-spacing="4" fill="#8aa6cf">{H.escape(footer)}</text></svg></body></html>"""
