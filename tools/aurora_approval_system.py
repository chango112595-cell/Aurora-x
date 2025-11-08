#!/usr/bin/env python3
"""
AURORA AI APPROVAL & GRADING SYSTEM
===================================

A collaborative learning system where Aurora must get approval before making any changes.
Includes a grading system to teach Aurora what's correct and what needs improvement.

Features:
- All changes require human approval
- Grading system with feedback
- Learning from mistakes
- Progress tracking
- Collaborative teaching approach
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any


class AuroraApprovalSystem:
    """
    Aurora's Learning and Approval System
    - Requires approval for all changes
    - Provides grading and feedback
    - Tracks learning progress
    """

    def __init__(self):
        self.approval_file = Path("/workspaces/Aurora-x/.aurora_approvals.json")
        self.grades_file = Path("/workspaces/Aurora-x/.aurora_grades.json")
        self.pending_changes = []
        self.grades_history = []
        self.load_data()

    def load_data(self):
        """Load existing approval and grading data"""
        if self.approval_file.exists():
            try:
                with open(self.approval_file) as f:
                    data = json.load(f)
                    self.pending_changes = data.get("pending_changes", [])
            except:
                self.pending_changes = []

        if self.grades_file.exists():
            try:
                with open(self.grades_file) as f:
                    data = json.load(f)
                    self.grades_history = data.get("grades", [])
            except:
                self.grades_history = []

    def save_data(self):
        """Save approval and grading data"""
        # Save pending changes
        with open(self.approval_file, "w") as f:
            json.dump(
                {"pending_changes": self.pending_changes, "last_updated": datetime.now().isoformat()}, f, indent=2
            )

        # Save grades
        with open(self.grades_file, "w") as f:
            json.dump({"grades": self.grades_history, "last_updated": datetime.now().isoformat()}, f, indent=2)

    def submit_change_request(self, file_path: str, proposed_change: str, reason: str, change_type: str = "fix") -> str:
        """
        Aurora submits a change request for approval

        Args:
            file_path: Path to file to be changed
            proposed_change: The exact change Aurora wants to make
            reason: Aurora's explanation for the change
            change_type: Type of change (fix, feature, refactor, etc.)

        Returns:
            request_id: Unique ID for tracking this request
        """
        request_id = str(uuid.uuid4())[:8]

        change_request = {
            "id": request_id,
            "timestamp": datetime.now().isoformat(),
            "file_path": file_path,
            "proposed_change": proposed_change,
            "reason": reason,
            "change_type": change_type,
            "status": "pending",
            "aurora_confidence": self._calculate_confidence(proposed_change, reason),
        }

        self.pending_changes.append(change_request)
        self.save_data()

        print(f"🤖 Aurora: I'd like to make a change (Request ID: {request_id})")
        print(f"📁 File: {file_path}")
        print(f"🔧 Type: {change_type}")
        print(f"💭 My reasoning: {reason}")
        print(f"📊 My confidence: {change_request['aurora_confidence']}/10")
        print("✨ Proposed change:")
        print(f"   {proposed_change}")
        print("⏳ Status: Awaiting approval...")

        return request_id

    def approve_change(self, request_id: str, grade: int, feedback: str = "") -> bool:
        """
        Approve a change request and give Aurora a grade

        Args:
            request_id: The request ID to approve
            grade: Grade from 1-10 (10 = perfect, 1 = needs major work)
            feedback: Detailed feedback for Aurora to learn from

        Returns:
            bool: True if approved and applied successfully
        """
        # Find the request
        request = None
        for i, req in enumerate(self.pending_changes):
            if req["id"] == request_id:
                request = req
                break

        if not request:
            print(f"❌ Request {request_id} not found!")
            return False

        # Record the grade
        grade_entry = {
            "request_id": request_id,
            "timestamp": datetime.now().isoformat(),
            "grade": grade,
            "feedback": feedback,
            "file_path": request["file_path"],
            "change_type": request["change_type"],
            "aurora_confidence": request["aurora_confidence"],
            "accuracy_score": abs(grade - request["aurora_confidence"]),  # How well Aurora predicted
        }

        self.grades_history.append(grade_entry)

        # Update request status
        request["status"] = "approved"
        request["grade"] = grade
        request["feedback"] = feedback
        request["approved_at"] = datetime.now().isoformat()

        # Remove from pending
        self.pending_changes = [req for req in self.pending_changes if req["id"] != request_id]

        self.save_data()

        print(f"✅ APPROVED: Request {request_id}")
        print(f"📊 Grade: {grade}/10")
        if feedback:
            print(f"💬 Feedback: {feedback}")

        # Give Aurora learning feedback
        self._provide_aurora_feedback(grade_entry)

        return True

    def reject_change(self, request_id: str, grade: int, feedback: str) -> bool:
        """
        Reject a change request and provide learning feedback

        Args:
            request_id: The request ID to reject
            grade: Grade from 1-10 explaining why it was rejected
            feedback: Detailed explanation of what went wrong

        Returns:
            bool: True if rejection was processed successfully
        """
        # Find the request
        request = None
        for i, req in enumerate(self.pending_changes):
            if req["id"] == request_id:
                request = req
                break

        if not request:
            print(f"❌ Request {request_id} not found!")
            return False

        # Record the grade (rejection)
        grade_entry = {
            "request_id": request_id,
            "timestamp": datetime.now().isoformat(),
            "grade": grade,
            "feedback": feedback,
            "file_path": request["file_path"],
            "change_type": request["change_type"],
            "aurora_confidence": request["aurora_confidence"],
            "accuracy_score": abs(grade - request["aurora_confidence"]),
            "status": "rejected",
        }

        self.grades_history.append(grade_entry)

        # Update request status
        request["status"] = "rejected"
        request["grade"] = grade
        request["feedback"] = feedback
        request["rejected_at"] = datetime.now().isoformat()

        # Remove from pending
        self.pending_changes = [req for req in self.pending_changes if req["id"] != request_id]

        self.save_data()

        print(f"❌ REJECTED: Request {request_id}")
        print(f"📊 Grade: {grade}/10")
        print(f"💬 Feedback: {feedback}")

        # Give Aurora learning feedback
        self._provide_aurora_feedback(grade_entry)

        return True

    def _provide_aurora_feedback(self, grade_entry: dict[str, Any]):
        """Provide structured feedback to help Aurora learn"""
        grade = grade_entry["grade"]

        print("\n🎓 AURORA LEARNING FEEDBACK:")
        print(f"   Request: {grade_entry['request_id']}")

        if grade >= 9:
            print("   🌟 EXCELLENT WORK! This was nearly perfect.")
        elif grade >= 7:
            print("   ✅ GOOD JOB! This was mostly correct with minor issues.")
        elif grade >= 5:
            print("   ⚠️  NEEDS IMPROVEMENT. The approach was okay but had problems.")
        elif grade >= 3:
            print("   🔄 SIGNIFICANT ISSUES. Please review the fundamentals.")
        else:
            print("   ❌ MAJOR PROBLEMS. This approach was incorrect.")

        print(f"   💭 Feedback: {grade_entry['feedback']}")

        # Confidence accuracy feedback
        accuracy = grade_entry["accuracy_score"]
        if accuracy <= 1:
            print("   🎯 Your confidence assessment was very accurate!")
        elif accuracy <= 3:
            print("   📊 Your confidence was reasonably accurate.")
        else:
            print("   🤔 Work on better self-assessment of your solutions.")

    def _calculate_confidence(self, proposed_change: str, reason: str) -> int:
        """Aurora's self-assessment of her confidence (1-10)"""
        # Simple heuristics for Aurora's confidence
        confidence = 5  # Base confidence

        # Increase confidence for simple changes
        if "# type: ignore" in proposed_change:
            confidence += 2

        # Increase confidence for well-reasoned changes
        if len(reason) > 50 and ("because" in reason.lower() or "since" in reason.lower()):
            confidence += 1

        # Decrease confidence for complex changes
        if len(proposed_change.split("\n")) > 10:
            confidence -= 1

        # Decrease confidence for risky patterns
        if any(word in proposed_change.lower() for word in ["delete", "remove", "drop"]):
            confidence -= 2

        return max(1, min(10, confidence))

    def show_pending_requests(self):
        """Show all pending change requests"""
        if not self.pending_changes:
            print("✅ No pending change requests!")
            return

        print(f"⏳ PENDING CHANGE REQUESTS ({len(self.pending_changes)}):")
        print("=" * 60)

        for req in self.pending_changes:
            print(f"🆔 ID: {req['id']}")
            print(f"📁 File: {req['file_path']}")
            print(f"🔧 Type: {req['change_type']}")
            print(f"📊 Aurora's Confidence: {req['aurora_confidence']}/10")
            print(f"💭 Reason: {req['reason']}")
            print("✨ Proposed Change:")
            print(f"   {req['proposed_change']}")
            print(f"⏰ Submitted: {req['timestamp']}")
            print("-" * 40)

    def show_grade_report(self, last_n: int = 10):
        """Show Aurora's recent grades and progress"""
        if not self.grades_history:
            print("📝 No grades recorded yet!")
            return

        recent_grades = self.grades_history[-last_n:]
        avg_grade = sum(g["grade"] for g in recent_grades) / len(recent_grades)

        print(f"📊 AURORA'S GRADE REPORT (Last {len(recent_grades)} submissions)")
        print("=" * 60)
        print(f"📈 Average Grade: {avg_grade:.1f}/10")

        # Grade distribution
        grade_counts = {}
        for g in recent_grades:
            grade = g["grade"]
            grade_counts[grade] = grade_counts.get(grade, 0) + 1

        print("📊 Grade Distribution:")
        for grade in sorted(grade_counts.keys(), reverse=True):
            count = grade_counts[grade]
            print(f"   {grade}/10: {'●' * count} ({count})")

        print("\n📚 Recent Submissions:")
        for grade in recent_grades[-5:]:  # Last 5
            status = "✅" if grade.get("status") != "rejected" else "❌"
            print(f"   {status} {grade['grade']}/10 - {grade['change_type']} in {Path(grade['file_path']).name}")
            if grade["feedback"]:
                print(f"      💬 {grade['feedback'][:50]}...")


