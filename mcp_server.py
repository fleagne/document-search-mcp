import asyncio
import meilisearch
from pathlib import Path
from mcp.server import Server
from mcp.types import Tool, TextContent
import json

# Meilisearchクライアント
client = meilisearch.Client('http://127.0.0.1:7700')
INDEX_NAME = 'documents'

# MCPサーバーインスタンス
app = Server("document-search")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """利用可能なツールのリスト"""
    return [
        Tool(
            name="search_documents",
            description=(
                "社内ドキュメント（Word、Excel、PNG、draw.io）を検索します。"
                "ユーザーの質問や意図から関連するキーワードを抽出して検索してください。"
                "例: 「コスト削減の方法」→「コスト削減」「経費削減」などで検索"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "検索クエリ（キーワードまたはフレーズ）"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "取得する結果の最大数（デフォルト: 5）",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """ツールの実行"""
    if name != "search_documents":
        raise ValueError(f"Unknown tool: {name}")
    
    query = arguments.get("query", "")
    limit = arguments.get("limit", 5)
    
    try:
        # Meilisearchで検索
        index = client.get_index(INDEX_NAME)
        results = index.search(query, {
            'limit': limit,
            'attributesToHighlight': ['content'],
            'highlightPreTag': '**',
            'highlightPostTag': '**'
        })
        
        if len(results['hits']) == 0:
            return [TextContent(
                type="text",
                text=f"検索クエリ「{query}」に一致するドキュメントが見つかりませんでした。"
            )]
        
        # 結果を整形
        response_parts = [f"検索クエリ「{query}」の結果:\n"]
        
        for idx, hit in enumerate(results['hits'], 1):
            response_parts.append(f"\n## {idx}. {hit['filename']}")
            response_parts.append(f"パス: {hit['path']}\n")
            
            # ハイライト部分を抽出
            if '_formatted' in hit and 'content' in hit['_formatted']:
                highlighted = hit['_formatted']['content']
                lines = highlighted.split('\n')
                matched_lines = [line for line in lines if '**' in line]
                
                if matched_lines:
                    response_parts.append("関連箇所:")
                    for line in matched_lines[:3]:  # 最大3件
                        response_parts.append(f"  {line}")
            else:
                # フォールバック
                preview = hit['content'][:200].replace('\n', ' ')
                response_parts.append(f"プレビュー: {preview}...")
        
        return [TextContent(
            type="text",
            text="\n".join(response_parts)
        )]
        
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"検索エラー: {str(e)}"
        )]


async def main():
    """サーバー起動"""
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())