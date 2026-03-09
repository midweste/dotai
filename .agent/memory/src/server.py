"""MCP server with tool registration and stdio transport."""

import json
from dataclasses import asdict
from typing import Optional

from src.stores import MemoryStore, LinkStore, BuildMetaStore
from src.inspector import Inspector


class McpServer:
    """MCP SDK server with tool registration and stdio transport."""

    def __init__(
        self,
        memory_store: MemoryStore,
        link_store: LinkStore,
        build_meta_store: BuildMetaStore,
        inspector: Inspector,
        build_agent: Optional['object'] = None,
    ):
        self._memories = memory_store
        self._links = link_store
        self._build_meta = build_meta_store
        self._inspector = inspector
        self._build_agent = build_agent

    def run(self) -> None:
        """Start the MCP server over stdio."""
        from mcp.server.fastmcp import FastMCP

        mcp = FastMCP("project-memory")

        @mcp.tool()
        def memory_query_file(
            path: str,
            limit: int = 20,
            min_importance: float = 0.0,
            include_links: bool = False,
        ) -> str:
            """Query memories associated with a file path or directory.

            Primary retrieval method. Returns memories sorted by importance.
            Use a directory path ending with / to match all files under it.
            """
            memories = self._memories.query_by_file(
                path, limit=limit, min_importance=min_importance,
            )
            # Touch each returned memory
            for m in memories:
                self._memories.touch(m.id)

            result = [m.to_dict() for m in memories]

            if include_links:
                for i, m in enumerate(memories):
                    links = self._links.get_links_for(m.id)
                    linked_ids = self._links.get_linked_ids(m.id)
                    linked_memories = [
                        self._memories.get(lid)
                        for lid in linked_ids
                    ]
                    result[i]["linked_memories"] = [
                        lm.to_dict() for lm in linked_memories if lm
                    ]

            return json.dumps(result, indent=2)

        @mcp.tool()
        def memory_search(
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
            memories = self._memories.search(
                query,
                memory_type=type or None,
                match=match,
                min_importance=min_importance,
                limit=limit,
            )
            for m in memories:
                self._memories.touch(m.id)
            return json.dumps([m.to_dict() for m in memories], indent=2)

        @mcp.tool()
        def memory_get(memory_id: int, include_links: bool = True) -> str:
            """Get a specific memory by ID with full detail.

            Includes all linked memories when include_links is True.
            """
            memory = self._memories.get(memory_id)
            if memory is None:
                return json.dumps({"error": f"Memory {memory_id} not found"})

            self._memories.touch(memory.id)
            result = memory.to_dict()

            if include_links:
                links = self._links.get_links_for(memory.id)
                result["links"] = [asdict(l) for l in links]
                linked_ids = self._links.get_linked_ids(memory.id)
                result["linked_memories"] = [
                    self._memories.get(lid).to_dict()
                    for lid in linked_ids
                    if self._memories.get(lid)
                ]

            return json.dumps(result, indent=2)

        @mcp.tool()
        def memory_stats() -> str:
            """Overview of the knowledge store.

            Returns total count, counts by type/confidence, top files,
            average importance, and last build info.
            """
            stats = self._memories.stats()
            last_build = self._build_meta.get_last()
            stats["last_build"] = asdict(last_build) if last_build else None
            return json.dumps(stats, indent=2)

        @mcp.tool()
        def memory_inspect(query: str) -> str:
            """Debug/inspect the memory system internals.

            Commands: tables, memories, memory <id>, links, builds, stats, schema, fts, help
            """
            return self._inspector.inspect(query)

        if self._build_agent:
            @mcp.tool()
            def memory_build(limit: int = 0) -> str:
                """Incremental build — process new commits since the last build.

                Only processes commits not yet seen. Safe to call frequently.
                Set limit to restrict the number of commits processed (0 = unlimited).
                """
                result = self._build_agent.build(limit=limit or None)
                return json.dumps(result, indent=2)

            @mcp.tool()
            def memory_rebuild(limit: int = 0) -> str:
                """Full rebuild — drop all memories and reprocess from git history.

                Destructive: deletes all existing memories, links, and build metadata,
                then reprocesses the entire git history. Use when schema has changed
                or memories need regenerating with an updated build prompt.
                Set limit to restrict the number of commits processed (0 = unlimited).
                """
                result = self._build_agent.rebuild(limit=limit or None)
                return json.dumps(result, indent=2)

        mcp.run(transport="stdio")
