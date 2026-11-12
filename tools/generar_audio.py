#!/usr/bin/env python3
"""
generar_audio.py — crea los MP3 de las frases con VOICEVOX (voz: No.7).

    python3 tools/generar_audio.py RUTA_VOICEVOX [--todo]

RUTA_VOICEVOX debe contener: 6.vvm, open_jtalk_dic_utf_8-1.11/ y
voicevox_onnxruntime-linux-x64-1.17.3/ (voicevox_core 0.16).
Sin --todo solo genera los archivos que faltan.

Salida:
    audio/A1/<id>.mp3        una por frase de database/A1
    audio/extra/<clave>.mp3  frases sueltas de index.html y como-se-lee.html
    audio/acentos.tsv        acento que ha calculado el motor, para revisarlo
Correcciones de acento: audio/correcciones.json  {"<id>": [núcleo de cada sintagma]}
  (0 = plano; n = la voz baja después de la mora n)
Crédito obligatorio en el sitio: «VOICEVOX:No.7»
"""
import glob, hashlib, json, os, subprocess, sys, tempfile

VOZ = 29          # No.7 — ノーマル
EXTRAS = ["寒い", "おいしい", "大丈夫です", "元気だよ", "はい", "じゃない", "元気", "水",
          "おばさん。おばあさん。", "来て。切手。", "寒いです", "新聞"]


def clave(texto):
    return hashlib.sha1(texto.encode("utf-8")).hexdigest()[:10]


def notacion(aq):
    out = []
    for ph in aq.accent_phrases:
        ms = [m.text for m in ph.moras]
        a = ph.accent
        out.append("".join(ms[:a]) + ("＼" if a < len(ms) else "￣") + "".join(ms[a:]))
    return "　".join(out)


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    vv, todo = sys.argv[1], "--todo" in sys.argv
    from voicevox_core.blocking import Onnxruntime, OpenJtalk, Synthesizer, VoiceModelFile
    ort = Onnxruntime.load_once(filename=glob.glob(f"{vv}/voicevox_onnxruntime-*/lib/libvoicevox_onnxruntime.so.*")[0])
    syn = Synthesizer(ort, OpenJtalk(f"{vv}/open_jtalk_dic_utf_8-1.11"))
    with VoiceModelFile.open(f"{vv}/6.vvm") as m:
        syn.load_voice_model(m)

    corr = {}
    if os.path.exists("audio/correcciones.json"):
        corr = json.load(open("audio/correcciones.json", encoding="utf-8"))

    trabajos = []
    for f in sorted(glob.glob("database/A1/*/*.json")):
        for e in json.load(open(f, encoding="utf-8"))["entradas"]:
            trabajos.append((e["id"], e["japonés"], f"audio/A1/{e['id']}.mp3"))
    for t in EXTRAS:
        trabajos.append((f"extra:{t}", t, f"audio/extra/{clave(t)}.mp3"))

    os.makedirs("audio/A1", exist_ok=True)
    os.makedirs("audio/extra", exist_ok=True)
    filas, hechos = [], 0
    for ident, texto, destino in trabajos:
        aq = syn.create_audio_query(texto, VOZ)
        if ident in corr:
            frases = aq.accent_phrases
            for ph, a in zip(frases, corr[ident]):
                ph.accent = a
            aq.accent_phrases = syn.replace_mora_data(frases, VOZ)
        filas.append(f"{ident}\t{texto}\t{notacion(aq)}\t{'corregido' if ident in corr else ''}")
        if os.path.exists(destino) and not todo and ident not in corr:
            continue
        wav = syn.synthesis(aq, VOZ)
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(wav)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", tmp.name,
                        "-ac", "1", "-b:a", "64k", destino], check=True)
        os.unlink(tmp.name)
        hechos += 1
    open("audio/acentos.tsv", "w", encoding="utf-8").write(
        "id\ttexto\tacento\tnota\n" + "\n".join(filas) + "\n")
    print(f"{hechos} archivos generados, {len(trabajos)} frases en total")


if __name__ == "__main__":
    main()
