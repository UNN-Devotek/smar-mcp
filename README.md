# Smartsheet MCP Server

A [Model Context Protocol](https://modelcontextprotocol.io/) (MCP) server for interacting with the Smartsheet API. This server provides tools for searching, retrieving, updating, and managing Smartsheet sheets, rows, workspaces, folders, discussions, users, and sheet summary fields through the MCP protocol.

> **Maintained by [Lance Strickland](https://github.com/UNN-Devotek)** — forked from [smartsheet-platform/smar-mcp](https://github.com/smartsheet-platform/smar-mcp) with additional tooling for sheet summary fields and expanded search/user/workspace coverage.

## Table of Contents

- [Local Development Setup](#local-development-setup)
- [Disclaimer](#disclaimer)
- [Features](#features)
- [Available MCP Tools](#available-mcp-tools)
- [API Endpoint Coverage](#api-endpoint-coverage)
- [Environment Variables](#environment-variables)
- [Development](#development)

---

## Local Development Setup

When you finish this setup you'll have the MCP server built locally and connected to your MCP client (Claude Desktop, Cursor, VS Code Copilot, Cline, etc.). The server communicates over stdio — no ports, no Docker, no database required.

### Prerequisites (all platforms)

- **Node.js 18+** — install via the platform-specific steps below
- **npm 7+** — bundled with Node.js
- **git**
- A [Smartsheet API token](https://developers.smartsheet.com/) — generate one at Account → Apps & Integrations → API Access

---

### Windows (WSL2)

> [!NOTE]
> Run the MCP server inside WSL2. Claude Desktop and other Windows MCP clients can call a WSL2 process — configure the client to invoke `wsl bash -c "node /path/to/build/index.js"` or use the Windows `node.exe` path directly (see MCP Client Config below).

**1. Install WSL2 + Ubuntu** (PowerShell as Administrator):
```powershell
wsl --install
# Restart when prompted, then open Ubuntu from the Start menu
```

**2. Install Node.js 20 inside WSL:**
```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs git
node --version   # should print v20.x.x
```

**3. Clone the repo inside WSL:**
```bash
git clone https://github.com/UNN-Devotek/smar-mcp.git ~/smar-mcp
cd ~/smar-mcp
```

**4. Install dependencies and build:**
```bash
npm install
npm run build
```

**5. Create your `.env` file:**
```bash
cp .env.example .env
# Edit .env and set SMARTSHEET_API_KEY=your_token_here
```

**6. Verify the server starts:**
```bash
node build/index.js
# Should print: Smartsheet MCP Server running on stdio
# Press Ctrl+C to stop
```

**7. Configure your MCP client** — see [MCP Client Config](#mcp-client-config) below.

**Troubleshooting (Windows/WSL2):**
- `wsl: command not found` — ensure you're in PowerShell, not CMD. Run `wsl --install` again.
- `node: command not found` — the NodeSource install may have missed your shell. Run `source ~/.bashrc` or restart the terminal.
- MCP client can't reach the server — if using Claude Desktop on Windows, use the Windows node path. Run `which node` in WSL to find the binary, then add a symlink or use the Windows store Node.js instead.
- `Permission denied` on `build/index.js` — run `chmod +x build/index.js`

---

### macOS

**1. Install Homebrew** (skip if already installed):
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

**2. Install Node.js and git:**
```bash
brew install node git
node --version   # should print v20.x.x or higher
```

**3. Clone the repo:**
```bash
git clone https://github.com/UNN-Devotek/smar-mcp.git ~/smar-mcp
cd ~/smar-mcp
```

**4. Install dependencies and build:**
```bash
npm install
npm run build
```

**5. Create your `.env` file:**
```bash
cp .env.example .env
# Open .env in any editor and set SMARTSHEET_API_KEY=your_token_here
```

**6. Verify the server starts:**
```bash
node build/index.js
# Should print: Smartsheet MCP Server running on stdio
# Press Ctrl+C to stop
```

**7. Configure your MCP client** — see [MCP Client Config](#mcp-client-config) below.

**Troubleshooting (macOS):**
- `brew: command not found` — Homebrew install may need you to add it to PATH. Follow the instructions printed at the end of the install script.
- `EACCES` permission errors on `npm install` — do not use `sudo npm`. Instead install Node.js via `nvm`: `brew install nvm && nvm install 20 && nvm use 20`.
- Apple Silicon (M1/M2/M3) — Node.js 18+ has native ARM64 builds; no Rosetta required.
- MCP client shows "server not found" — make sure you used the absolute path to `node` in the config (run `which node` to get it).

---

### Linux

**1. Install Node.js 20 and git:**
```bash
# Debian/Ubuntu
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs git

# Fedora/RHEL
curl -fsSL https://rpm.nodesource.com/setup_20.x | sudo bash -
sudo dnf install -y nodejs git

node --version   # should print v20.x.x
```

**2. Clone the repo:**
```bash
git clone https://github.com/UNN-Devotek/smar-mcp.git ~/smar-mcp
cd ~/smar-mcp
```

**3. Install dependencies and build:**
```bash
npm install
npm run build
```

**4. Create your `.env` file:**
```bash
cp .env.example .env
# Edit .env and set SMARTSHEET_API_KEY=your_token_here
```

**5. Verify the server starts:**
```bash
node build/index.js
# Should print: Smartsheet MCP Server running on stdio
# Press Ctrl+C to stop
```

**6. Configure your MCP client** — see [MCP Client Config](#mcp-client-config) below.

**Troubleshooting (Linux):**
- `curl: command not found` — install with `sudo apt install curl` or `sudo dnf install curl`.
- `node: command not found` after install — run `source ~/.bashrc` or log out and back in.
- `EACCES` on npm install — do not use `sudo npm`. Use `nvm` instead: install from [nvm.sh](https://github.com/nvm-sh/nvm), then `nvm install 20 && nvm use 20`.

---

### MCP Client Config

The server requires two values in the config: the path to your `node` binary and the path to `build/index.js`. Use absolute paths.

**Find your node path:**
```bash
which node        # e.g. /home/user/.nvm/versions/node/v20.19.0/bin/node
```

**Find your repo path:**
```bash
realpath build/index.js   # e.g. /home/user/smar-mcp/build/index.js
```

**Claude Desktop** (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS, `%APPDATA%\Claude\claude_desktop_config.json` on Windows):
```json
{
  "mcpServers": {
    "smartsheet": {
      "command": "/absolute/path/to/node",
      "args": ["/absolute/path/to/smar-mcp/build/index.js"],
      "env": {
        "SMARTSHEET_API_KEY": "your-api-key-here",
        "SMARTSHEET_ENDPOINT": "https://api.smartsheet.com/2.0",
        "ALLOW_DELETE_TOOLS": "false"
      }
    }
  }
}
```

> [!TIP]
> See `claude_desktop_config-example.json` in the project root for a ready-to-copy template.

**VS Code Copilot / Cline / Cursor** — the config format is identical. Check your client's MCP settings panel and paste the same block under `mcpServers`.

> [!WARNING]
> Restart your MCP client after editing the config. Most clients only read the config on startup.

---

## Disclaimer

MCP is a new technology. This integration relies on a Smartsheet API token allowing access to your account. While powerful, MCP servers can be susceptible to prompt injection when processing untrusted data. Review actions taken through these clients to ensure secure operation.

## Features

- Get detailed information about sheets, rows, and cells
- Create, update, and delete sheets and rows
- Create version backups of sheets at specific timestamps
- Manage sheet summary fields (get, add, update, delete)
- Search sheets, folders, workspaces, reports, and within sheet data
- Manage discussions on sheets and rows
- Create and send update requests to collaborators
- Manage workspaces and folders
- Look up users and check current user identity
- Formatted responses optimized for AI consumption

## Available MCP Tools

### Sheets

#### `get_sheet`
Retrieves the current state of a sheet, including rows, columns, and cells.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `sheetId` | string | Yes | The ID of the sheet |
| `include` | string | No | Comma-separated elements to include (e.g. `format,formulas`) |

#### `get_sheet_by_url`
Retrieves a sheet using its Smartsheet URL instead of its ID.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `url` | string | Yes | The full Smartsheet URL of the sheet |
| `include` | string | No | Comma-separated elements to include |

#### `get_sheet_version`
Gets the current version number of a sheet.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `sheetId` | string | Yes | The ID of the sheet |

#### `get_sheet_location`
Gets the folder ID where a sheet is located.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `sheetId` | string | Yes | The ID of the sheet |

#### `create_sheet`
Creates a new sheet.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | Yes | Name for the new sheet |
| `columns` | array | Yes | Array of column objects |
| `folderId` | string | No | ID of the destination folder |

#### `copy_sheet`
Creates a copy of a sheet.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `sheetId` | string | Yes | The ID of the sheet to copy |
| `destinationName` | string | Yes | Name for the sheet copy |
| `destinationFolderId` | string | No | ID of the destination folder (defaults to same as source) |

#### `create_version_backup`
Creates a backup sheet with data from a specific timestamp using cell history.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `sheetId` | string | Yes | The ID of the source sheet |
| `timestamp` | string | Yes | ISO 8601 timestamp (e.g. `2025-03-27T13:00:00Z`) |
| `archiveName` | string | No | Name for the archive sheet |
| `includeFormulas` | boolean | No | Include formulas (default: true) |
| `includeFormatting` | boolean | No | Include formatting (default: true) |
| `batchSize` | number | No | Rows per batch (default: 100) |
| `maxConcurrentRequests` | number | No | Max concurrent API requests (default: 5) |

---

### Rows

#### `get_row`
Retrieves a single row from a sheet by row ID.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `sheetId` | string | Yes | The ID of the sheet |
| `rowId` | string | Yes | The ID of the row |
| `include` | string | No | Comma-separated elements to include |

#### `add_rows`
Adds new rows to a sheet.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `sheetId` | string | Yes | The ID of the sheet |
| `rows` | array | Yes | Array of row objects to add |

#### `update_rows`
Updates rows in a sheet, including cell values, formatting, and formulas.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `sheetId` | string | Yes | The ID of the sheet |
| `rows` | array | Yes | Array of row objects to update |

#### `delete_rows`
Deletes rows from a sheet. Requires `ALLOW_DELETE_TOOLS=true`.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `sheetId` | string | Yes | The ID of the sheet |
| `rowIds` | array | Yes | Array of row IDs to delete |
| `ignoreRowsNotFound` | boolean | No | Skip error if rows not found |

#### `get_cell_history`
Retrieves the history of changes for a specific cell.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `sheetId` | string | Yes | The ID of the sheet |
| `rowId` | string | Yes | The ID of the row |
| `columnId` | string | Yes | The ID of the column |
| `include` | string | No | Additional information to include |
| `pageSize` | number | No | History entries per page |
| `page` | number | No | Page number |

---

### Sheet Summary Fields

#### `get_sheet_summary`
Retrieves the full sheet summary including all fields and their current values.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `sheetId` | string | Yes | The ID of the sheet |
| `include` | string | No | Elements to include (e.g. `writerInfo`) |

#### `get_sheet_summary_fields`
Retrieves all summary fields defined on a sheet.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `sheetId` | string | Yes | The ID of the sheet |
| `include` | string | No | Elements to include |

#### `add_sheet_summary_fields`
Adds one or more new summary fields to a sheet. Supports formulas and static values.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `sheetId` | string | Yes | The ID of the sheet |
| `fields` | array | Yes | Array of field objects (title, type, formula/value, format) |

#### `update_sheet_summary_fields`
Updates existing summary fields. Each field must include its `id`.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `sheetId` | string | Yes | The ID of the sheet |
| `fields` | array | Yes | Array of field objects including `id` |

#### `delete_sheet_summary_fields`
Deletes summary fields by ID. Requires `ALLOW_DELETE_TOOLS=true`.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `sheetId` | string | Yes | The ID of the sheet |
| `fieldIds` | array | Yes | Array of field IDs to delete |

---

### Discussions

#### `get_discussions_by_sheet_id`
Retrieves all discussions on a sheet.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `sheetId` | string | Yes | The ID of the sheet |

#### `get_discussions_by_row_id`
Retrieves discussions for a specific row.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `sheetId` | string | Yes | The ID of the sheet |
| `rowId` | string | Yes | The ID of the row |

#### `create_sheet_discussion`
Creates a new discussion thread on a sheet.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `sheetId` | string | Yes | The ID of the sheet |
| `commentText` | string | Yes | The discussion comment text |

#### `create_row_discussion`
Creates a new discussion thread on a specific row.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `sheetId` | string | Yes | The ID of the sheet |
| `rowId` | string | Yes | The ID of the row |
| `commentText` | string | Yes | The discussion comment text |

---

### Search

#### `search_sheets`
Searches for sheets by name across the account.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | Yes | Search query string |

#### `search_in_sheet`
Searches for a value within a specific sheet by ID.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `sheetId` | string | Yes | The ID of the sheet |
| `query` | string | Yes | Search query string |

#### `search_in_sheet_by_url`
Searches within a sheet using its Smartsheet URL.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `url` | string | Yes | The full Smartsheet URL of the sheet |
| `query` | string | Yes | Search query string |

#### `what_am_i_assigned_to_by_sheet_id`
Returns all rows in a sheet where the current user is assigned (contact columns).

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `sheetId` | string | Yes | The ID of the sheet |

#### `what_am_i_assigned_to_by_sheet_url`
Same as above, but using the sheet's Smartsheet URL.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `url` | string | Yes | The full Smartsheet URL of the sheet |

#### `search_folders`
Searches for folders by name.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | Yes | Search query string |

#### `search_workspaces`
Searches for workspaces by name.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | Yes | Search query string |

#### `search_reports`
Searches for reports by name.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | Yes | Search query string |

#### `search_dashboards`
Searches for dashboards by name.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | Yes | Search query string |

---

### Folders

#### `get_folder`
Retrieves a folder and its contents.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `folderId` | string | Yes | The ID of the folder |

#### `create_folder`
Creates a sub-folder inside an existing folder.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `folderId` | string | Yes | The ID of the parent folder |
| `name` | string | Yes | Name for the new folder |

---

### Update Requests

#### `create_update_request`
Sends an update request to collaborators for specific rows.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `sheetId` | string | Yes | The ID of the sheet |
| `rowIds` | array | Yes | Array of row IDs to include in the request |
| `sendTo` | array | Yes | Array of recipient objects with `email` |
| `subject` | string | No | Email subject |
| `message` | string | No | Email message body |
| `columnIds` | array | No | Specific columns to include |
| `includeAttachments` | boolean | No | Include row attachments |
| `includeDiscussions` | boolean | No | Include row discussions |

---

### Users

#### `get_current_user`
Retrieves the profile of the currently authenticated user.

_(No parameters)_

#### `get_user`
Retrieves a user by their ID.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `userId` | string | Yes | The ID of the user |

#### `list_users`
Lists users in the organization (admin access required).

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `email` | string | No | Filter by email address |
| `include` | string | No | Elements to include |
| `pageSize` | number | No | Users per page |
| `page` | number | No | Page number |

---

### Workspaces

#### `get_workspaces`
Lists all workspaces accessible to the current user.

_(No parameters)_

#### `get_workspace`
Retrieves a workspace and its contents.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `workspaceId` | string | Yes | The ID of the workspace |

#### `create_workspace`
Creates a new workspace.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | Yes | Name for the new workspace |

#### `create_workspace_folder`
Creates a folder inside a workspace.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `workspaceId` | string | Yes | The ID of the workspace |
| `name` | string | Yes | Name for the new folder |

---

## API Endpoint Coverage

**Legend:**
- **Yes**: Covered by an MCP tool
- **No**: Not yet covered
- **Consider**: Could work but has limitations (large responses, binary data, pagination)
- **N/A**: Not suitable for MCP (binary data, OAuth flows, streaming)

| API Path | Covered? | HTTP Method(s) | Tool(s) | MCP Suitable? |
|----------|----------|----------------|---------|---------------|
| `/contacts` | No | GET | — | Consider |
| `/contacts/{contactId}` | No | GET | — | Yes |
| `/events` | No | GET | — | No |
| `/folders/{folderId}` | Yes | GET | `get_folder` | Yes |
| `/folders/{folderId}/folders` | Yes | POST | `create_folder` | Yes |
| `/folders/{folderId}/sheets` | Yes | POST | `create_sheet` | Yes |
| `/search` | No | GET | — | Consider |
| `/search/sheets` | Yes | GET | `search_sheets` | Yes |
| `/search/sheets/{sheetId}` | Yes | GET | `search_in_sheet`, `search_in_sheet_by_url` | Yes |
| `/sheets` | Yes | POST | `create_sheet` | Yes |
| `/sheets/{sheetId}` | Yes | GET | `get_sheet`, `get_sheet_by_url` | Yes |
| `/sheets/{sheetId}/copy` | Yes | POST | `copy_sheet` | Yes |
| `/sheets/{sheetId}/discussions` | Yes | GET, POST | `get_discussions_by_sheet_id`, `create_sheet_discussion` | Yes |
| `/sheets/{sheetId}/rows` | Yes | GET, POST, PUT, DELETE | `add_rows`, `update_rows`, `delete_rows` | Yes |
| `/sheets/{sheetId}/rows/{rowId}` | Yes | GET | `get_row` | Yes |
| `/sheets/{sheetId}/rows/{rowId}/columns/{columnId}/history` | Yes | GET | `get_cell_history` | Yes |
| `/sheets/{sheetId}/rows/{rowId}/discussions` | Yes | GET, POST | `get_discussions_by_row_id`, `create_row_discussion` | Yes |
| `/sheets/{sheetId}/summary` | Yes | GET | `get_sheet_summary` | Yes |
| `/sheets/{sheetId}/summary/fields` | Yes | GET, POST, PUT, DELETE | `get_sheet_summary_fields`, `add_sheet_summary_fields`, `update_sheet_summary_fields`, `delete_sheet_summary_fields` | Yes |
| `/sheets/{sheetId}/updaterequests` | Yes | POST | `create_update_request` | Yes |
| `/sheets/{sheetId}/version` | Yes | GET | `get_sheet_version` | Yes |
| `/users` | Yes | GET | `list_users` | Consider |
| `/users/me` | Yes | GET | `get_current_user` | Yes |
| `/users/{userId}` | Yes | GET | `get_user` | Yes |
| `/workspaces` | Yes | GET, POST | `get_workspaces`, `create_workspace` | Yes |
| `/workspaces/{workspaceId}` | Yes | GET | `get_workspace` | Yes |
| `/workspaces/{workspaceId}/folders` | Yes | POST | `create_workspace_folder` | Yes |

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SMARTSHEET_API_KEY` | Yes | — | Your Smartsheet API token |
| `SMARTSHEET_ENDPOINT` | No | `https://api.smartsheet.com/2.0` | API base URL |
| `ALLOW_DELETE_TOOLS` | No | `false` | Set to `true` to enable `delete_rows` and `delete_sheet_summary_fields` |

## Development

### Prerequisites

- Node.js 16 or higher
- npm 7 or higher

### Commands

```bash
npm run build      # Compile TypeScript
npm run dev        # Build and start
npm run start      # Start (requires prior build)
npm test           # Run tests
npm run typecheck  # Type-check without emitting
```

### Project Structure

```
src/
  ├── apis/
  │   ├── smartsheet-api.ts              # Base API class
  │   ├── smartsheet-sheet-api.ts        # Sheets, rows, columns, cell history
  │   ├── smartsheet-summary-api.ts      # Sheet summary fields (GET/POST/PUT/DELETE)
  │   ├── smartsheet-discussion-api.ts   # Discussions & comments
  │   ├── smartsheet-folder-api.ts       # Folders
  │   ├── smartsheet-search-api.ts       # Search
  │   ├── smartsheet-user-api.ts         # Users
  │   └── smartsheet-workspace-api.ts    # Workspaces
  ├── tools/
  │   ├── smartsheet-sheet-tools.ts
  │   ├── smartsheet-summary-tools.ts
  │   ├── smartsheet-discussion-tools.ts
  │   ├── smartsheet-folder-tools.ts
  │   ├── smartsheet-search-tools.ts
  │   ├── smartsheet-update-request-tools.ts
  │   ├── smartsheet-user-tools.ts
  │   └── smartsheet-workspace-tools.ts
  ├── smartsheet-types/                  # TypeScript interfaces
  └── utils/
      └── response-limiter.ts            # Truncates large API responses for MCP
scripts/
  ├── setup-claude-config.sh
  ├── create_metrics_sheet.py
  └── create_summary_fields.py
```

### Adding New Tools

Every tool follows the same three-layer pattern:

1. **API class** (`src/apis/smartsheet-*.ts`) — thin wrapper around `fetch`
2. **Tools file** (`src/tools/smartsheet-*-tools.ts`) — registers `server.tool()` with Zod schemas
3. **Registration** (`src/index.ts`) — imports and calls the tools function with `(server, api, allowDeleteTools)`

Destructive tools must be gated behind the `allowDeleteTools` flag.

### Conventional Commits

- `feat`: New feature (minor version bump)
- `fix`: Bug fix (patch version bump)
- `docs`: Documentation only
- `style`: No code meaning change
- `refactor`: Neither fix nor feature
- `perf`: Performance improvement
- `test`: Adding or updating tests
- `chore`: Build process or tooling
