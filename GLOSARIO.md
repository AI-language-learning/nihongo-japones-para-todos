# GLOSARIO — 用語集と表記の基準（初版 2026-11-11）

このサイトで使う用語と表記の基準です。新しいページを書くとき、AIに下書きを頼むとき、
協力者に確認を頼むときは、この表を基準にします。
出典は `gramatica/terminologia.html` です。**【未決】** は著者の判断待ちで、決まるまでは「現状」の欄の揺れが残ります。

## 1. 基本用語（確定）

| 日本語 | スペイン語（採用） | 記号 | 使わない語 |
|---|---|---|---|
| 述部 | predicado | — | — |
| 述部の核 | núcleo del predicado | — | — |
| 述語機能表現 | expresiones funcionales del predicado | — | verbo auxiliar, auxiliares |
| 動詞 | verbo | V | — |
| 来る動詞 / する動詞 | verbo kuru / verbo suru | Vkuru / Vsuru | — |
| 形容詞 | adjetivo | A | adjetivo -i |
| 形容名詞 | nominal adjetival | Na | adjetivo -na, adjetivo verbal |
| 宣言詞「だ」 | declarativo | Da | cópula, verbo ser |
| 宣言詞丁寧形「です」 | forma cortés del declarativo | Desu | — |
| 完了詞「た（だ）」 | perfectivo | Ta | pasado, pretérito（対比の説明を除く） |
| 否定形容詞「ない」 | negativo（adjetivo negativo） | — | partícula negativa |
| 意志詞「う・よう」 | volitivo | — | — |
| 仮定詞「ば」 | supositivo | — | — |
| 後置詞 | posposición | — | partícula, partícula de caso |
| 補語 | complemento | — | sujeto, objeto directo / indirecto |
| 主格補語（〜が） | complemento nominativo | — | sujeto |
| 文末表現 | expresiones finales | — | partícula final |
| 話題主 | agente del tópico | — | sujeto |
| 副詞 / 接続詞 | adverbio / conjunción | — | — |

## 2. 未決の用語

| 項目 | 候補と現状 |
|---|---|
| 動詞の分類 **【未決】** | 用語表は verbo tipo -u / tipo -ru（V-u / V-ru）。レッスンとデータベースは Grupo 1 / Grupo 2 |
| ます **【未決】** | 用語表は honorativo。基礎文書と文法リファレンスは marcador de cortesía |
| 名詞 **【未決】** | 用語表は nominal（N）。文法リファレンスに nombre、レッスンとデータベースに sustantivo |
| は **【未決】** | tópico が主。tema も併用されている |
| が の説明 **【未決】** | ガイドは「述語が指す要素」「同定」。レッスンとデータベースは foco = información nueva |
| 文体 **【未決】** | 文法リファレンスは estilo ordinario / estilo cortés。データベースは forma llana、registro llano、informal |

## 3. 説明の方針（確定）

- 「主語」は統語的主語（concordancia のある sujeto sintáctico）に限って論じる。
- 言語化しないことを「省略（omisión）」と呼ばない。「場面に応じた発話の設計」として説明する。
- 普通体を丁寧体より先に扱う。
- 状況 → 問い → 発見 → 体系化の順に示す。

## 4. 表記

| 項目 | 基準 |
|---|---|
| ローマ字の長音 **【未決】** | 方針は母音の後ろに「:」（do:shi）。公開ページは長音符号（dōshi）。レッスン画面はローマ字を表示せず、ふりがなのみ |
| フォント | 本文はゴシック系。ローマ字はローマン系イタリック。スペイン語訳は本文と別のゴシック系 |
| 表の例文訳 | 三人称単数に統一 |
| 直訳（lit.）**【未決】** | 修正メモの方針は日本語の語順のまま示す形：«En cuanto a ella, la cabeza, buena» |
| 引用符 | スペイン語本文は « »、日本語は「 」 |
| 配色 | 落ち着いた色。黒背景は使わない |

## 5. 作業の決まり

- `lecciones/` は自動生成。直すときは `database/` を直して `python3 generate_lessons.py` を実行する。
- 公開前に `python3 tools/check_links.py .` を実行し、リンク切れ0を確認する。
- 例文は著者が自然さを確認したら、データベースの `calidad.validado` を `true` にする。
