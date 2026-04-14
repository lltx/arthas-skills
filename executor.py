#!/usr/bin/env python3
"""
Arthas MCP Skill Executor
=========================
Connects to the fixed Arthas MCP streamable HTTP endpoint and performs
tool discovery or execution.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import Any


try:
    from mcp import ClientSession
    from mcp.client.streamable_http import streamablehttp_client
    from mcp.types import EmbeddedResource, ImageContent, TextContent
    HAS_MCP = True
except ImportError:
    HAS_MCP = False


def load_server_config() -> tuple[str, str]:
    config_path = Path(__file__).with_name("mcp-config.json")
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with config_path.open("r", encoding="utf-8") as handle:
        config = json.load(handle)

    servers = config.get("mcpServers", {})
    if not servers:
        raise ValueError("No MCP servers were defined in mcp-config.json")

    server_name, server = next(iter(servers.items()))
    server_type = server.get("type")
    server_url = server.get("url")

    if server_type != "streamableHttp":
        raise ValueError(f"Unsupported MCP transport: {server_type!r}")
    if not server_url:
        raise ValueError("Missing MCP server URL in configuration")

    return server_name, server_url


def serialize_content_item(item: Any) -> dict[str, Any]:
    if isinstance(item, TextContent):
        return {"type": item.type, "text": item.text}
    if isinstance(item, ImageContent):
        return {
            "type": item.type,
            "mimeType": item.mimeType,
            "data": item.data,
        }
    if isinstance(item, EmbeddedResource):
        resource = item.resource
        return {
            "type": item.type,
            "resource": resource.model_dump(by_alias=True, exclude_none=True),
        }
    if hasattr(item, "model_dump"):
        return item.model_dump(by_alias=True, exclude_none=True)
    if hasattr(item, "__dict__"):
        return item.__dict__
    return {"value": str(item)}


class ArthasMCPExecutor:
    def __init__(self, server_name: str, server_url: str):
        self.server_name = server_name
        self.server_url = server_url

    async def list_tools(self) -> list[dict[str, Any]]:
        async with streamablehttp_client(self.server_url) as (read_stream, write_stream, _):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                result = await session.list_tools()
                return [
                    {
                        "name": tool.name,
                        "description": tool.description,
                        "inputSchema": tool.inputSchema,
                    }
                    for tool in result.tools
                ]

    async def describe_tool(self, tool_name: str) -> dict[str, Any]:
        tools = await self.list_tools()
        for tool in tools:
            if tool["name"] == tool_name:
                return tool
        raise KeyError(f"Tool not found: {tool_name}")

    async def call_tool(self, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        async with streamablehttp_client(self.server_url) as (read_stream, write_stream, _):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                result = await session.call_tool(tool_name, arguments)
                return {
                    "tool": tool_name,
                    "isError": result.isError,
                    "structuredContent": result.structuredContent,
                    "content": [serialize_content_item(item) for item in result.content],
                }


def build_error_message(error: Exception, server_name: str, server_url: str) -> str:
    details = str(error).strip() or error.__class__.__name__
    return (
        f"Failed to communicate with MCP server '{server_name}' at {server_url}.\n"
        f"Reason: {details}\n\n"
        "Checks:\n"
        "- confirm Arthas MCP is exposed at the fixed /mcp route\n"
        "- confirm the service speaks streamable HTTP MCP, not only the Arthas web console\n"
        "- confirm the local Python environment has the 'mcp' package installed\n"
        "- confirm the target JVM / Arthas attachment has been prepared on the server side"
    )


async def async_main() -> int:
    parser = argparse.ArgumentParser(description="Arthas MCP skill executor")
    parser.add_argument("--list", action="store_true", help="List all available tools")
    parser.add_argument("--describe", metavar="TOOL", help="Describe one tool")
    parser.add_argument("--call", metavar="JSON", help="Call a tool with JSON input")
    args = parser.parse_args()

    if not HAS_MCP:
        print("Error: Python package 'mcp' is not installed. Run: pip install mcp", file=sys.stderr)
        return 1

    if not any((args.list, args.describe, args.call)):
        parser.print_help()
        return 0

    try:
        server_name, server_url = load_server_config()
        executor = ArthasMCPExecutor(server_name, server_url)

        if args.list:
            tools = await executor.list_tools()
            print(json.dumps(tools, indent=2, ensure_ascii=False))
            return 0

        if args.describe:
            tool = await executor.describe_tool(args.describe)
            print(json.dumps(tool, indent=2, ensure_ascii=False))
            return 0

        if args.call:
            payload = json.loads(args.call)
            tool_name = payload["tool"]
            arguments = payload.get("arguments", {})
            result = await executor.call_tool(tool_name, arguments)
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return 0

    except KeyError as error:
        print(str(error), file=sys.stderr)
        return 1
    except Exception as error:
        try:
            server_name, server_url = load_server_config()
        except Exception:
            server_name, server_url = "unknown", "unknown"
        print(build_error_message(error, server_name, server_url), file=sys.stderr)
        return 1

    return 0


def main() -> None:
    raise SystemExit(asyncio.run(async_main()))


if __name__ == "__main__":
    main()
