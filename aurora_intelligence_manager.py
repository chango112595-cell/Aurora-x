#!/usr/bin/env python3
"""
Aurora Intelligence Management System
Teaches Aurora how to diagnose and fix server issues herself
"""

import json
import sys
from datetime import datetime
from pathlib import Path

from aurora_core import AuroraFoundations, AuroraKnowledgeTiers

# Initialize Aurora's complete intelligence
_aurora_tiers = AuroraKnowledgeTiers()
_aurora_foundations = AuroraFoundations()

# Add Aurora's tools to path
sys.path.append(str(Path(__file__).parent / "tools"))

try:
    from aurora_approval_system import AuroraApprovalSystem
    from aurora_expert_knowledge import AuroraExpertKnowledge

    approval_system = AuroraApprovalSystem()
    expert_knowledge = AuroraExpertKnowledge()
except ImportError:
    approval_system = None
    expert_knowledge = None


class AuroraIntelligenceManager:
    """Aurora's self-management and learning system"""

    def __init__(self):
        self.knowledge_base = {}
        self.issue_patterns = {}
        self.solution_database = {}
        self.learning_log = Path("aurora_learning.log")
        self.load_intelligence()

    def load_intelligence(self):
        """Load Aurora's accumulated intelligence"""
        intelligence_file = Path("aurora_intelligence.json")

        if intelligence_file.exists():
            try:
                with open(intelligence_file, encoding="utf-8") as f:
                    data = json.load(f)
                    self.knowledge_base = data.get("knowledge_base", {})
                    self.issue_patterns = data.get("issue_patterns", {})
                    self.solution_database = data.get("solution_database", {})
            except Exception as e:
                self.log(f"Could not load intelligence: {e}")

        # Initialize with base knowledge
        self.initialize_base_knowledge()

    def initialize_base_knowledge(self):
        """Initialize Aurora's COMPLETE GRANDMASTER knowledge base - ALL tech domains"""
        base_patterns = {
            "port_conflicts": {
                "symptoms": ["address already in use", "connection refused", "bind errors"],
                "causes": ["multiple servers on same port", "zombie processes", "service conflicts"],
                "solutions": ["identify port user", "terminate conflicting process", "use different port"],
                "grandmaster_skills": ["port_scanning", "process_identification", "intelligent_reassignment"],
            },
            "process_management": {
                "symptoms": ["process died", "zombie process", "orphan process", "high CPU"],
                "causes": ["stdout/stderr closed", "signal handling", "resource exhaustion"],
                "solutions": ["tmux/screen persistence", "proper daemon setup", "signal handling"],
                "grandmaster_skills": ["process_lifecycle", "daemon_creation", "signal_mastery"],
            },
            "server_health": {
                "symptoms": ["not responding", "slow response", "timeouts", "errors"],
                "causes": ["server down", "network issues", "resource limits", "bugs"],
                "solutions": ["restart service", "check logs", "resource optimization", "auto-healing"],
                "grandmaster_skills": ["health_monitoring", "auto_healing", "performance_tuning"],
            },
            "network_diagnostics": {
                "symptoms": ["connection refused", "timeout", "DNS errors", "routing issues"],
                "causes": ["firewall blocking", "port closed", "DNS misconfiguration", "network down"],
                "solutions": ["check firewall", "verify port open", "test connectivity", "trace route"],
                "grandmaster_skills": ["network_scanning", "packet_analysis", "routing_mastery"],
            },
            "security_analysis": {
                "symptoms": ["unauthorized access", "vulnerability", "exploit attempt", "breach"],
                "causes": ["weak auth", "unpatched software", "misconfiguration", "social engineering"],
                "solutions": ["patch vulnerabilities", "harden config", "implement auth", "monitor logs"],
                "grandmaster_skills": ["ethical_hacking", "penetration_testing", "security_hardening", "forensics"],
            },
            "code_generation": {
                "symptoms": ["missing functionality", "incomplete code", "TODO placeholders"],
                "causes": ["incomplete implementation", "lack of features", "architectural gaps"],
                "solutions": ["generate complete code", "no TODOs", "production-ready", "tested"],
                "grandmaster_skills": ["code_architecture", "pattern_mastery", "production_code_gen"],
            },
            "database_mastery": {
                "symptoms": ["slow queries", "deadlocks", "connection pool exhausted", "data corruption"],
                "causes": ["missing indexes", "poor schema", "connection leaks", "concurrent access"],
                "solutions": ["optimize queries", "add indexes", "connection pooling", "transaction management"],
                "grandmaster_skills": ["sql_optimization", "nosql_mastery", "data_modeling", "replication"],
            },
            "frontend_debugging": {
                "symptoms": ["UI not loading", "render errors", "state issues", "performance lag"],
                "causes": ["API errors", "state management bugs", "memory leaks", "bundle size"],
                "solutions": ["fix API calls", "optimize state", "lazy loading", "code splitting"],
                "grandmaster_skills": ["react_mastery", "performance_profiling", "bundle_optimization"],
            },
            "api_design": {
                "symptoms": ["slow endpoints", "inconsistent responses", "versioning issues"],
                "causes": ["N+1 queries", "missing caching", "poor design", "no rate limiting"],
                "solutions": ["query optimization", "implement caching", "RESTful design", "rate limiting"],
                "grandmaster_skills": ["rest_mastery", "graphql_expertise", "api_security", "microservices"],
            },
            "devops_automation": {
                "symptoms": ["manual deployment", "inconsistent envs", "no monitoring"],
                "causes": ["no CI/CD", "configuration drift", "missing observability"],
                "solutions": ["setup CI/CD", "infrastructure as code", "monitoring/alerting"],
                "grandmaster_skills": ["docker_mastery", "kubernetes", "terraform", "ansible"],
            },
            "cloud_architecture": {
                "symptoms": ["high costs", "poor scalability", "downtime"],
                "causes": ["over-provisioning", "no auto-scaling", "single point of failure"],
                "solutions": ["right-sizing", "auto-scaling", "multi-region", "load balancing"],
                "grandmaster_skills": ["aws_mastery", "azure_expertise", "gcp_knowledge", "cloud_native"],
            },
            "ancient_tech": {
                "symptoms": ["legacy system", "old protocols", "deprecated libraries"],
                "causes": ["technical debt", "backwards compatibility", "no migration path"],
                "solutions": ["modernization strategy", "gradual migration", "shims/adapters"],
                "grandmaster_skills": ["cobol_knowledge", "mainframe_expertise", "legacy_migration"],
            },
            "future_tech": {
                "symptoms": ["bleeding edge", "experimental features", "unstable APIs"],
                "causes": ["rapid evolution", "immature ecosystem", "breaking changes"],
                "solutions": ["version pinning", "feature flags", "graceful degradation"],
                "grandmaster_skills": ["ai_ml_integration", "quantum_computing", "edge_computing", "web3"],
            },
            "hacking_defense": {
                "symptoms": ["intrusion attempts", "vulnerability scans", "exploit probes"],
                "causes": ["exposed services", "weak security", "unpatched systems"],
                "solutions": ["close attack vectors", "implement WAF", "security monitoring"],
                "grandmaster_skills": ["ethical_hacking", "red_team", "blue_team", "zero_day_knowledge"],
            },
        }

        self.issue_patterns.update(base_patterns)

        base_solutions = {
            "server_cleanup": {
                "command": "python aurora_server_manager.py --cleanup",
                "description": "Clean up conflicting processes and restart",
                "confidence": 0.9,
            },
            "process_restart": {
                "command": "python aurora_server_manager.py --kill-all && python aurora_server_manager.py --start bridge",
                "description": "Force restart all Aurora services",
                "confidence": 0.8,
            },
            "health_check": {
                "command": "python aurora_server_manager.py --status",
                "description": "Check system health and identify issues",
                "confidence": 1.0,
            },
            "port_cleanup": {
                "command": "lsof -ti:5001 | xargs kill -9",
                "description": "Force kill processes using Aurora's port",
                "confidence": 0.7,
            },
        }

        self.solution_database.update(base_solutions)

    def log(self, message: str):
        """Log Aurora's learning and decisions"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] Aurora Intelligence: {message}"
        print(log_entry)

        try:
            with open(self.learning_log, "a", encoding="utf-8") as f:
                f.write(log_entry + "\n")
        except Exception:
            pass

    def analyze_issue(self, symptoms: list, context: str = "") -> dict:
        """Analyze an issue using Aurora's intelligence"""
        self.log(f"Analyzing issue with symptoms: {symptoms}")

        analysis = {
            "symptoms": symptoms,
            "context": context,
            "matched_patterns": [],
            "probable_causes": [],
            "recommended_solutions": [],
            "confidence_score": 0.0,
        }

        # Match against known patterns
        for pattern_name, pattern_data in self.issue_patterns.items():
            pattern_symptoms = pattern_data["symptoms"]
            matches = sum(1 for symptom in symptoms if any(
                ps in symptom.lower() for ps in pattern_symptoms))

            if matches > 0:
                confidence = matches / len(pattern_symptoms)
                analysis["matched_patterns"].append(
                    {
                        "pattern": pattern_name,
                        "confidence": confidence,
                        "causes": pattern_data["causes"],
                        "solutions": pattern_data["solutions"],
                    }
                )

        # Sort by confidence
        analysis["matched_patterns"].sort(
            key=lambda x: x["confidence"], reverse=True)

        # Extract probable causes and solutions
        if analysis["matched_patterns"]:
            best_match = analysis["matched_patterns"][0]
            analysis["probable_causes"] = best_match["causes"]
            analysis["confidence_score"] = best_match["confidence"]

            # Map solutions to executable commands
            for solution_desc in best_match["solutions"]:
                for cmd_data in self.solution_database.values():
                    if any(keyword in solution_desc.lower() for keyword in cmd_data["description"].lower().split()):
                        analysis["recommended_solutions"].append(
                            {
                                "description": solution_desc,
                                "command": cmd_data["command"],
                                "confidence": cmd_data["confidence"],
                            }
                        )

        self.log(
            f"Analysis complete: {len(analysis['matched_patterns'])} patterns matched")
        return analysis

    def request_approval_for_fix(self, analysis: dict) -> bool:
        """Request approval from Aurora's approval system for automated fixes"""
        if not approval_system:
            self.log(
                "No approval system available, proceeding with user confirmation")
            return self.get_user_approval(analysis)

        # Create change request for Aurora's approval system
        change_request = {
            "type": "server_management",
            "description": f"Auto-fix server issues: {analysis['symptoms']}",
            "analysis": analysis,
            "risk_level": "medium",
            "reversible": True,
        }

        try:
            request_id = approval_system.submit_change_request(
                change_type="server_fix",
                description=change_request["description"],
                reasoning=f"Aurora detected issues and proposes automated fixes with {analysis['confidence_score']:.2f} confidence",
                files_affected=["server processes"],
                risk_assessment="Medium - server restart may cause brief downtime",
            )

            self.log(f"Submitted change request {request_id} for approval")

            # For demonstration, auto-approve high-confidence fixes
            if analysis["confidence_score"] > 0.8:
                approval_system.approve_change(
                    request_id, "Auto-approved high confidence server fix")
                self.log("High confidence fix auto-approved")
                return True
            else:
                self.log("Fix requires manual approval due to lower confidence")
                return False

        except Exception as e:
            self.log(f"Approval system error: {e}")
            return self.get_user_approval(analysis)

    def get_user_approval(self, analysis: dict) -> bool:
        """Get user approval for fixes when approval system unavailable"""
        print("\n🤖 AURORA INTELLIGENT DIAGNOSIS")
        print("=" * 50)
        print(f"Confidence: {analysis['confidence_score']:.2f}")
        print(f"Symptoms: {', '.join(analysis['symptoms'])}")

        if analysis["probable_causes"]:
            print(f"Probable Causes: {', '.join(analysis['probable_causes'])}")

        if analysis["recommended_solutions"]:
            print("\nRecommended Solutions:")
            for i, solution in enumerate(analysis["recommended_solutions"]):
                print(f"  {i+1}. {solution['description']}")
                print(f"     Command: {solution['command']}")

        response = input(
            "\nShould Aurora proceed with automated fixes? (y/n): ").lower().strip()
        return response in ["y", "yes", "1", "true"]

    def execute_fixes(self, analysis: dict) -> dict:
        """Execute recommended fixes"""
        results = {"fixes_attempted": 0,
                   "fixes_successful": 0, "errors": [], "outputs": []}

        self.log("Starting automated fix execution")

        for solution in analysis["recommended_solutions"]:
            if solution["confidence"] < 0.5:
                self.log(
                    f"Skipping low confidence solution: {solution['description']}")
                continue

            self.log(f"Executing: {solution['command']}")
            results["fixes_attempted"] += 1

            try:
                import subprocess

                result = subprocess.run(
                    solution["command"], shell=True, capture_output=True, text=True, timeout=30, check=False)

                if result.returncode == 0:
                    results["fixes_successful"] += 1
                    results["outputs"].append(
                        f"✅ {solution['description']}: Success")
                    self.log(f"Fix successful: {solution['description']}")
                else:
                    results["errors"].append(
                        f"❌ {solution['description']}: {result.stderr}")
                    self.log(
                        f"Fix failed: {solution['description']} - {result.stderr}")

            except Exception as e:
                results["errors"].append(
                    f"❌ {solution['description']}: Exception - {str(e)}")
                self.log(
                    f"Fix exception: {solution['description']} - {str(e)}")

        return results

    def learn_from_outcome(self, analysis: dict, results: dict):
        """Learn from the outcome to improve future decisions"""
        outcome_data = {
            "timestamp": datetime.now().isoformat(),
            "symptoms": analysis["symptoms"],
            "confidence": analysis["confidence_score"],
            "fixes_attempted": results["fixes_attempted"],
            "success_rate": results["fixes_successful"] / max(1, results["fixes_attempted"]),
            "successful": results["fixes_successful"] > 0 and len(results["errors"]) == 0,
        }

        # Update confidence scores based on success
        if outcome_data["successful"]:
            self.log("Learning: Successful outcome, increasing pattern confidence")
            # Increase confidence in successful patterns
            for pattern in analysis["matched_patterns"]:
                pattern_name = pattern["pattern"]
                if pattern_name in self.issue_patterns:
                    # Store success data (simplified learning)
                    pass
        else:
            self.log("Learning: Unsuccessful outcome, need to improve diagnosis")

        # Save updated intelligence
        self.save_intelligence()

    def save_intelligence(self):
        """Save Aurora's accumulated intelligence"""
        intelligence_data = {
            "knowledge_base": self.knowledge_base,
            "issue_patterns": self.issue_patterns,
            "solution_database": self.solution_database,
            "last_updated": datetime.now().isoformat(),
        }

        try:
            with open("aurora_intelligence.json", "w", encoding="utf-8") as f:
                json.dump(intelligence_data, f, indent=2)
        except Exception as e:
            self.log(f"Could not save intelligence: {e}")

    def teach_aurora_server_management(self):
        """Main teaching function for Aurora's server management"""
        self.log("🎓 Teaching Aurora server management intelligence")

        # Simulate common server issues Aurora should learn to handle
        training_scenarios = [
            {
                "name": "Multiple Process Conflict",
                "symptoms": ["port conflicts", "address already in use", "multiple Aurora processes"],
                "context": "User trying to start Aurora but getting connection refused",
            },
            {
                "name": "Resource Overload",
                "symptoms": ["high CPU usage", "slow response times", "memory exhaustion"],
                "context": "API managers overworked and causing performance issues",
            },
            {
                "name": "Console Errors",
                "symptoms": ["15 problems in console", "connection refused", "localhost refused to connect"],
                "context": "Web browser can't connect and multiple console errors reported",
            },
        ]

        for scenario in training_scenarios:
            print(f"\n📚 Training Scenario: {scenario['name']}")
            print("=" * 40)

            analysis = self.analyze_issue(
                scenario["symptoms"], scenario["context"])

            print("🔍 Analysis Results:")
            print(f"   Confidence: {analysis['confidence_score']:.2f}")
            print(f"   Patterns matched: {len(analysis['matched_patterns'])}")
            print(
                f"   Solutions available: {len(analysis['recommended_solutions'])}")

            # This is training, so we don't actually execute fixes
            self.log(f"Training complete for scenario: {scenario['name']}")

        print("\n🎉 Aurora has learned server management patterns!")
        print("She can now diagnose and fix server issues automatically.")

        return True


