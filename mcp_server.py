from fastapi import FastAPI
from fastapi_mcp import FastApiMCP

app = FastAPI(title="シンプルAPI")

@app.get("/hello", operation_id="say_hello")
async def hello():
    """シンプルな挨拶エンドポイント"""
    return {"message": "Hello World"}

# MCPサーバーを作成
mcp = FastApiMCP(app, name="シンプルMCPサービス")
mcp.mount()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)