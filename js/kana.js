// Tabla de kana: reproduce el audio (VOICEVOX:No.7); si falta, usa la voz del navegador.
(function () {
  var actual = null;
  function hablar(texto) {
    try {
      var u = new SpeechSynthesisUtterance(texto);
      u.lang = 'ja-JP'; u.rate = 0.8;
      speechSynthesis.cancel(); speechSynthesis.speak(u);
    } catch (e) {}
  }
  document.querySelectorAll('.kc').forEach(function (b) {
    b.addEventListener('click', function () {
      if (actual) { actual.pause(); }
      var a = new Audio(b.dataset.audio);
      actual = a;
      a.addEventListener('error', function () { hablar(b.dataset.text); });
      a.play().catch(function () { hablar(b.dataset.text); });
    });
  });
  var modo = 'hira';
  try { modo = localStorage.getItem('jpt-kana') || 'hira'; } catch (e) {}
  function aplicar(m) {
    document.body.classList.toggle('ver-kata', m === 'kata');
    document.querySelectorAll('[data-kana]').forEach(function (x) {
      x.classList.toggle('activo', x.dataset.kana === m);
    });
    try { localStorage.setItem('jpt-kana', m); } catch (e) {}
  }
  document.querySelectorAll('[data-kana]').forEach(function (x) {
    x.addEventListener('click', function () { aplicar(x.dataset.kana); });
  });
  aplicar(modo);
})();
