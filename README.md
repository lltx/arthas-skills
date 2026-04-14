# arthas-skills

Arthas MCP skill for diagnosing Java applications through a fixed streamable HTTP MCP endpoint.

## Files

- `SKILL.md`: skill definition and operating rules
- `executor.py`: local executor for listing, describing, and calling MCP tools
- `mcp-config.json`: MCP server configuration
- `references/arthas-workflows.md`: troubleshooting workflows and reporting guidance

## Usage

List tools:

```bash
python executor.py --list
```

Describe one tool:

```bash
python executor.py --describe TOOL_NAME
```

Call one tool:

```bash
python executor.py --call '{"tool":"TOOL_NAME","arguments":{"key":"value"}}'
```
