import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from google import genai
from google.genai.types import Tool, GenerateContentConfig, GoogleSearch
from PIL import Image
from io import BytesIO

class GeminiMCPClient:
    def __init__(self, api_key=None, discord_mcp_path=None, search_mcp_path=None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=self.api_key)
        
        # Discord MCPサーバーの設定
        self.discord_mcp_path = discord_mcp_path or os.getenv("DISCORD_MCP_PATH")
        if self.discord_mcp_path and os.getenv("DISCORD_GUILD_ID"):
            self.discord_server_params = StdioServerParameters(
                command="python",
                args=[self.discord_mcp_path],
                env={"DISCORD_TOKEN": os.getenv("DISCORD_TOKEN"),
                     "DISCORD_GUILD_ID": os.getenv("DISCORD_GUILD_ID")}
            )
        else:
            self.discord_server_params = None
            
        # Search MCPサーバーの設定
        self.search_mcp_path = search_mcp_path or os.getenv("SEARCH_MCP_PATH")
        if self.search_mcp_path:
            self.search_server_params = StdioServerParameters(
                command="python",
                args=[self.search_mcp_path]
            )
        else:
            self.search_server_params = None
        
        # Fallback用のGoogle検索ツール
        self.google_search_tool = Tool(google_search=GoogleSearch())

    async def ask(self, prompt: str) -> str:
        if isinstance(prompt, list):
            prompt_text = " ".join(prompt)
        else:
            prompt_text = str(prompt)
            
        with open("log/gemini_debug.log", "a", encoding="utf-8") as logf:
            logf.write(f"[ask] prompt: {prompt}\n")
        
        # プロンプトから必要な機能を判定
        try:
            # Discord関連キーワードをチェック
            if any(word in prompt_text for word in ["サーバー情報", "メンバーリスト", "メンバー", "ロール", "チャンネル", "Discord"]):
                return await self.use_discord_mcp(prompt)
            
            # 検索関連キーワードをチェック
            elif any(word in prompt_text for word in ["天気", "検索", "調べて", "Wikipedia", "ググって", "ニュース"]):
                return await self.use_search_mcp(prompt)
            
            # その他は基本的なGoogle検索ツール付きで応答
            else:
                return await self.basic_response_with_search(prompt)
                
        except Exception as e:
            with open("log/gemini_debug.log", "a", encoding="utf-8") as logf:
                logf.write(f"[ERROR] {e}\n")
            
            # 全てのエラー時は最もシンプルな応答
            return await self.basic_response(prompt)
    
    async def use_discord_mcp(self, prompt):
        """Discord MCP サーバーを使用して応答"""
        if not self.discord_server_params:
            with open("log/gemini_debug.log", "a", encoding="utf-8") as logf:
                logf.write("[Discord MCP] Not configured, fallback to basic response\n")
            return await self.basic_response(prompt)
        
        try:
            async with stdio_client(self.discord_server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    tools = await session.list_tools()
                    
                    with open("log/gemini_debug.log", "a", encoding="utf-8") as logf:
                        logf.write(f"[Discord MCP] Available tools: {[tool.name for tool in tools.tools]}\n")
                    
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
                    
        except Exception as e:
            with open("log/gemini_debug.log", "a", encoding="utf-8") as logf:
                logf.write(f"[Discord MCP ERROR] {e}\n")
            return await self.basic_response_with_search(prompt)
    
    async def use_search_mcp(self, prompt):
        """Search MCP サーバーを使用して応答"""
        if not self.search_server_params:
            with open("log/gemini_debug.log", "a", encoding="utf-8") as logf:
                logf.write("[Search MCP] Not configured, fallback to Google Search\n")
            return await self.basic_response_with_search(prompt)
        
        try:
            async with stdio_client(self.search_server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    tools = await session.list_tools()
                    
                    with open("log/gemini_debug.log", "a", encoding="utf-8") as logf:
                        logf.write(f"[Search MCP] Available tools: {[tool.name for tool in tools.tools]}\n")
                    
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
                    
        except Exception as e:
            with open("log/gemini_debug.log", "a", encoding="utf-8") as logf:
                logf.write(f"[Search MCP ERROR] {e}\n")
            return await self.basic_response_with_search(prompt)
    
    async def basic_response_with_search(self, prompt):
        """Google検索ツール付きの基本応答"""
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
    
    async def basic_response(self, prompt):
        """最もシンプルな基本応答（ツールなし）"""
        response = await self.client.aio.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config=GenerateContentConfig(
                response_modalities=["TEXT"],
                temperature=0,
            ),
        )
        return response.text

    async def generate_image(self, prompt: str, input_image_path: str = None, input_image_obj: Image.Image = None) -> str:
        """
        Gemini 2.0 Flash Image Generation APIを使い、テキストまたは画像＋テキストから画像生成を行う。
        画像生成結果はPIL.Image.Imageオブジェクトとして返す（ローカル保存しない）。
        """
        import asyncio
        from google.genai import types
        contents = [prompt]
        if input_image_obj is not None:
            contents = [prompt, input_image_obj]
        elif input_image_path:
            img = Image.open(input_image_path)
            contents = [prompt, img]
        response = await self.client.aio.models.generate_content(
            model="gemini-2.0-flash-preview-image-generation",
            contents=contents,
            config=types.GenerateContentConfig(
                response_modalities=["TEXT", "IMAGE"]
            )
        )
        text_result = None
        image_result = None
        for part in response.candidates[0].content.parts:
            if hasattr(part, "text") and part.text is not None:
                text_result = part.text
            elif hasattr(part, "inline_data") and part.inline_data is not None:
                image_result = Image.open(BytesIO(part.inline_data.data))
        if image_result:
            return text_result, image_result
        return text_result or "画像生成に失敗しました。", None

    # generate_image_imagen3は削除
# 例: bot.py から呼び出す場合
# gemini = GeminiMCPClient()
# reply = await gemini.ask("ロンドンの今日の天気を教えて")
