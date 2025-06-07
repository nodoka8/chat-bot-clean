import os
import asyncio
import requests
from mcp.server import Server
from mcp.types import Tool, TextContent
from mcp.server.stdio import stdio_server

# ログ出力関数
def log(msg):
    print(msg, flush=True)
    with open("/tmp/search_mcp.log", "a", encoding="utf-8") as log_file:
        log_file.write(msg + "\n")

# MCPサーバーのインスタンスを作成
server = Server("search-mcp")

@server.list_tools()
async def list_tools():
    """利用可能なツールのリストを返す"""
    return [
        Tool(
            name="google_search",
            description="Google検索を実行して結果を取得する",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "検索クエリ"
                    },
                    "num_results": {
                        "type": "integer",
                        "description": "取得する検索結果の数（デフォルト: 5）",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="weather_search",
            description="天気情報を検索して取得する",
            inputSchema={
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "場所（都市名、地域名など）"
                    }
                },
                "required": ["location"]
            }
        ),
        Tool(
            name="wikipedia_search",
            description="Wikipedia検索を実行して記事の概要を取得する",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Wikipedia検索クエリ"
                    },
                    "language": {
                        "type": "string",
                        "description": "言語コード（ja, en など）",
                        "default": "ja"
                    }
                },
                "required": ["query"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    """ツールを呼び出す"""
    log(f"Tool called: {name} with arguments: {arguments}")
    
    try:
        if name == "google_search":
            return await google_search(arguments.get("query"), arguments.get("num_results", 5))
        elif name == "weather_search":
            return await weather_search(arguments.get("location"))
        elif name == "wikipedia_search":
            return await wikipedia_search(arguments.get("query"), arguments.get("language", "ja"))
        else:
            log(f"Unknown tool: {name}")
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
    except Exception as e:
        log(f"Error in {name}: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]

async def google_search(query: str, num_results: int = 5):
    """Google検索を実行"""
    try:
        # Google Custom Search API または SerpAPI などを使用
        # ここでは簡単な例として DuckDuckGo検索を使用
        import urllib.parse
        import json
        
        encoded_query = urllib.parse.quote(query)
        url = f"https://api.duckduckgo.com/?q={encoded_query}&format=json&no_html=1&skip_disambig=1"
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        results = []
        
        # Abstract（要約）がある場合
        if data.get("Abstract"):
            results.append(f"要約: {data['Abstract']}")
        
        # Related Topics（関連トピック）
        related_topics = data.get("RelatedTopics", [])[:num_results]
        for topic in related_topics:
            if isinstance(topic, dict) and topic.get("Text"):
                results.append(f"関連: {topic['Text']}")
        
        if not results:
            results.append(f"'{query}'に関する詳細な情報は見つかりませんでした。")
        
        result_text = f"検索クエリ: {query}\n\n" + "\n\n".join(results[:num_results])
        
        log(f"Google search completed for: {query}")
        return [TextContent(type="text", text=result_text)]
        
    except Exception as e:
        log(f"Google search error: {e}")
        return [TextContent(type="text", text=f"検索エラー: {str(e)}")]

async def weather_search(location: str):
    """天気情報を検索"""
    try:
        # 簡易的な天気情報検索（実際にはOpenWeatherMap APIなどを使用）
        result_text = f"{location}の天気情報を取得中...\n\n"
        result_text += "注意: 実際の天気APIの実装が必要です。\n"
        result_text += f"現在は{location}の天気情報のモックデータです。"
        
        log(f"Weather search completed for: {location}")
        return [TextContent(type="text", text=result_text)]
        
    except Exception as e:
        log(f"Weather search error: {e}")
        return [TextContent(type="text", text=f"天気検索エラー: {str(e)}")]

async def wikipedia_search(query: str, language: str = "ja"):
    """Wikipedia検索を実行"""
    try:
        import urllib.parse
        
        encoded_query = urllib.parse.quote(query)
        api_url = f"https://{language}.wikipedia.org/api/rest_v1/page/summary/{encoded_query}"
        
        response = requests.get(api_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            title = data.get("title", "不明")
            extract = data.get("extract", "概要が見つかりませんでした。")
            
            result_text = f"Wikipedia: {title}\n\n{extract}"
            
            if data.get("content_urls", {}).get("desktop", {}).get("page"):
                result_text += f"\n\n詳細: {data['content_urls']['desktop']['page']}"
            
        else:
            result_text = f"'{query}'に関するWikipedia記事が見つかりませんでした。"
        
        log(f"Wikipedia search completed for: {query}")
        return [TextContent(type="text", text=result_text)]
        
    except Exception as e:
        log(f"Wikipedia search error: {e}")
        return [TextContent(type="text", text=f"Wikipedia検索エラー: {str(e)}")]


async def main():
    """MCPサーバーを起動"""
    log("Starting Search MCP Server...")
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())