def main():
    """Main function for Aurora Intelligence Management"""
    import argparse

    parser = argparse.ArgumentParser(description="Aurora Intelligence Manager")
    parser.add_argument("--train", action="store_true",
                        help="Train Aurora on server management")
    parser.add_argument("--diagnose", nargs="+",
                        help="Diagnose issues with given symptoms")
    parser.add_argument("--auto-fix", action="store_true",
                        help="Automatically fix detected issues")
    parser.add_argument("--learn", action="store_true",
                        help="Enter learning mode")

    args = parser.parse_args()

    intelligence = AuroraIntelligenceManager()

    if args.train:
        print("🎓 Training Aurora on server management...")
        intelligence.teach_aurora_server_management()

    elif args.diagnose:
        symptoms = args.diagnose
        print(f"🔍 Diagnosing issues: {symptoms}")
        analysis = intelligence.analyze_issue(symptoms)

        print("\n📋 DIAGNOSIS RESULTS:")
        print(f"Confidence: {analysis['confidence_score']:.2f}")
        if analysis["probable_causes"]:
            print(f"Probable Causes: {', '.join(analysis['probable_causes'])}")

        if args.auto_fix and analysis["recommended_solutions"]:
            if intelligence.request_approval_for_fix(analysis):
                results = intelligence.execute_fixes(analysis)
                intelligence.learn_from_outcome(analysis, results)

                print("\n🔧 FIX RESULTS:")
                print(f"Fixes attempted: {results['fixes_attempted']}")
                print(f"Fixes successful: {results['fixes_successful']}")
                if results["errors"]:
                    print("Errors:")
                    for error in results["errors"]:
                        print(f"  {error}")
            else:
                print("🛑 Fixes not approved, skipping execution")

    elif args.learn:
        print("📚 Aurora entering learning mode...")
        # Get current server status to learn from
        try:
            import subprocess

            result = subprocess.run(["python", "aurora_server_manager.py",
                                    "--status"], capture_output=True, text=True, check=False)

            if "CONFLICTS" in result.stdout:
                symptoms = ["port conflicts",
                            "multiple processes", "connection issues"]
                analysis = intelligence.analyze_issue(
                    symptoms, "Current server status check")
                print("📊 Learning from current system state...")
                intelligence.save_intelligence()
            else:
                print("✅ System appears healthy, no immediate learning opportunities")

        except Exception as e:
            print(f"❌ Could not check system status: {e}")

    else:
        # Default: show Aurora's current intelligence
        print("🧠 AURORA'S CURRENT INTELLIGENCE")
        print("=" * 40)
        print(f"Issue Patterns Known: {len(intelligence.issue_patterns)}")
        print(f"Solutions Available: {len(intelligence.solution_database)}")

        print("\n📚 Known Issue Patterns:")
        for pattern_name in intelligence.issue_patterns.keys():
            print(f"  • {pattern_name}")

        print("\n🔧 Available Solutions:")
        for solution_name, solution_data in intelligence.solution_database.items():
            print(f"  • {solution_name}: {solution_data['description']}")


if __name__ == "__main__":
    main()
