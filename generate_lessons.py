#!/usr/bin/env python3
"""
generate_lessons.py
Genera un archivo HTML por cada発見セット（conjunto de descubrimiento）
a partir de los archivos JSON del database A1.

Uso:
    python3 generate_lessons.py

Salida:
    output/leccion-ds-core-01.html
    output/leccion-ds-core-02.html
    ...
"""

import json
import re
from pathlib import Path


# ─────────────────────────────────────────────
# RUTAS
# ─────────────────────────────────────────────
DB_FILES = [
    "database/A1/00-cuatro-clases/bloque-0-predicado-core.json",
    "database/A1/01-negacion/bloque-1-negacion.json",
    "database/A1/02-perfectivo/bloque-2-perfectivo.json",
    "database/A1/03-perfectivo-negativo/bloque-3-perfectivo-negativo.json",
    "database/A1/04-cortesia/bloque-4-cortesia.json",
    "database/A1/05-complementos/bloque-5-complementos.json",
    "database/A1/06-topico/bloque-6-topico.json",
    "database/A1/07-finales/bloque-7-finales.json",
]

OUTPUT_DIR = Path("lecciones")
OUTPUT_DIR.mkdir(exist_ok=True)


# ─────────────────────────────────────────────
# COLORES POR CLASE
# ─────────────────────────────────────────────
CLASS_COLORS = {
    "A":  {"cls": "#2e8b57", "bg": "#edf7f1", "border": "#a8d8bc"},
    "Na": {"cls": "#7b4ea0", "bg": "#f5effe", "border": "#c9aee6"},
    "N":  {"cls": "#b05c1a", "bg": "#fef3e8", "border": "#e8b87a"},
    "V":  {"cls": "#1a68b0", "bg": "#e8f2fe", "border": "#8ab9e8"},
}

CLASS_NAMES = {
    "A":  "Adjetivo",
    "Na": "Nominal adjetival",
    "N":  "Nominal",
    "V":  "Verbo",
}


# ─────────────────────────────────────────────
# UTILIDADES
# ─────────────────────────────────────────────
def conjunto_to_slug(cid):
    """DS-CORE-01 → ds-core-01"""
    return cid.lower().replace("_", "-")


