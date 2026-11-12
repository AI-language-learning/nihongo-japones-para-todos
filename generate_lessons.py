#!/usr/bin/env python3
"""
generate_lessons.py
Genera lecciones/ a partir de database/A1/*.json.

    python3 generate_lessons.py

Salida:
    lecciones/index.html
    lecciones/leccion-ds-core-01.html ...

Presentación (decidida el 2026-11-11):
  - Alfabeto en primer plano, kana y kanji debajo.
  - Notación «Hepburn con señales»: letras h, j, z y g(+e/i) marcadas,
    vocales largas dobles, u débil de desu/masu atenuada, ん = m ante b/p/m.
  - Estilos en css/aprender.css, comportamiento en js/leccion.js.
  - Audio: audio/A1/<id>.mp3 (tools/generar_audio.py). Si falta el archivo,
    el botón usa la voz del navegador.
No editar a mano los HTML de lecciones/: se regeneran.
"""

import json
import re
import sys
from pathlib import Path

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

CLASS_NAMES = {"A": "Adjetivo", "Na": "Nominal adjetival", "N": "Nominal", "V": "Verbo"}

# Qué escritura va en grande al abrir la lección: "alfa", "kana" o "kanji".
# Plan: bloques 4-5 → "kana", 6-7 → "kanji", cuando exista la sección «kana de hoy».
MODO_POR_BLOQUE = {0: "alfa", 1: "alfa", 2: "alfa", 3: "alfa",
                   4: "kana", 5: "kana", 6: "kanji", 7: "kanji"}
# Unidades 4-6 (bloques 1-3): alfabeto grande, kana algo mayor. Unidades 9-10 (bloques 6-7): alfabeto oculto hasta pulsar.
BLOQUES_KANA_MEDIO = {1, 2, 3}
BLOQUES_ALFA_OCULTO = {6, 7}

# Bloques en los que se muestra la pista «Suena como …»
BLOQUES_CON_PISTA = {0, 1}


# ─────────────────────────────────────────────
# NOTACIÓN
# ─────────────────────────────────────────────
_MACRON = {"ā": "aa", "ī": "ii", "ū": "uu", "ē": "ee", "ō": "oo",
           "Ā": "Aa", "Ī": "Ii", "Ū": "Uu", "Ē": "Ee", "Ō": "Oo"}


def lectura(romaji):
    """Romaji de la base de datos (Hepburn con macrones) → notación del sitio."""
    r = romaji or ""
    for k, v in _MACRON.items():
        r = r.replace(k, v)
    r = re.sub(r"\bwo\b", "o", r)
    r = re.sub(r"n(?=[bpm])", "m", r)          # ん = m ante b/p/m
    r = re.sub(r"n'(?=[aiueoy])", "n-", r)     # ん + vocal: kin-en
    return r


def lectura_html(texto):
    """Marca las letras con trampa y atenúa la u débil de desu/masu."""
    s = esc(texto)
    s = re.sub(r"\b([Dd]es|[Mm]as)u\b", "\\1\x00", s)
    s = re.sub(r"(?<![sScC])[hH]|[jJ]|[zZ]|[gG](?=[eiEI])",
               lambda m: f'<span class="t">{m.group(0)}</span>', s)
    return s.replace("\x00", '<span class="d">u</span>')


def tiene_trampa(texto):
    return bool(re.search(r"(?<![sc])h|j|z|g(?=[ei])", texto.lower()))


def suena_como(texto):
    """Pronunciación figurada con ortografía española, solo como pista."""
    out = []
    for w in re.split(r"(\W+)", texto):
        cap = w[:1].isupper()
        x = w.lower()
        x = x.replace("j", "dy")
        x = re.sub(r"(?<![sc])h", "j", x)
        x = re.sub(r"g(?=[ei])", "gu", x)
        x = x.replace("z", "dz")
        x = re.sub(r"ny(?=[auo])", "ñ", x)
        x = re.sub(r"(des|mas)u$", r"\1", x)
        out.append(x.capitalize() if cap else x)
    return "".join(out).rstrip(".。")


_BASE = {
    "あ": "a", "い": "i", "う": "u", "え": "e", "お": "o",
    "か": "ka", "き": "ki", "く": "ku", "け": "ke", "こ": "ko",
    "が": "ga", "ぎ": "gi", "ぐ": "gu", "げ": "ge", "ご": "go",
    "さ": "sa", "し": "shi", "す": "su", "せ": "se", "そ": "so",
    "ざ": "za", "じ": "ji", "ず": "zu", "ぜ": "ze", "ぞ": "zo",
    "た": "ta", "ち": "chi", "つ": "tsu", "て": "te", "と": "to",
    "だ": "da", "ぢ": "ji", "づ": "zu", "で": "de", "ど": "do",
    "な": "na", "に": "ni", "ぬ": "nu", "ね": "ne", "の": "no",
    "は": "ha", "ひ": "hi", "ふ": "fu", "へ": "he", "ほ": "ho",
    "ば": "ba", "び": "bi", "ぶ": "bu", "べ": "be", "ぼ": "bo",
    "ぱ": "pa", "ぴ": "pi", "ぷ": "pu", "ぺ": "pe", "ぽ": "po",
    "ま": "ma", "み": "mi", "む": "mu", "め": "me", "も": "mo",
    "や": "ya", "ゆ": "yu", "よ": "yo",
    "ら": "ra", "り": "ri", "る": "ru", "れ": "re", "ろ": "ro",
    "わ": "wa", "を": "o", "ゔ": "vu",
    "ぁ": "a", "ぃ": "i", "ぅ": "u", "ぇ": "e", "ぉ": "o",
}
_YOON = {"ゃ": "a", "ゅ": "u", "ょ": "o"}
_PALATAL = {"shi": "sh", "chi": "ch", "ji": "j"}


