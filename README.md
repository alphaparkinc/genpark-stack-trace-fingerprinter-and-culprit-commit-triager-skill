# genpark-stack-trace-fingerprinter-and-culprit-commit-triager-skill

Multi-language stack trace normalizer, deterministic error fingerprinter, and regression culprit commit triager.

100% Python Standard Library implementation with zero external dependencies.

## Key Capabilities

- **Deterministic Stack Trace Fingerprinting**: Normalizes volatile file paths, hex addresses, and line numbers to generate canonical hashes for error deduplication.
- **Deep Frame Decomposition**: Extracts innermost exception root cause, call stack frames, and caller execution context.
- **Culprit Commit Triage & Likelihood Scoring**: Correlates call stack frames with recent git commit diffs, scoring candidates based on frame depth and commit semantics.

## Architecture

```
[Raw Application Traceback + Recent Git Commit Diffs]
                          │
                          ▼
┌─────────────────────────────────────────────────────┐
│             StackTraceFingerprinter                 │
│  - Path & Volatile Memory Address Normalizer        │
│  - SHA-256 Error Cluster Fingerprint Hash Engine    │
│  - Innermost Frame & Exception Extractor            │
│  - Git Commit Diff Overlap & Regression Scorer      │
└─────────────────────────────────────────────────────┘
                          │
                          ▼
[Deterministic Error Fingerprint + Ranked Culprit Commits]
```

## MCP Server Integration

Run standard MCP stdio server:
```bash
python mcp_server.py
```

Exposed Tools:
- `fingerprint_stack_trace`: Parses error tracebacks, normalizes volatile runtime tokens, and computes deterministic fingerprint hashes.
- `triage_culprit_commits`: Cross-references stack trace frames against recent git commit diffs to identify regression culprits.

## Quickstart (Python API)

```python
from client import StackTraceFingerprinter

tb = \"\"\"Traceback (most recent call last):
  File "app/main.py", line 12, in run
    do_calc()
ZeroDivisionError: division by zero\"\"\"

res = StackTraceFingerprinter.fingerprint_stack_trace(tb)
print("Fingerprint:", res["fingerprint"])
```

---

## GenPark Ecosystem

- **Official Website**: [https://www.genpark.ai](https://www.genpark.ai)
- **LinkedIn Page**: [https://www.linkedin.com/company/92955550](https://www.linkedin.com/company/92955550)
