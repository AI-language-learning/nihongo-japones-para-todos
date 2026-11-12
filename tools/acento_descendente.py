#!/usr/bin/env python3
"""Genera audio/correcciones.json: la última frase de acento de cada oración
que termina en plano (￣) pasa a descendente (＼). Lee audio/acentos.tsv.
Decisión del autor (2026-11-12): las frases completas no terminan en acento plano.
Reglas (núcleo = mora tras la cual baja el tono; no puede caer en ッ ン ー ni en
la 2ª vocal de un diptongo/vocal larga):
  …ナカッタ → sobre ナ;  …ナイ(デス) → antes de ナ;  …ダ/ダッタ → antes de ダ;
  partículas finales ヨ・ネ・ヨネ se ignoran;  resto → penúltima mora (2 moras → 1)."""
import json, re, sys

def moras(s):
    return re.findall(r".[ャュョァィゥェォ]?", s)

VOC = {}
for fila, v in (("アカサタナハマヤラワガザダバパ", "a"), ("イキシチニヒミリギジヂビピ", "i"),
                ("ウクスツヌフムユルグズヅブプ", "u"), ("エケセテネヘメレゲゼデベペ", "e"),
                ("オコソトノホモヨロヲゴゾドボポ", "o")):
    for c in fila:
        VOC[c] = v

def vocal(m):
    if m in ("ッ", "ン", "ー"):
        return ""
    if len(m) == 2:  # きゃ etc.
        return VOC.get(m[1], "")
    if m in ("ア", "イ", "ウ", "エ", "オ"):
        return {"ア": "a", "イ": "i", "ウ": "u", "エ": "e", "オ": "o"}[m]
    return VOC.get(m, "")

def especial(ms, i):          # i: índice 0-based
    m = ms[i]
    if m in ("ッ", "ン", "ー"):
        return True
    if i > 0 and m in ("ア", "イ", "ウ", "エ", "オ"):
        return True           # 2ª vocal de vocal larga o diptongo
    return False

def ajustar(ms, pos):          # pos: 1-based
    while pos > 1 and especial(ms, pos - 1):
        pos -= 1
    return pos

def nucleo(frase):
    ms = moras(frase)
    n = len(ms)
    s = "".join(ms)
    for p in ("ヨネ", "ヨ", "ネ"):
        if s.endswith(p) and n > len(moras(p)) and re.search(r"(ダ|ク|ル|ス|ウ|ツ|ム|ブ|グ|ヌ|イ|タ)" + p + "$", s):
            ms2 = ms[: n - len(moras(p))]
            return nucleo_base(ms2)
    return nucleo_base(ms)

def nucleo_base(ms):
    n = len(ms)
    s = "".join(ms)
    if s.endswith("ナカッタ"):
        return ajustar(ms, max(1, n - 3))
    if s.endswith("ナイデス"):
        return ajustar(ms, max(1, n - 4))
    if s.endswith("ナイ"):
        return ajustar(ms, max(1, n - 2))
    if s.endswith("ダッタ"):
        return ajustar(ms, n - 3)
    if s.endswith("ダ") and n >= 3:
        return ajustar(ms, n - 1)
    if n <= 2:
        return 1
    return ajustar(ms, n - 1)

def main():
    filas = [l.rstrip("\n").split("\t") for l in open("audio/acentos.tsv", encoding="utf-8")][1:]
    corr, cambios = {}, []
    for ident, texto, ac, *_ in filas:
        if ident.startswith("extra:"):
            continue
        frases = ac.split("　")
        acentos = []
        for f in frases:
            ms = moras(f.replace("＼", "").replace("￣", ""))
            if "＼" in f:
                acentos.append(len(moras(f.split("＼")[0])))
            else:
                acentos.append(len(ms))
        if frases[-1].endswith("￣"):
            ult = frases[-1].replace("￣", "")
            k = nucleo(ult)
            acentos[-1] = k
            ms = moras(ult)
            nueva = "".join(ms[:k]) + "＼" + "".join(ms[k:])
            cambios.append((ident, texto, frases[-1], nueva))
            corr[ident] = acentos
    json.dump(corr, open("audio/correcciones.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for c in cambios:
        print("\t".join(c))
    print(len(cambios), "oraciones cambiadas", file=sys.stderr)

main()