def kana_a_lectura(kana, verbo=False):
    """Hiragana/katakana → notación del sitio (para el vocabulario, sin espacios)."""
    k = "".join(chr(ord(c) - 0x60) if "ァ" <= c <= "ヶ" else c for c in (kana or ""))
    sil = []
    i = 0
    while i < len(k):
        c = k[i]
        nxt = k[i + 1] if i + 1 < len(k) else ""
        if c == "ふ" and nxt in "ぁぃぇぉ" and nxt:
            sil.append("f" + _BASE[nxt]); i += 2
        elif c in _BASE and nxt in _YOON:
            b = _BASE[c]
            stem = _PALATAL.get(b, b[:-1] + "y")
            sil.append(stem + _YOON[nxt])
            i += 2
        elif c in _BASE:
            sil.append(_BASE[c]); i += 1
        elif c == "っ":
            sil.append("Q"); i += 1
        elif c == "ん":
            sil.append("N"); i += 1
        elif c == "ー":
            sil.append("L"); i += 1
        else:
            i += 1                              # puntuación y otros signos
    out = ""
    for n, s in enumerate(sil):
        sig = sil[n + 1] if n + 1 < len(sil) else ""
        if s == "Q":
            out += "t" if sig.startswith("ch") else sig[:1]
        elif s == "N":
            if sig[:1] in ("b", "p", "m"):
                out += "m"
            elif sig[:1] in ("a", "i", "u", "e", "o", "y"):
                out += "n-"
            else:
                out += "n"
        elif s == "L":
            out += out[-1:] if out[-1:] in "aiueo" else ""
        else:
            out += s
    if verbo and out.endswith("ou"):            # 思う = omou, no «omoo»
        return out[:-2].replace("ou", "oo") + "ou"
    return out.replace("ou", "oo")


# ─────────────────────────────────────────────
# UTILIDADES
# ─────────────────────────────────────────────
def conjunto_to_slug(cid):
    """DS-CORE-01 → ds-core-01"""
    return cid.lower().replace("_", "-")


def esc(text):
    if text is None:
        return ""
    return (str(text).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def class_pill(clase):
    if not clase:
        return ""
    nombre = CLASS_NAMES.get(clase, clase)
    return (f'<span class="pill pill-{esc(clase.lower())}" title="{esc(nombre)}">'
            f'{esc(clase)}</span>')


def sin_punto(texto):
    return (texto or "").rstrip("。、？！")



# ─────────────────────────────────────────────
# UNIDADES DEL CURSO (10). Los bloques 0–7 de la base de datos son las unidades 3–10.
# ─────────────────────────────────────────────
UNIDADES = [
    # (nº, título, qué podrás hacer, ejemplo romaji, ejemplo es, bloque BD o None, enlace fijo)
    (1, "Los sonidos", "Leer el alfabeto japonés tal como lo escribimos aquí.",
     "Hai.", "Sí.", None, "../como-se-lee.html"),
    (2, "El esqueleto de la frase", "Ver cómo se arma una frase japonesa, de dentro hacia fuera.",
     "Watashi wa gohan o taberu.", "Yo voy a comer arroz.", None, "../lecciones/leccion-ds-esq-01.html"),
    (3, "El núcleo de la frase", "Decir frases completas con una sola palabra.",
     "Samui.", "¡Qué frío!", 0, None),
    (4, "Decir que no", "Negar lo que dices: no hace frío, no estoy bien, no voy.",
     "Samukunai.", "No hace frío.", 1, None),
    (5, "Lo que ya pasó", "Hablar del pasado: hacía frío, estaba bien, fui.",
     "Samukatta.", "Hacía frío.", 2, None),
    (6, "Lo que no pasó", "Negar el pasado: no hacía frío, no fui.",
     "Samukunakatta.", "No hacía frío.", 3, None),
    (7, "Hablar con cortesía", "Hablar con desconocidos, profesores y en el trabajo.",
     "Samui desu.", "Hace frío.", 4, None),
    (8, "Qué, dónde, adónde", "Añadir qué comes, adónde vas, dónde estudias.",
     "Tookyoo ni iku.", "Voy a Tokio.", 5, None),
    (9, "De qué estás hablando", "Elegir el tema de la frase con wa.",
     "Sushi wa oishii.", "El sushi, qué rico.", 6, None),
    (10, "Tu voz al final de la frase", "Sonar natural con yo, ne y ka.",
     "Oishii ne.", "Qué rico, ¿verdad?", 7, None),
]
AP_BLOQUES = (0, 1, 2, 3, 4, 5, 6, 7)   # bloques cuyas notas ya están reescritas para estudiantes
UNIDAD_DE_BLOQUE = {u[5]: u for u in UNIDADES if u[5] is not None}

HEAD_FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">\n'
              '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
              '<link href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;800'
              '&family=M+PLUS+Rounded+1c:wght@400;500;700&display=swap" rel="stylesheet">\n'
              '<link rel="stylesheet" href="../css/aprender.css">')

