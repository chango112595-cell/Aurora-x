"""
Aurora Phase 7 - Manual Approval Gate
Review and approve/reject proposed core/foundation modifications.
Provides human oversight for critical system changes.
"""

import json
import sys
from pathlib import Path

REVIEW_FILE = Path("aurora_supervisor/data/knowledge/models/evolution_log.jsonl")


def list_pending():
    """List all pending improvements requiring approval"""
    if not REVIEW_FILE.exists():
        print("No evolution log found.")
        return []

    pending = []
    seen_targets = set()

    try:
        for line in REVIEW_FILE.read_text().splitlines():
            if not line.strip():
                continue
            entry = json.loads(line)

            if entry.get("type") == "approval_decision":
                item = entry.get("item", {})
                target = item.get("target")
                if target:
                    seen_targets.add(target)
                continue

            for item in entry.get("queued", []):
                if item.get("requires_approval"):
                    target = item.get("target")
                    if target and target not in seen_targets:
                        pending.append(item)
                        seen_targets.add(target)

            for imp in entry.get("improvements", []):
                if imp.get("requires_approval"):
                    target = imp.get("target")
                    if target and target not in seen_targets:
                        pending.append(imp)
                        seen_targets.add(target)
    except Exception as e:
        print(f"Error reading evolution log: {e}")

    return pending


def approve(target):
    """Approve a pending improvement by target name"""
    pending = list_pending()
    for item in pending:
        if item.get("target") == target:
            print(f"Approved change: {target}")

            approval_entry = {
                "timestamp": __import__("datetime").datetime.now().isoformat(),
                "type": "approval_decision",
                "item": {
                    **item,
                    "requires_approval": False,
                    "approved": True,
                    "approved_at": __import__("datetime").datetime.now().isoformat(),
                },
            }
            with REVIEW_FILE.open("a") as f:
                f.write(json.dumps(approval_entry) + "\n")

            print("  -> Recorded approval in evolution log")
            print("  -> To apply, supervisor will pick up on next evolution cycle")
            return True

    print(f"No pending item found for target: {target}")
    return False


def reject(target, reason=""):
    """Reject a pending improvement by target name"""
    pending = list_pending()
    for item in pending:
        if item.get("target") == target:
            print(f"Rejected change: {target}")

            rejection_entry = {
                "timestamp": __import__("datetime").datetime.now().isoformat(),
                "type": "approval_decision",
                "item": {
                    **item,
                    "requires_approval": False,
                    "rejected": True,
                    "rejection_reason": reason,
                    "rejected_at": __import__("datetime").datetime.now().isoformat(),
                },
            }
            with REVIEW_FILE.open("a") as f:
                f.write(json.dumps(rejection_entry) + "\n")

            print("  -> Rejection recorded in evolution log")
            return True

    print(f"No pending item found for target: {target}")
    return False


def show_details(target):
    """Show detailed information about a pending improvement"""
    pending = list_pending()
    for item in pending:
        if item.get("target") == target:
            print(f"\n=== Details for: {target} ===")
            for key, value in item.items():
                print(f"  {key}: {value}")
            return
    print(f"No pending item found for target: {target}")


def interactive_review():
    """Interactive review session for pending improvements"""
    pending = list_pending()
    if not pending:
        print("No pending improvements requiring approval.")
        return

    print(f"\n=== Interactive Review ({len(pending)} pending) ===\n")

    for idx, item in enumerate(pending, 1):
        print(f"[{idx}/{len(pending)}] Target: {item.get('target')}")
        print(f"    Level: {item.get('level', 'unknown')}")
        print(f"    Proposed: {item.get('proposed', item.get('proposal', 'N/A'))}")
        print(f"    Delta: {item.get('delta', 'N/A')}")

        while True:
            action = input("\n    (a)pprove, (r)eject, (s)kip, (q)uit? ").lower().strip()
            if action == "a":
                approve(item.get("target"))
                break
            elif action == "r":
                reason = input("    Rejection reason (optional): ").strip()
                reject(item.get("target"), reason)
                break
            elif action == "s":
                print("    Skipped.")
                break
            elif action == "q":
                print("Review session ended.")
                return
            else:
                print("    Invalid choice. Use a/r/s/q")
        print()


def main():
    """Main entry point for CLI usage"""
    args = sys.argv[1:]

    if not args or args[0] in ("-h", "--help", "help"):
        print("""
Aurora Phase 7 - Manual Approval Gate

Usage:
  python approve_changes.py              List pending improvements
  python approve_changes.py list         List pending improvements
  python approve_changes.py approve <target>   Approve an improvement
  python approve_changes.py reject <target>    Reject an improvement
  python approve_changes.py details <target>   Show improvement details
  python approve_changes.py interactive        Interactive review session
        """)
        return

    command = args[0].lower()

    if command == "list" or len(args) == 0:
        print("=== Pending Critical Improvements ===\n")
        pending = list_pending()
        if not pending:
            print("No pending improvements requiring approval.")
        else:
            for p in pending:
                target = p.get("target", "unknown")
                level = p.get("level", "unknown")
                proposal = p.get("proposed", p.get("proposal", "N/A"))
                print(f"  - {target}")
                print(f"      Level: {level}")
                print(f"      Proposal: {proposal}")
                print()

    elif command == "approve" and len(args) > 1:
        approve(args[1])

    elif command == "reject" and len(args) > 1:
        reason = " ".join(args[2:]) if len(args) > 2 else ""
        reject(args[1], reason)

    elif command == "details" and len(args) > 1:
        show_details(args[1])

    elif command == "interactive":
        interactive_review()

    else:
        print(f"Unknown command: {command}")
        print("Run with --help for usage information.")


if __name__ == "__main__":
    main()
