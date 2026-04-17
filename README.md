# RSS Notification System

RSS・ニュース・note系の記事を定期監視し、条件に一致した記事をLINEへ通知するPythonシステムです。  
要約は **Grok -> OpenAI -> Gemini** の順でフォールバックします。

## できること

- 複数RSSを15分ごとに巡回
- タイトル/本文のキーワードで記事を抽出
- AIで日本語200文字以内の要約を生成
- LINE Messaging APIでユーザーID宛にPush通知
- `processed_articles.json` で重複通知を防止
- `requests.json` に追加した検索リクエストを後追い処理
- LINE Webhook受信で `requests.json` へ自動登録（FastAPI）

## ディレクトリ構成

```text
.
├── main.py
├── rss_fetcher.py
├── filter.py
├── request_handler.py
├── config.yaml
├── processed_articles.json
├── requests.json
├── requirements.txt
├── .env.example
├── api/
│   ├── __init__.py
│   └── line_webhook.py
├── notifier/
│   ├── __init__.py
│   └── line_client.py
├── storage/
│   ├── __init__.py
│   └── storage.py
├── summarizer/
│   ├── __init__.py
│   ├── grok_client.py
│   ├── openai_client.py
│   └── gemini_client.py
└── .github/
    └── workflows/
        └── run.yml
```

## セットアップ（初心者向け）

1. このリポジトリを作成し、ファイルを配置する
2. ローカルで依存関係を入れる
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. `.env.example` を `.env` にコピーして値を設定する
   ```bash
   cp .env.example .env
   ```
4. ローカル実行して動作確認
   ```bash
   python main.py
   ```
5. GitHubへpush
6. GitHubリポジトリの `Settings > Secrets and variables > Actions` で以下を登録
   - `LINE_CHANNEL_TOKEN`
   - `LINE_USER_ID`
   - `OPENAI_API_KEY`
   - `GEMINI_API_KEY`
   - `GROK_API_KEY`
7. `Actions` タブで `RSS Notification` が15分ごとに実行されることを確認

## requests.json の使い方

`requests.json` に以下形式で追加すると、次回実行時に検索処理されます。

```json
[
  {
    "query": "AI 最新ニュース",
    "timestamp": "2026-04-18T00:00:00"
  }
]
```

- `query` の単語がタイトルまたは本文にすべて含まれる記事を抽出します。
- 処理に成功したリクエストは自動で削除されます。
- 通知失敗時は再試行できるように残します。

## Webhookで自動登録（FastAPI）

### 1) ローカル起動

```bash
uvicorn api.line_webhook:app --host 0.0.0.0 --port 8000
```

### 2) LINE Developers側の設定

1. Messaging APIチャネルを開く
2. Webhook URLに `https://<公開URL>/webhook/line` を設定
3. Webhookを有効化
4. チャネルシークレットを `.env` の `LINE_CHANNEL_SECRET` に設定

### 3) メッセージ例

- `AI 最新ニュースを探して`
- `iOSな記事を探して`

上記のようなテキストを送ると、Webhookがクエリを抽出して `requests.json` に追加します。  
次回の定期実行（GitHub Actions）で検索・要約・通知されます。

## 設計メモ（拡張ポイント）

- 将来、LINE Webhookで受けた検索文を `requests.json` に追加するハンドラを作れば、そのまま連携可能
- Webhook実装済み。公開URLはCloud Run/Render/Railwayなどでホスティング可能
- 要約プロバイダ追加時は `summarizer/__init__.py` のフォールバック順へ関数を追加
- 永続化先をDB化する場合は `storage/storage.py` を差し替えるだけで対応しやすい構成

## 通知フォーマット

```text
【タイトル】
要約文

URL
```

## 補足

- API呼び出し失敗時はログを出力し、可能な限り処理を継続します。
- 要約がすべて失敗した場合は `要約失敗` を通知します。