FOOTER = '''<footer class="pie">
  <nav aria-label="Navegación del pie de página">
    <a href="../index.html">Inicio</a>
    <a href="index.html">Lecciones</a>
    <a href="../herramientas/kana.html">Kana</a>
    <a href="../gramatica/index.html">Para profes y curiosos</a>
  </nav>
  <p>日本語 — Japonés para Todos · Voz: VOICEVOX:No.7</p>
</footer>'''


# ─────────────────────────────────────────────
# COMPONENTES
# ─────────────────────────────────────────────
def render_example_card(entry):
    clase = entry.get("clase", "")
    sit   = entry.get("situación", {}).get("descripción", "")
    jp    = entry.get("japonés", "")
    fur   = entry.get("furigana", jp)
    es    = entry.get("español", "")
    audio = entry.get("audio_text", sin_punto(jp))
    note  = entry.get("notas_hispanohablante") or ""
    lec   = lectura(entry.get("romaji", ""))

    mp3 = Path(entry.get("audio_dir", "audio/A1")) / f"{entry.get('id', '')}.mp3"
    archivo = f' data-audio="../{mp3.as_posix()}"' if mp3.exists() else ""

    pista = ""
    if entry.get("bloque") in BLOQUES_CON_PISTA and tiene_trampa(lec):
        pista = f'\n      <p class="ej-pista">Suena como «{esc(suena_como(lec))}»</p>'
    nota = f'\n      <p class="ej-nota">{esc(note)}</p>' if note else ""

    return f'''
    <article class="ej">
      <p class="ej-sit">{class_pill(clase)} {esc(sit)}</p>
      <p class="ej-ro" lang="ja-Latn">{lectura_html(lec)}</p>
      <p class="ej-ka" lang="ja">{esc(fur)}</p>
      <p class="ej-kj" lang="ja">{esc(jp)}</p>
      <p class="ej-es">{esc(es)}</p>{pista}
      <button type="button" class="oir" data-text="{esc(audio)}"{archivo}>▶ Escuchar</button>{nota}
    </article>'''


def render_box(clase_css, etiqueta, text):
    if not text:
        return ""
    if "\n\n" in text:
        parts = text.strip().split("\n\n")
    else:
        parts = re.split(r"(?=\d+\.\s)", text.strip())
    def fmt(p):
        return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", esc(p.strip()))
    inner = "\n".join(f"      <p>{fmt(p)}</p>" for p in parts if p.strip())
    return f'''
    <div class="caja {clase_css}">
      <p class="caja-etq">{etiqueta}</p>
{inner}
    </div>'''


def render_vocab_table(entries):
    seen, rows = set(), []
    for entry in entries:
        for v in entry.get("vocabulario", []):
            key = v.get("jp", "")
            if key in seen:
                continue
            seen.add(key)
            fur = v.get("furigana", key)
            cls = v.get("clase", "")
            lec = "".join(p if re.fullmatch(r"[\s/]+", p) else kana_a_lectura(p, verbo=(cls == "V"))
                          for p in re.split(r"([\s/]+)", fur))
            if v.get("es", "")[:1].isupper():   # nombres propios: Tookyoo, Tanaka
                lec = lec[:1].upper() + lec[1:]
            if fur.endswith("さん") and len(fur) > 2 and lec.endswith("san") and not lec.endswith("-san"):
                lec = lec[:-3] + "-san"
            rows.append(
                "<tr>"
                f'<td class="v-ro" lang="ja-Latn">{lectura_html(lec)}</td>'
                f'<td class="v-ja" lang="ja">{esc(fur)}'
                + (f' <span class="v-kj">{esc(key)}</span>' if key != fur else "")
                + "</td>"
                f'<td>{esc(v.get("es", ""))}</td>'
                f"<td>{class_pill(cls)}</td>"
                "</tr>")
    if not rows:
        return ""
    return f'''
    <div class="vocab">
      <h3>Palabras de esta lección</h3>
      <div class="tabla"><table>
        <thead><tr><th>Se lee</th><th>Se escribe</th><th>Significa</th><th>Clase</th></tr></thead>
        <tbody>
          {chr(10).join(rows)}
        </tbody>
      </table></div>
    </div>'''


SELECTOR = '''<div class="modo" role="group" aria-label="Escritura en grande">
    <span>Ver en grande:</span>
    <button type="button" data-modo="alfa">Alfabeto</button>
    <button type="button" data-modo="kana">Kana</button>
    <button type="button" data-modo="kanji">Kanji</button>
  </div>'''



