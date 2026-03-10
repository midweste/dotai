"""Tests for BuildAgent with mock LLM."""

import json

from src.models import Memory, MemoryLink
from src.git import GitLogParser
from src.build import BuildAgent


class MockLLMClient:
    """Mock LLM client that returns pre-defined responses."""

    def __init__(self, response: dict):
        self._response = response
        self.calls = []

    def chat(self, messages: list[dict], *, temperature: float = 0.2,
             max_tokens: int = 16384) -> str:
        self.calls.append(messages)
        return json.dumps(self._response)

    def get_model_info(self) -> dict:
        return {
            "context_length": 1_000_000,
            "max_completion_tokens": 65_536,
            "name": "mock-model",
        }

    def validate_model(self) -> None:
        pass  # Always valid in tests


class TestBuildAgent:
    def _make_agent(self, components, llm_response):
        mock_llm = MockLLMClient(llm_response)

        # Patch the parser to return canned data
        class PatchedParser(GitLogParser):
            def get_file_list(self, *, since_hash=None, limit=None):
                return """commit aaa111
Author: Dev
Date: 2026-03-09 10:00:00 -0500

Add auth service

Type: feature
Confidence: high

 src/auth.py | 50 ++++++++++++++++++++
 1 file changed, 50 insertions(+)

---END_COMMIT---"""

            def get_current_hash(self):
                return "aaa111"

        return BuildAgent(
            components["db"],
            components["memory_store"],
            components["link_store"],
            components["build_meta_store"],
            PatchedParser(),
            mock_llm,
        ), mock_llm

    def test_build_creates_memories(self, components):
        """Build should create new memories from LLM output."""
        agent, mock = self._make_agent(components, {
            "new_memories": [
                {
                    "summary": "Auth service uses JWT tokens",
                    "type": "decision",
                    "confidence": "high",
                    "importance": 0.8,
                    "source_commits": ["aaa111"],
                    "files": ["src/auth.py"],
                }
            ],
            "update_memories": [],
            "deactivate_memory_ids": [],
            "new_links": [],
        })
        result = agent.build()
        assert result["status"] == "success"
        assert result["new_memories"] == 1
        assert result["commits_processed"] == 1

        # Verify memory was stored
        memories = components["memory_store"].list_all()
        assert len(memories) == 1
        assert memories[0].summary == "Auth service uses JWT tokens"

    def test_build_records_meta(self, components):
        """Build should record build metadata."""
        agent, _ = self._make_agent(components, {
            "new_memories": [
                {
                    "summary": "Placeholder",
                    "type": "context",
                    "confidence": "medium",
                    "importance": 0.5,
                    "source_commits": ["aaa111"],
                    "files": [],
                }
            ],
            "update_memories": [],
            "deactivate_memory_ids": [], "new_links": [],
        })
        agent.build()
        last = components["build_meta_store"].get_last()
        assert last is not None
        assert last.last_commit == "aaa111"
        assert last.build_type == "full"

    def test_build_creates_links(self, components):
        """Build should create memory links from LLM output."""
        agent, _ = self._make_agent(components, {
            "new_memories": [
                {
                    "key": "memory_a",
                    "summary": "Memory A",
                    "type": "decision",
                    "confidence": "high",
                    "importance": 0.8,
                    "source_commits": ["aaa111"],
                    "files": [],
                },
                {
                    "key": "memory_b",
                    "summary": "Memory B",
                    "type": "pattern",
                    "confidence": "high",
                    "importance": 0.7,
                    "source_commits": ["aaa111"],
                    "files": [],
                },
            ],
            "update_memories": [],
            "deactivate_memory_ids": [],
            "new_links": [
                {
                    "source": "memory_a",
                    "target": "memory_b",
                    "relationship": "related_to",
                    "strength": 0.8,
                }
            ],
        })
        result = agent.build()
        assert result["new_links"] == 1

    def test_build_creates_links_with_string_keys(self, components):
        """Build should resolve string keys to actual DB IDs for linking."""
        agent, _ = self._make_agent(components, {
            "new_memories": [
                {
                    "key": "first_mem",
                    "summary": "First memory",
                    "type": "decision",
                    "confidence": "high",
                    "importance": 0.8,
                    "source_commits": ["aaa111"],
                    "files": ["src/a.py"],
                },
                {
                    "key": "second_mem",
                    "summary": "Second memory",
                    "type": "pattern",
                    "confidence": "high",
                    "importance": 0.7,
                    "source_commits": ["aaa111"],
                    "files": ["src/b.py"],
                },
            ],
            "update_memories": [],
            "deactivate_memory_ids": [],
            "new_links": [
                {
                    "source": "first_mem",
                    "target": "second_mem",
                    "relationship": "implements",
                    "strength": 0.9,
                }
            ],
        })
        result = agent.build()
        assert result["new_memories"] == 2
        assert result["new_links"] == 1
        # Verify the link exists
        memories = components["memory_store"].list_all()
        links = components["link_store"].get_links_for(memories[0].id)
        assert len(links) == 1

    def test_build_skips_links_with_unresolvable_refs(self, components):
        """Build should skip links with unresolvable string keys."""
        agent, _ = self._make_agent(components, {
            "new_memories": [
                {
                    "key": "only_mem",
                    "summary": "Only memory",
                    "type": "context",
                    "confidence": "medium",
                    "importance": 0.5,
                    "source_commits": ["aaa111"],
                    "files": [],
                },
            ],
            "update_memories": [],
            "deactivate_memory_ids": [],
            "new_links": [
                {
                    "source": "only_mem",
                    "target": "nonexistent_key",
                    "relationship": "related_to",
                    "strength": 0.5,
                }
            ],
        })
        result = agent.build()
        assert result["new_memories"] == 1
        assert result["new_links"] == 0

    def test_build_deactivates_memories(self, components):
        """Build should deactivate memories marked by LLM."""
        # Create a memory, then build with deactivation
        agent, _ = self._make_agent(components, {
            "new_memories": [
                {
                    "summary": "Will be deactivated",
                    "type": "decision",
                    "confidence": "high",
                    "importance": 0.8,
                    "source_commits": ["aaa111"],
                    "files": [],
                },
            ],
            "update_memories": [],
            "deactivate_memory_ids": [],
            "new_links": [],
        })
        result = agent.build()
        memories = components["memory_store"].list_all()
        assert len(memories) == 1
        old_id = memories[0].id

        # Second build that deactivates the memory
        agent2, _ = self._make_agent(components, {
            "new_memories": [
                {
                    "summary": "Replacement memory",
                    "type": "decision",
                    "confidence": "high",
                    "importance": 0.9,
                    "source_commits": ["aaa111"],
                    "files": [],
                },
            ],
            "update_memories": [],
            "deactivate_memory_ids": [old_id],
            "new_links": [],
        })
        result2 = agent2.build()
        assert result2["deactivated_memories"] == 1
        fetched = components["memory_store"].get(old_id)
        assert fetched.active is False

    def test_build_always_does_full_rebuild(self, components):
        """Build should always drop and recreate (full rebuild)."""
        # First build creates a memory
        agent, _ = self._make_agent(components, {
            "new_memories": [
                {
                    "summary": "Should be gone after rebuild",
                    "type": "context",
                    "confidence": "medium",
                    "importance": 0.5,
                    "source_commits": ["aaa111"],
                    "files": [],
                }
            ],
            "update_memories": [],
            "deactivate_memory_ids": [],
            "new_links": [],
        })
        result = agent.build()
        assert result["new_memories"] == 1

        # Second build (always rebuilds) — old memory should be gone
        agent2, _ = self._make_agent(components, {
            "new_memories": [
                {
                    "summary": "Fresh start",
                    "type": "context",
                    "confidence": "medium",
                    "importance": 0.5,
                    "source_commits": ["aaa111"],
                    "files": [],
                }
            ],
            "update_memories": [],
            "deactivate_memory_ids": [],
            "new_links": [],
        })
        result2 = agent2.build()
        assert result2["status"] == "success"
        memories = components["memory_store"].list_all(active_only=False)
        # Only the new memory should exist
        assert len(memories) == 1
        assert memories[0].summary == "Fresh start"

    def test_llm_called_with_commits(self, components):
        """Build should send commits to the LLM."""
        agent, mock = self._make_agent(components, {
            "new_memories": [
                {
                    "summary": "Placeholder",
                    "type": "context",
                    "confidence": "medium",
                    "importance": 0.5,
                    "source_commits": ["aaa111"],
                    "files": [],
                }
            ],
            "update_memories": [],
            "deactivate_memory_ids": [], "new_links": [],
        })
        agent.build()
        assert len(mock.calls) == 1
        user_msg = mock.calls[0][1]["content"]
        assert "aaa111" in user_msg
        assert "Add auth service" in user_msg

    def test_build_result_has_no_decay(self, components):
        """Build result should not include decayed_memories key."""
        agent, _ = self._make_agent(components, {
            "new_memories": [
                {
                    "summary": "Placeholder",
                    "type": "context",
                    "confidence": "medium",
                    "importance": 0.5,
                    "source_commits": ["aaa111"],
                    "files": [],
                }
            ],
            "update_memories": [],
            "deactivate_memory_ids": [],
            "new_links": [],
        })
        result = agent.build()
        assert "decayed_memories" not in result

    def test_build_auto_deactivates_superseded_memories(self, components):
        """Supersedes links should auto-deactivate the target memory."""
        # Pre-create a memory that will be superseded
        from src.models import Memory
        old = Memory(
            summary="Old approach",
            type="decision",
            confidence="high",
            importance=0.8,
            source_commits=["bbb222"],
            files=["src/old.py"],
        )
        old = components["memory_store"].create(old)
        old_id = old.id

        # Build with a supersedes link pointing to the old memory
        agent, _ = self._make_agent(components, {
            "new_memories": [
                {
                    "key": "new_approach",
                    "summary": "New approach replaces old",
                    "type": "decision",
                    "confidence": "high",
                    "importance": 0.9,
                    "source_commits": ["aaa111"],
                    "files": ["src/new.py"],
                },
            ],
            "update_memories": [],
            "deactivate_memory_ids": [],  # NOT explicitly deactivating
            "new_links": [
                {
                    "source": "new_approach",
                    "target": old_id,
                    "relationship": "supersedes",
                    "strength": 0.9,
                }
            ],
        })
        result = agent.build()
        assert result["new_memories"] == 1
        assert result["new_links"] == 1
        assert result["deactivated_memories"] == 1

        # Verify old memory is deactivated
        fetched = components["memory_store"].get(old_id)
        assert fetched.active is False
