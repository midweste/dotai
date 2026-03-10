"""Project Memory System — persistent, queryable project knowledge derived from git history."""

from pathlib import Path as _Path

# Single source of truth: project root derived from package location.
# The memory system lives at {project_root}/.agent/memory/src/
#   src/ → memory/ → .agent/ → project_root
PROJECT_ROOT = str(_Path(__file__).resolve().parent.parent.parent.parent)

from src.models import Memory, MemoryLink, BuildMetaEntry, ParsedCommit
from src.models import MEMORY_TYPES, CONFIDENCE_LEVELS, RELATIONSHIP_TYPES
from src.db import Database
from src.stores import MemoryStore, LinkStore, BuildMetaStore
from src.decay import DecayEngine
from src.git import GitLogParser
from src.llm import LLMClient
from src.build import BuildAgent, BUILD_SYSTEM_PROMPT
from src.inspector import Inspector
from src.server import McpServer
from src.deps import DependencyChecker

__all__ = [
    "Memory", "MemoryLink", "BuildMetaEntry", "ParsedCommit",
    "MEMORY_TYPES", "CONFIDENCE_LEVELS", "RELATIONSHIP_TYPES",
    "Database",
    "MemoryStore", "LinkStore", "BuildMetaStore",
    "DecayEngine",
    "GitLogParser",
    "LLMClient",
    "BuildAgent", "BUILD_SYSTEM_PROMPT",
    "Inspector",
    "McpServer",
    "DependencyChecker",
]
