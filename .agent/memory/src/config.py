"""Centralized configuration with defaults — single source of truth for all settings."""

import os
from dataclasses import dataclass, field


@dataclass
class Config:
    """All project-memory settings with sensible defaults.

    Resolution order: explicit constructor arg > env var > default.
    """

    # API
    openrouter_api_key: str = ""
    api_url: str = "https://openrouter.ai/api/v1/chat/completions"
    model: str = "anthropic/claude-sonnet-4.6"

    # Build batching
    commit_limit: int = 0          # 0 = all commits
    batch_token_budget: int = 5000
    batch_max_commits: int = 20

    # Model constraints
    min_context_length: int = 32_000

    @classmethod
    def from_env(cls, **overrides) -> "Config":
        """Create a Config, filling unset values from environment variables.

        Explicit overrides take priority, then env vars, then class defaults.
        """
        env_map = {
            "openrouter_api_key": "OPENROUTER_API_KEY",
            "api_url": "MEMORY_BUILD_API_URL",
            "model": "MEMORY_BUILD_MODEL",
            "commit_limit": "MEMORY_COMMIT_LIMIT",
            "batch_token_budget": "MEMORY_BATCH_TOKEN_BUDGET",
            "batch_max_commits": "MEMORY_BATCH_MAX_COMMITS",
        }

        kwargs = {}
        defaults = cls()
        for attr_name, env_name in env_map.items():
            if attr_name in overrides:
                kwargs[attr_name] = overrides[attr_name]
            else:
                env_val = os.environ.get(env_name)
                if env_val is not None:
                    # Cast to match the field's default type
                    default_val = getattr(defaults, attr_name)
                    if isinstance(default_val, int):
                        kwargs[attr_name] = int(env_val)
                    else:
                        kwargs[attr_name] = env_val

        return cls(**kwargs)
