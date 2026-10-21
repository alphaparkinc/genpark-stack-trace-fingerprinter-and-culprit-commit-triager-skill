"""Stack Trace Fingerprinter and Culprit Commit Triager.
100% Python Standard Library.
"""

import re
import hashlib
from typing import List, Dict, Any, Optional


class StackTraceFingerprinter:
    """Parses, normalizes, and groups application stack traces into deterministic fingerprints,
    then correlates offending frames with recent code changes to triage culprit commits."""

    @classmethod
    def fingerprint_stack_trace(cls, traceback_text: str) -> Dict[str, Any]:
        """Normalizes dynamic parameters (hex, memory addresses, timestamps, line numbers)
        to extract canonical exception types, call frames, and SHA-256 fingerprint hash."""
        lines = traceback_text.strip().splitlines()
        frames = []
        exception_type = "UnknownException"
        exception_message = ""

        # Pattern to capture frames: File "path", line X, in func
        frame_pattern = re.compile(r'File\s+["\'](?P<file>[^"\']+)["\'],\s+line\s+(?P<line>\d+)(?:,\s+in\s+(?P<func>\w+))?')
        # Pattern to capture exception line at end: TypeError: message
        exc_pattern = re.compile(r'^(?P<type>[A-Za-z0-9_]+Error|[A-Za-z0-9_]+Exception):\s*(?P<msg>.*)$')

        for line in lines:
            trimmed = line.strip()
            f_match = frame_pattern.search(trimmed)
            if f_match:
                f_path = f_match.group("file").replace("\\", "/")
                # Normalize relative path (keep basename or relative segments)
                path_parts = f_path.split("/")
                norm_file = "/".join(path_parts[-3:]) if len(path_parts) > 3 else f_path
                frames.append({
                    "raw_file": f_path,
                    "normalized_file": norm_file,
                    "line": int(f_match.group("line")),
                    "function": f_match.group("func") or "<module>",
                })
                continue

            e_match = exc_pattern.match(trimmed)
            if e_match:
                exception_type = e_match.group("type")
                exception_message = e_match.group("msg").strip()

        if not exception_message and lines:
            # Fallback for last line if not standard Python exception
            exception_message = lines[-1].strip()

        # Build normalized representation for hashing
        # Focus on exception_type + top application frames (excluding line numbers for stability across refactors)
        normalized_elements = [exception_type]
        for f in frames:
            normalized_elements.append(f"{f['normalized_file']}:{f['function']}")

        normalized_repr = " | ".join(normalized_elements)
        fingerprint_hash = hashlib.sha256(normalized_repr.encode("utf-8")).hexdigest()[:16]

        return {
            "fingerprint": fingerprint_hash,
            "exception_type": exception_type,
            "exception_message": exception_message,
            "total_frames": len(frames),
            "frames": frames,
            "normalized_signature": normalized_repr,
        }

    @classmethod
    def triage_culprit_commits(
        cls,
        fingerprint_result: Dict[str, Any],
        recent_commits: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Correlates stack trace frames with recent commits to identify likely regressions.
        Each commit in recent_commits should contain:
          - 'commit_hash': str
          - 'author': str
          - 'message': str
          - 'changed_files': list of file paths
        """
        frames = fingerprint_result.get("frames", [])
        trace_files = {f["normalized_file"].split("/")[-1].lower() for f in frames}

        scored_candidates = []
        for commit in recent_commits:
            score = 0
            matching_files = []
            changed = commit.get("changed_files", [])

            for cf in changed:
                cf_norm = cf.replace("\\", "/").split("/")[-1].lower()
                if cf_norm in trace_files:
                    score += 40
                    matching_files.append(cf)

            # Heuristics based on commit message keywords
            msg_lower = commit.get("message", "").lower()
            if any(kw in msg_lower for kw in ["refactor", "fix", "migrate", "upgrade", "cleanup", "remove"]):
                score += 15

            # Root frame bonus (frame 0 or innermost frame)
            if frames:
                innermost = frames[-1]["normalized_file"].split("/")[-1].lower()
                if any(innermost == cf.replace("\\", "/").split("/")[-1].lower() for cf in changed):
                    score += 35

            if score > 0:
                scored_candidates.append({
                    "commit_hash": commit.get("commit_hash"),
                    "author": commit.get("author"),
                    "message": commit.get("message"),
                    "likelihood_score": min(100, score),
                    "matched_files": matching_files,
                    "rationale": f"Modifies {len(matching_files)} file(s) present in active call stack frames.",
                })

        scored_candidates.sort(key=lambda x: x["likelihood_score"], reverse=True)

        return {
            "fingerprint": fingerprint_result.get("fingerprint"),
            "culprit_found": len(scored_candidates) > 0,
            "top_culprit": scored_candidates[0] if scored_candidates else None,
            "ranked_candidates": scored_candidates,
        }
