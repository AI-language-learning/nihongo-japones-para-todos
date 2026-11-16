#!/usr/bin/env python3
"""Genera una página HTML autónoma para que una persona hispanohablante revise los textos.
Uso: python3 tools/generar_revision.py SALIDA.html"""
import glob, html, json, re, sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
esc = html.escape


def md(t):
    t = esc(t or "")
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    return "".join(f"<p>{p.strip()}</p>" for p in t.split("\n\n") if p.strip())


def cargar():
    a = json.loads((RAIZ / "database/A1/aprendiz.json").read_text(encoding="utf-8"))
    notas = a.get("_notas_ejemplos", {})
    u2 = json.loads((RAIZ / "database/esqueleto/unidad-2.json").read_text(encoding="utf-8"))
    entradas = {}
    for f in sorted(glob.glob(str(RAIZ / "database/A1/*/*.json"))):
        d = json.loads(Path(f).read_text(encoding="utf-8"))
        for e in d["entradas"]:
            entradas.setdefault(e["conjunto"], []).append(e)
    bloques = []
    c = u2["conjuntos"][0]
    es = u2["entradas"]
    bloques.append(("Unidad 2", c["id"], {k: c.get(k, "") for k in ("título", "lead", "descubrimiento", "sistematización", "nota")},
                    [(e["id"], e["japonés"], e["romaji"], e["español"], e.get("notas_hispanohablante", "")) for e in es]))
    for cid, txt in a.items():
        if cid.startswith("_"):
            continue
        ej = [(e["id"], e["japonés"], e["romaji"], e["español"], notas.get(e["id"], "")) for e in entradas.get(cid, [])]
        bloques.append((cid.split("-")[1], cid, txt, ej))
    return bloques


CAMPOS = (("título", "Título"), ("lead", "Introducción"), ("descubrimiento", "Descubrimiento"),
          ("sistematización", "Explicación"), ("nota", "Nota para hispanohablantes"))

INTERFAZ = [
    ("ui/prueba-intro", "Escucha la frase y elige qué significa. No hay nota: es para que te oigas a ti mismo."),
    ("ui/hueco-intro", "Lee qué significa la frase y elige la palabra que falta. Después la oirás completa."),
    ("ui/ok", "¡Eso es!"), ("ui/mal", "Era otra. / Falta «da»."),
    ("ui/fin", "Has acertado 3 de 5. Escucha de nuevo las frases de arriba y repite."),
    ("ui/perfecto", "¡Perfecto!"),
    ("ui/kana", "Kana de hoy: las letras japonesas que aparecen en esta lección."),
]


def render():
    out, n = [], 0
    for unidad, cid, txt, ejs in cargar():
        out.append(f'<section class="conj" id="{cid}"><h2>{esc(cid)} <span>{esc(txt.get("título", ""))}</span></h2>')
        for k, et in CAMPOS:
            if not txt.get(k):
                continue
            n += 1
            out.append(item(f"{cid}/{k}", et, md(txt[k]), txt[k]))
        if ejs:
            out.append("<h3>Frases de ejemplo y sus notas</h3>")
        for eid, jp, ro, es, nota in ejs:
            n += 1
            cuerpo = f'<p class="jp"><span lang="ja">{esc(jp)}</span> · <b>{esc(ro)}</b></p><p>{esc(es)}</p>'
            if nota:
                cuerpo += f'<p class="nota">{esc(nota)}</p>'
            out.append(item(f"{eid}", eid, cuerpo, f"{ro} — {es}" + (f" — {nota}" if nota else ""), ejercicio=True))
        out.append("</section>")
    out.append('<section class="conj" id="ui"><h2>Textos de los ejercicios <span>interfaz</span></h2>')
    for iid, t in INTERFAZ:
        n += 1
        out.append(item(iid, iid, md(t), t))
    out.append("</section>")
    return "\n".join(out), n


def item(iid, etiqueta, cuerpo, original, ejercicio=False):
    extra = ('<label class="amb"><input type="checkbox" data-amb> En los ejercicios, otra opción también sería correcta</label>' if ejercicio else "")
    return (f'<article class="it" data-id="{esc(iid)}" data-orig="{esc(original, quote=True)}">'
            f'<div class="et">{esc(etiqueta)}</div><div class="cu">{cuerpo}</div>'
            f'<div class="bt"><button type="button" data-s="ok">✔ Está bien</button>'
            f'<button type="button" data-s="fix">✎ Corregir</button></div>'
            f'<textarea placeholder="Escribe aquí el texto corregido, tal como lo dirías tú (o un comentario si prefieres)" hidden></textarea>{extra}</article>')


