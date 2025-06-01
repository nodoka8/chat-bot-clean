# Chat-Bot

## セットアップ手順（UV使用）

1. 必要な環境変数を設定してください：
   - `DISCORD_TOKEN`（Discord Botのトークン）
   - `GEMINI_API_KEY`（Google Gemini APIキー）
   - `MCP_SERVER_PATH`（MCPサーバーのパス、省略可）
   - `SAWAI_PROFILE_DRIVE_ID`（Google Drive上のプロフィールファイルID）
   - `STARTUP_CHANNEL_ID`（起動通知を送るDiscordチャンネルID、省略可）

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

## 機能
- DiscordでボットをメンションするとGemini 2.0 Flash（無料枠）でAI応答
- !imgコマンドで画像生成
- !promptでGoogle Driveプロフィールファイルの案内
- !resetでボット再起動
- 起動時に指定チャンネルへ通知
- MCPサーバー拡張を見据えた設計

---

Gemini APIの無料枠利用にはGoogle CloudのAPIキーが必要です。
プロフィール共有にはGoogle Driveの「リンクを知っている全員が閲覧可」設定推奨。
