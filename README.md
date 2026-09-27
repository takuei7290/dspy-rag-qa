# dspy-rag-qa

自分で書いたMarkdown/テキストをもとに質問に答える、RAG(検索拡張生成)搭載のQAボットです。
DSPyの基本(Signature・Module・Retriever)から、評価・最適化(Optimizer)までを学ぶために作成しています。
LLMと埋め込みモデルはOllamaでローカル実行するため、APIキーや利用料金は不要です。

## 要件

### 必須の機能

| # | 機能 | コマンド(予定) | 内容 |
|---|---|---|---|
| 1 | インデックス作成 | `index` | `docs/` 配下のMarkdown/テキストをチャンクに分割し、埋め込みを計算して保存する |
| 2 | 質問応答 | `ask` | 質問を1つ受け取り、関連チャンクを検索して回答を返す。回答の根拠にしたファイル名(出典)も表示する |
| 3 | 対話モード | `chat` | 質問を続けて入力できるモード。`exit` で終了する(各質問は独立して扱い、会話履歴は持たない) |
| 4 | 評価 | `evaluate` | 自作の評価データ(質問と正解のセット)でボットを採点し、スコアを表示する |
| 5 | 最適化 | `optimize` | DSPyのOptimizerでボットを最適化して保存する。`ask` / `chat` で最適化済みのボットを読み込めるようにする |

### あとで作る機能

- 資料に答えがないときに「分かりません」と答える
- より強力なOptimizer(MIPROv2・GEPAなど)での最適化と、結果の比較(GEPAでは `gemma3:12b` を振り返り役にする)
- 大きいモデル(`gemma3:12b`)を教師役にした最適化
- 検索の設定を変えたときのスコア比較
  - チャンク分割の方法・検索件数
  - ハイブリッド検索(BM25 + 埋め込み)と、埋め込み検索のみ
  - 埋め込みの次元(768 / 512 / 256 / 128)
  - 埋め込みの前置き(タスクプロンプト)の有無と種類
- ツールを使うエージェント化(`dspy.ReAct`)
- LINEボット化(LINE Messaging API + Webhookサーバーで、LINEから質問できるようにする)

### 対象外(今回はやらない)

- PDF・Webページなど、Markdown/テキスト以外の取り込み
- 外部のベクトルデータベース(Chroma・Qdrant など)の利用
- クラウドLLM(OpenAI・Anthropic など)への対応

## DSPyで学ぶこと

各機能で、DSPyの次の要素を学びます。

| 機能 | 使うDSPyの要素 | 学ぶこと |
|---|---|---|
| 共通 | `dspy.LM` / `dspy.configure` | DSPyからOllamaのモデルを呼び出す設定 |
| インデックス作成 | `dspy.Embedder` / `dspy.retrievers.Embeddings` | 埋め込みによる類似検索の仕組み |
| 質問応答 | `dspy.Signature` / `dspy.ChainOfThought` / `dspy.Module` | プロンプトを「入力と出力の宣言」として書く考え方と、検索→回答を1つのモジュールにまとめる方法 |
| 評価 | `dspy.Example` / メトリクス関数 / `dspy.Evaluate` | 「良い回答」を数値で測る方法 |
| 最適化 | `BootstrapFewShot` などのOptimizer / `save` / `load` | プロンプトを手で直す代わりに、データとメトリクスから自動で改善する方法 |

## 構成

| 役割 | 使うもの |
|---|---|
| 回答用LLM | Ollama `gemma3:4b`(軽くて速いので、呼び出し回数が多い最適化にも使いやすい) |
| 教師・採点用LLM | Ollama `gemma3:12b`(最適化のお手本作り、LLMによる採点、4bとのスコア比較に使う。重いので回答用には使わない) |
| 埋め込みモデル | Ollama `embeddinggemma`(日本語を含む多言語に対応) |
| 検索 | `dspy.retrievers.Embeddings`(小規模なのでベクトルDBは使わない) |
| 知識のもと | `docs/` 配下の自作Markdown/テキスト(過去プロジェクトのREADME・振り返り・学習メモなど) |
| 評価データ | `data/` 配下のJSONL(質問と正解のペアを20〜30問、自作する) |
| インターフェース | CLI(`argparse` のサブコマンド) |

### 評価の方針

1. まずは「回答に正解のキーワードが含まれているか」で判定する、自作のシンプルなメトリクスから始める
2. 慣れてきたら、LLMに意味の近さを判定させるメトリクス(`dspy.evaluate.SemanticF1` など)も試す。採点には回答用より大きい `gemma3:12b` を使う
3. 最適化の前後で同じ評価データのスコアを比べ、効果を数値で確認する(評価データは学習用と検証用に分ける)

## 必要環境

- Python 3.12
- [uv](https://docs.astral.sh/uv/)(仮想環境とパッケージの管理)
- [Ollama](https://ollama.com/)(ローカルでLLMを動かす)
- 動作確認環境: Windows 11 / RAM 16GB / GeForce GTX 1660 SUPER

## セットアップ

```bash
git clone https://github.com/takuei7290/dspy-rag-qa.git
cd dspy-rag-qa

# 仮想環境の作成とパッケージのインストール(uv.lock どおりに入る)
uv sync

# 使うモデルを取得(Ollama が起動している状態で)
ollama pull gemma3:4b
ollama pull gemma3:12b
ollama pull embeddinggemma
```

## 使い方(予定)

```bash
# docs/ の資料からインデックスを作る
uv run dspy-rag-qa index

# 1問だけ質問する
uv run dspy-rag-qa ask "python-todo-cli ではタスクをどこに保存している?"

# 対話モード
uv run dspy-rag-qa chat

# 評価データで採点する
uv run dspy-rag-qa evaluate

# 最適化して保存する
uv run dspy-rag-qa optimize
```

## テスト・開発

```bash
# テストを実行(Ollama は使わず、LLMはダミーに差し替えてテストする)
uv run pytest

# lint / フォーマットチェック
uv run ruff check .
uv run ruff format --check .
```
