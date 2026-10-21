"""MCP server for Stack Trace Fingerprinter and Culprit Commit Triager."""
import sys
import json
from client import StackTraceFingerprinter


def handle_request(req):
    method = req.get("method")
    if method == "tools/list":
        return {
            "tools": [
                {
                    "name": "fingerprint_stack_trace",
                    "description": "Parses error tracebacks, normalizes volatile runtime tokens, and computes deterministic fingerprint hashes",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "traceback_text": {"type": "string", "description": "Raw multi-line stack trace string"},
                        },
                        "required": ["traceback_text"],
                    },
                },
                {
                    "name": "triage_culprit_commits",
                    "description": "Cross-references stack trace frames against recent git commit diffs to identify regression culprits",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "fingerprint_result": {"type": "object", "description": "Output of fingerprint_stack_trace"},
                            "recent_commits": {
                                "type": "array",
                                "description": "List of recent commits with 'commit_hash', 'author', 'message', 'changed_files'",
                            },
                        },
                        "required": ["fingerprint_result", "recent_commits"],
                    },
                },
            ]
        }
    elif method == "tools/call":
        params = req.get("params", {})
        tool_name = params.get("name")
        args = params.get("arguments", {})
        if tool_name == "fingerprint_stack_trace":
            res = StackTraceFingerprinter.fingerprint_stack_trace(args.get("traceback_text", ""))
            return {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}
        elif tool_name == "triage_culprit_commits":
            res = StackTraceFingerprinter.triage_culprit_commits(
                fingerprint_result=args.get("fingerprint_result", {}),
                recent_commits=args.get("recent_commits", []),
            )
            return {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}
    return {"error": "Method not found"}


if __name__ == "__main__":
    for line in sys.stdin:
        if line.strip():
            print(json.dumps(handle_request(json.loads(line))))
            sys.stdout.flush()