# ─────────────────────────────────────────────
# KANA DE HOY: los kana nuevos que aparecen en cada lección (máx. 5), en orden de aparición
# ─────────────────────────────────────────────
KANA_HOY = {}
KANA_MAX = 5
_PEQ = "ゃゅょャュョ"
_LECT_ESPECIAL = {"は": "ha", "へ": "he", "を": "o", "っ": "(pausa)", "ー": "(larga)"}
_NOTA_ESPECIAL = {"は": "Como posposición se lee wa.", "へ": "Como posposición se lee e.",
                  "を": "Se escribe wo, pero se lee o.",
                  "っ": "No suena: duplica la consonante siguiente (datta)."}


def _unidades_kana(furi):
    """Unidades de kana de una frase: letra sola o letra + ゃゅょ. Sin signos ni 'ー'."""
    out, i = [], 0
    while i < len(furi):
        c = furi[i]
        es_kana = ("\u3041" <= c <= "\u3096" or "\u30a1" <= c <= "\u30fa") and c not in _PEQ \
            and c not in "ぁぃぅぇぉゎァィゥェォヮ"
        if es_kana:
            if i + 1 < len(furi) and furi[i + 1] in _PEQ:
                out.append(c + furi[i + 1]); i += 2
                continue
            out.append(c)
        i += 1
    return out


def calcular_kana_hoy(todos):
    ensenados, resultado = set(), {}
    for _, _, conj, entries in todos:
        nuevos = []
        for e in entries:
            for u in _unidades_kana(e.get("furigana", "")):
                if u not in ensenados and u not in [n[0] for n in nuevos]:
                    nuevos.append((u, e))
        elegidos = nuevos[:KANA_MAX]
        for u, _ in elegidos:
            ensenados.add(u)
        resultado[conj["id"]] = elegidos
    return resultado


def render_kana_hoy(cid):
    items = KANA_HOY.get(cid) or []
    if not items:
        return ""
    fichas = []
    for u, e in items:
        hira = "".join(chr(ord(c) - 0x60) if "ァ" <= c <= "ヶ" else c for c in u)
        lect = _LECT_ESPECIAL.get(hira) or kana_a_lectura(hira)
        nota = _NOTA_ESPECIAL.get(hira, "")
        tipo = " <small>(katakana)</small>" if "ァ" <= u[0] <= "ヶ" else ""
        ej = lectura_html(lectura(e.get("romaji", "")).rstrip("。.？?"))
        fichas.append(f'''
      <div class="kana-f">
        <span class="k-j" lang="ja">{esc(u)}</span>
        <span class="k-r">{lectura_html(lect) if lect[0] != "(" else esc(lect)}{tipo}</span>
        <span class="k-e">en «{ej}»</span>{f'<span class="k-n">{esc(nota)}</span>' if nota else ""}
      </div>''')
    return f'''
  <section class="parte">
    <h2>Kana de hoy <span class="h2-ja" lang="ja">今日のかな</span></h2>
    <p>Ya los has visto en las frases. Ahora ponles nombre: mira cada letra y di su sonido. Tabla completa en <a href="../herramientas/kana.html">Kana</a>.</p>
    <div class="kanas">{"".join(fichas)}
    </div>
  </section>'''

# ─────────────────────────────────────────────
# PÁGINA DE LECCIÓN
# ─────────────────────────────────────────────
def render_page(conjunto, entries, bloque_titulo, bloque_num, prev_url, next_url):
    cid      = conjunto["id"]
    titulo   = conjunto.get("título", cid)
    objetivo = conjunto.get("objetivo", "")
    nota     = conjunto.get("nota_hispanohablante", "")
    modo     = MODO_POR_BLOQUE.get(bloque_num, "alfa")

    extra_cuerpo = (" kana-medio" if bloque_num in BLOQUES_KANA_MEDIO else
                    " ro-oculto" if bloque_num in BLOQUES_ALFA_OCULTO else "")
    selector = SELECTOR
    if bloque_num in BLOQUES_ALFA_OCULTO:
        selector = selector.replace("</div>", '<button type="button" id="ro-toggle" class="ro-toggle">Mostrar alfabeto</button>\n  </div>')
    cards = "\n".join(render_example_card(e) for e in entries)
    nota_html = render_box("caja-es", "Para hispanohablantes", nota)
    prev_btn = (f'<a href="{esc(prev_url)}" class="paso">← Anterior</a>'
                if prev_url else "<span></span>")
    next_btn = (f'<a href="{esc(next_url)}" class="paso paso-sig">Siguiente →</a>'
                if next_url else "<span></span>")
    lead = f'\n    <p class="lead">{esc(objetivo)}</p>' if objetivo else ""
    ayuda_inicial = ('\n    <p class="ayuda-ini">¿No sabes cómo leerlo? Mira primero <a href="../como-se-lee.html">Cómo se lee</a>: son 10 minutos.</p>'
                     if cid in ("DS-ESQ-01", "DS-CORE-01") else "")

    return f'''<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(titulo)} — Japonés para Todos</title>
{HEAD_FONTS}
</head>
<body class="modo-{modo}{extra_cuerpo}" data-modo-inicial="{modo}">

<nav class="migas" aria-label="Ruta de navegación">
  <a href="../index.html">Inicio</a> <span>›</span>
  <a href="index.html">Lecciones</a> <span>›</span>
  <span>{esc(titulo)}</span>
</nav>

<header class="cab">
  <div class="ancho">
    <p class="cab-meta">{esc(bloque_titulo)} · {esc(cid)}</p>
    <h1>{esc(titulo)}</h1>{lead}
  </div>
</header>

<main class="ancho">

  <section class="parte">
    <h2>Escucha y repite</h2>
    <p>Pulsa ▶ en cada frase y dila en voz alta. Las letras <span class="t">en color</span> no suenan como en español: <a href="../como-se-lee.html">cómo se lee</a>.</p>{ayuda_inicial}
    {selector}
    <div class="ejs">{cards}
    </div>
  </section>

  <section class="parte">
    <h2>¿Qué observas?</h2>{render_box("caja-desc", "Fíjate", conjunto.get("descubrimiento", ""))}
  </section>

  <section class="parte">
    <h2>Cómo funciona</h2>{render_box("caja-sis", "El patrón", conjunto.get("sistematización", ""))}{nota_html}{render_vocab_table(entries)}
  </section>
{render_kana_hoy(cid)}

  <nav class="pasos" aria-label="Lección anterior y siguiente">
    {prev_btn}
    <a href="index.html" class="paso-id">{esc(cid)}</a>
    {next_btn}
  </nav>

</main>

{FOOTER}
<script src="../js/leccion.js"></script>
</body>
</html>'''


