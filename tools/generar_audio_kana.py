#!/usr/bin/env python3
"""Audio de cada kana (hiragana; el katakana usa el mismo archivo) con VOICEVOX:No.7.
Uso: python3 tools/generar_audio_kana.py RUTA_VOICEVOX
Escribe audio/kana/<codepoint hex del hiragana>.mp3"""
import glob, os, subprocess, sys, tempfile

VOZ = 29
LECTURA = {"は": "ハ", "へ": "ヘ",   # solos, la voz los leería como partículas (wa, e)
           "ぢゅ": "ジュ", "ぢょ": "ジョ"}   # si no, la voz los lee en dos moras (ji + yu)
FILAS = ["あいうえお", "かきくけこ", "さしすせそ", "たちつてと", "なにぬねの", "はひふへほ", "まみむめも",
         "や　ゆ　よ", "らりるれろ", "わ　　　を", "ん", "がぎぐげご", "ざじずぜぞ", "だぢづでど", "ばびぶべぼ", "ぱぴぷぺぽ"]
AJUSTE = {"か": (0.075, 5.85)}   # (largo de la consonante, tono); elegido de oído
YOON = ["き", "し", "ち", "に", "ひ", "み", "り", "ぎ", "じ", "ぢ", "び", "ぴ"]


def unidades():
    u = [c for f in FILAS for c in f if c != "　"]
    u += [b + s for b in YOON for s in "ゃゅょ"]
    return u


def nombre(u):
    return "-".join(f"{ord(c):x}" for c in u)


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    vv = sys.argv[1]
    from voicevox_core.blocking import Onnxruntime, OpenJtalk, Synthesizer, VoiceModelFile
    ort = Onnxruntime.load_once(filename=glob.glob(f"{vv}/voicevox_onnxruntime-*/lib/libvoicevox_onnxruntime.so.*")[0])
    syn = Synthesizer(ort, OpenJtalk(f"{vv}/open_jtalk_dic_utf_8-1.11"))
    with VoiceModelFile.open(f"{vv}/6.vvm") as m:
        syn.load_voice_model(m)
    os.makedirs("audio/kana", exist_ok=True)
    n = 0
    for u in unidades():
        destino = f"audio/kana/{nombre(u)}.mp3"
        aq = syn.create_audio_query("カ" if u in AJUSTE else LECTURA.get(u, u), VOZ)
        if u in AJUSTE:   # か: con los valores por defecto casi no se oye la vocal
            m0 = aq.accent_phrases[0].moras[0]
            m0.consonant_length, m0.pitch = AJUSTE[u]
        wav = syn.synthesis(aq, VOZ)
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(wav)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", tmp.name, "-ac", "1", "-b:a", "64k", destino], check=True)
        os.unlink(tmp.name)
        n += 1
    print(n, "archivos")


if __name__ == "__main__":
    main()
