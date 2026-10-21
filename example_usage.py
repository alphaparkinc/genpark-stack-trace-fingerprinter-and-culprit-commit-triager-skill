"""Example usage for Stack Trace Fingerprinter and Culprit Commit Triager."""
from client import StackTraceFingerprinter


def main():
    sample_traceback = """
Traceback (most recent call last):
  File "/srv/app/services/billing.py", line 142, in process_charge
    token = self.auth_provider.get_active_token()
  File "/srv/app/services/auth.py", line 58, in get_active_token
    return self.session_cache[user_id].token
KeyError: 'user_id'
"""

    print("=== 1. Extracting Traceback Fingerprint ===")
    fp_res = StackTraceFingerprinter.fingerprint_stack_trace(sample_traceback)
    print("Fingerprint Hash:", fp_res["fingerprint"])
    print("Exception Type:", fp_res["exception_type"])
    print("Total Frames:", fp_res["total_frames"])

    print("\n=== 2. Triaging Culprit Commits ===")
    recent_commits = [
        {
            "commit_hash": "c1a998b",
            "author": "Alice Dev",
            "message": "docs: update API documentation",
            "changed_files": ["docs/index.md", "README.md"],
        },
        {
            "commit_hash": "e4f810c",
            "author": "Bob Engineer",
            "message": "refactor: optimize session auth caching layer",
            "changed_files": ["services/auth.py", "tests/test_auth.py"],
        },
    ]

    triage_res = StackTraceFingerprinter.triage_culprit_commits(fp_res, recent_commits)
    print("Culprit Found:", triage_res["culprit_found"])
    if triage_res["top_culprit"]:
        top = triage_res["top_culprit"]
        print(f"Top Culprit: {top['commit_hash']} by {top['author']} (Score: {top['likelihood_score']}%)")
        print("Message:", top["message"])
        print("Rationale:", top["rationale"])


if __name__ == "__main__":
    main()
