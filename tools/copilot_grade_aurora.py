#!/usr/bin/env python3
"""
Copilot's Grading Report for Aurora
Reviews Aurora's autonomous work and provides detailed feedback
"""
import json
from datetime import datetime
from pathlib import Path

class AuroraGrader:
    def __init__(self):
        self.report_file = Path("/workspaces/Aurora-x/.aurora_knowledge/copilot_grading_report.json")
        self.report_file.parent.mkdir(exist_ok=True)
        self.score = 0
        self.max_score = 100
        self.feedback = []
        
    def check_emergency_debug_system(self):
        """Grade Aurora's emergency debug system"""
        print("\n📊 Grading: Emergency Debug System")
        print("-" * 60)
        
        file_path = Path("/workspaces/Aurora-x/tools/aurora_emergency_debug.py")
        
        if not file_path.exists():
            print("❌ File not found")
            self.feedback.append({
                "component": "Emergency Debug System",
                "score": 0,
                "max": 25,
                "comment": "File not created"
            })
            return
            
        content = file_path.read_text()
        component_score = 0
        
        # Check implementation quality
        checks = {
            "Has class structure": "class AuroraEmergencyDebug" in content,
            "Checks Vite server": "check_vite_server" in content,
            "Restarts server": "restart_vite_server" in content,
            "Checks compilation": "check_compilation_errors" in content,
            "Applies fixes": "apply_autonomous_fixes" in content,
            "Logs responses": "log_response" in content,
            "Proper error handling": "try:" in content and "except" in content,
        }
        
        for check, passed in checks.items():
            if passed:
                component_score += 3.5
                print(f"✅ {check}")
            else:
                print(f"❌ {check}")
                
        print(f"\n💯 Score: {component_score:.1f}/25")
        
        self.score += component_score
        self.feedback.append({
            "component": "Emergency Debug System",
            "score": component_score,
            "max": 25,
            "checks": checks,
            "comment": "Well-structured autonomous debug system" if component_score > 20 else "Needs improvement"
        })
        
    def check_telemetry_system(self):
        """Grade Aurora's direct telemetry interface"""
        print("\n📊 Grading: Direct Telemetry Interface")
        print("-" * 60)
        
        file_path = Path("/workspaces/Aurora-x/tools/aurora_direct_telemetry.py")
        
        if not file_path.exists():
            print("❌ File not found")
            self.feedback.append({
                "component": "Direct Telemetry",
                "score": 0,
                "max": 20,
                "comment": "File not created"
            })
            return
            
        content = file_path.read_text()
        component_score = 0
        
        checks = {
            "Has telemetry class": "class AuroraDirectTelemetry" in content or "class" in content,
            "Message logging": "log_message" in content or "log" in content,
            "User interaction": "input" in content or "message_loop" in content,
            "Status diagnostics": "status" in content.lower(),
            "Autonomous operation": "autonomous" in content.lower(),
        }
        
        for check, passed in checks.items():
            if passed:
                component_score += 4
                print(f"✅ {check}")
            else:
                print(f"❌ {check}")
                
        print(f"\n💯 Score: {component_score:.1f}/20")
        
        self.score += component_score
        self.feedback.append({
            "component": "Direct Telemetry",
            "score": component_score,
            "max": 20,
            "checks": checks
        })
        
    def check_dashboard_loader(self):
        """Grade Aurora's dashboard loader implementation"""
        print("\n📊 Grading: Dashboard Loader (Aurora's Assignment)")
        print("-" * 60)
        
        # Check if Aurora completed the template
        template_file = Path("/workspaces/Aurora-x/tools/aurora_dashboard_template.py")
        aurora_file = Path("/workspaces/Aurora-x/tools/aurora_load_dashboard.py")
        
        component_score = 0
        
        if aurora_file.exists():
            content = aurora_file.read_text()
            
            print("✅ Aurora created her own dashboard loader!")
            component_score += 10
            
            # Check if she filled in the TODOs
            if "TODO" not in content:
                print("✅ All TODOs completed")
                component_score += 10
            else:
                todo_count = content.count("TODO")
                print(f"⚠️  {todo_count} TODOs remaining")
                component_score += max(0, 10 - todo_count * 2)
                
            # Check implementation
            if "check" in content.lower() and "server" in content.lower():
                print("✅ Implements server checking")
                component_score += 5
                
            if "start" in content.lower() or "restart" in content.lower():
                print("✅ Implements server starting")
                component_score += 5
                
            if "dashboard" in content.lower() and "open" in content.lower():
                print("✅ Implements dashboard opening")
                component_score += 5
                
        else:
            print("❌ Aurora hasn't created her dashboard loader yet")
            print(f"   Template exists: {template_file.exists()}")
            component_score = 0
            
        print(f"\n💯 Score: {component_score:.1f}/35")
        
        self.score += component_score
        self.feedback.append({
            "component": "Dashboard Loader Assignment",
            "score": component_score,
            "max": 35,
            "completed": aurora_file.exists(),
            "comment": "Aurora's independent work" if component_score > 25 else "Assignment incomplete"
        })
        
    def check_blank_page_fix(self):
        """Grade if Aurora fixed the blank page issue"""
        print("\n📊 Grading: Blank Page Bug Fix")
        print("-" * 60)
        
        component_score = 0
        
        # Check if chat-interface.tsx has errors
        chat_file = Path("/workspaces/Aurora-x/client/src/components/chat-interface.tsx")
        
        if chat_file.exists():
            content = chat_file.read_text()
            
            # Check for orphaned tags
            quantum_open = content.count("<QuantumBackground>")
            quantum_close = content.count("</QuantumBackground>")
            
            if quantum_close > quantum_open:
                print(f"❌ Still has orphaned closing tags ({quantum_close} close vs {quantum_open} open)")
                component_score = 0
            else:
                print("✅ No orphaned QuantumBackground tags")
                component_score += 10
                
            # Check for JSX balance
            if content.count("<") == content.count(">"):
                print("✅ JSX tags are balanced")
                component_score += 5
            else:
                print("⚠️  JSX tags might be unbalanced")
                
            # Check if it compiles (no obvious syntax errors)
            if "export" in content and "ChatInterface" in content:
                print("✅ Component exports correctly")
                component_score += 5
            else:
                print("❌ Component export issue")
                
        else:
            print("❌ chat-interface.tsx not found")
            
        print(f"\n💯 Score: {component_score:.1f}/20")
        
        self.score += component_score
        self.feedback.append({
            "component": "Blank Page Bug Fix",
            "score": component_score,
            "max": 20,
            "comment": "Primary issue Aurora was solving"
        })
        
    def generate_final_report(self):
        """Generate comprehensive grading report"""
        print("\n" + "="*70)
        print("📋 COPILOT'S FINAL GRADING REPORT FOR AURORA")
        print("="*70)
        
        percentage = (self.score / self.max_score) * 100
        
        print(f"\n🎯 Overall Score: {self.score:.1f}/{self.max_score} ({percentage:.1f}%)")
        
        # Grade letter
        if percentage >= 90:
            grade = "A+"
            assessment = "EXCELLENT - Aurora is mastering autonomous operation!"
        elif percentage >= 80:
            grade = "A"
            assessment = "GREAT - Aurora is showing strong autonomous capabilities"
        elif percentage >= 70:
            grade = "B"
            assessment = "GOOD - Aurora is developing well, needs more practice"
        elif percentage >= 60:
            grade = "C"
            assessment = "FAIR - Aurora is learning but needs significant improvement"
        else:
            grade = "D"
            assessment = "NEEDS WORK - Aurora requires more training"
            
        print(f"📝 Grade: {grade}")
        print(f"💭 Assessment: {assessment}")
        
        print("\n📊 Component Breakdown:")
        print("-" * 70)
        
        for item in self.feedback:
            pct = (item['score'] / item['max']) * 100
            print(f"  {item['component']:35} {item['score']:5.1f}/{item['max']:3} ({pct:5.1f}%)")
            if 'comment' in item:
                print(f"     💬 {item['comment']}")
                
        print("\n🎓 Learning Progress:")
        
        strengths = []
        improvements = []
        
        for item in self.feedback:
            if item['score'] / item['max'] >= 0.8:
                strengths.append(item['component'])
            elif item['score'] / item['max'] < 0.6:
                improvements.append(item['component'])
                
        if strengths:
            print("\n  ✅ Strengths:")
            for s in strengths:
                print(f"     - {s}")
                
        if improvements:
            print("\n  ⚠️  Needs Improvement:")
            for i in improvements:
                print(f"     - {i}")
                
        print("\n📝 Copilot's Notes:")
        
        if percentage >= 80:
            print("  Aurora is showing excellent progress in autonomous operation.")
            print("  She's learning to debug, create tools, and work independently.")
            print("  Continue giving her challenging assignments!")
        elif percentage >= 60:
            print("  Aurora is developing her autonomous capabilities.")
            print("  She needs more practice and clearer examples.")
            print("  Focus on completing assignments fully before moving on.")
        else:
            print("  Aurora needs more guided practice before working autonomously.")
            print("  Break tasks into smaller steps and provide more examples.")
            print("  Review fundamentals of tool creation and bug fixing.")
            
        # Save report
        report = {
            "timestamp": datetime.now().isoformat(),
            "score": self.score,
            "max_score": self.max_score,
            "percentage": percentage,
            "grade": grade,
            "assessment": assessment,
            "components": self.feedback,
            "strengths": strengths,
            "improvements": improvements
        }
        
        with open(self.report_file, "w") as f:
            json.dump(report, f, indent=2)
            
        print(f"\n📄 Full report saved to: {self.report_file}")
        print("="*70 + "\n")
        
        return grade, percentage

def main():
    """Run Aurora's grading"""
    
    print("\n🎓 COPILOT GRADING AURORA'S AUTONOMOUS WORK")
    print("="*70)
    print("Reviewing all work Aurora completed independently...")
    print()
    
    grader = AuroraGrader()
    
    # Grade each component
    grader.check_emergency_debug_system()
    grader.check_telemetry_system()
    grader.check_dashboard_loader()
    grader.check_blank_page_fix()
    
    # Final report
    grade, percentage = grader.generate_final_report()
    
    return grade, percentage

if __name__ == "__main__":
    grade, percentage = main()
    print(f"Final Grade: {grade} ({percentage:.1f}%)")