PLANTILLA = r"""<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Revisión · Japonés para Todos</title>
<style>
:root{--bg:#fffdf9;--fg:#23303a;--mut:#667;--line:#e6dfd3;--card:#fff;--kaki:#d9481a;--mizu:#0f8b8d;--ok:#2b8a3e;--okbg:#ebfbee;--fixbg:#fff1e6}
@media (prefers-color-scheme:dark){:root{--bg:#1b1f23;--fg:#e8e6e1;--mut:#a9a9a0;--line:#3a3f44;--card:#242a2f;--okbg:#1f3a27;--fixbg:#47291b}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.6 system-ui,"Hiragino Sans",sans-serif;padding:0 max(16px,env(safe-area-inset-left)) 90px}
main{max-width:760px;margin:0 auto}
h1{font-size:1.5rem;margin:24px 0 4px}h2{font-size:1.15rem;margin:36px 0 10px;border-bottom:2px solid var(--kaki);padding-bottom:4px}
h2 span{font-weight:400;color:var(--mut);font-size:.95rem;margin-left:6px}h3{font-size:1rem;margin:20px 0 6px;color:var(--mizu)}
.intro{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:14px 18px}
.intro li{margin:4px 0}
.it{background:var(--card);border:2px solid var(--line);border-radius:14px;padding:12px 16px;margin:10px 0}
.it.ok{border-color:var(--ok);background:var(--okbg)}.it.fix{border-color:var(--kaki);background:var(--fixbg)}
.et{font-size:.8rem;color:var(--mut);text-transform:uppercase;letter-spacing:.06em}
.cu p{margin:.3em 0}.jp{font-size:1.05rem}.nota{color:var(--mut);font-size:.93rem}
.bt{display:flex;gap:8px;margin-top:8px;flex-wrap:wrap}
button{font:inherit;border:2px solid var(--line);background:var(--card);color:var(--fg);border-radius:999px;padding:5px 14px;cursor:pointer}
.it.ok button[data-s=ok],.it.fix button[data-s=fix]{border-color:currentColor;font-weight:700}
textarea{width:100%;min-height:70px;margin-top:8px;font:inherit;padding:8px;border:2px solid var(--line);border-radius:10px;background:var(--bg);color:var(--fg)}
.amb{display:block;margin-top:8px;font-size:.9rem;color:var(--mut)}
.barra{position:fixed;left:0;right:0;bottom:0;background:var(--card);border-top:1px solid var(--line);padding:8px max(16px,env(safe-area-inset-left));display:flex;gap:8px;align-items:center;flex-wrap:wrap;justify-content:center}
.barra b{margin-right:6px}.barra button{background:var(--kaki);color:#fff;border-color:var(--kaki)}.barra .sec{background:var(--card);color:var(--fg);border-color:var(--line)}
#com{width:100%;min-height:90px;margin:8px 0}
[hidden]{display:none!important}
</style></head><body><main>
<h1>Revisión de textos <small style="color:var(--mut);font-weight:400">Japonés para Todos</small></h1>
<div class="intro"><p>Gracias por ayudar. Esta página reúne los textos en español de la web (curso de japonés para hispanohablantes). Son borradores escritos con ayuda de IA y <b>todavía no los ha revisado ningún hablante nativo</b>.</p>
<p>En cada bloque pulsa <b>✔ Está bien</b> o <b>✎ Corregir</b>. Si corriges, escribe cómo lo dirías tú. Fíjate sobre todo en:</p>
<ol><li><b>Naturalidad:</b> ¿suena a español real o a traducción?</li><li><b>Tono:</b> se usa «tú» siempre y frases cortas.</li><li><b>Términos:</b> ¿alguna palabra técnica confunde?</li><li><b>Traducciones de las frases:</b> ¿es la que dirías en esa situación?</li><li><b>Ejercicios:</b> marca la casilla si en una frase otra opción también sería correcta.</li></ol>
<p>Tu trabajo se guarda solo en este navegador. Para seguir en <b>otro navegador u ordenador</b>, pulsa <b>Guardar progreso</b> (crea un archivo) y, allí, <b>Cargar progreso</b>. Para enviarme tus correcciones, pulsa <b>Copiar informe</b> o <b>Descargar</b>. No hace falta revisarlo todo de una vez.</p></div>
%%CUERPO%%
<h2>Comentario general</h2><textarea id="com" placeholder="Cualquier otra cosa que quieras decirnos"></textarea>
</main>
<div class="barra"><span><b id="cnt">0</b> de %%N%% revisados</span>
<button type="button" id="copiar">Copiar informe</button><button type="button" class="sec" id="desc">Descargar</button><button type="button" class="sec" id="gp">Guardar progreso</button><button type="button" class="sec" id="cp">Cargar progreso</button><input type="file" id="cpf" accept=".json,application/json" hidden><button type="button" class="sec" id="filt">Ver solo pendientes</button><span id="msg" aria-live="polite"></span></div>
<script>
(function(){
var KEY='jpt-revision-v1',est={};
function load(){try{est=JSON.parse(localStorage.getItem(KEY)||'{}')}catch(e){est={}}}
function save(){try{localStorage.setItem(KEY,JSON.stringify(est))}catch(e){}}
load();
var its=[].slice.call(document.querySelectorAll('.it')),com=document.getElementById('com');
com.value=est['_com']||'';com.addEventListener('input',function(){est['_com']=com.value;save()});
function pinta(it){var s=est[it.dataset.id]||{};it.classList.toggle('ok',s.s==='ok');it.classList.toggle('fix',s.s==='fix');
var t=it.querySelector('textarea');t.hidden=s.s!=='fix';t.value=s.t||'';var a=it.querySelector('[data-amb]');if(a)a.checked=!!s.a}
function cuenta(){var n=0;its.forEach(function(it){var s=est[it.dataset.id];if(s&&s.s)n++});document.getElementById('cnt').textContent=n}
its.forEach(function(it){pinta(it);var id=it.dataset.id;
it.querySelectorAll('button[data-s]').forEach(function(b){b.addEventListener('click',function(){var s=est[id]||{};s.s=(s.s===b.dataset.s)?'':b.dataset.s;est[id]=s;save();pinta(it);cuenta()})});
it.querySelector('textarea').addEventListener('input',function(e){var s=est[id]||{};s.t=e.target.value;est[id]=s;save()});
var a=it.querySelector('[data-amb]');if(a)a.addEventListener('change',function(){var s=est[id]||{};s.a=a.checked;est[id]=s;save()})});
cuenta();
function informe(){var L=['INFORME DE REVISIÓN — Japonés para Todos',''],ok=0;
its.forEach(function(it){var s=est[it.dataset.id]||{};
if(s.s==='fix'||s.a){L.push('['+(s.s==='fix'?'CORREGIR':'EJERCICIO')+'] '+it.dataset.id);L.push('  Original: '+it.dataset.orig.replace(/\n+/g,' / '));
if(s.t)L.push('  Propuesta: '+s.t);if(s.a)L.push('  Ejercicio: otra opción también es correcta');L.push('')}
else if(s.s==='ok')ok++});
L.push('Marcados como correctos: '+ok+' de '+its.length);if(est['_com'])L.push('','Comentario general: '+est['_com']);return L.join('\n')}
var msg=document.getElementById('msg');function di(t){msg.textContent=t;setTimeout(function(){msg.textContent=''},3000)}
document.getElementById('copiar').addEventListener('click',function(){var t=informe();
function viejo(){var x=document.createElement('textarea');x.value=t;document.body.appendChild(x);x.select();try{document.execCommand('copy');di('Copiado')}catch(e){di('No se pudo copiar: usa Descargar')}document.body.removeChild(x)}
if(navigator.clipboard&&navigator.clipboard.writeText)navigator.clipboard.writeText(t).then(function(){di('Copiado')},viejo);else viejo()});
document.getElementById('desc').addEventListener('click',function(){try{var b=new Blob([informe()],{type:'text/plain;charset=utf-8'}),a=document.createElement('a');a.href=URL.createObjectURL(b);a.download='revision-japones.txt';document.body.appendChild(a);a.click();document.body.removeChild(a);di('Descargado')}catch(e){di('No se pudo descargar: usa Copiar informe')}});
document.getElementById('gp').addEventListener('click',function(){try{var b=new Blob([JSON.stringify(est)],{type:'application/json'}),a=document.createElement('a');a.href=URL.createObjectURL(b);a.download='progreso-revision.json';document.body.appendChild(a);a.click();document.body.removeChild(a);di('Progreso guardado en un archivo')}catch(e){di('No se pudo guardar')}});
document.getElementById('cp').addEventListener('click',function(){document.getElementById('cpf').click()});
document.getElementById('cpf').addEventListener('change',function(e){var f=e.target.files[0];if(!f)return;var r=new FileReader();r.onload=function(){try{var o=JSON.parse(r.result);for(var k in o){est[k]=o[k]}save();if(est['_com'])com.value=est['_com'];its.forEach(pinta);cuenta();di('Progreso cargado')}catch(x){di('Archivo no válido')}};r.readAsText(f);e.target.value=''});
var solo=false;document.getElementById('filt').addEventListener('click',function(e){solo=!solo;e.target.textContent=solo?'Ver todos':'Ver solo pendientes';
its.forEach(function(it){var s=est[it.dataset.id];it.hidden=solo&&!!(s&&s.s)})});
})();
</script></body></html>"""

if __name__ == "__main__":
    cuerpo, n = render()
    Path(sys.argv[1]).write_text(PLANTILLA.replace("%%CUERPO%%", cuerpo).replace("%%N%%", str(n)), encoding="utf-8")
    print("items:", n)
