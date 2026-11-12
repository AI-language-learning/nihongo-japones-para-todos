// practica.js — «Ponte a prueba»: escuchar una frase y elegir su significado.
// Sin notas guardadas. Usa el mismo audio (VOICEVOX:No.7) y, si falta, la voz del navegador.
(function () {
  var datosEl = document.getElementById('p-datos');
  if (!datosEl) return;
  var items = JSON.parse(datosEl.textContent);
  var caja = document.getElementById('p-caja'), fin = document.getElementById('p-fin');
  var cuenta = document.getElementById('p-cuenta'), ops = document.getElementById('p-ops');
  var res = document.getElementById('p-res'), sig = document.getElementById('p-sig');
  var ini = document.getElementById('p-ini'), oir = document.getElementById('p-oir');
  var nota = document.getElementById('p-nota'), otra = document.getElementById('p-otra');
  var orden, i, aciertos, audio = null, respondida;

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
  function sonar() {
    var it = orden[i];
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
    res.innerHTML = ''; sig.hidden = true;
    var otras = barajar(items.filter(function (x) { return x !== it; })).slice(0, 3);
    var opciones = barajar(otras.concat([it]));
    ops.innerHTML = '';
    opciones.forEach(function (o) {
      var b = document.createElement('button');
      b.type = 'button'; b.className = 'p-op'; b.textContent = o.e;
      b.addEventListener('click', function () { elegir(b, o === it); });
      ops.appendChild(b);
    });
    sonar();
  }
  function elegir(b, ok) {
    if (respondida) return;
    respondida = true;
    var it = orden[i];
    if (ok) aciertos++;
    Array.prototype.forEach.call(ops.children, function (x) {
      x.disabled = true;
      if (x.textContent === it.e) x.classList.add('ok');
    });
    if (!ok) b.classList.add('mal');
    res.innerHTML = '<p class="p-v ' + (ok ? 'ok' : 'mal') + '">' + (ok ? '¡Eso es!' : 'Era otra.') +
      '</p><p class="p-fr"><span class="p-ro" lang="ja-Latn">' + it.r + '</span> <span lang="ja">' + it.k + '</span> — ' + it.e + '</p>';
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
      (aciertos === orden.length ? '¡Perfecto!' : 'Escucha de nuevo las frases de arriba y repite.');
  });
  oir.addEventListener('click', sonar);
  ini.addEventListener('click', empezar);
  otra.addEventListener('click', empezar);
})();
