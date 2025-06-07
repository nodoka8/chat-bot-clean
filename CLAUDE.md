# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Commands

Run the bot:
```bash
uv run python main.py
```

Install dependencies:
```bash
uv pip install -r pyproject.toml
```

## Architecture Overview

This is a Discord bot that integrates with Google's Gemini 2.0 Flash API for AI responses and image generation. The bot is designed with MCP (Model Context Protocol) server integration capabilities.

### Core Components

- `main.py` - Entry point, simply imports and runs the bot
- `bot.py` - Main Discord bot implementation with command handlers and event listeners
- `gemini_client.py` - Wrapper class for Gemini API interactions, handles both text generation and image generation/editing

### Key Features

The bot responds to:
- Mentions with AI chat responses using Gemini 2.0 Flash
- `!img <prompt>` - Image generation using Gemini Imagen 3
- `!imgedit <prompt>` + image attachment - Image editing
- `!prompt` - Returns Google Drive profile file link
- `!reset` - Restarts the bot process

### Configuration

Required environment variables:
- `DISCORD_TOKEN` - Discord bot token
- `GEMINI_API_KEY` - Google Gemini API key
- `SAWAI_PROFILE_DRIVE_ID` - Google Drive file ID for bot profile
- `STARTUP_CHANNEL_ID` - Discord channel for startup notifications (optional)
- `MCP_SERVER_PATH` - Path to MCP server (optional)

### Chat System

The bot maintains a global chat history with a system prompt that includes the bot's personality (loaded from Google Drive). Conversations are logged to `log/chat_history.txt`. The system intelligently uses Google Search tool when search-related keywords are detected in user prompts.

### Image Generation

Uses Gemini's image generation API with both text-to-image and image-to-image capabilities. Generated images are returned as PIL Image objects and sent directly to Discord without local file storage.