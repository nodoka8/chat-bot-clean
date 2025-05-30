# chat-bot-clean

機密情報を含まないクリーンなGemini 2.0 Flash＋MCPサーバー連携Discordボットのリポジトリです。

---

## セットアップ手順（uv推奨）

1. 必要な環境変数を`.env`等で設定してください（Git管理外）:
   - `DISCORD_TOKEN`（Discord Botのトークン）
   - `GEMINI_API_KEY`（Google Gemini APIキー）

2. 依存パッケージのインストール（uvを使用）：

```
uv pip install -r pyproject.toml
```

または、初回セットアップ時は
```
uv pip install httpx discord.py
```

3. Botの起動：

```
uv pip run python main.py
```

---

## 主な機能
- DiscordでボットをメンションするとGemini 2.0 Flash（無料枠）でAI応答
- Web検索グラウンディング・画像生成（!imgコマンド）
- 会話履歴・プロフィール自動反映
- MCPサーバー拡張・ツール自動連携設計
- .envやlog/など機密・生成ファイルはGit管理外

---

> Gemini APIの無料枠利用にはGoogle CloudのAPIキーが必要です。
> 機密情報は絶対にGitHubへpushしないでください。
