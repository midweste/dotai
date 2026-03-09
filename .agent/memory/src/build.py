"""Build agent — orchestrates commit processing, LLM calls, and memory creation."""

import json
import os
import sys
from typing import Optional

from src.models import Memory, MemoryLink, BuildMetaEntry, ParsedCommit
from src.db import Database
from src.stores import MemoryStore, LinkStore, BuildMetaStore
from src.decay import DecayEngine
from src.git import GitLogParser
from src.llm import LLMClient


def _is_http_transient(e: Exception) -> bool:
    """Check if an exception is a transient HTTP error (429 or 5xx)."""
    try:
        from requests.exceptions import HTTPError
        if isinstance(e, HTTPError) and e.response is not None:
            return e.response.status_code == 429 or e.response.status_code >= 500
    except ImportError:
        pass
    return False


BUILD_SYSTEM_PROMPT = """You are a build agent for a project memory system.
You analyze git commits and produce structured memories about the project.

RULES:
- Only create memories where there is clear evidence from the commits
- Never infer beyond what the commit shows
- High confidence = explicit in trailers or detailed commit message
- Medium confidence = inferred from clear diff patterns across multiple commits
- Low confidence = inferred from a single ambiguous diff or bare message
- Score importance 0.0-1.0 based on how much the memory would affect future development
- When new info contradicts an existing memory, mark the old one for deactivation
- Always create links between related memories (see LINKS section below)
- For bare commits ("hotfix", "fix stuff"), derive what you can from the diff, confidence=low
- Never fabricate — silence is better than fiction

SUMMARY GUIDELINES:
- Be specific and descriptive — mention the what, why, and relevant domain concepts
- Include the memory type concept naturally (e.g. "Decided to use X over Y" not "The project is doing X")
- Mention file names, patterns, or technologies by name when relevant
- Avoid generic phrasing like "The project is..." — be precise about what changed and why

TAGS:
- Include 3-8 lowercase keyword tags per memory
- Tags should cover: domain concepts, technologies, subsystems, patterns, affected areas
- Use consistent naming (e.g. "dead-code" not "deadCode", "audit" not "auditing")
- Tags make memories discoverable via search — choose terms a developer would search for

MEMORY TYPES: decision, pattern, convention, debt, bug_fix, context

LINKS — this section is MANDATORY, do not skip it:
- After creating all memories, review them and create links between any that are related
- If two memories share files, tags, or affect the same subsystem, they MUST be linked
- For N memories, expect roughly N/3 to N/2 links — 0 links is almost never correct
- Link both new↔new memories AND new↔existing memories
- Choose the most specific relationship type:
  supersedes    — A newer decision/convention replaces an older one
                  Example: ".agent/ directory system" supersedes ".ai/ directory system"
  implements    — One memory is the concrete implementation of an abstract decision
                  Example: "Added core-pre-flight.md rule" implements "Decided on mandatory pre-flight checklist"
  caused_by     — A bug or debt was caused by a prior decision or change
                  Example: "FTS index out of sync bug" caused_by "Switched to WAL journal mode"
  resolved_by   — A bug or debt memory was fixed by a subsequent change
                  Example: "FTS sync issue" resolved_by "Added FTS rebuild on schema migration"
  convention_group — Two conventions belong to the same logical group
                  Example: "PHP strict_types" convention_group "PHP namespace conventions"
  debt_in       — A debt memory exists within a specific subsystem or area
                  Example: "Missing test coverage" debt_in "Authentication module"
  related_to    — LAST RESORT — use only when no other type fits
                  If you're tempted to use related_to, ask: is one superseding the other?
                  Is one implementing the other? Is one caused by the other?

CRITICAL: Your response MUST be a raw JSON object and NOTHING else.
Do NOT wrap it in markdown code fences. Do NOT include any text before or after the JSON.
The response must be parseable by json.loads() directly.

Return this exact JSON structure:
{
  "new_memories": [
    {
      "summary": "...",
      "type": "decision|pattern|convention|debt|bug_fix|context",
      "confidence": "high|medium|low",
      "importance": 0.0-1.0,
      "source_commits": ["hash1"],
      "files": ["path/to/file"],
      "tags": ["keyword1", "keyword2"]
    }
  ],
  "update_memories": [
    {
      "id": 123,
      "summary": "updated summary",
      "confidence": "high",
      "importance": 0.8
    }
  ],
  "deactivate_memory_ids": [456],
  "new_links": [
    {
      "memory_id_a": 1,
      "memory_id_b": 2,
      "relationship": "supersedes",
      "strength": 0.9
    }
  ]
}
"""