# ─────────────────────────────────────────────
# ÍNDICE DE LECCIONES
# ─────────────────────────────────────────────
def render_index(all_conjuntos):
    bloques = []
    for bloque_titulo, bloque_num, conj, entries in all_conjuntos:
        if not bloques or bloques[-1][0] != bloque_titulo:
            bloques.append((bloque_titulo, bloque_num, []))
        fname = f"leccion-{conjunto_to_slug(conj['id'])}.html"
        bloques[-1][2].append((conj, len(entries), fname))

    secciones = []
    for bloque_titulo, bloque_num, items in bloques:
        jp, es = "", bloque_titulo
        un = UNIDAD_DE_BLOQUE.get(bloque_num)
        numero = un[0] if un else bloque_num + 1
        jp = un[2] if un else ""
        filas = "\n".join(
            f'        <li><a href="{esc(fname)}">'
            f'<span class="li-t">{esc(conj.get("título", conj["id"]))}</span>'
            f'<span class="li-m">{k} frases</span></a></li>'
            for conj, k, fname in items)
        secciones.append(f'''
  <section class="bloque" id="unidad-{numero}">
    <div class="bloque-cab">
      <span class="bloque-n">{numero}</span>
      <div><h2>{esc(es)}</h2><p>{esc(jp)}</p></div>
    </div>
    <ol class="lista">
{filas}
    </ol>
  </section>''')

    # unidades 1 y 2 (sin lecciones generadas): enlace fijo o «en preparación»
    previas = []
    for n, titulo, hacer, ro, es, bloque, enlace in UNIDADES:
        if bloque is not None:
            continue
        if enlace:
            nombre = "Una frase crece como una cebolla" if "leccion-" in enlace else "Cómo se lee el alfabeto japonés"
            medida = "4 frases" if "leccion-" in enlace else "1 página"
            fila = (f'        <li><a href="{esc(enlace.replace("../lecciones/", ""))}"><span class="li-t">{nombre}</span>'
                    f'<span class="li-m">{medida}</span></a></li>')
        else:
            fila = ('        <li class="pronto"><span class="li-pronto"><span class="li-t">Cómo se arma una frase</span>'
                    '<span class="li-m">En preparación</span></span></li>')
        previas.append(f'''
  <section class="bloque" id="unidad-{n}">
    <div class="bloque-cab">
      <span class="bloque-n">{n}</span>
      <div><h2>{esc(titulo)}</h2><p>{esc(hacer)}</p></div>
    </div>
    <ol class="lista">
{fila}
    </ol>
  </section>''')
    secciones = previas + secciones

    total   = sum(len(items) for _, _, items in bloques)
    total  += 1 if Path('database/esqueleto/unidad-2.json').exists() else 0
    primera = bloques[0][2][0][2] if bloques else "#"

    return f'''<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Lecciones — Japonés para Todos</title>
{HEAD_FONTS}
</head>
<body>

<nav class="migas" aria-label="Ruta de navegación">
  <a href="../index.html">Inicio</a> <span>›</span>
  <span>Lecciones</span>
</nav>

<header class="cab">
  <div class="ancho">
    <h1>Lecciones</h1>
    <p class="lead">{total} lecciones cortas. En cada una escuchas frases reales, las repites y descubres cómo funcionan.</p>
    <p><a href="{esc(primera)}" class="boton">▶ Empezar por la primera</a></p>
  </div>
</header>

<main class="ancho">
{"".join(secciones)}
</main>

{FOOTER}
</body>
</html>'''



