"""
Quick manual runner to exercise the full agent on the synthetic cases.
Not part of the app - just for watching the agent work end to end.
"""
import sys
from agent.graph import agent
from data.sample_notes import ALL_CASES


def run_case(key: str):
    note = ALL_CASES[key]
    print(f"\n{'='*70}\nCASE: {key}  ({note.requested_service.display})\n{'='*70}")

    result = agent.invoke({"note": note})

    print("\n--- TRACE ---")
    for line in result.get("trace", []):
        print(" ", line)

    print("\n--- OUTCOME ---")
    print("  PA required:", result.get("pa_required"))
    if result.get("criteria_checks"):
        print("  Criteria:")
        for c in result["criteria_checks"]:
            print(f"    [{c['status']}] {c['criterion']}")
    if result.get("draft"):
        print("\n--- DRAFT ---")
        print(result["draft"])
        print("\n  Confidence:", result.get("confidence"))


if __name__ == "__main__":
    key = sys.argv[1] if len(sys.argv) > 1 else "mri_back"
    run_case(key)