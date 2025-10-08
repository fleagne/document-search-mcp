# 使い方

1. Tesseractのインストール

```bash
sudo apt-get update
sudo apt-get install tesseract-ocr tesseract-ocr-jpn
```

2. Meilisearchを起動

```bash
docker run -p 7700:7700 getmeili/meilisearch:latest
```

3. ファイルをインデックス化

```bash
uv run main.py index /mnt/c/svn
```

4. 検索

```bash
uv run main.py search GitHub
```

5. MCP登録

WSL (Ubuntu): `.vscode-server/data/User/mcp.json`

```json
{
	"servers": {
		"document-search": {
			"type": "stdio",
			"command": "uv",
			"args": [
				"run",
				"--directory",
				"/home/{username}}/{workspace}",
				"mcp_server.py"
			],
		}
	},
	"inputs": []
}
```
