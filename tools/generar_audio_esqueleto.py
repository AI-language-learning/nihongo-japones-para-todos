#!/usr/bin/env python3
"""Audio de la unidad 2 (database/esqueleto/unidad-2.json) con VOICEVOX:No.7.
Uso: python3 tools/generar_audio_esqueleto.py RUTA_VOICEVOX   → audio/esqueleto/<id>.mp3
Correcciones de acento opcionales: audio/correcciones.json (mismas claves por id)."""
import glob, json, os, subprocess, sys, tempfile
VOZ = 29

def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    vv = sys.argv[1]
    from voicevox_core.blocking import Onnxruntime, OpenJtalk, Synthesizer, VoiceModelFile
    ort = Onnxruntime.load_once(filename=glob.glob(f"{vv}/voicevox_onnxruntime-*/lib/libvoicevox_onnxruntime.so.*")[0])
    syn = Synthesizer(ort, OpenJtalk(f"{vv}/open_jtalk_dic_utf_8-1.11"))
    with VoiceModelFile.open(f"{vv}/6.vvm") as m:
        syn.load_voice_model(m)
    corr = json.load(open("audio/correcciones.json", encoding="utf-8")) if os.path.exists("audio/correcciones.json") else {}
    os.makedirs("audio/esqueleto", exist_ok=True)
    db = json.load(open("database/esqueleto/unidad-2.json", encoding="utf-8"))
    for e in db["entradas"]:
        aq = syn.create_audio_query(e["audio_text"], VOZ)
        if e["id"] in corr:
            for ph, a in zip(aq.accent_phrases, corr[e["id"]]):
                ph.accent = a
            aq.accent_phrases = syn.replace_mora_data(aq.accent_phrases, VOZ)
        nota = "　".join("".join(m.text for m in ph.moras[:ph.accent]) + ("＼" if ph.accent < len(ph.moras) else "￣") +
                        "".join(m.text for m in ph.moras[ph.accent:]) for ph in aq.accent_phrases)
        print(e["id"], e["japonés"], nota)
        wav = syn.synthesis(aq, VOZ)
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(wav)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", tmp.name, "-ac", "1", "-b:a", "64k",
                        f"audio/esqueleto/{e['id']}.mp3"], check=True)
        os.unlink(tmp.name)

if __name__ == "__main__":
    main()