def render_mapa(todos):
    """aprender/index.html: el mapa de las 10 unidades."""
    por_bloque = {}
    for _, num, conj, entries in todos:
        por_bloque.setdefault(num, []).append(conj)
    tarjetas = []
    for n, titulo, hacer, ro, es, bloque, enlace in UNIDADES:
        if bloque is not None:
            convs = por_bloque.get(bloque, [])
            primera = f"../lecciones/leccion-{conjunto_to_slug(convs[0]['id'])}.html"
            meta = f"{len(convs)} lecciones"
            href = primera
            estado = ""
        elif enlace:
            href, meta, estado = enlace, ("1 lección" if "leccion-" in enlace else "Una página"), ""
        else:
            href, meta, estado = None, "En preparación", " pronto"
        ej = (f'<p class="u-ej"><span lang="ja-Latn">{lectura_html(ro)}</span> <span class="u-es">{esc(es)}</span></p>'
              if ro else "")
        cuerpo = f'''<span class="u-n">{n}</span>
      <div class="u-tx">
        <h3>{esc(titulo)}</h3>
        <p>{esc(hacer)}</p>
        {ej}
        <p class="u-meta">{meta}</p>
      </div>'''
        if href:
            tarjetas.append(f'    <a class="unidad" href="{esc(href)}">{cuerpo}</a>')
        else:
            tarjetas.append(f'    <div class="unidad{estado}">{cuerpo}</div>')
    pie = FOOTER.replace('href="index.html">Lecciones', 'href="../lecciones/index.html">Lecciones')
    return f'''<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Mapa del curso — Japonés para Todos</title>
{HEAD_FONTS}
</head>
<body>

<nav class="migas" aria-label="Ruta de navegación">
  <a href="../index.html">Inicio</a> <span>›</span>
  <span>Mapa del curso</span>
</nav>

<header class="cab">
  <div class="ancho">
    <h1>Mapa del curso</h1>
    <p class="lead">Diez unidades cortas. Empiezas por los sonidos y terminas hablando con naturalidad. Puedes seguir el orden o saltar a la que necesites.</p>
    <p><a href="../lecciones/leccion-ds-core-01.html" class="boton">▶ Empezar la primera lección</a>
       <a href="../lecciones/index.html" class="enlace2">Ver todas las lecciones</a></p>
  </div>
</header>

<main class="ancho">
  <div class="unidades">
{chr(10).join(tarjetas)}
  </div>
  <p class="nota-mapa">¿Eres profe o te interesa la gramática que hay detrás? Visita <a href="../gramatica/index.html">Para profes y curiosos</a>.</p>
</main>

{pie}
</body>
</html>'''


# ─────────────────────────────────────────────
# TABLA DE KANA (herramientas/kana.html), con la notación del sitio
# ─────────────────────────────────────────────
_FILAS_KANA = [
    ("", ["あ", "い", "う", "え", "お"]), ("k", ["か", "き", "く", "け", "こ"]),
    ("s", ["さ", "し", "す", "せ", "そ"]), ("t", ["た", "ち", "つ", "て", "と"]),
    ("n", ["な", "に", "ぬ", "ね", "の"]), ("h", ["は", "ひ", "ふ", "へ", "ほ"]),
    ("m", ["ま", "み", "む", "め", "も"]), ("y", ["や", "", "ゆ", "", "よ"]),
    ("r", ["ら", "り", "る", "れ", "ろ"]), ("w", ["わ", "", "", "", "を"]),
    ("", ["ん", "", "", "", ""]),
]
_FILAS_SONORAS = [
    ("g", ["が", "ぎ", "ぐ", "げ", "ご"]), ("z", ["ざ", "じ", "ず", "ぜ", "ぞ"]),
    ("d", ["だ", "ぢ", "づ", "で", "ど"]), ("b", ["ば", "び", "ぶ", "べ", "ぼ"]),
    ("p", ["ぱ", "ぴ", "ぷ", "ぺ", "ぽ"]),
]
_YOON_BASES = ["き", "し", "ち", "に", "ひ", "み", "り", "ぎ", "じ", "ぢ", "び", "ぴ"]
_ESP_KANA = {"は": "ha", "へ": "he", "を": "o", "ん": "n"}
_PIE_KANA = {"は": "wa", "へ": "e", "を": "o"}


def _a_kata(s):
    return "".join(chr(ord(c) + 0x60) if "ぁ" <= c <= "ゖ" else c for c in s)


def _celda_kana(u):
    if not u:
        return '<td class="vacio"></td>'
    lect = _ESP_KANA.get(u) or kana_a_lectura(u)
    audio = "-".join(f"{ord(c):x}" for c in u)
    pie = f'<span class="kc-n">posp.: {_PIE_KANA[u]}</span>' if u in _PIE_KANA else ""
    return (f'<td><button type="button" class="kc" data-audio="../audio/kana/{audio}.mp3" data-text="{esc(u)}" '
            f'aria-label="Escuchar {esc(lect)}">'
            f'<span class="kc-h" lang="ja">{esc(u)}</span><span class="kc-k" lang="ja">{esc(_a_kata(u))}</span>'
            f'<span class="kc-r">{lectura_html(lect)}</span>{pie}</button></td>')


def _tabla_kana(filas, cols, titulo):
    cab = "".join(f"<th>{c}</th>" for c in cols)
    cuerpo = ""
    for etiqueta, celdas in filas:
        cuerpo += f'<tr><th class="fila">{lectura_html(etiqueta) if etiqueta else "·"}</th>' + \
                  "".join(_celda_kana(c) for c in celdas) + "</tr>"
    return f'''
    <div class="tabla-kana"><table>
      <caption>{titulo}</caption>
      <thead><tr><th></th>{cab}</tr></thead>
      <tbody>{cuerpo}</tbody>
    </table></div>'''