def main():
    """CLI interface for the approval system"""
    import sys

    approval_system = AuroraApprovalSystem()

    if len(sys.argv) < 2:
        print("🤖 AURORA APPROVAL SYSTEM")
        print("Usage:")
        print("  python aurora_approval_system.py pending    # Show pending requests")
        print("  python aurora_approval_system.py grades     # Show grade report")
        print("  python aurora_approval_system.py approve <id> <grade> [feedback]")
        print("  python aurora_approval_system.py reject <id> <grade> <feedback>")
        return

    command = sys.argv[1]

    if command == "pending":
        approval_system.show_pending_requests()

    elif command == "grades":
        approval_system.show_grade_report()

    elif command == "approve" and len(sys.argv) >= 4:
        request_id = sys.argv[2]
        grade = int(sys.argv[3])
        feedback = " ".join(sys.argv[4:]) if len(sys.argv) > 4 else ""
        approval_system.approve_change(request_id, grade, feedback)

    elif command == "reject" and len(sys.argv) >= 5:
        request_id = sys.argv[2]
        grade = int(sys.argv[3])
        feedback = " ".join(sys.argv[4:])
        approval_system.reject_change(request_id, grade, feedback)

    else:
        print("❌ Invalid command or missing arguments!")


if __name__ == "__main__":
    main()
