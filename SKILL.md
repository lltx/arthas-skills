---
name: arthas-skills
description: Use this skill when diagnosing Java applications with Arthas through the arthas-mcp-server, including thread analysis, hot methods, exceptions, class inspection, method tracing, watch/stack/monitor workflows, or when the user asks to use Arthas or Arthas MCP. This skill connects to a fixed streamable HTTP MCP endpoint at http://localhost:8563/mcp.
---

# Arthas MCP Server

This skill connects to a fixed Arthas MCP endpoint:

- `http://localhost:8563/mcp`

Use it when the user wants Arthas-based JVM diagnostics, including:

- Java process and runtime inspection
- Thread blocking, CPU spikes, and deadlock triage
- Method tracing and call-path analysis
- Class, bytecode, and classloader inspection
- Exception-path observation
- Online troubleshooting with Arthas commands exposed as MCP tools

## What To Load

- Start here for the workflow and command discipline.
- Read [references/arthas-workflows.md](references/arthas-workflows.md) when the task is about:
  - high CPU, blocking, deadlock, request latency, or hotspots
  - method entry/exit observation with `watch`
  - call stack or call path investigation with `stack` or `trace`
  - class decompilation / code inspection with `jad`
  - ongoing metrics with `monitor`

## Operating Rules

- Treat the endpoint as fixed. Do not ask the user to provide a host or port unless they explicitly ask to change the skill itself.
- Prefer low-risk diagnostics first. Start from broad observation before attaching high-cardinality tracing.
- If the user has not identified the application/process yet, use the Arthas MCP tools to discover the available JVM targets before deeper diagnostics.
- Explain performance risk before using commands that can add noticeable overhead, especially wide `trace`, frequent `watch`, or long-running `monitor`.
- Keep probes narrow:
  - target one class or method at a time
  - add conditions where possible
  - limit sample counts and duration when the tool supports it
- When the task is ambiguous, use this sequence:
  1. inspect available processes / sessions
  2. inspect runtime overview
  3. inspect threads or hotspots
  4. narrow to classes and methods
  5. trace or watch the smallest useful scope

## Tool Discovery

List the available Arthas MCP tools:

```bash
cd $SKILL_DIR
python executor.py --list
```

Inspect one tool's schema:

```bash
cd $SKILL_DIR
python executor.py --describe TOOL_NAME
```

Call a tool:

```bash
cd $SKILL_DIR
python executor.py --call '{"tool":"TOOL_NAME","arguments":{"key":"value"}}'
```

## Recommended Diagnostic Flow

### 1. Confirm target scope

- Find the available JVM / target-selection tools first.
- If multiple applications are present, select the target before deeper analysis.

### 2. Start broad

Prefer tools that map to Arthas commands such as:

- `dashboard`
- `thread`
- `sysprop`
- `sysenv`
- `jvm`

Use these to determine whether the problem looks like CPU saturation, blocked threads, GC pressure, classloader issues, or slow business methods.

### 3. Narrow to code paths

For code-level diagnosis, look for tools that map to:

- `jad`
- `sc`
- `sm`
- `trace`
- `stack`
- `watch`
- `monitor`

Recommended progression:

- Use `jad` / `sc` / `sm` to identify the exact class and method.
- Use `stack` when you need who-called-this visibility.
- Use `trace` when you need per-invocation timing along a call path.
- Use `watch` when you need parameters, return values, or thrown exceptions.
- Use `monitor` when you need a lightweight rolling view over time.

### 4. Summarize carefully

- Separate facts from inference.
- Include the exact class, method, condition, and sampling scope used.
- Mention if the MCP endpoint itself failed, timed out, or did not expose the expected tool.

## Failure Handling

If a call fails, first distinguish which layer failed:

- Skill/runtime issue: `python` or `mcp` package problem
- MCP transport issue: `http://localhost:8563/mcp` unreachable or returns protocol errors
- Arthas-side issue: target JVM not attached, command unsupported, or selection incomplete
- Input issue: wrong tool name or missing arguments

The current environment may expose the Arthas Console web UI on `http://localhost:8563/` even if `/mcp` is not enabled. If `--list` or `--describe` fails with session or protocol errors, report that the fixed endpoint exists in skill config but the MCP route may not be active yet.

## Response Style

- Keep operational summaries concise and evidence-based.
- For production-like troubleshooting, call out risky probes before using them.
- When possible, propose the next safest narrowing step instead of jumping straight to a broad trace.
