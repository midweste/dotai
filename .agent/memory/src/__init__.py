"""Project Memory System — persistent, queryable project knowledge derived from git history."""

from pathlib import Path as _Path
import subprocess as _subprocess


def _detect_project_root() -> str:
    """Detect project root from git, not from file path.

    Using __file__.resolve() follows symlinks back to the source repo,
    which breaks when the memory system is shared across projects via
    symlinks. git rev-parse always returns the actual repo root.
    """
    try:
        result = _subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    # Fallback: derive from file path (works when not symlinked)
    return str(_Path(__file__).resolve().parent.parent.parent.parent)


PROJECT_ROOT = _detect_project_root()

from src.models import Memory, MemoryLink, BuildMetaEntry, ParsedCommit
from src.models import MEMORY_TYPES, RELATIONSHIP_TYPES
from src.config import Config
from src.db import Database
from src.stores import MemoryStore, LinkStore, BuildMetaStore
from src.git import GitLogParser
from src.llm import LLMClient
from src.build import BuildAgent, BUILD_SYSTEM_PROMPT
from src.inspector import Inspector
from src.server import McpServer
from src.deps import DependencyChecker

__all__ = [
    "Memory", "MemoryLink", "BuildMetaEntry", "ParsedCommit",
    "MEMORY_TYPES", "RELATIONSHIP_TYPES",
    "Config",
    "Database",
    "MemoryStore", "LinkStore", "BuildMetaStore",
    "GitLogParser",
    "LLMClient",
    "BuildAgent", "BUILD_SYSTEM_PROMPT",
    "Inspector",
    "McpServer",
    "DependencyChecker",
]
