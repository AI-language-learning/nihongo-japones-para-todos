# 日本語 — Japonés para Todos

**スペイン語話者のための日本語学習サイト**  
Sitio de aprendizaje de japonés para hispanohablantes

## 概要 | Descripción

Este sitio ofrece un enfoque único para aprender japonés, basado en:

- **Sistema gramatical unificado** que describe el japonés desde su lógica interna
- **Enfoque inductivo**: situación → descubrimiento → comprensión → uso
- **El predicado como centro** de la oración japonesa
- **Sistema de complementos** (no "sujeto/objeto" del español)

## 構成 | Estructura

```
nihongo-japones-para-todos/
├── index.html              # Página principal
├── css/                    # common.css (sitio) · base.css (aprender, kana)
├── js/speech.js            # Web Speech API (audio)
├── gramatica/              # Guías, terminología y documento fundamental
├── aprender/               # Mapa de etapas
├── lecciones/              # Lecciones — GENERADAS, no editar a mano
├── database/A1/            # Fuente de las lecciones (JSON por bloque)
├── generate_lessons.py     # database/ → lecciones/
└── herramientas/           # Tablas de kana
```

## 技術 | Tecnología

- HTML + CSS + JavaScript (vanilla)
- Web Speech API para síntesis de voz
- Alojado en GitHub Pages
- Sin dependencias externas

## ライセンス | Licencia

[Por definir]

## 開発 | Desarrollo

Proyecto en desarrollo activo.
