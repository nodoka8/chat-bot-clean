# Chat-Bot

## セットアップ手順（UV使用）

1. 必要な環境変数を設定してください：
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

## 機能
- DiscordでボットをメンションするとGemini 2.0 Flash（無料枠）でAI応答
- MCPサーバー拡張を見据えた設計

---

Gemini APIの無料枠利用にはGoogle CloudのAPIキーが必要です。