def esc(text):
    """Escapa caracteres HTML básicos."""
    if text is None:
        return ""
    return (str(text)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;"))


def class_pill(clase):
    c = CLASS_COLORS.get(clase, {})
    return (f'<span class="cls-pill" style="'
            f'background:{c.get("bg","#eee")};'
            f'color:{c.get("cls","#333")};'
            f'border:1px solid {c.get("border","#ccc")};'
            f'">{esc(clase)}</span>')


def card_style(clase):
    c = CLASS_COLORS.get(clase, {})
    return f'border-left:4px solid {c.get("border","#ccc")};'


def speak_btn(audio_text):
    return (f'<button class="speak-btn" data-text="{esc(audio_text)}" '
            f'aria-label="Escuchar pronunciación">🔊</button>')


def format_furigana(jp, furigana):
    """
    Devuelve el japonés con furigana en ruby si es distinto del jp llano.
    Simplificación: muestra el furigana completo sobre el texto completo.
    Para A1 esto es suficiente.
    """
    jp_clean  = jp.rstrip("。、？！")
    fur_clean = furigana.rstrip("。、？！")
    if jp_clean == fur_clean:
        return f'<span class="jp-text">{esc(jp)}</span>'
    return (f'<ruby class="jp-text">'
            f'{esc(jp_clean)}<rt>{esc(fur_clean)}</rt>'
            f'</ruby>{"。" if jp.endswith("。") else ""}')


# ─────────────────────────────────────────────
# COMPONENTES HTML
# ─────────────────────────────────────────────
def render_example_card(entry):
    clase   = entry.get("clase", "")
    colors  = CLASS_COLORS.get(clase, {})
    sit     = entry.get("situación", {}).get("descripción", "")
    jp      = entry.get("japonés", "")
    fur     = entry.get("furigana", jp)
    es      = entry.get("español", "")
    audio   = entry.get("audio_text", jp.rstrip("。、"))
    note    = entry.get("notas_hispanohablante") or ""

    note_html = ""
    if note:
        note_html = f'''
        <p class="card-note">
          <span class="note-label">Nota</span> {esc(note)}
        </p>'''

    return f'''
    <div class="example-card" style="{card_style(clase)}">
      <div class="card-header">
        {class_pill(clase)}
        {speak_btn(audio)}
      </div>
      <p class="card-situation">{esc(sit)}</p>
      <p class="card-jp">{format_furigana(jp, fur)}</p>
      <p class="card-es">{esc(es)}</p>{note_html}
    </div>'''


def render_discovery_box(text):
    if not text:
        return ""
    # Convierte preguntas numeradas en párrafos
    parts = re.split(r'(?=\d+\.\s)', text.strip())
    inner = "\n".join(f"<p>{esc(p.strip())}</p>" for p in parts if p.strip())
    return f'''
    <div class="discovery-box">
      <div class="box-label">💡 Descubrimiento</div>
      {inner}
    </div>'''


def render_system_box(text):
    if not text:
        return ""
    sentences = text.split(". ")
    inner = " ".join(f"{esc(s.strip())}." if not s.strip().endswith(".") else esc(s.strip())
                     for s in sentences if s.strip())
    return f'''
    <div class="system-box">
      <div class="box-label">📐 Sistematización</div>
      <p>{inner}</p>
    </div>'''


def render_vocab_table(entries):
    """Tabla de vocabulario único de un conjunto."""
    seen = set()
    rows = []
    for entry in entries:
        for v in entry.get("vocabulario", []):
            key = v.get("jp", "")
            if key in seen:
                continue
            seen.add(key)
            fur  = v.get("furigana", key)
            es   = v.get("es", "")
            cls  = v.get("clase", "")
            jlpt = v.get("jlpt", "—")
            rows.append(
                f'<tr>'
                f'<td class="vocab-jp"><ruby>{esc(key)}<rt>{esc(fur)}</rt></ruby></td>'
                f'<td>{esc(es)}</td>'
                f'<td>{class_pill(cls) if cls else ""}</td>'
                f'<td class="vocab-jlpt">{esc(jlpt)}</td>'
                f'</tr>'
            )
    if not rows:
        return ""
    rows_html = "\n".join(rows)
    return f'''
    <div class="vocab-section">
      <h3>Vocabulario de esta lección</h3>
      <table class="vocab-table">
        <thead>
          <tr>
            <th>Japonés</th><th>Español</th><th>Clase</th><th>JLPT</th>
          </tr>
        </thead>
        <tbody>
          {rows_html}
        </tbody>
      </table>
    </div>'''


# ─────────────────────────────────────────────
# PLANTILLA HTML COMPLETA
# ─────────────────────────────────────────────
def render_page(conjunto, entries, bloque_titulo, prev_url, next_url):
    cid        = conjunto["id"]
    titulo     = conjunto.get("título", cid)
    objetivo   = conjunto.get("objetivo", "")
    discovery  = conjunto.get("descubrimiento", "")
    sistema    = conjunto.get("sistematización", "")
    nota_hisp  = conjunto.get("nota_hispanohablante", "")

    slug       = conjunto_to_slug(cid)
    filename   = f"leccion-{slug}.html"

    cards_html = "\n".join(render_example_card(e) for e in entries)

    objetivo_html = f'<p class="objetivo">{esc(objetivo)}</p>' if objetivo else ""
    nota_html     = f'''
    <div class="hispanohablante-box">
      <div class="box-label">🇪🇸 Para hispanohablantes</div>
      <p>{esc(nota_hisp)}</p>
    </div>''' if nota_hisp else ""

    vocab_html    = render_vocab_table(entries)
    discovery_html = render_discovery_box(discovery)
    system_html    = render_system_box(sistema)

    prev_btn = (f'<a href="{esc(prev_url)}" class="nav-btn btn-prev">← Anterior</a>'
                if prev_url else '<span></span>')
    next_btn = (f'<a href="{esc(next_url)}" class="nav-btn btn-next">Siguiente →</a>'
                if next_url else '<span></span>')

    return f'''<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(titulo)} — Japonés para Todos</title>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@300;400;500;700&family=Noto+Serif+JP:wght@400;700&family=DM+Serif+Display:ital@0;1&family=Source+Sans+3:ital,wght@0,300;0,400;0,600;0,700;1,400&display=swap" rel="stylesheet">
<style>
/* ── TOKENS ── */
:root {{
  --teal:#3a8fa0; --teal-dark:#1d5f6e; --teal-light:#d6eef3;
  --accent:#c8703a; --ink:#1a1a1a; --warm-gray:#6b6560;
  --light-gray:#e8e4df; --bg:#faf8f5; --white:#fff;
  --font-jp:'Noto Sans JP',sans-serif;
  --font-jp-s:'Noto Serif JP',serif;
  --font-disp:'DM Serif Display',serif;
  --font-body:'Source Sans 3',sans-serif;
  --radius:12px; --shadow:0 4px 24px rgba(0,0,0,0.08);
}}
*, *::before, *::after {{ box-sizing:border-box; margin:0; padding:0; }}
html {{ scroll-behavior:smooth; }}
body {{ font-family:var(--font-body); font-size:1.05rem; line-height:1.75;
        color:var(--ink); background:var(--bg); -webkit-font-smoothing:antialiased; }}
.container {{ max-width:760px; margin:0 auto; padding:0 clamp(1.25rem,5vw,2.5rem); }}
h2 {{ font-family:var(--font-disp); font-size:clamp(1.5rem,4vw,2rem);
      line-height:1.2; margin:2.5rem 0 0.7rem; }}
h3 {{ font-family:var(--font-disp); font-size:1.1rem; color:var(--teal-dark);
      margin:2rem 0 0.6rem; }}
p {{ margin-bottom:0.8rem; }}
ruby rt {{ font-size:0.6em; color:var(--warm-gray); }}

/* ── HEADER ── */
.lesson-header {{
  background:linear-gradient(160deg,var(--teal-dark) 0%,var(--teal) 100%);
  color:#fff; padding:clamp(2.5rem,8vw,4rem) clamp(1.25rem,5vw,2.5rem) clamp(1.5rem,4vw,2.5rem);
  position:relative; overflow:hidden;
}}
.lesson-header::before {{
  content:'語'; font-family:var(--font-jp-s); font-size:clamp(7rem,18vw,12rem);
  font-weight:900; opacity:0.07; position:absolute; bottom:-1rem; right:0;
  line-height:1; pointer-events:none; color:#fff;
}}
.lesson-header-inner {{ max-width:760px; margin:0 auto; }}
.lesson-meta {{ font-size:0.8rem; opacity:0.7; letter-spacing:0.08em;
                text-transform:uppercase; margin-bottom:0.5rem; }}
.lesson-header h1 {{ font-family:var(--font-disp); font-size:clamp(1.6rem,5vw,2.4rem);
                     line-height:1.15; margin-bottom:0.6rem; }}
.lesson-lead {{ font-size:1rem; opacity:0.88; max-width:540px; line-height:1.65; }}
.objetivo {{ background:rgba(255,255,255,0.12); border-radius:8px;
             padding:0.8rem 1rem; font-size:0.95rem; margin-top:1rem;
             border-left:3px solid rgba(255,255,255,0.4); }}

/* ── BREADCRUMB ── */
.breadcrumb {{ background:var(--white); border-bottom:1px solid var(--light-gray);
               padding:0.7rem clamp(1.25rem,5vw,2.5rem); font-size:0.85rem;
               color:var(--warm-gray); }}
.breadcrumb a {{ color:var(--teal); text-decoration:none; }}
.breadcrumb a:hover {{ text-decoration:underline; }}
.breadcrumb .sep {{ margin:0 0.3rem; opacity:0.4; }}

/* ── SECTION ── */
.lesson-section {{ padding:clamp(2rem,5vw,3.5rem) 0;
                   border-top:1px solid var(--light-gray); }}
.lesson-section:first-of-type {{ border-top:none; }}
.section-tag {{ font-size:0.75rem; font-weight:700; letter-spacing:0.12em;
                text-transform:uppercase; color:var(--accent);
                display:block; margin-bottom:0.4rem; }}

/* ── EXAMPLE CARDS ── */
.example-grid {{ display:grid; gap:1rem; margin:1.2rem 0; }}
.example-card {{
  background:var(--white); border:1px solid var(--light-gray);
  border-radius:var(--radius); padding:1.2rem 1.3rem;
  box-shadow:0 2px 12px rgba(0,0,0,0.05);
  transition:box-shadow .25s;
}}
.example-card:hover {{ box-shadow:var(--shadow); }}
.card-header {{ display:flex; justify-content:space-between;
                align-items:center; margin-bottom:0.6rem; }}
.cls-pill {{ display:inline-block; padding:.12rem .55rem; border-radius:100px;
             font-size:.78rem; font-weight:700; font-family:var(--font-body); }}
.speak-btn {{ width:34px; height:34px; border-radius:50%; border:1.5px solid #ccc;
              background:#f5f5f5; cursor:pointer; font-size:0.95rem;
              display:flex; align-items:center; justify-content:center;
              transition:.25s; flex-shrink:0; }}
.speak-btn:hover {{ background:var(--teal); color:#fff; border-color:var(--teal);
                    transform:scale(1.08); }}
.speak-btn.playing {{ background:var(--teal); color:#fff;
                      animation:pulse .8s infinite; }}
@keyframes pulse {{ 0%,100%{{transform:scale(1)}} 50%{{transform:scale(1.1)}} }}
.card-situation {{ font-size:.88rem; color:var(--warm-gray); font-style:italic;
                   margin-bottom:.5rem; }}
.card-jp {{ font-family:var(--font-jp); font-size:1.5rem; font-weight:500;
            line-height:1.3; margin-bottom:.3rem; }}
.jp-text {{ font-family:var(--font-jp); }}
.card-es {{ font-size:.94rem; color:var(--warm-gray); font-style:italic; }}
.card-note {{ font-size:.88rem; color:var(--warm-gray); margin-top:.6rem;
              padding:.5rem .7rem; background:#f8f6f3; border-radius:6px;
              border-left:2px solid var(--accent); }}
.note-label {{ font-size:.72rem; font-weight:700; letter-spacing:.1em;
               text-transform:uppercase; color:var(--accent); margin-right:.3rem; }}

/* ── DISCOVERY & SYSTEM BOXES ── */
.discovery-box, .system-box, .hispanohablante-box {{
  border-radius:var(--radius); padding:1.2rem 1.4rem; margin:1.2rem 0;
}}
.discovery-box {{
  background:linear-gradient(135deg,#fff9f4,#fdf0e8);
  border:1px solid #e8c8a8; border-left:4px solid var(--accent);
}}
.system-box {{
  background:linear-gradient(135deg,#edf7fb,var(--teal-light));
  border:1px solid #b0d8e8; border-left:4px solid var(--teal);
}}
.hispanohablante-box {{
  background:#f5f0ff; border:1px solid #c9aee6; border-left:4px solid #7b4ea0;
}}
.box-label {{ font-size:.73rem; font-weight:700; letter-spacing:.14em;
              text-transform:uppercase; margin-bottom:.7rem; color:var(--warm-gray); }}
.discovery-box .box-label {{ color:var(--accent); }}
.system-box .box-label {{ color:var(--teal-dark); }}
.hispanohablante-box .box-label {{ color:#7b4ea0; }}

/* ── VOCAB TABLE ── */
.vocab-section {{ margin:2rem 0 1rem; }}
.vocab-table {{ width:100%; border-collapse:collapse; font-size:.95rem;
                background:var(--white); border-radius:var(--radius);
                overflow:hidden; box-shadow:0 2px 12px rgba(0,0,0,.05); }}
.vocab-table thead {{ background:var(--teal-light); }}
.vocab-table th {{ padding:.7rem 1rem; text-align:left; font-size:.82rem;
                   font-weight:700; color:var(--teal-dark);
                   border-bottom:2px solid var(--teal); }}
.vocab-table td {{ padding:.7rem 1rem; border-bottom:1px solid var(--light-gray); }}
.vocab-table tbody tr:last-child td {{ border-bottom:none; }}
.vocab-table tbody tr:hover {{ background:#faf8f5; }}
.vocab-jp {{ font-family:var(--font-jp); font-size:1.05rem; }}
.vocab-jlpt {{ color:var(--warm-gray); font-size:.85rem; }}

/* ── LESSON FOOTER NAV ── */
.lesson-footer {{ background:var(--white); border-top:1px solid var(--light-gray);
                  padding:1.5rem 0; margin-top:2rem; }}
.lesson-footer-inner {{ max-width:760px; margin:0 auto;
                         padding:0 clamp(1.25rem,5vw,2.5rem);
                         display:flex; justify-content:space-between;
                         align-items:center; gap:.8rem; flex-wrap:wrap; }}
.nav-btn {{ display:inline-flex; align-items:center; gap:.4rem;
            padding:.6rem 1.2rem; border-radius:100px; font-size:.9rem;
            font-weight:700; text-decoration:none; transition:.25s;
            font-family:var(--font-body); }}
.btn-prev {{ background:var(--light-gray); color:var(--warm-gray); }}
.btn-prev:hover {{ background:#d8d4cf; color:var(--ink); }}
.btn-next {{ background:var(--teal); color:#fff;
             box-shadow:0 3px 12px rgba(58,143,160,.35); }}
.btn-next:hover {{ background:var(--teal-dark); transform:translateY(-1px); }}
.footer-id {{ font-size:.82rem; color:var(--warm-gray); text-align:center; }}

/* ── SITE FOOTER ── */
.site-footer {{ background:var(--ink); color:rgba(255,255,255,.65);
                text-align:center; padding:2rem 1.5rem; font-size:.88rem; }}
.site-footer a {{ color:rgba(255,255,255,.8); text-decoration:none; }}

/* ── SCROLL REVEAL ── */
.reveal {{ opacity:0; transform:translateY(16px); transition:opacity .5s, transform .5s; }}
.reveal.visible {{ opacity:1; transform:none; }}
</style>
</head>
<body>

<nav class="breadcrumb">
  <a href="../index.html">Inicio</a>
  <span class="sep">›</span>
  <a href="index.html">Aprender</a>
  <span class="sep">›</span>
  <span>{esc(titulo)}</span>
</nav>

<header class="lesson-header">
  <div class="lesson-header-inner">
    <p class="lesson-meta">{esc(bloque_titulo)} · {esc(cid)}</p>
    <h1>{esc(titulo)}</h1>
    <p class="lesson-lead">{esc(objetivo)}</p>
  </div>
</header>

<main>

<section class="lesson-section" id="situaciones">
<div class="container">
  <span class="section-tag reveal">📍 Situaciones</span>
  <h2 class="reveal">Observa estos ejemplos</h2>
  <p class="reveal">Escucha cada ejemplo. Todavía no analices — solo absorbe.</p>
  <div class="example-grid reveal">
    {cards_html}
  </div>
</div>
</section>

<section class="lesson-section" id="descubrimiento">
<div class="container">
  <span class="section-tag reveal">🔍 Descubrimiento</span>
  <h2 class="reveal">¿Qué observas?</h2>
  <div class="reveal">
    {discovery_html}
  </div>
</div>
</section>

<section class="lesson-section" id="sistematizacion">
<div class="container">
  <span class="section-tag reveal">📐 Sistematización</span>
  <h2 class="reveal">El patrón</h2>
  <div class="reveal">
    {system_html}
  </div>
  {nota_html}
  {vocab_html}
</div>
</section>

</main>

<footer class="lesson-footer">
  <div class="lesson-footer-inner">
    {prev_btn}
    <span class="footer-id">{esc(cid)}</span>
    {next_btn}
  </div>
</footer>

<footer class="site-footer">
  <p><a href="../index.html">日本語 — Japonés para Todos</a></p>
</footer>

<script>
// TTS
const synth = window.speechSynthesis;
function getJPVoice() {{
  return synth.getVoices().find(v => v.lang.startsWith('ja')) || null;
}}
document.querySelectorAll('.speak-btn').forEach(btn => {{
  btn.addEventListener('click', () => {{
    if (synth.speaking) synth.cancel();
    const u = new SpeechSynthesisUtterance(btn.dataset.text);
    u.lang = 'ja-JP'; u.rate = 0.85;
    const v = getJPVoice(); if (v) u.voice = v;
    btn.classList.add('playing');
    u.onend = u.onerror = () => btn.classList.remove('playing');
    synth.speak(u);
  }});
}});
if (synth.onvoiceschanged !== undefined) synth.onvoiceschanged = () => {{}};

// Scroll reveal
const obs = new IntersectionObserver(es => {{
  es.forEach(e => {{ if (e.isIntersecting) e.target.classList.add('visible'); }});
}}, {{ threshold: 0.08, rootMargin: '0px 0px -20px 0px' }});
document.querySelectorAll('.reveal').forEach(el => obs.observe(el));
</script>
</body>
</html>'''


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
def build_all_conjuntos():
    """Recorre todos los JSON y construye la lista ordenada de conjuntos."""
    all_conjuntos = []   # [(bloque_titulo, conjunto, [entries])]

    for path_str in DB_FILES:
        path = Path(path_str)
        if not path.exists():
            print(f"  ⚠️  No encontrado: {path_str}")
            continue

        with open(path, encoding="utf-8") as f:
            db = json.load(f)

        bloque_titulo = db.get("título", path.stem)
        entry_map = {e["id"]: e for e in db.get("entradas", [])}

        for conj in db.get("conjuntos", []):
            ids     = conj.get("ids_entradas", [])
            entries = [entry_map[i] for i in ids if i in entry_map]
            all_conjuntos.append((bloque_titulo, conj, entries))

    return all_conjuntos


def main():
    print("🔨 Generando lecciones HTML...\n")
    all_conjuntos = build_all_conjuntos()
    n = len(all_conjuntos)

    for i, (bloque_titulo, conj, entries) in enumerate(all_conjuntos):
        slug     = conjunto_to_slug(conj["id"])
        filename = f"leccion-{slug}.html"

        prev_url = None
        next_url = None
        if i > 0:
            prev_slug = conjunto_to_slug(all_conjuntos[i-1][1]["id"])
            prev_url  = f"leccion-{prev_slug}.html"
        if i < n - 1:
            next_slug = conjunto_to_slug(all_conjuntos[i+1][1]["id"])
            next_url  = f"leccion-{next_slug}.html"

        html = render_page(conj, entries, bloque_titulo, prev_url, next_url)
        out  = OUTPUT_DIR / filename
        out.write_text(html, encoding="utf-8")

        print(f"  ✓  {filename}  ({len(entries)} ejemplos)")

    print(f"\n✅ {n} lecciones generadas en '{OUTPUT_DIR}/'")


if __name__ == "__main__":
    main()
