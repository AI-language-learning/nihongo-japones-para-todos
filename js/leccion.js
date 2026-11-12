/* leccion.js — audio y selector de escritura
   Cada botón .oir reproduce su archivo (data-audio). Si no hay archivo o
   falla, usa la voz del navegador (Web Speech API) con data-text. */
(function () {
  var synth = window.speechSynthesis;
  var actual = null, boton = null;

  function vozJa() {
    if (!synth) return null;
    return synth.getVoices().filter(function (v) { return v.lang && v.lang.indexOf('ja') === 0; })[0] || null;
  }
  function parar() {
    if (actual) { actual.pause(); actual = null; }
    if (synth) synth.cancel();
    if (boton) boton.classList.remove('sonando');
  }
  function conNavegador(btn) {
    if (!synth) { btn.classList.remove('sonando'); return; }
    var u = new SpeechSynthesisUtterance(btn.dataset.text);
    u.lang = 'ja-JP'; u.rate = 0.85;
    var v = vozJa(); if (v) u.voice = v;
    u.onend = u.onerror = function () { btn.classList.remove('sonando'); };
    synth.speak(u);
  }
  document.querySelectorAll('.oir').forEach(function (btn) {
    btn.addEventListener('click', function () {
      parar();
      boton = btn; btn.classList.add('sonando');
      if (!btn.dataset.audio) { conNavegador(btn); return; }
      var a = new Audio(btn.dataset.audio);
      actual = a;
      a.onended = function () { btn.classList.remove('sonando'); };
      a.onerror = function () { if (actual === a) { actual = null; conNavegador(btn); } };
      var p = a.play();
      if (p && p.catch) p.catch(function () { if (actual === a) { actual = null; conNavegador(btn); } });
    });
  });
  if (synth && synth.onvoiceschanged !== undefined) synth.onvoiceschanged = function () {};

  var tog = document.getElementById('ro-toggle');
  if (tog) {
    tog.addEventListener('click', function () {
      var v = document.body.classList.toggle('ro-visible');
      tog.textContent = v ? 'Ocultar alfabeto' : 'Mostrar alfabeto';
    });
  }

  var botones = document.querySelectorAll('.modo button[data-modo]');
  if (!botones.length) return;
  function poner(modo, guardar) {
    document.body.classList.remove('modo-alfa', 'modo-kana', 'modo-kanji');
    document.body.classList.add('modo-' + modo);
    botones.forEach(function (b) { b.setAttribute('aria-pressed', b.dataset.modo === modo ? 'true' : 'false'); });
    if (guardar) { try { localStorage.setItem('jpt-modo', modo); } catch (e) {} }
  }
  var inicial = document.body.dataset.modoInicial || 'alfa';
  try { inicial = localStorage.getItem('jpt-modo') || inicial; } catch (e) {}
  if (['alfa', 'kana', 'kanji'].indexOf(inicial) < 0) inicial = 'alfa';
  poner(inicial, false);
  botones.forEach(function (b) { b.addEventListener('click', function () { poner(b.dataset.modo, true); }); });
})();
