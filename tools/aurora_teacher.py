#!/usr/bin/env python3
"""
AURORA TEACHER CLI
==================

A simple command-line interface for teaching Aurora through the approval system.
Makes it easy to review, grade, and provide feedback on Aurora's change requests.

Usage:
    python aurora_teacher.py                    # Show pending requests
    python aurora_teacher.py grade <id> <1-10> <feedback>   # Grade a request
    python aurora_teacher.py approve <id>       # Quick approve (grade 8)
    python aurora_teacher.py reject <id>        # Quick reject (grade 3)
    python aurora_teacher.py report             # Show Aurora's progress
"""

import sys
import os
from pathlib import Path

# Add tools directory to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from aurora_approval_system import AuroraApprovalSystem
except ImportError:
    print("❌ Could not import Aurora Approval System!")
    print("Make sure aurora_approval_system.py is in the same directory.")
    sys.exit(1)


class AuroraTeacher:
    """Simple CLI for teaching Aurora"""
    
    def __init__(self):
        self.approval_system = AuroraApprovalSystem()
    
    def show_help(self):
        """Show usage help"""
        print("🎓 AURORA TEACHER - Help Aurora Learn!")
        print("="*40)
        print()
        print("📚 Commands:")
        print("  python aurora_teacher.py                    # Show pending requests")
        print("  python aurora_teacher.py grade <id> <1-10> <feedback>")
        print("  python aurora_teacher.py approve <id>       # Quick approve (grade 8)")
        print("  python aurora_teacher.py reject <id>        # Quick reject (grade 3)")
        print("  python aurora_teacher.py report             # Show Aurora's grades")
        print()
        print("🎯 Grading Scale:")
        print("  10 = Perfect! Excellent work")
        print("  8-9 = Very good, minor improvements")
        print("  6-7 = Good approach, needs some work")
        print("  4-5 = Needs improvement, problematic")
        print("  1-3 = Major issues, wrong approach")
        print()
        print("💡 Tips:")
        print("  • Be specific in feedback - help Aurora learn!")
        print("  • Explain WHY something is good or bad")
        print("  • Encourage Aurora when she's learning")
        
    def grade_request(self, request_id: str, grade: int, feedback: str):
        """Grade a request with detailed feedback"""
        if grade >= 7:
            success = self.approval_system.approve_change(request_id, grade, feedback)
            if success:
                print(f"\n🎉 Great job teaching Aurora! Grade: {grade}/10")
        else:
            success = self.approval_system.reject_change(request_id, grade, feedback)
            if success:
                print(f"\n📚 Aurora will learn from this feedback! Grade: {grade}/10")
        
        return success
    
    def quick_approve(self, request_id: str):
        """Quickly approve with a good grade"""
        feedback = "Good work! This approach is correct and well-reasoned."
        return self.grade_request(request_id, 8, feedback)
    
    def quick_reject(self, request_id: str):
        """Quickly reject with learning feedback"""
        feedback = "This needs improvement. Please reconsider the approach and think about potential side effects."
        return self.grade_request(request_id, 3, feedback)
    
    def show_interactive_pending(self):
        """Show pending requests with interactive options"""
        self.approval_system.show_pending_requests()
        
        if not self.approval_system.pending_changes:
            print("✅ No requests to grade! Aurora is waiting for new challenges.")
            return
        
        print("\n💡 Quick Actions:")
        for req in self.approval_system.pending_changes[:3]:  # Show first 3
            req_id = req['id']
            print(f"   🟢 Approve {req_id}: python aurora_teacher.py approve {req_id}")
            print(f"   🔴 Reject {req_id}:  python aurora_teacher.py reject {req_id}")
            print(f"   📝 Grade {req_id}:   python aurora_teacher.py grade {req_id} <1-10> '<feedback>'")
    
    def run(self):
        """Main CLI interface"""
        if len(sys.argv) == 1:
            # No arguments - show pending requests
            self.show_interactive_pending()
            return
        
        command = sys.argv[1].lower()
        
        if command in ['help', '-h', '--help']:
            self.show_help()
        
        elif command == 'report':
            self.approval_system.show_grade_report()
        
        elif command == 'approve' and len(sys.argv) >= 3:
            request_id = sys.argv[2]
            if self.quick_approve(request_id):
                print("✅ Aurora's request approved!")
        
        elif command == 'reject' and len(sys.argv) >= 3:
            request_id = sys.argv[2]
            if self.quick_reject(request_id):
                print("📚 Aurora will learn from this rejection!")
        
        elif command == 'grade' and len(sys.argv) >= 5:
            request_id = sys.argv[2]
            try:
                grade = int(sys.argv[3])
                if not 1 <= grade <= 10:
                    print("❌ Grade must be between 1 and 10!")
                    return
                
                feedback = " ".join(sys.argv[4:])
                if self.grade_request(request_id, grade, feedback):
                    print("✅ Aurora has been graded!")
            except ValueError:
                print("❌ Grade must be a number between 1 and 10!")
        
        elif command == 'pending':
            self.approval_system.show_pending_requests()
        
        else:
            print("❌ Unknown command or missing arguments!")
            print("Use: python aurora_teacher.py help")


if __name__ == "__main__":
    teacher = AuroraTeacher()
    teacher.run()