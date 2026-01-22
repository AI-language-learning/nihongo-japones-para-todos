/* ============================================
   Web Speech API — 音声合成機能
   nihongo-japones-para-todos
   ============================================ */

(function() {
    'use strict';

    // --------------------------------------------
    // 設定
    // --------------------------------------------
    const CONFIG = {
        lang: 'ja-JP',
        rate: 0.9,      // 速度 (0.1 - 10)
        pitch: 1.0,     // ピッチ (0 - 2)
        volume: 1.0     // 音量 (0 - 1)
    };

    // --------------------------------------------
    // 音声合成が利用可能かチェック
    // --------------------------------------------
    function isSupported() {
        return 'speechSynthesis' in window;
    }

    // --------------------------------------------
    // 日本語の音声を取得
    // --------------------------------------------
    function getJapaneseVoice() {
        const voices = speechSynthesis.getVoices();
        
        // 優先順位: ja-JP > ja で始まるもの
        let voice = voices.find(v => v.lang === 'ja-JP');
        if (!voice) {
            voice = voices.find(v => v.lang.startsWith('ja'));
        }
        
        return voice;
    }

    // --------------------------------------------
    // テキストを読み上げる
    // --------------------------------------------
    function speak(text, options = {}) {
        if (!isSupported()) {
            console.warn('Este navegador no soporta Web Speech API.');
            alert('Tu navegador no soporta la síntesis de voz. Prueba con Chrome o Edge.');
            return;
        }

        // 現在の読み上げを停止
        speechSynthesis.cancel();

        const utterance = new SpeechSynthesisUtterance(text);
        
        // 設定を適用
        utterance.lang = options.lang || CONFIG.lang;
        utterance.rate = options.rate || CONFIG.rate;
        utterance.pitch = options.pitch || CONFIG.pitch;
        utterance.volume = options.volume || CONFIG.volume;

        // 日本語音声を設定
        const jaVoice = getJapaneseVoice();
        if (jaVoice) {
            utterance.voice = jaVoice;
        }

        // イベントハンドラ
        utterance.onstart = function() {
            document.querySelectorAll('.speak-btn').forEach(btn => {
                btn.classList.remove('speaking');
            });
            if (options.button) {
                options.button.classList.add('speaking');
            }
        };

        utterance.onend = function() {
            if (options.button) {
                options.button.classList.remove('speaking');
            }
            if (options.onEnd) {
                options.onEnd();
            }
        };

        utterance.onerror = function(event) {
            console.error('Speech error:', event.error);
            if (options.button) {
                options.button.classList.remove('speaking');
            }
        };

        // 読み上げ開始
        speechSynthesis.speak(utterance);
    }

    // --------------------------------------------
    // 読み上げを停止
    // --------------------------------------------
    function stop() {
        if (isSupported()) {
            speechSynthesis.cancel();
            document.querySelectorAll('.speak-btn').forEach(btn => {
                btn.classList.remove('speaking');
            });
        }
    }

    // --------------------------------------------
    // 速度を設定
    // --------------------------------------------
    function setRate(rate) {
        CONFIG.rate = Math.max(0.1, Math.min(10, rate));
    }

    // --------------------------------------------
    // ボタンの初期化
    // --------------------------------------------
    function initButtons() {
        document.querySelectorAll('.speak-btn').forEach(btn => {
            btn.addEventListener('click', function(e) {
                e.preventDefault();
                const text = this.dataset.text || this.getAttribute('aria-label');
                if (text) {
                    speak(text, { button: this });
                }
            });
        });
    }

    // --------------------------------------------
    // 音声リストの読み込み待ち
    // --------------------------------------------
    function init() {
        if (!isSupported()) {
            console.warn('Web Speech API no disponible');
            return;
        }

        // Chrome では voiceschanged イベントを待つ必要がある
        if (speechSynthesis.getVoices().length === 0) {
            speechSynthesis.addEventListener('voiceschanged', function() {
                initButtons();
            }, { once: true });
        } else {
            initButtons();
        }
    }

    // --------------------------------------------
    // DOMContentLoaded で初期化
    // --------------------------------------------
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // --------------------------------------------
    // グローバルに公開
    // --------------------------------------------
    window.NihongoSpeech = {
        speak: speak,
        stop: stop,
        setRate: setRate,
        isSupported: isSupported
    };

})();
