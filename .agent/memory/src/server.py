"""MCP server with tool registration and stdio transport."""

import json
import sys
from dataclasses import asdict
from typing import Callable, Optional
from urllib.parse import urlparse


class McpServer:
    """MCP SDK server with tool registration and stdio transport.

    Uses MCP roots to detect the project directory at runtime.
    Components (stores, build agent, etc.) are created lazily on
    the first tool call via a factory function.
    """

    def __init__(self, component_factory: Callable):
        self._factory = component_factory
        self._components: Optional[dict] = None

    async def _ensure_components(self, ctx) -> dict:
        """Lazily resolve project root from MCP roots and create components."""
        if self._components is not None:
            return self._components

        project_root = None
        try:
            result = await ctx.session.list_roots()
            if result.roots:
                uri = str(result.roots[0].uri)
                parsed = urlparse(uri)
                if parsed.scheme == "file":
                    project_root = parsed.path
        except Exception as e:
            print(
                f"  warning: could not resolve MCP roots: {e}",
                file=sys.stderr, flush=True,
            )

        # Override the single source of truth so all modules (db, llm, git)
        # use the MCP client's project, not where the server code lives.
        if project_root:
            import src
            src.PROJECT_ROOT = project_root

        project_name = project_root.rstrip("/").rsplit("/", 1)[-1] if project_root else "unknown"
        print(
            f"  project: {project_name} ({project_root})",
            file=sys.stderr, flush=True,
        )

        self._components = self._factory(project_root=project_root)
        if self._components is None:
            raise RuntimeError("Component factory returned None")
        return self._components

    def run(self) -> None:
        """Start the MCP server over stdio."""
        from mcp.server.fastmcp import FastMCP, Context

        mcp = FastMCP("project-memory")
        server = self  # capture for closures

        @mcp.tool()
        async def memory_debug_roots(ctx: Context) -> str:
            """DEBUG: Check if the MCP client sends workspace roots."""
            try:
                result = await ctx.session.list_roots()
                roots_data = [
                    {"uri": str(r.uri), "name": r.name}
                    for r in result.roots
                ]
                return json.dumps({"roots": roots_data, "count": len(roots_data)}, indent=2)
            except Exception as e:
                return json.dumps({"error": str(e), "type": type(e).__name__})

        @mcp.tool()
        async def memory_search(
            ctx: Context,
            query: str,
            type: str = "",
            match: str = "all",
            min_importance: float = 0.0,
            limit: int = 20,
        ) -> str:
            """Full-text search across memory summaries.

            Secondary retrieval method. All filters optional.
            Returns matching memories sorted by FTS rank.
            """
            c = await server._ensure_components(ctx)
            memories = c["memory_store"].search(
                query,
                memory_type=type or None,
                match=match,
                min_importance=min_importance,
                limit=limit,
            )
            for m in memories:
                c["memory_store"].touch(m.id)
            return json.dumps([m.to_dict() for m in memories], indent=2)

        @mcp.tool()
        async def memory_get(
            ctx: Context, memory_id: int, include_links: bool = True,
        ) -> str:
            """Get a specific memory by ID with full detail.

            Includes all linked memories when include_links is True.
            """
            c = await server._ensure_components(ctx)
            memory = c["memory_store"].get(memory_id)
            if memory is None:
                return json.dumps({"error": f"Memory {memory_id} not found"})

            c["memory_store"].touch(memory.id)
            result = memory.to_dict()

            if include_links:
                links = c["link_store"].get_links_for(memory.id)
                result["links"] = [asdict(l) for l in links]
                linked_ids = c["link_store"].get_linked_ids(memory.id)
                result["linked_memories"] = [
                    c["memory_store"].get(lid).to_dict()
                    for lid in linked_ids
                    if c["memory_store"].get(lid)
                ]

            return json.dumps(result, indent=2)

        @mcp.tool()
        async def memory_stats(ctx: Context) -> str:
            """Overview of the knowledge store.

            Returns total count, counts by type/confidence, top files,
            average importance, and last build info.
            """
            c = await server._ensure_components(ctx)
            stats = c["memory_store"].stats()
            last_build = c["build_meta_store"].get_last()
            stats["last_build"] = asdict(last_build) if last_build else None
            return json.dumps(stats, indent=2)

        @mcp.tool()
        async def memory_inspect(ctx: Context, query: str) -> str:
            """Debug/inspect the memory system internals.

            Commands: tables, memories, memory <id>, links, builds, stats, schema, fts, help
            """
            c = await server._ensure_components(ctx)
            return c["inspector"].inspect(query)

        @mcp.tool()
        async def memory_build(ctx: Context, limit: int = 0) -> str:
            """Incremental build — process new commits since the last build.

            Only processes commits not yet seen. Safe to call frequently.
            Set limit to restrict the number of commits processed (0 = unlimited).
            """
            c = await server._ensure_components(ctx)
            if not c.get("build_agent"):
                return json.dumps({"error": "Build agent not available"})
            result = c["build_agent"].build(limit=limit or None)
            return json.dumps(result, indent=2)

        @mcp.tool()
        async def memory_rebuild(ctx: Context, limit: int = 0) -> str:
            """Full rebuild — drop all memories and reprocess from git history.

            Destructive: deletes all existing memories, links, and build metadata,
            then reprocesses the entire git history. Use when schema has changed
            or memories need regenerating with an updated build prompt.
            Set limit to restrict the number of commits processed (0 = unlimited).
            """
            c = await server._ensure_components(ctx)
            if not c.get("build_agent"):
                return json.dumps({"error": "Build agent not available"})
            result = c["build_agent"].rebuild(limit=limit or None)
            return json.dumps(result, indent=2)

        mcp.run(transport="stdio")

    def cleanup(self) -> None:
        """Close the database connection if components were created."""
        if self._components and "db" in self._components:
            self._components["db"].close()
