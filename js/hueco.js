// hueco.js — «Completa la frase»: elegir la partícula o la forma que falta.
// Las opciones nunca incluyen un par que también sería correcto (wa/ga, da/desu).
(function () {
  var datosEl = document.getElementById('h-datos');
  if (!datosEl) return;
  var items = JSON.parse(datosEl.textContent);
  var $ = function (id) { return document.getElementById(id); };
  var caja = $('h-caja'), fin = $('h-fin'), cuenta = $('h-cuenta'), es = $('h-es'),
      fr = $('h-fr'), ops = $('h-ops'), res = $('h-res'), sig = $('h-sig'),
      ini = $('h-ini'), nota = $('h-nota'), otra = $('h-otra');
  var POOL = { p: ['wa', 'ga', 'o', 'ni', 'de', 'kara', 'made'], f: ['da', 'desu', 'datta', 'nai', 'nakatta'],
    sa: ['kunai', 'katta', 'kunakatta', 'i'], sv: ['masu', 'nai', 'nakatta', 'ta', 'da'] };
  var PAR = { wa: 'ga', ga: 'wa', da: 'desu', desu: 'da' };
  var PAR_V = { ta: 'da', da: 'ta' };
  function par(it) { return it.g === 'sv' ? PAR_V[it.ok] : (it.g === 'p' || it.g === 'f') ? PAR[it.ok] : null; }
  function rot(it, o) { return (it.g === 'sa' || it.g === 'sv') ? '-' + o : o; }
  var orden, i, aciertos, respondida, audio = null;

  function barajar(a) {
    a = a.slice();
    for (var k = a.length - 1; k > 0; k--) {
      var j = Math.floor(Math.random() * (k + 1)), t = a[k]; a[k] = a[j]; a[j] = t;
    }
    return a;
  }
  function hablar(it) {
    try {
      var u = new SpeechSynthesisUtterance(it.t);
      u.lang = 'ja-JP'; u.rate = 0.85;
      speechSynthesis.cancel(); speechSynthesis.speak(u);
    } catch (e) {}
  }
  function sonar(it) {
    if (audio) { audio.pause(); audio = null; }
    if (!it.a) { hablar(it); return; }
    var a = new Audio(it.a); audio = a;
    a.onerror = function () { hablar(it); };
    var p = a.play(); if (p && p.catch) p.catch(function () { hablar(it); });
  }
  function pregunta() {
    var it = orden[i];
    respondida = false;
    cuenta.textContent = 'Frase ' + (i + 1) + ' de ' + orden.length;
    es.textContent = it.e;
    fr.innerHTML = it.p + '<span class="p-hueco">＿＿</span>' + it.q;
    res.innerHTML = ''; sig.hidden = true;
    var malos = POOL[it.g].filter(function (x) { return x !== it.ok && x !== par(it); });
    var opciones = barajar(barajar(malos).slice(0, 3).concat([it.ok]));
    ops.innerHTML = '';
    opciones.forEach(function (o) {
      var b = document.createElement('button');
      b.type = 'button'; b.className = 'p-op h-op'; b.textContent = rot(it, o);
      b.addEventListener('click', function () { elegir(b, o === it.ok); });
      ops.appendChild(b);
    });
  }
  function elegir(b, ok) {
    if (respondida) return;
    respondida = true;
    var it = orden[i];
    if (ok) aciertos++;
    Array.prototype.forEach.call(ops.children, function (x) {
      x.disabled = true;
      if (x.textContent === rot(it, it.ok)) x.classList.add('ok');
    });
    if (!ok) b.classList.add('mal');
    fr.innerHTML = it.r;
    res.innerHTML = '<p class="p-v ' + (ok ? 'ok' : 'mal') + '">' + (ok ? '¡Eso es!' : 'Falta «' + rot(it, it.ok) + '».') +
      '</p><p class="p-fr"><span lang="ja">' + it.k + '</span> — ' + it.e + '</p>';
    sonar(it);
    sig.textContent = (i + 1 < orden.length) ? 'Siguiente →' : 'Ver resultado';
    sig.hidden = false; sig.focus();
  }
  function empezar() {
    orden = barajar(items); i = 0; aciertos = 0;
    ini.hidden = true; fin.hidden = true; caja.hidden = false;
    pregunta();
  }
  sig.addEventListener('click', function () {
    i++;
    if (i < orden.length) { pregunta(); return; }
    caja.hidden = true; fin.hidden = false;
    nota.textContent = 'Has acertado ' + aciertos + ' de ' + orden.length + '. ' +
      (aciertos === orden.length ? '¡Perfecto!' : 'Vuelve a mirar las frases de arriba y prueba otra vez.');
  });
  ini.addEventListener('click', empezar);
  otra.addEventListener('click', empezar);
})();
