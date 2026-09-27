# CLAUDE.md

このプロジェクトについて、Claude Codeが守るべきルール。

## プロジェクトの目的

DSPy学習用の練習プロジェクト。自作のMarkdown/テキストをもとに答えるRAG搭載QAボット(CLI)を作りながら、DSPyの基本から評価・最適化までを学ぶ。
要件と構成は `README.md` の「要件」「構成」に書いてある。機能を追加・変更するときはREADMEも合わせて更新する。

前のプロジェクト `../python-todo-cli/` と同じ流れで進める。設定ファイル(`ci.yml`、`pyproject.toml`、`.vscode/settings.json`、`.claude/skills/git-message/`)はそちらを参考・コピー元にしてよい。ただし今回は仮想環境・パッケージ管理に **uv** を使うので、pip前提の部分は読み替える。

## 返答のルール

- 返答は必ず日本語で書く(短いメッセージへの返答でも)

## コードの教え方

- 聞かれるまでコードを書かない・提示しない。まずヒントのみ出す
- ユーザーが実際に書いた/試した内容を見てから、必要に応じてフィードバックする
- git操作などのコマンドも、まず自分で思い出させ、詰まったらヒント→それでも分からなければ正解を教える
- ユーザーが「教えて」「わからん」と言ったら、答えを出してよい
- ユーザーが「できた」と言ったら、`git status`・`git diff`・`uv run pytest` などの読み取り専用の確認で結果を検証してから次に進む
- 新しい用語やツールは、使う前に「なんのためにやるのか」を短く説明する
- DSPyの新しい要素(Signature・Module・Optimizerなど)は、「普通にプロンプトを書く場合と何が違うのか」をあわせて説明する
- 各Issueの実装を始めるときに、その機能に関係する一次資料(公式ドキュメント・論文・ソース・モデルカード)の該当部分を、ページや節を示して解説する。全文は訳さず要点をまとめ、確認した内容と記憶を分けて伝える

## uvの使い方

- 仮想環境は `uv sync` / `uv add` で uv が作る `.venv` を使う(`python -m venv` や `pip install` は使わない)
- パッケージの追加は `uv add <パッケージ>`、開発用(pytest・ruffなど)は `uv add --dev <パッケージ>`
- 依存関係は `pyproject.toml` と `uv.lock` で管理する。`uv.lock` はコミットする。`requirements.txt` は作らない
- コマンドは `uv run` 経由で実行する(例: `uv run pytest`、`uv run ruff check .`)
- Pythonのバージョンは `.python-version`(3.12)で固定する。このPCには uv が入れた3.11もあるので、uvのコマンドで3.12が使われているか注意する

## Git / GitHubの運用

- 作業は必ず機能・ドキュメント単位でブランチを切ってから行う(mainに直接コミットしない)
- ブランチ名は用途に応じたプレフィックスをつける(`feature/` `fix/` `refactor/` `test/` `docs/` `chore/` `ci/` `style/`)
- 変更 → コミット → push → Pull Request → マージ、のサイクルで進める
- PRのマージ方式は **Merge commit** を使う
- マージ後は不要になったブランチをローカル・リモート両方から削除する
- Claudeは branch作成・commit・push・PR作成を自分で実行しない。コマンドや文面を提案し、ユーザーが実行する
- コミットメッセージ・PR本文に Co-Authored-By や「Generated with Claude Code」などのAI署名を付けない
- コミットメッセージは `<prefix>: <日本語の要約>` 形式(例: `feat: 質問応答機能を実装`)
- 1つの意図に1コミット。関係ない変更は別コミット・別PRに分ける
- PR本文には対応するIssueを書く。Issueが完了するPRは `Closes #N`、途中のPRは `Refs #N`

## 進め方(この順番で進める)

前のプロジェクトで学んだとおり、**土台を最初にそろえてから機能を作る**。

1. **何を作るか決める**: READMEに要件(必須の機能・あとで作る機能・対象外)を書く ← 済
2. **リポジトリ作成**: GitHub上でLICENSE(MIT)付きで作成 → clone → リポジトリ単位で noreply のメールアドレスを設定 → `docs/` ブランチで `README.md` と `CLAUDE.md` を入れる ← 実施中
3. **開発環境と土台**(`chore/setup` ブランチ、PR 1つ)
   - `uv init --python 3.12` で `pyproject.toml` と `.python-version` を作成(`--python` を付けないと、uvが自動で入れた3.11が選ばれる)
   - `uv add dspy`、`uv add --dev pytest ruff` → `uv.lock` ができる
   - `pyproject.toml` に pytest(`pythonpath`)と ruff の設定
   - `.gitignore` を作成(リポジトリ作成時に付け忘れたため。GitHubの `Python.gitignore` テンプレートをもとに、`.venv` `__pycache__` `.pytest_cache` `.ruff_cache`、作成したインデックスなどの生成物が入っているか確認する)
   - `.vscode/settings.json`(cSpell辞書に `dspy` `ollama` `gemma` など)、`.claude/skills/git-message/` をコピー
   - Ollama から DSPy 経由で `gemma3:4b` を1回呼び出せることを確認する