class BuildAgent:
    """Orchestrates build: parse commits → LLM call → memory diffing → DB writes → decay."""

    def __init__(
        self,
        db: Database,
        memory_store: MemoryStore,
        link_store: LinkStore,
        build_meta_store: BuildMetaStore,
        decay_engine: DecayEngine,
        git_parser: GitLogParser,
        llm_client: LLMClient,
    ):
        self._db = db
        self._memories = memory_store
        self._links = link_store
        self._build_meta = build_meta_store
        self._decay = decay_engine
        self._git = git_parser
        self._llm = llm_client

    def build(self, *, limit: Optional[int] = None) -> dict:
        """Incremental build — process commits since last build."""
        last_build = self._build_meta.get_last()
        since_hash = last_build.last_commit if last_build else None

        return self._run_build(
            since_hash=since_hash,
            limit=limit,
            build_type="incremental",
        )

    def rebuild(self, *, limit: Optional[int] = None) -> dict:
        """Full rebuild — delete DB files and reprocess all history.

        Physically removes the database, WAL, and SHM files for a clean start.
        Backs up the existing DB first. If the rebuild produces zero memories
        (total failure), restores the backup.
        """
        import shutil

        db_path = self._db.db_path
        is_file_db = db_path != ":memory:" and os.path.exists(db_path)
        backup_path = f"{db_path}.bak" if is_file_db else None

        if is_file_db:
            # Close existing connection before file operations
            self._db.close()

            # Backup existing DB
            shutil.copy2(db_path, backup_path)  # type: ignore[arg-type]

            # Delete DB and associated WAL/SHM files
            for suffix in ("", "-wal", "-shm"):
                path = db_path + suffix
                if os.path.exists(path):
                    os.remove(path)

        # Fresh connection and schema
        self._db.__init__(db_path)  # type: ignore[misc]
        self._db.init_schema()

        result = self._run_build(
            since_hash=None,
            limit=limit,
            build_type="full",
        )

        # Restore backup if rebuild produced nothing
        if result.get("new_memories", 0) == 0 and backup_path and os.path.exists(backup_path):
            self._db.close()
            # Delete the failed DB files
            for suffix in ("", "-wal", "-shm"):
                path = db_path + suffix
                if os.path.exists(path):
                    os.remove(path)
            shutil.move(backup_path, db_path)
            self._db.__init__(db_path)  # type: ignore[misc]
            self._db.init_schema()
            result["status"] = "failed_restored"
            result["message"] = "Rebuild failed — no memories created. Previous DB restored."
            print("  rebuild failed, previous DB restored", file=sys.stderr, flush=True)
        elif backup_path and os.path.exists(backup_path):
            os.remove(backup_path)

        return result

    # Overhead tokens for system prompt + existing-memories context
    _OVERHEAD_TOKENS = 8_000
    # Minimum output tokens to reserve for the response
    _MIN_OUTPUT_TOKENS = 4_000
    # Fallback budget if model info is unavailable
    _FALLBACK_BUDGET = 10_000

    def _compute_budget(self) -> tuple[int, int]:
        """Compute (input_budget, max_output_tokens) from model capabilities.

        Uses the model's context_length and max_completion_tokens to
        dynamically allocate space:
          input_budget = context_length - overhead - output_reserve
          max_output  = min(max_completion_tokens, context_length // 3)
        """
        env_budget = os.environ.get("MEMORY_BATCH_TOKEN_BUDGET")
        info = self._llm.get_model_info()
        ctx = info["context_length"]
        model_max_output = info["max_completion_tokens"]

        # Output: use model's max but cap at 1/3 of context to leave room
        max_output = min(model_max_output, ctx // 3)
        max_output = max(max_output, self._MIN_OUTPUT_TOKENS)

        if env_budget:
            # User override — respect it, but still use dynamic output
            return int(env_budget), max_output

        # Dynamic: context - overhead - output = available for commits
        input_budget = ctx - self._OVERHEAD_TOKENS - max_output
        input_budget = max(input_budget, 5_000)  # floor
        return input_budget, max_output

    def _run_build(
        self,
        *,
        since_hash: Optional[str],
        limit: Optional[int],
        build_type: str,
    ) -> dict:
        # Validate model and compute dynamic budget
        self._llm.validate_model()
        token_budget, max_output = self._compute_budget()
        info = self._llm.get_model_info()
        print(
            f"  model: {info['name']} "
            f"(context: {info['context_length']:,}, "
            f"max_output: {info['max_completion_tokens']:,})",
            file=sys.stderr, flush=True,
        )
        print(
            f"  budget: {token_budget:,} input / {max_output:,} output",
            file=sys.stderr, flush=True,
        )
        """Core build logic shared by build() and rebuild()."""
        # Get commits
        raw_log = self._git.get_file_list(since_hash=since_hash, limit=limit)
        commits = self._git.parse(raw_log)

        if not commits:
            return {"status": "no_new_commits", "commits_processed": 0}

        # Split into token-aware batches using dynamic budget
        batches = self._make_batches(commits, token_budget)
        total = len(commits)
        new_count = 0
        updated_count = 0
        deactivated_count = 0
        link_count = 0
        errors: list[str] = []

        for batch_num, batch in enumerate(batches, 1):
            est_tokens = sum(self._estimate_commit_tokens(c) for c in batch)
            print(
                f"  batch {batch_num}/{len(batches)} "
                f"({len(batch)} commits, ~{est_tokens} tokens)...",
                file=sys.stderr, flush=True,
            )

            result = self._process_batch(batch, max_output_tokens=max_output)
            if result is None:
                continue
            if "error" in result:
                errors.append(result["error"])
                continue

            new_count += result.get("new", 0)
            updated_count += result.get("updated", 0)
            deactivated_count += result.get("deactivated", 0)
            link_count += result.get("links", 0)

        # Apply decay
        commit_hashes = [c.hash for c in commits]
        reinforced = self._memories.get_ids_for_commits(commit_hashes)
        last_build = self._build_meta.get_last()
        accessed_since = last_build.built_at if last_build else ""
        accessed = self._memories.get_ids_accessed_since(accessed_since) if accessed_since else set()
        decayed = self._decay.apply(accessed_ids=accessed, reinforced_ids=reinforced)

        # Record build
        current_hash = commits[-1].hash if commits else self._git.get_current_hash()
        self._build_meta.record(BuildMetaEntry(
            build_type=build_type,
            last_commit=current_hash,
            commit_count=total,
            memory_count=self._memories.count(),
        ))

        result_dict: dict = {
            "status": "success" if not errors else "partial",
            "commits_processed": total,
            "new_memories": new_count,
            "updated_memories": updated_count,
            "deactivated_memories": deactivated_count,
            "new_links": link_count,
            "decayed_memories": decayed,
        }
        if errors:
            result_dict["errors"] = errors
        return result_dict

    @staticmethod
    def _estimate_commit_tokens(commit: ParsedCommit) -> int:
        """Rough token estimate for a single commit (~4 chars per token)."""
        chars = (
            len(commit.hash) + len(commit.author) + len(commit.date)
            + len(commit.message) + len(commit.body)
            + sum(len(f) for f in commit.files)
            + sum(len(k) + len(v) for k, v in commit.trailers.items())
            + 80  # formatting overhead
        )
        return max(chars // 4, 1)

    def _make_batches(self, commits: list[ParsedCommit],
                      budget: int) -> list[list[ParsedCommit]]:
        """Split commits into batches that fit within the given token budget."""
        batches: list[list[ParsedCommit]] = []
        current_batch: list[ParsedCommit] = []
        current_tokens = 0

        for commit in commits:
            tokens = self._estimate_commit_tokens(commit)
            if current_batch and current_tokens + tokens > budget:
                batches.append(current_batch)
                current_batch = []
                current_tokens = 0
            current_batch.append(commit)
            current_tokens += tokens

        if current_batch:
            batches.append(current_batch)
        return batches

    def _process_batch(self, batch: list[ParsedCommit],
                       *, max_output_tokens: int = 16_384) -> Optional[dict]:
        """Process a single batch of commits through the LLM.

        Retries up to 3 times with exponential backoff for transient errors
        (429 rate limit, 5xx server errors, timeouts).
        """
        # Refresh existing memories for context each batch
        existing = self._memories.list_all(limit=200)
        existing_summary = [
            {"id": m.id, "summary": m.summary, "type": m.type, "files": m.files}
            for m in existing
        ]

        commits_text = self._format_commits(batch)
        user_msg = (
            f"Existing memories (for context, linking, and superseding):\n"
            f"{json.dumps(existing_summary, indent=2)}\n\n"
            f"New commits to process:\n{commits_text}"
        )

        max_retries = 3
        last_error = None
        for attempt in range(max_retries):
            try:
                response_text = self._llm.chat(
                    [
                        {"role": "system", "content": BUILD_SYSTEM_PROMPT},
                        {"role": "user", "content": user_msg},
                    ],
                    max_tokens=max_output_tokens,
                )
                result = json.loads(response_text)
                break  # Success
            except Exception as e:
                last_error = e
                # Retry on transient HTTP errors and truncated JSON
                is_transient = False
                if isinstance(e, json.JSONDecodeError):
                    is_transient = True  # LLM returned truncated output
                elif _is_http_transient(e):
                    is_transient = True
                elif isinstance(e, (ConnectionError, TimeoutError, OSError)):
                    is_transient = True

                if is_transient and attempt < max_retries - 1:
                    wait = 2 ** (attempt + 1)  # 2s, 4s
                    print(
                        f"    retry {attempt + 1}/{max_retries - 1} after {wait}s ({e})",
                        file=sys.stderr, flush=True,
                    )
                    import time
                    time.sleep(wait)
                    continue
                return {"error": f"batch failed: {e}"}
        else:
            return {"error": f"batch failed after {max_retries} attempts: {last_error}"}

        new_count = 0
        updated_count = 0
        deactivated_count = 0
        link_count = 0

        # New memories
        new_id_map: dict[int, int] = {}
        for i, mem_data in enumerate(result.get("new_memories", [])):
            memory = Memory(
                summary=mem_data.get("summary", ""),
                type=mem_data.get("type", "context"),
                confidence=mem_data.get("confidence", "medium"),
                importance=mem_data.get("importance", 0.5),
                source_commits=mem_data.get("source_commits", []),
                files=mem_data.get("files", []),
                tags=mem_data.get("tags", []),
            )
            created = self._memories.create(memory)
            if created.id is not None:
                new_id_map[i] = created.id
            new_count += 1

        # Update existing memories
        for update_data in result.get("update_memories", []):
            mem_id = update_data.get("id")
            if mem_id is None:
                continue
            existing_mem = self._memories.get(mem_id)
            if existing_mem is None:
                continue
            if "summary" in update_data:
                existing_mem.summary = update_data["summary"]
            if "confidence" in update_data:
                existing_mem.confidence = update_data["confidence"]
            if "importance" in update_data:
                existing_mem.importance = update_data["importance"]
            self._memories.update(existing_mem)
            updated_count += 1

        # Deactivate memories
        for mem_id in result.get("deactivate_memory_ids", []):
            self._memories.deactivate(mem_id)
            deactivated_count += 1

        # Create links
        for link_data in result.get("new_links", []):
            link = MemoryLink(
                memory_id_a=link_data.get("memory_id_a", 0),
                memory_id_b=link_data.get("memory_id_b", 0),
                relationship=link_data.get("relationship", "related_to"),
                strength=link_data.get("strength", 0.5),
            )
            if link.memory_id_a and link.memory_id_b:
                self._links.create(link)
                link_count += 1

        return {
            "new": new_count,
            "updated": updated_count,
            "deactivated": deactivated_count,
            "links": link_count,
        }

    def _format_commits(self, commits: list[ParsedCommit]) -> str:
        """Format commits for the LLM prompt."""
        parts = []
        for c in commits:
            section = f"=== Commit {c.hash[:8]} ===\n"
            section += f"Author: {c.author}\n"
            section += f"Date: {c.date}\n"
            section += f"Message: {c.message}\n"
            if c.body:
                section += f"Body:\n{c.body}\n"
            if c.trailers:
                section += f"Trailers: {json.dumps(c.trailers)}\n"
            if c.files:
                section += f"Files: {', '.join(c.files)}\n"
            parts.append(section)
        return "\n".join(parts)
