import discord
from discord.ext import commands
from gemini_client import GeminiMCPClient
import os
from dotenv import load_dotenv
import requests

load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

gemini = GeminiMCPClient(api_key=os.getenv('GEMINI_API_KEY'), mcp_server_path=os.getenv('MCP_SERVER_PATH'))

# Google Drive共有リンクのファイルIDを指定
GOOGLE_DRIVE_FILE_ID = os.getenv("SAWAI_PROFILE_DRIVE_ID")  # 例: '1a2b3c4d5e6f...'
DRIVE_RAW_URL = f"https://drive.google.com/uc?export=download&id={GOOGLE_DRIVE_FILE_ID}"

# sawai_profile.txtの内容をGoogle Driveから取得
try:
    response = requests.get(DRIVE_RAW_URL, timeout=10)
    response.raise_for_status()
    SAWAI_PROFILE = response.text.strip()
except Exception as e:
    print(f"[ERROR] Google Driveからプロフィール取得失敗: {e}")
    SAWAI_PROFILE = "(プロフィール取得失敗)"

SYSTEM_PROMPT = f"""あなたは特定のDiscordサーバー(ID: 722353633491943446)に存在する親切で有能なAIアシスタントで、名前はコンシェルジュ澤井です。Discordの会話で役立つ情報を簡潔に日本語で返答してください。\n\n{SAWAI_PROFILE}"""

# グローバルで会話履歴を保持
chat_history = [{"role": "user", "content": SYSTEM_PROMPT}]
#print("chat履歴", chat_history)

# logディレクトリ作成
os.makedirs("log", exist_ok=True)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    # 起動時に指定チャンネルへメッセージ投稿
    channel_id = os.getenv("STARTUP_CHANNEL_ID")
    if channel_id:
        try:
            channel = bot.get_channel(int(channel_id))
            if channel:
                await channel.send("ボットが起動しました。")
            else:
                print(f"[ERROR] チャンネルID {channel_id} が見つかりませんでした")
        except Exception as e:
            print(f"[ERROR] 起動メッセージ送信失敗: {e}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    # !promptコマンドでGoogle Driveのプロフィールファイルリンクを返す
    if message.content.strip() == "!prompt":
        if GOOGLE_DRIVE_FILE_ID:
            drive_link = f"https://drive.google.com/file/d/{GOOGLE_DRIVE_FILE_ID}/view?usp=sharing"
            await message.reply(f"プロフィールファイルはこちらです：\n{drive_link}\n\n編集後は `!reset` でボットを再起動してください。")
        else:
            await message.reply("Google DriveのファイルIDが設定されていません。")
        return
    # !resetコマンドでボットを再起動
    if message.content.strip() == "!reset":
        await message.reply("Botを再起動します…")
        import sys, os
        os.execv(sys.executable, [sys.executable] + sys.argv)
        return
    if bot.user in message.mentions:
        prompt = message.content.replace(f'<@{bot.user.id}>', '').strip()
        if prompt:
            chat_history.append({"role": "user", "content": prompt})
            contents = [m["content"] for m in chat_history]
            reply = await gemini.ask(contents)
            chat_history.append({"role": "model", "content": reply})
            # 履歴をlog/chat_history.txtに追記
            with open("log/chat_history.txt", "a", encoding="utf-8") as f:
                f.write(f"user: {prompt}\n")
                f.write(f"model: {reply}\n")
            # Discordのメッセージ長制限に対応（2000文字）
            MAX_DISCORD_MESSAGE_LEN = 2000
            if len(reply) > MAX_DISCORD_MESSAGE_LEN:
                reply = reply[:MAX_DISCORD_MESSAGE_LEN - 20] + "\n...(省略)"
            await message.reply(reply)
    await bot.process_commands(message)

@bot.command(name="img")
async def generate_image_command(ctx, *, prompt: str):
    """
    !img <プロンプト> でGemini画像生成APIを呼び出し、画像を生成して送信する
    """
    async with ctx.typing():
        result = await gemini.generate_image(prompt)
        # 結果が「\n画像ファイル: ...」形式なら画像も送信
        if "画像ファイル:" in result:
            text, img_path = result.split("画像ファイル:", 1)
            text = text.strip()
            img_path = img_path.strip()
            import os
            if os.path.exists(img_path):
                if text:
                    await ctx.send(text)
                await ctx.send(file=discord.File(img_path))
            else:
                await ctx.send(f"画像ファイルの保存に失敗しました: {img_path}")
        else:
            await ctx.send(result)

def run():
    bot.run(DISCORD_TOKEN)
