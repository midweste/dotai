"""Tests for GitLogParser."""

from src.git import GitLogParser


class TestGitLogParser:
    def test_parse_simple_commit(self):
        """Should parse a basic commit with message and files."""
        raw = """commit abc12345
Author: Test User
Date: 2026-03-09 10:00:00 -0500

Fix login bug

 src/auth.py | 5 ++---
 1 file changed, 2 insertions(+), 3 deletions(-)

---END_COMMIT---"""
        parser = GitLogParser()
        commits = parser.parse(raw)
        assert len(commits) == 1
        assert commits[0].hash == "abc12345"
        assert commits[0].author == "Test User"
        assert commits[0].message == "Fix login bug"
        assert "src/auth.py" in commits[0].files

    def test_parse_commit_with_trailers(self):
        """Should extract git trailers from commit messages."""
        raw = """commit def67890
Author: Test User
Date: 2026-03-09 10:00:00 -0500

Add webhook handler pattern

Implemented the handler class pattern for webhooks.
Each handler type gets its own class.

Type: feature
Rationale: Keeps handler logic isolated and testable
Confidence: high

 src/webhooks/handler.py | 50 ++++++++++++++++++++
 1 file changed, 50 insertions(+)

---END_COMMIT---"""
        parser = GitLogParser()
        commits = parser.parse(raw)
        assert len(commits) == 1
        c = commits[0]
        assert c.message == "Add webhook handler pattern"
        assert "handler class pattern" in c.body
        assert c.trailers.get("type") == "feature"
        assert c.trailers.get("rationale") == "Keeps handler logic isolated and testable"
        assert c.trailers.get("confidence") == "high"

    def test_parse_multiple_commits(self):
        """Should parse multiple commits from a single log output."""
        raw = """commit aaa111
Author: Dev A
Date: 2026-03-01 09:00:00 -0500

First commit

 README.md | 1 +
 1 file changed, 1 insertion(+)

---END_COMMIT---
commit bbb222
Author: Dev B
Date: 2026-03-02 10:00:00 -0500

Second commit

 src/app.py | 10 ++++++++++
 1 file changed, 10 insertions(+)

---END_COMMIT---"""
        parser = GitLogParser()
        commits = parser.parse(raw)
        assert len(commits) == 2
        assert commits[0].hash == "aaa111"
        assert commits[1].hash == "bbb222"

    def test_parse_bare_commit(self):
        """Should handle minimal 'hotfix' style commits."""
        raw = """commit ccc333
Author: Dev
Date: 2026-03-09 10:00:00 -0500

hotfix

 src/fix.py | 1 +
 1 file changed, 1 insertion(+)

---END_COMMIT---"""
        parser = GitLogParser()
        commits = parser.parse(raw)
        assert len(commits) == 1
        assert commits[0].message == "hotfix"
        assert commits[0].body == ""
        assert len(commits[0].trailers) == 0

    def test_parse_rename(self):
        """Should handle file renames in stat output."""
        raw = """commit ddd444
Author: Dev
Date: 2026-03-09 10:00:00 -0500

Rename file

 {old => new}/file.py | 0
 1 file changed

---END_COMMIT---"""
        parser = GitLogParser()
        commits = parser.parse(raw)
        assert len(commits) == 1
        # Rename should produce a cleaned-up path
        assert len(commits[0].files) >= 1
