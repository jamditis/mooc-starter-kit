# MCP configuration examples — optional advanced

**Note:** Module 4 no longer centers on MCP. The current Module 4 material is in `docs/context-management.md` and `docs/cross-model-review.md`. MCP is still useful for specific integrations (connecting Claude to local files, specific databases, third-party services) but it's no longer the spine of the module.

## When to use MCP

- You need Claude to read from or write to a local data source repeatedly across many sessions
- You need to wire Claude into a third-party service (Airtable, Google Drive, etc.) that has an MCP server
- Your final project calls for a persistent integration

## When NOT to use MCP

- You only need the data for a single session (just paste or read the files)
- The data is already in the repo (use `sample-docs/` directly)
- You're doing context management or sub-agents — those don't need MCP

## What is MCP?

MCP (Model Context Protocol) lets Claude connect to external tools and data sources through a standard interface. The config file tells Claude which servers to start and what to call them.

## Files in this directory

### filesystem-example.json

Gives Claude access to files on your computer.

**Setup:**
1. Copy this file to your Claude config directory
2. Replace `YOUR_USERNAME` with your actual username
3. Replace the path with the directory you want Claude to access

**Config file location:**
- macOS / Linux: `~/.claude/mcp.json`
- Windows: `%APPDATA%\claude\mcp.json`

Restart Claude Code after editing.

## Security notes

- Only grant access to directories you actually need
- Never include sensitive directories like `.ssh`, `.aws`, or anything with credentials
- Review what each MCP server requests before installing it — third-party servers run with the access you give them

## Common issues

- **"Server not found"** — make sure Node.js is installed and `npx` is on your PATH
- **"Permission denied"** — check the directory exists and you have read access
- **Changes not taking effect** — restart Claude Code after editing the config

## More servers

Find additional MCP servers at: https://github.com/modelcontextprotocol/servers
