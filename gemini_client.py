import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from google import genai
from google.genai.types import Tool, GenerateContentConfig, GoogleSearch
from PIL import Image
from io import BytesIO

class GeminiMCPClient:
    def __init__(self, api_key=None, mcp_server_path=None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.mcp_server_path = mcp_server_path or os.getenv("MCP_SERVER_PATH")
        self.client = genai.Client(api_key=self.api_key)
        self.server_params = StdioServerParameters(
            command="python",
            args=[self.mcp_server_path],
            env={"DISCORD_TOKEN": os.getenv("DISCORD_TOKEN"),
                 "DISCORD_GUILD_ID": os.getenv("GUILD_ID")}
        )
        self.google_search_tool = Tool(google_search=GoogleSearch())

    async def ask(self, prompt: str) -> str:
        if isinstance(prompt, list):
            prompt_text = " ".join(prompt)
        else:
            prompt_text = str(prompt)
        use_search = any(word in prompt_text for word in ["検索", "web", "ニュース", "調べて", "search", "Wikipedia", "ググって", "教えて"])
        with open("log/gemini_debug.log", "a", encoding="utf-8") as logf:
            logf.write(f"[ask] prompt: {prompt}\nuse_search: {use_search}\n")
        if use_search:
            response = await self.client.aio.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt,
                config=GenerateContentConfig(
                    tools=[self.google_search_tool],
                    response_modalities=["TEXT"],
                    temperature=0,
                ),
            )
            return response.text
        else:
            async with stdio_client(self.server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    response = await self.client.aio.models.generate_content(
                        model="gemini-2.0-flash",
                        contents=prompt,
                        config=GenerateContentConfig(
                            tools=[session],
                            response_modalities=["TEXT"],
                            temperature=0,
                        ),
                    )
                    return response.text

    async def generate_image(self, prompt: str, input_image_path: str = None) -> str:
        """
        Gemini 2.0 Flash Image Generation APIを使い、テキストまたは画像＋テキストから画像生成を行う。
        画像生成結果はファイルとして保存し、パスを返す。
        """
        import asyncio
        from google.genai import types
        contents = [prompt]
        if input_image_path:
            img = Image.open(input_image_path)
            contents = [prompt, img]
        response = await self.client.aio.models.generate_content(
            model="gemini-2.0-flash-preview-image-generation",
            contents=contents,
            config=types.GenerateContentConfig(
                response_modalities=["TEXT", "IMAGE"]
            )
        )
        # テキスト応答と画像応答を分離して返す
        text_result = None
        image_result_path = None
        for part in response.candidates[0].content.parts:
            if hasattr(part, "text") and part.text is not None:
                text_result = part.text
            elif hasattr(part, "inline_data") and part.inline_data is not None:
                image = Image.open(BytesIO(part.inline_data.data))
                image_result_path = f"log/gemini_generated_{asyncio.get_event_loop().time()}.png"
                image.save(image_result_path)
        if image_result_path:
            return f"{text_result}\n画像ファイル: {image_result_path}"
        return text_result or "画像生成に失敗しました。"

    async def generate_image_imagen3(self, prompt: str) -> str:
        """
        Gemini Imagen 3 APIを使い、テキストから高品質な画像生成を行う。
        画像生成結果はファイルとして保存し、パスを返す。
        """
        import asyncio
        from google.genai import types
        response = await self.client.aio.models.generate_content(
            model="imagen-3-preview",
            contents=[prompt],
            config=types.GenerateContentConfig(
                response_modalities=["TEXT", "IMAGE"]
            )
        )
        text_result = None
        image_result_path = None
        for part in response.candidates[0].content.parts:
            if hasattr(part, "text") and part.text is not None:
                text_result = part.text
            elif hasattr(part, "inline_data") and part.inline_data is not None:
                image = Image.open(BytesIO(part.inline_data.data))
                image_result_path = f"log/gemini_generated_img3_{asyncio.get_event_loop().time()}.png"
                image.save(image_result_path)
        if image_result_path:
            return f"{text_result}\n画像ファイル: {image_result_path}"
        return text_result or "画像生成に失敗しました。"

# 例: bot.py から呼び出す場合
# gemini = GeminiMCPClient()
# reply = await gemini.ask("ロンドンの今日の天気を教えて")