def render_kana_pagina():
    base = _tabla_kana(_FILAS_KANA, ["a", "i", "u", "e", "o"], "Vocal en la columna, consonante en la fila")
    sonoras = _tabla_kana(_FILAS_SONORAS, ["a", "i", "u", "e", "o"], "Con dos rayitas (g, z, d, b) o un círculo (p)")
    filas_y = [(kana_a_lectura(b)[:-1] if False else "", [b + s for s in "ゃゅょ"]) for b in _YOON_BASES]
    filas_y = [(b, [b + s for s in "ゃゅょ"]) for b in _YOON_BASES]
    cuerpo_y = ""
    for b, celdas in filas_y:
        cuerpo_y += f'<tr><th class="fila" lang="ja">{esc(b)}</th>' + "".join(_celda_kana(c) for c in celdas) + "</tr>"
    yoon = f'''
    <div class="tabla-kana"><table>
      <caption>Sonidos con ゃ ゅ ょ pequeñas</caption>
      <thead><tr><th></th><th>ya</th><th>yu</th><th>yo</th></tr></thead>
      <tbody>{cuerpo_y}</tbody>
    </table></div>'''
    pie = FOOTER.replace('href="index.html">Lecciones', 'href="../lecciones/index.html">Lecciones')
    return f'''<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Tabla de kana — Japonés para Todos</title>
{HEAD_FONTS}
</head>
<body class="pag-kana">

<nav class="migas" aria-label="Ruta de navegación">
  <a href="../index.html">Inicio</a> <span>›</span>
  <span>Tabla de kana</span>
</nav>

<header class="cab">
  <div class="ancho">
    <h1>Tabla de kana <span class="h1-ja" lang="ja">かな表</span></h1>
    <p class="lead">Para consultar, no para memorizar de golpe. En el curso aprendes unos pocos kana en cada lección. Toca cualquiera para oírlo.</p>
  </div>
</header>

<main class="ancho">

  <section class="parte">
    <div class="selector" role="group" aria-label="Ver kana">
      <button type="button" data-kana="hira" class="activo">Hiragana</button>
      <button type="button" data-kana="kata">Katakana</button>
    </div>
    <p class="nota-kana">Hiragana se usa para las palabras japonesas y las terminaciones. Katakana, para palabras extranjeras, como <span lang="ja">コーヒー</span> (koohii). Las letras <span class="t">en color</span> no suenan como en español: <a href="../como-se-lee.html">cómo se lee</a>.</p>
  </section>

  <section class="parte">
    <h2>Los sonidos básicos</h2>{base}
    <div class="caja caja-es">
      <p class="caja-etq">Tres casos especiales</p>
      <p><strong>は</strong> se lee ha, pero como posposición se lee <strong>wa</strong>. <strong>へ</strong> se lee he, pero como posposición se lee <strong>e</strong>. <strong>を</strong> se lee <strong>o</strong>.</p>
    </div>
  </section>

  <section class="parte">
    <h2>Con rayitas y círculo</h2>{sonoras}
    <div class="caja caja-sis">
      <p class="caja-etq">Dos pares que suenan igual</p>
      <p><strong>じ</strong> y <strong>ぢ</strong> suenan ji. <strong>ず</strong> y <strong>づ</strong> suenan zu. Casi siempre se escribe じ y ず.</p>
    </div>
  </section>

  <section class="parte">
    <h2>Sonidos con ゃ ゅ ょ</h2>{yoon}
    <div class="caja caja-sis">
      <p class="caja-etq">Pequeñas, pero importantes</p>
      <p>Un kana pequeño se une al anterior y forma una sola sílaba: <strong>き + ゃ = きゃ</strong> (kya). No es lo mismo que <strong>きや</strong> (ki-ya).</p>
    </div>
  </section>

  <section class="parte">
    <h2>Dos signos más</h2>
    <div class="caja caja-desc">
      <p class="caja-etq">っ y ー</p>
      <p><strong>っ</strong> (pequeña) hace una pausa y duplica la consonante siguiente: <span lang="ja">きって</span> → kitte, <span lang="ja">だった</span> → datta.</p>
      <p><strong>ー</strong> (en katakana) alarga la vocal: <span lang="ja">コーヒー</span> → koohii.</p>
    </div>
  </section>

</main>

{pie}
<script src="../js/kana.js"></script>
</body>
</html>'''

# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
def _aprendiz_crudo():
    p = Path("database/A1/aprendiz.json")
    if not p.exists():
        return {}
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def cargar_aprendiz():
    """Textos para estudiantes (database/A1/aprendiz.json), por id de conjunto."""
    return {k: v for k, v in _aprendiz_crudo().items() if not k.startswith("_")}


def con_texto_aprendiz(conj, aprendiz):
    a = aprendiz.get(conj.get("id"))
    if not a:
        return conj
    c = dict(conj)
    for destino, origen in (("título", "título"), ("objetivo", "lead"),
                            ("descubrimiento", "descubrimiento"),
                            ("sistematización", "sistematización"),
                            ("nota_hispanohablante", "nota")):
        if a.get(origen):
            c[destino] = a[origen]
    return c


