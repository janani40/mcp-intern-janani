# Expense Tracker MCP Server

A small MCP (Model Context Protocol) server, written in Python, that stores expenses in a local SQLite database. An AI app such as Claude Desktop can add expenses and answer questions like "How much did I spend this month?".

## What it provides

| Type | Name | What it does |
|---|---|---|
| Tool | `add_expense` | Saves an expense (amount, category, optional description and date) |
| Tool | `monthly_total` | Total spent in a month (format `YYYY-MM`, default current month) |
| Tool | `top_categories` | Categories with the highest spending in a month |
| Resource | `expenses://current-month` | All expenses of the current month |
| Prompt | `budget-summary` | Asks the AI for a short budget summary and a saving tip |

Bad input (negative amount, wrong date or month format, empty category) returns a clear `Error: ...` message instead of crashing.

## Requirements

- Python 3.10 or higher
- Node.js 18 or higher (only needed for MCP Inspector)

## Setup (Windows PowerShell)

```
git clone https://github.com/janani40/mcp-intern-janani.git
cd mcp-intern-janani
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

The MCP SDK is pinned to version 1.x (`mcp<2`) because version 2 renamed `FastMCP`.

## Run the tests

```
python -m pytest -v
```

The tests use a temporary database, so your real `expenses.db` is never touched.

## Try it in MCP Inspector

```
npx @modelcontextprotocol/inspector python expense_server.py
```

Click the connect toggle, then open the Tools, Resources and Prompts tabs.

## Connect to Claude Desktop

Open Claude Desktop, go to Settings, Developer, Edit config. Add this inside `"mcpServers"` (use your own full paths, with `\\` for each backslash):

```json
"expense-tracker": {
  "command": "C:\\path\\to\\mcp-intern-janani\\.venv\\Scripts\\python.exe",
  "args": ["C:\\path\\to\\mcp-intern-janani\\expense_server.py"]
}
```

Save the file, fully quit Claude Desktop (end all Claude tasks in Task Manager), and open it again. Then ask, for example:

- "Add an expense of 90 rupees for snacks today"
- "How much did I spend this month in total?"
- "Which categories did I spend the most on this month?"

## Files

- `expense_server.py`: the MCP server (tools, resource, prompt)
- `test_expense_server.py`: 5 automated tests
- `requirements.txt`: Python dependencies
- `screenshots/`: proof screenshots (Inspector, Claude Desktop, tests)

## Data

Expenses are saved in `expenses.db` next to the script (created automatically, not uploaded to GitHub). Set the `EXPENSE_DB` environment variable to use a different file.