4. **GitHubの仕組み**
   - `.github/workflows/ci.yml`(`uv sync` → pytest + `ruff check` + `ruff format --check`)を `ci/` ブランチで追加
   - READMEにバッジ(CI・ライセンス・Pythonバージョン)
   - CIが1回緑になったら、Rulesetでmainを保護(PR必須・`test` チェック必須・Merge commitのみ)
5. **機能をIssueに分解**: READMEの必須機能を1機能 = 1 Issueにする。PR 1つで終わる大きさにする。`docs/` の資料作成と `data/` の評価データ作成もIssueにする
6. **開発サイクル**: Issueを選ぶ → ブランチ → 実装と**テストを同時に**書く → `uv run pytest` / `uv run ruff check .` / `uv run ruff format --check .` → コミット → push → PR → CIが緑 → Merge commitでマージ → ブランチ削除 → `git pull`
7. **仕上げ**: READMEに使い方と設計のポイント、評価スコア(最適化の前後)、型ヒント、docstring、pytest-covでカバレッジ、タグと GitHub Release v0.1.0

## コードとテストの方針

- 最初から関数に分けて書く。ファイル名・フォルダ名・モデル名などは引数で受け取り、テストから差し替えられるようにする
- **中身と入り口を分ける**。中身(検索してDSPyで回答と出典を返す処理)は入り口(CLIなど)と別のファイルにし、中身では `print` や `input` を使わない。あとでLINEボットなど別の入り口を足すときに、中身を作り直さずに済むようにする
- CLIの処理は `if __name__ == "__main__":` の中に書く。引数解析は `argparse` を使い、`build_parser()` に切り出す
- テストは1つの分岐に1つ。成功パターンと失敗パターンをペアで書く
- ファイルを使うテストは最初から `tmp_path` を使う(リポジトリ直下にテスト用ファイルを作らない)
- `print` の出力は `capsys`、終了するケースは `pytest.raises(SystemExit)` で検証する
- エラーで終了するときは `sys.exit(1)` を使い、メッセージに原因(ファイル名など)を含める
- **テストでは Ollama を呼ばない**。LLMはDSPyのダミーLM(`dspy.utils.DummyLM` など)、埋め込みはダミー関数に差し替える。CIにはOllamaが無いので、実際のモデルを使う確認は手動で行う
- チャンク分割・データ読み込み・メトリクス関数など、LLMを使わない部分はふつうの関数としてしっかりテストする

## DSPy / Ollama の注意

- 回答用LLMは `gemma3:4b`、教師・採点用LLMは `gemma3:12b`、埋め込みは `embeddinggemma`(すべてOllama)。モデルを変えるときはREADMEの「構成」も更新する
- `gemma3:12b` はGPU(6GB)に収まらず遅いので、回答用や大量の呼び出しには使わない
- 最適化はLLMを何度も呼ぶので時間がかかる。評価データは20〜30問程度の小さい規模から始める
- 評価データは学習用(trainset)と検証用(devset)に分け、最適化の効果は検証用のスコアで判断する
- 最適化済みのプログラムは `save` / `load` で保存・読み込みし、毎回最適化し直さない

## Claudeへの注意

- DSPyはAPIの変化が速い。DSPyのクラス・引数は記憶で書かず、インストール済みのソース(`.venv` 内)や一次資料(GitHub `stanfordnlp/dspy` の README に載っている公式ドキュメント https://dspy.ai と論文)で確認してから説明する。README に載っていない資料を使うときは、そのことを明示する
- GitHub Actions の action のバージョン(`actions/checkout@vN`、`astral-sh/setup-uv@vN` など)は記憶で書かず、GitHub API でリリースを確認してから提案する
- `gh` コマンドはClaudeの環境では使えないことがある。GitHubの状態は `git fetch -p` や `https://api.github.com/repos/<owner>/<repo>/...` で確認する
- Ollamaの状態は `ollama list` などで確認する(モデルが無い・Ollamaが起動していない、を最初に疑う)
- 1セッション = 1タスク(1 Issue)を基本にする。セッションの最初に、今どのステップ・どのIssueかを確認する
