# CLAUDE.md

This file contains configuration and instructions for Claude to help with this repository.

## Repository Overview
This repository contains a Smartsheet Model Context Protocol (MCP) server that provides tools for interacting with the Smartsheet API.

## GitHub CLI Setup and Authentication

To use GitHub CLI (gh) commands, you need to authenticate first:

```bash
# Log in to GitHub CLI
gh auth login

# Follow the prompts to complete authentication
# This will open a browser window and ask for a one-time code
```

## GitHub Commands

### Creating Issues
```bash
# Basic issue creation
gh issue create --title "Issue title" --body "Issue description"

# With labels and assignees
gh issue create --title "Issue title" --body "Issue description" --label "bug,enhancement" --assignee "username"
```

### Creating Pull Requests
```bash
# Basic PR creation
gh pr create --title "PR title" --body "PR description"

# With reviewers and labels
gh pr create --title "PR title" --body "PR description" --reviewer "username" --label "enhancement"

# Using a HEREDOC for better formatting of the PR body
gh pr create --title "PR title" --body "$(cat <<'EOF'
## Summary
Summary text here

## Test plan
- Testing details
EOF
)"
```

### Updating Pull Requests
```bash
# Update title and body
gh pr edit [PR number] --title "New title" --body "New description"

# Add/remove labels
gh pr edit [PR number] --add-label "enhancement" --remove-label "bug"

# Add/remove reviewers
gh pr edit [PR number] --add-reviewer "username" --remove-reviewer "another-user"
```

### Fetching PR Comments
```bash
# View PR with comments
gh pr view [PR number] --comments

# Get comments in JSON format
gh pr view [PR number] --comments --json comments
```

### Adding Comments to PRs
```bash
# Add a comment to a PR
gh pr comment [PR number] --body "This looks good!"
```

## Git Workflow

### Creating a new branch
```bash
# Create and switch to a new branch
git checkout -b feature/branch-name
```

### Committing changes with conventional commit messages
```bash
# Stage changes
git add .

# Commit with conventional format
git commit -m "$(cat <<'EOF'
feat: short summary of changes

- Detailed bullet point 1
- Detailed bullet point 2

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

### Pushing and creating a PR
```bash
# Push with branch tracking
git push -u origin feature/branch-name

# Create PR using the GitHub CLI
gh pr create --title "PR Title" --body "PR description"
```

## Repository Structure
```
.github/
  ├── ISSUE_TEMPLATE/
  │   ├── bug_report.md      # Template for bug reports
  │   ├── feature_request.md # Template for feature requests
  │   └── config.yml         # Issue template configuration
  └── PULL_REQUEST_TEMPLATE/
      └── default.md         # Default PR template
src/
  ├── apis/
  │   ├── smartsheet-api.ts              # Base API class — all domain APIs hang off this
  │   ├── smartsheet-sheet-api.ts        # Sheets (CRUD, rows, columns)
  │   ├── smartsheet-summary-api.ts      # Sheet Summary fields (GET/POST/PUT/DELETE)
  │   ├── smartsheet-discussion-api.ts   # Discussions & comments
  │   ├── smartsheet-folder-api.ts       # Folders
  │   ├── smartsheet-search-api.ts       # Search
  │   ├── smartsheet-user-api.ts         # Users
  │   └── smartsheet-workspace-api.ts    # Workspaces
  ├── tools/
  │   ├── smartsheet-sheet-tools.ts
  │   ├── smartsheet-summary-tools.ts    # get/add/update/delete sheet summary fields
  │   ├── smartsheet-discussion-tools.ts
  │   ├── smartsheet-folder-tools.ts
  │   ├── smartsheet-search-tools.ts
  │   ├── smartsheet-update-request-tools.ts
  │   ├── smartsheet-user-tools.ts
  │   └── smartsheet-workspace-tools.ts
  ├── smartsheet-types/                  # TypeScript interfaces
  └── utils/
      └── response-limiter.ts            # Truncates large API responses for MCP
```

## Development Commands

```bash
# Build TypeScript
npm run build

# Run in dev mode (ts-node / watch)
npm run dev

# Run tests
npm test
```

## Adding New Tools — Pattern

Every tool follows the same three-layer pattern:

1. **API class** (`src/apis/smartsheet-*.ts`) — thin wrapper around `fetch`, calls `this.api.makeRequest()`
2. **Tools file** (`src/tools/smartsheet-*-tools.ts`) — registers `server.tool()` with Zod schemas
3. **Registration** (`src/index.ts`) — imports the tools function and calls it with `(server, api, allowDeleteTools)`

Delete-capable tools must be gated behind the `allowDeleteTools` flag.

## Sheet Summary Fields

- **Column range syntax** `[Column Name]:[Column Name]` references the **entire column** — covers all current and future rows automatically.
- **Column type matters** — `MIN`/`MAX` on dates only work if the column type is `DATE`, not `TEXT_NUMBER`. Convert via `PUT /sheets/{id}/columns/{colId}` with `{ "type": "DATE" }`.
- **Transient #REF bug** — if a formula is stored as `=SUM(#REF:#REF)`, the column reference failed to resolve at creation time. Fix by re-PUTting the same formula to force re-resolution.
- **Percent fields** — formula should return a decimal (0–1), not 0–100. Pair with `numberFormat=3` format string.
- **COUNTIF vs COUNTIFS** — use `COUNTIFS` (plural) when the criterion is a function like `ISDATE(@cell)`.

### Format String Reference

Format strings are 17-element comma-separated values (indices 0–16):

| Index | Field | Common values |
|-------|-------|---------------|
| 11 | currency | `13` = USD ($) |
| 12 | decimalCount | `0`–`5` |
| 13 | thousandsSeparator | `1` = yes |
| 14 | numberFormat | `1` = NUMBER, `2` = CURRENCY, `3` = PERCENT |

**Quick reference:**
```
Currency $ no decimal : ,,,,,,,,,,,13,0,1,2,,
Integer with commas   : ,,,,,,,,,,,,0,1,1,,
Percent (0–1 value)   : ,,,,,,,,,,,,0,,3,,
```

## Conventional Commits

This repository follows the conventional commits standard:

- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation changes
- `style`: Changes that don't affect code meaning
- `refactor`: Code changes that neither fix bugs nor add features
- `test`: Adding/modifying tests
- `chore`: Changes to build process or auxiliary tools

## Code Conventions

- Use `limitResponseSize()` on all GET tool responses to prevent MCP context overflow.
- Gate destructive tools (delete, bulk-modify) behind the `allowDeleteTools` boolean passed into every tools registration function.
- Always pass `sheetId` as `string` in Zod schemas — Smartsheet IDs exceed JavaScript's safe integer range.