def build_all_conjuntos():
    """[(título del bloque, nº de bloque, conjunto, [entradas])] en orden."""
    todos = []
    aprendiz = cargar_aprendiz()
    crudo = _aprendiz_crudo()
    notas = crudo.get("_notas_ejemplos", {})
    bloques = crudo.get("_bloques", {})
    for path_str in DB_FILES:
        path = Path(path_str)
        if not path.exists():
            print(f"  ⚠️  No encontrado: {path_str}")
            continue
        with open(path, encoding="utf-8") as f:
            db = json.load(f)
        num    = db.get("bloque", 0)
        titulo = UNIDAD_DE_BLOQUE[num][1] if num in UNIDAD_DE_BLOQUE else bloques.get(str(num), db.get("título", path.stem))
        mapa   = {e["id"]: e for e in db.get("entradas", [])}
        if notas:
            for e in mapa.values():
                if e["id"] in notas:
                    e["notas_hispanohablante"] = notas[e["id"]]
                elif any(e["id"].startswith(f"A1-{b}-") for b in AP_BLOQUES):
                    e["notas_hispanohablante"] = ""
        for conj in db.get("conjuntos", []):
            entries = [mapa[i] for i in conj.get("ids_entradas", []) if i in mapa]
            todos.append((titulo, num, con_texto_aprendiz(conj, aprendiz), entries))
    return todos


def comprobar_notacion(all_conjuntos):
    """Compara el romaji de cada frase con el que sale de su furigana."""
    dudas, vistos = [], set()
    for _, _, _, entries in all_conjuntos:
        for e in entries:
            if e["id"] in vistos:
                continue
            vistos.add(e["id"])
            a = re.sub(r"[^a-z]", "", lectura(e.get("romaji", "")).lower())
            b = re.sub(r"[^a-z]", "", kana_a_lectura(e.get("furigana", "")))
            if a.replace("wa", "ha") != b.replace("wa", "ha"):   # は se lee wa
                dudas.append((e["id"], e.get("furigana", ""), lectura(e.get("romaji", "")), b))
    return dudas


def generar_esqueleto():
    """Unidad 2 (database/esqueleto/unidad-2.json): una lección propia, fuera de la base A1."""
    p = Path("database/esqueleto/unidad-2.json")
    if not p.exists():
        return
    db = json.loads(p.read_text(encoding="utf-8"))
    entradas = {e["id"]: dict(e, audio_dir="audio/esqueleto") for e in db["entradas"]}
    for c in db["conjuntos"]:
        conj = dict(c, objetivo=c["lead"], nota_hispanohablante=c["nota"])
        entries = [entradas[i] for i in c["ids_entradas"]]
        html = render_page(conj, entries, db["título"], -1, "../como-se-lee.html",
                           "leccion-ds-core-01.html")
        (OUTPUT_DIR / f"leccion-{conjunto_to_slug(c['id'])}.html").write_text(html, encoding="utf-8")
        print(f"  ✓  leccion-{conjunto_to_slug(c['id'])}.html  (unidad 2)")


def main():
    print("🔨 Generando lecciones HTML...\n")
    todos = build_all_conjuntos()
    n = len(todos)
    KANA_HOY.update(calcular_kana_hoy(todos))

    for i, (titulo, num, conj, entries) in enumerate(todos):
        filename = f"leccion-{conjunto_to_slug(conj['id'])}.html"
        prev_url = f"leccion-{conjunto_to_slug(todos[i-1][2]['id'])}.html" if i > 0 else "leccion-ds-esq-01.html"
        next_url = f"leccion-{conjunto_to_slug(todos[i+1][2]['id'])}.html" if i < n - 1 else None
        html = render_page(conj, entries, titulo, num, prev_url, next_url)
        (OUTPUT_DIR / filename).write_text(html, encoding="utf-8")
        print(f"  ✓  {filename}  ({len(entries)} ejemplos)")

    generar_esqueleto()
    (OUTPUT_DIR / "index.html").write_text(render_index(todos), encoding="utf-8")
    print("  ✓  index.html  (índice de lecciones)")
    Path("aprender").mkdir(exist_ok=True)
    Path("aprender/index.html").write_text(render_mapa(todos), encoding="utf-8")
    print("  ✓  aprender/index.html  (mapa del curso)")
    Path("herramientas").mkdir(exist_ok=True)
    Path("herramientas/kana.html").write_text(render_kana_pagina(), encoding="utf-8")
    print("  ✓  herramientas/kana.html  (tabla de kana)")
    print(f"\n✅ {n} lecciones generadas en '{OUTPUT_DIR}/'")

    dudas = comprobar_notacion(todos)
    if dudas:
        print(f"\n⚠️  {len(dudas)} frases cuyo romaji no coincide con su furigana (revisar):")
        for d in dudas:
            print(f"   {d[0]}  {d[1]}  base: {d[2]}  ← kana: {d[3]}")
    if "--estricto" in sys.argv and dudas:
        sys.exit(1)


if __name__ == "__main__":
    main()
