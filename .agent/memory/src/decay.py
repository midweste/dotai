"""Importance decay logic — memories not accessed or reinforced lose importance."""

from datetime import datetime, timezone
from typing import Optional

from src.db import Database


class DecayEngine:
    """Importance decay logic — memories not accessed or reinforced lose importance."""

    DEFAULT_RATE = 0.95

    def __init__(self, db: Database, *, decay_rate: float = DEFAULT_RATE):
        self._db = db
        self.decay_rate = decay_rate

    def apply(
        self,
        *,
        accessed_ids: Optional[set[int]] = None,
        reinforced_ids: Optional[set[int]] = None,
    ) -> int:
        """Apply decay to all active memories not in the accessed or reinforced sets.

        Returns the number of memories decayed.
        """
        exempt = (accessed_ids or set()) | (reinforced_ids or set())
        rows = self._db.conn.execute(
            "SELECT id, importance FROM memories WHERE active = 1"
        ).fetchall()
        decayed = 0
        for row in rows:
            if row["id"] in exempt:
                continue
            new_importance = row["importance"] * self.decay_rate
            self._db.conn.execute(
                "UPDATE memories SET importance = ?, updated_at = ? WHERE id = ?",
                (new_importance, datetime.now(timezone.utc).isoformat(), row["id"]),
            )
            decayed += 1
        self._db.conn.commit()
        return decayed
