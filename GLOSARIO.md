# GLOSARIO — 用語集と表記の基準（第2版 2026-11-11）

このサイトで使う用語と表記の基準です。新しいページを書くとき、AIに下書きを頼むとき、
協力者に確認を頼むときは、この表を基準にします。
出典は `gramatica/terminologia.html` です。**【未決】** は著者の判断待ちです。

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

## 2. 2026-11-11 に決まったこと

| 項目 | 決定 |
|---|---|
| 学習順序 | 機能別・4品詞並行（データベースのブロック0〜7の順） |
| 入門編 | 10単元：音、枠組み、核、否定、完了、否定完了、丁寧、補語、話題、文末表現 |
| 3月の目標 | 全10単元を新表示で公開。前半5単元は文章も書き直した完全版 |
| 動詞の分類 | verbo tipo -u / tipo -ru。初出で「他の教材では Grupo 1 / Grupo 2」と1回注記 |
| 対象 | スペインを基本にし、中南米との違いは説明で補う |
| 学習者向けページの用語 | A・Na・N・V の記号、núcleo、posposición などは使う。初出のたびに説明する |
| レッスンの題とリード文 | 学習者向けに付け替える（内容は変えない） |
| 文法ガイド | 「Para profes y curiosos」の入口に移す |
| デザイン | 案A（白地、柿色と青緑、丸みのある書体）。写真・イラストを入れる |

## 3. 未決の用語

| 項目 | 候補と現状 |
|---|---|
| ます **【未決】** | 用語表は honorativo。基礎文書と文法リファレンスは marcador de cortesía |
| 名詞 **【未決】** | 用語表は nominal（N）。文法リファレンスに nombre、レッスンとデータベースに sustantivo |
| は **【未決】** | tópico が主。tema も併用されている |
| が の説明 **【未決】** | ガイドは「述語が指す要素」「同定」。レッスンとデータベースは foco = información nueva |
| 文体 **【未決】** | 文法リファレンスは estilo ordinario / estilo cortés。データベースは forma llana、registro llano、informal |
| 直訳（lit.）**【未決】** | 修正メモの方針は日本語の語順のまま示す形：«En cuanto a ella, la cabeza, buena» |

## 4. 説明の方針（確定）

- 「主語」は統語的主語（concordancia のある sujeto sintáctico）に限って論じる。
- 言語化しないことを「省略（omisión）」と呼ばない。「場面に応じた発話の設計」として説明する。
- 普通体を丁寧体より先に扱う。
- 状況 → 問い → 発見 → 体系化の順に示す。
- 学習者向けページは tú で書く。1文は20語まで、1段落は3文まで。日本語の一言と場面から始める。
- 「〜ではない」ではなく肯定で書く。他の教え方への批判は書かない。

## 5. 表記（確定）：ヘボン骨格＋合図

画面ではアルファベットを主にし、かな・漢字をその下に添える。単元が進むにつれて主従を入れ替える。
実装は `generate_lessons.py` の `lectura()`、`lectura_html()`、`kana_a_lectura()`。学習者向けの説明は `como-se-lee.html`。

| 項目 | 規則 | 例 |
|---|---|---|
| 綴り | ヘボン式 | shi、chi、tsu、fu、ji |
| 色の印を付ける文字 | h、j、z、e・i の前の g | **h**ai、**j**a nai、**g**enki、mi**z**u |
| 長音 | 母音を2つ書く。「えい」は ei | Tookyoo、oishii、sensei |
| 促音 | 子音を2つ書く（ち の前は tch） | datta、kitte |
| 弱く読む母音 | 薄い色で表示。綴りは省かない。現在は です・ます の u のみ | desu、masu |
| ん | n。b・p・m の前では m。母音と y の前では n- | shimbun、kin-en |
| は・へ・を | wa、e、o | mizu o nomu |
| 分かち書き | 後置詞は離す。述語機能表現は核に続ける。だ・です は離す | tabenakatta、ame da、samui desu |
| 大文字 | 文頭と固有名詞 | Tookyoo ni iku. |
| アクセント記号 | 使わない。高低アクセントは表記せず、説明と音声で扱う | — |
| 「こう聞こえる」 | 最初の2ブロックだけ、印のある文にスペイン語式の綴りを添える | Suena como «Guenki dya nai» |

その他：

| 項目 | 基準 |
|---|---|
| フォント | 学習者向けページは Nunito と M PLUS Rounded 1c |
| 表の例文訳 | 三人称単数に統一 |
| 引用符 | スペイン語本文は « »、日本語は「 」 |
| 配色 | 白地、柿色（強調と音声ボタン）、青緑、黄。黒背景は使わない |

## 6. 作業の決まり

- `lecciones/` は自動生成。直すときは `database/` を直して `python3 generate_lessons.py` を実行する。
- 生成時に、各例文のローマ字とふりがなが一致するかを自動で照合する。不一致は一覧で表示される。
- 公開前に `python3 tools/check_links.py .` を実行し、リンク切れ0を確認する。
- 例文は著者が自然さを確認したら、データベースの `calidad.validado` を `true` にする。
