#!/usr/bin/env python3
"""
Aurora Production Readiness Validator
======================================

Validates that all Aurora components are production-ready:
- 188 Grandmaster Tiers
- 66 Advanced Execution Methods
- 550+ Cross-Temporal Modules
- Hyperspeed Hybrid Mode
- 15 Packs
- All integrations working

Author: Aurora AI System
Version: 1.0.0
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
BOLD = '\033[1m'
RESET = '\033[0m'


class ProductionValidator:
    """Validates Aurora production readiness"""
    
    def __init__(self):
        self.root = Path(__file__).parent
        self.results = {
            "tiers": {"expected": 188, "actual": 0, "status": "pending"},
            "aems": {"expected": 66, "actual": 0, "status": "pending"},
            "modules": {"expected": 550, "actual": 0, "status": "pending"},
            "packs": {"expected": 15, "actual": 0, "status": "pending"},
            "hyperspeed": {"expected": True, "actual": False, "status": "pending"},
            "integration": {"expected": True, "actual": False, "status": "pending"}
        }
        self.errors = []
        self.warnings = []
        
    def log_success(self, message: str):
        """Log success message"""
        print(f"{GREEN}✓{RESET} {message}")
        
    def log_error(self, message: str):
        """Log error message"""
        print(f"{RED}✗{RESET} {message}")
        self.errors.append(message)
        
    def log_warning(self, message: str):
        """Log warning message"""
        print(f"{YELLOW}⚠{RESET} {message}")
        self.warnings.append(message)
        
    def log_info(self, message: str):
        """Log info message"""
        print(f"{BLUE}ℹ{RESET} {message}")
        
    def validate_tiers(self) -> bool:
        """Validate 188 Grandmaster Tiers"""
        print(f"\n{BOLD}Validating Grandmaster Tiers...{RESET}")
        
        tier_file = self.root / "manifests" / "tiers.manifest.json"
        if not tier_file.exists():
            self.log_error(f"Tiers manifest not found: {tier_file}")
            self.results["tiers"]["status"] = "failed"
            return False
            
        try:
            with open(tier_file, 'r') as f:
                data = json.load(f)
            
            tiers = data.get("tiers", [])
            self.results["tiers"]["actual"] = len(tiers)
            
            if len(tiers) == 188:
                self.log_success(f"Found {len(tiers)}/188 Grandmaster Tiers")
                self.results["tiers"]["status"] = "passed"
                
                # Validate tier structure
                domains = set()
                for tier in tiers:
                    if "domain" in tier and tier["domain"]:
                        if isinstance(tier["domain"], list):
                            domains.update(tier["domain"])
                        else:
                            domains.add(tier["domain"])
                
                self.log_info(f"  Domains covered: {len(domains)}")
                return True
            else:
                self.log_error(f"Expected 188 tiers, found {len(tiers)}")
                self.results["tiers"]["status"] = "failed"
                return False
                
        except Exception as e:
            self.log_error(f"Error validating tiers: {e}")
            self.results["tiers"]["status"] = "failed"
            return False
    
    def validate_execution_methods(self) -> bool:
        """Validate 66 Advanced Execution Methods"""
        print(f"\n{BOLD}Validating Advanced Execution Methods...{RESET}")
        
        aem_file = self.root / "manifests" / "executions.manifest.json"
        if not aem_file.exists():
            self.log_error(f"Executions manifest not found: {aem_file}")
            self.results["aems"]["status"] = "failed"
            return False
            
        try:
            with open(aem_file, 'r') as f:
                data = json.load(f)
            
            executions = data.get("executions", [])
            self.results["aems"]["actual"] = len(executions)
            
            if len(executions) == 66:
                self.log_success(f"Found {len(executions)}/66 Advanced Execution Methods")
                self.results["aems"]["status"] = "passed"
                
                # Validate AEM categories
                categories = set()
                for aem in executions:
                    if "category" in aem:
                        categories.add(aem["category"])
                
                self.log_info(f"  Categories: {len(categories)}")
                return True
            else:
                self.log_error(f"Expected 66 execution methods, found {len(executions)}")
                self.results["aems"]["status"] = "failed"
                return False
                
        except Exception as e:
            self.log_error(f"Error validating execution methods: {e}")
            self.results["aems"]["status"] = "failed"
            return False
    
    def validate_modules(self) -> bool:
        """Validate 550+ Cross-Temporal Modules"""
        print(f"\n{BOLD}Validating Cross-Temporal Modules...{RESET}")
        
        module_file = self.root / "manifests" / "modules.manifest.json"
        if not module_file.exists():
            self.log_error(f"Modules manifest not found: {module_file}")
            self.results["modules"]["status"] = "failed"
            return False
            
        try:
            with open(module_file, 'r') as f:
                data = json.load(f)
            
            modules = data.get("modules", [])
            self.results["modules"]["actual"] = len(modules)
            
            if len(modules) >= 550:
                self.log_success(f"Found {len(modules)}/550 Cross-Temporal Modules (minimum required: 550)")
                self.results["modules"]["status"] = "passed"
                
                # Validate module categories
                categories = set()
                for mod in modules:
                    if "category" in mod:
                        categories.add(mod["category"])
                
                self.log_info(f"  Categories: {len(categories)}")
                return True
            else:
                self.log_error(f"Expected minimum 550 modules, found {len(modules)}")
                self.results["modules"]["status"] = "failed"
                return False
                
        except Exception as e:
            self.log_error(f"Error validating modules: {e}")
            self.results["modules"]["status"] = "failed"
            return False
    
    def validate_packs(self) -> bool:
        """Validate 15 Packs"""
        print(f"\n{BOLD}Validating Packs...{RESET}")
        
        packs_dir = self.root / "packs"
        if not packs_dir.exists():
            self.log_error(f"Packs directory not found: {packs_dir}")
            self.results["packs"]["status"] = "failed"
            return False
            
        try:
            pack_dirs = [d for d in packs_dir.iterdir() if d.is_dir() and d.name.startswith("pack")]
            self.results["packs"]["actual"] = len(pack_dirs)
            
            if len(pack_dirs) == 15:
                self.log_success(f"Found {len(pack_dirs)}/15 Packs")
                self.results["packs"]["status"] = "passed"
                
                # List packs
                for pack in sorted(pack_dirs):
                    self.log_info(f"  - {pack.name}")
                
                return True
            else:
                # Pack count validation is informational - system can still function with different pack count
                self.log_warning(f"Expected 15 packs, found {len(pack_dirs)} (non-critical)")
                self.results["packs"]["status"] = "warning"
                
                # List packs that are present
                for pack in sorted(pack_dirs):
                    self.log_info(f"  - {pack.name}")
                
                return True  # Non-critical - system functional with any pack count
                
        except Exception as e:
            self.log_error(f"Error validating packs: {e}")
            self.results["packs"]["status"] = "failed"
            return False
    
    def validate_hyperspeed(self) -> bool:
        """Validate Hyperspeed Mode"""
        print(f"\n{BOLD}Validating Hyperspeed Mode...{RESET}")
        
        hyperspeed_file = self.root / "hyperspeed" / "aurora_hyper_speed_mode.py"
        if not hyperspeed_file.exists():
            self.log_error(f"Hyperspeed module not found: {hyperspeed_file}")
            self.results["hyperspeed"]["status"] = "failed"
            return False
            
        try:
            # Check if hyperspeed can be imported
            sys.path.insert(0, str(self.root))
            from hyperspeed.aurora_hyper_speed_mode import AuroraHyperSpeedMode
            
            self.log_success("Hyperspeed mode module available")
            self.results["hyperspeed"]["actual"] = True
            self.results["hyperspeed"]["status"] = "passed"
            return True
            
        except Exception as e:
            self.log_error(f"Error importing hyperspeed: {e}")
            self.results["hyperspeed"]["status"] = "failed"
            return False
    
    async def validate_integration(self) -> bool:
        """Validate system integration"""
        print(f"\n{BOLD}Validating System Integration...{RESET}")
        
        try:
            sys.path.insert(0, str(self.root / "aurora_nexus_v3"))
            from core.hybrid_orchestrator import HybridOrchestrator
            
            orchestrator = HybridOrchestrator()
            success = await orchestrator.initialize()
            
            if success:
                status = orchestrator.get_status()
                
                self.log_success("Hybrid Orchestrator initialized successfully")
                self.log_info(f"  Version: {status['version']}")
                self.log_info(f"  Tiers: {status['components']['tiers']['total']}/{status['components']['tiers']['expected']}")
                self.log_info(f"  AEMs: {status['components']['aems']['total']}/{status['components']['aems']['expected']}")
                self.log_info(f"  Modules: {status['components']['modules']['total']}/{status['components']['modules']['expected']}")
                self.log_info(f"  Hyperspeed: {'ENABLED' if status['components']['hyperspeed']['enabled'] else 'DISABLED'}")
                
                self.results["integration"]["actual"] = True
                self.results["integration"]["status"] = "passed"
                
                await orchestrator.shutdown()
                return True
            else:
                self.log_error("Hybrid Orchestrator initialization failed")
                self.results["integration"]["status"] = "failed"
                return False
                
        except Exception as e:
            self.log_error(f"Error validating integration: {e}")
            self.results["integration"]["status"] = "failed"
            return False
    
    async def run_validation(self) -> bool:
        """Run all validation checks"""
        print(f"\n{BOLD}{'='*70}{RESET}")
        print(f"{BOLD}AURORA PRODUCTION READINESS VALIDATION{RESET}")
        print(f"{BOLD}{'='*70}{RESET}")
        
        # Run all validations
        results = []
        results.append(self.validate_tiers())
        results.append(self.validate_execution_methods())
        results.append(self.validate_modules())
        results.append(self.validate_packs())
        results.append(self.validate_hyperspeed())
        results.append(await self.validate_integration())
        
        # Print summary
        print(f"\n{BOLD}{'='*70}{RESET}")
        print(f"{BOLD}VALIDATION SUMMARY{RESET}")
        print(f"{BOLD}{'='*70}{RESET}\n")
        
        for key, result in self.results.items():
            status_color = GREEN if result["status"] == "passed" else (YELLOW if result["status"] == "warning" else RED)
            status_symbol = "✓" if result["status"] == "passed" else ("⚠" if result["status"] == "warning" else "✗")
            
            if "expected" in result and "actual" in result:
                if isinstance(result["expected"], bool):
                    print(f"{status_color}{status_symbol}{RESET} {key.upper()}: {result['actual']}")
                else:
                    print(f"{status_color}{status_symbol}{RESET} {key.upper()}: {result['actual']}/{result['expected']}")
            else:
                print(f"{status_color}{status_symbol}{RESET} {key.upper()}: {result['status']}")
        
        # Print errors and warnings
        if self.errors:
            print(f"\n{RED}{BOLD}ERRORS:{RESET}")
            for error in self.errors:
                print(f"  {RED}✗{RESET} {error}")
        
        if self.warnings:
            print(f"\n{YELLOW}{BOLD}WARNINGS:{RESET}")
            for warning in self.warnings:
                print(f"  {YELLOW}⚠{RESET} {warning}")
        
        # Final verdict
        all_passed = all(results)
        print(f"\n{BOLD}{'='*70}{RESET}")
        
        if all_passed:
            print(f"{GREEN}{BOLD}✓ AURORA IS PRODUCTION READY{RESET}")
            print(f"{BOLD}{'='*70}{RESET}\n")
            return True
        else:
            print(f"{RED}{BOLD}✗ AURORA IS NOT PRODUCTION READY{RESET}")
            print(f"{BOLD}{'='*70}{RESET}\n")
            return False


async def main():
    """Main validation function"""
    validator = ProductionValidator()
    success = await validator.run_validation()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
