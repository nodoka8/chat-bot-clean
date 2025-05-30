import os
import asyncio
from datetime import datetime
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from google import genai
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Create server parameters for stdio connection
server_params = StdioServerParameters(
            command="python",
            args=[os.getenv("MCP_SERVER_PATH")],
            env={"DISCORD_TOKEN": os.getenv("DISCORD_TOKEN")},
        )

async def run():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            # Discordクライアントのreadyを待つ（5秒待機など）
            await asyncio.sleep(5)
            prompt = f"あなたは親切で有能なAIアシスタントで、名前はコンシェルジュ澤井です。Discordの会話で役立つ情報を簡潔に日本語で返答してください。あなたが操作するDiscordサーバーのIDは722353633491943446です。"
            response = await client.aio.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt,
                config=genai.types.GenerateContentConfig(
                    temperature=0,
                    tools=[session],
                ),
            )
            print(response.text)

async def chat_loop():
    print("MCP Gemini CLI チャット開始。'exit'で終了。")
    SYSTEM_PROMPT = "あなたは特定のDiscordサーバーに存在する親切で有能なAIアシスタントで、名前はコンシェルジュ澤井です。Discordの会話で役立つ情報を簡潔に日本語で返答してください。あなたが操作するDiscordサーバーのIDは722353633491943446です。"
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            messages = [{"role": "user", "content": SYSTEM_PROMPT}]
            while True:
                prompt = input("あなた: ").strip()
                if prompt.lower() in ("exit", "quit"): break
                messages.append({"role": "user", "content": prompt})
                contents = [m["content"] for m in messages]
                response = await client.aio.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=contents,
                    config=genai.types.GenerateContentConfig(
                        temperature=0,
                        tools=[session],
                    ),
                )
                ai_text = response.text
                messages.append({"role": "model", "content": ai_text})
                print("AI:", ai_text)

# Start the asyncio event loop and run the main function
if __name__ == "__main__":
    asyncio.run(chat_loop())