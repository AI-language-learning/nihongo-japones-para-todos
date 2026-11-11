/* leccion.js — audio (Web Speech API) y selector de escritura */
(function () {
  var synth = window.speechSynthesis;
  function vozJa() {
    if (!synth) return null;
    return synth.getVoices().filter(function (v) { return v.lang && v.lang.indexOf('ja') === 0; })[0] || null;
  }
  document.querySelectorAll('.oir').forEach(function (btn) {
    var rotulo = btn.textContent;
    btn.addEventListener('click', function () {
      if (!synth) { btn.textContent = 'Tu navegador no tiene voz'; return; }
      synth.cancel();
      var u = new SpeechSynthesisUtterance(btn.dataset.text);
      u.lang = 'ja-JP'; u.rate = 0.85;
      var v = vozJa(); if (v) u.voice = v;
      btn.classList.add('sonando');
      u.onend = u.onerror = function () { btn.classList.remove('sonando'); btn.textContent = rotulo; };
      synth.speak(u);
    });
  });
  if (synth && synth.onvoiceschanged !== undefined) synth.onvoiceschanged = function () {};

  var botones = document.querySelectorAll('.modo button');
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
