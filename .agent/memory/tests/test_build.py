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
            components["decay_engine"],
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
            "new_memories": [], "update_memories": [],
            "deactivate_memory_ids": [], "new_links": [],
        })
        agent.build()
        last = components["build_meta_store"].get_last()
        assert last is not None
        assert last.last_commit == "aaa111"
        assert last.build_type == "incremental"

    def test_build_creates_links(self, components):
        """Build should create memory links from LLM output."""
        # Pre-create memories to link
        m1 = components["memory_store"].create(Memory(
            summary="Existing A", type="decision",
        ))
        m2 = components["memory_store"].create(Memory(
            summary="Existing B", type="pattern",
        ))
        agent, _ = self._make_agent(components, {
            "new_memories": [],
            "update_memories": [],
            "deactivate_memory_ids": [],
            "new_links": [
                {
                    "memory_id_a": m1.id,
                    "memory_id_b": m2.id,
                    "relationship": "related_to",
                    "strength": 0.8,
                }
            ],
        })
        result = agent.build()
        assert result["new_links"] == 1
        links = components["link_store"].get_links_for(m1.id)
        assert len(links) == 1

    def test_build_deactivates_memories(self, components):
        """Build should deactivate memories marked by LLM."""
        old = components["memory_store"].create(Memory(
            summary="Outdated", type="decision",
        ))
        agent, _ = self._make_agent(components, {
            "new_memories": [],
            "update_memories": [],
            "deactivate_memory_ids": [old.id],
            "new_links": [],
        })
        result = agent.build()
        assert result["deactivated_memories"] == 1
        fetched = components["memory_store"].get(old.id)
        assert fetched.active is False

    def test_rebuild_drops_and_recreates(self, components):
        """Rebuild should drop all data first."""
        components["memory_store"].create(Memory(
            summary="Should be gone", type="context",
        ))
        agent, _ = self._make_agent(components, {
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
        result = agent.rebuild()
        assert result["status"] == "success"
        memories = components["memory_store"].list_all(active_only=False)
        # Only the new memory should exist
        assert len(memories) == 1
        assert memories[0].summary == "Fresh start"

    def test_llm_called_with_commits(self, components):
        """Build should send commits to the LLM."""
        agent, mock = self._make_agent(components, {
            "new_memories": [], "update_memories": [],
            "deactivate_memory_ids": [], "new_links": [],
        })
        agent.build()
        assert len(mock.calls) == 1
        user_msg = mock.calls[0][1]["content"]
        assert "aaa111" in user_msg
        assert "Add auth service" in user_msg
