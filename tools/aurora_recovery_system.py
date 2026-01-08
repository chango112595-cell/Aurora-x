#!/usr/bin/env python3
"""
Aurora Emergency Recovery System
Recovers Aurora from any platform (Windows, Mac, Linux, Replit)
"""

import json
import shutil
import sys
from datetime import datetime
from pathlib import Path


class AuroraRecoverySystem:
    """Platform-independent recovery for Aurora"""

    def __init__(self):
        self.backup_dir = Path.home() / ".aurora_backups"
        self.backup_dir.mkdir(exist_ok=True)
        self.critical_dirs = ["aurora_x", "server", "client/src", ".aurora"]

    def create_backup(self) -> bool:
        """Create emergency backup of Aurora system"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = self.backup_dir / f"backup_{timestamp}"
            backup_path.mkdir(parents=True)

            print(f"Creating backup: {backup_path}")

            for dir_name in self.critical_dirs:
                src = Path(dir_name)
                if src.exists():
                    dst = backup_path / dir_name
                    shutil.copytree(src, dst)
                    print(f"  Backed up {dir_name}")

            state_files = [
                ".self_learning_state.json",
                ".aurora_diagnostics.json",
                ".aurora_healing_log.json",
            ]

            for state_file in state_files:
                src = Path(state_file)
                if src.exists():
                    shutil.copy2(src, backup_path / state_file)
                    print(f"  Backed up {state_file}")

            metadata = {
                "timestamp": datetime.now().isoformat(),
                "platform": sys.platform,
                "backup_version": "1.0",
                "critical_dirs": self.critical_dirs,
            }

            (backup_path / "recovery_metadata.json").write_text(json.dumps(metadata, indent=2))

            print("Backup created successfully")
            return True

        except Exception as e:
            print(f"Backup failed: {e}")
            return False

    def restore_from_backup(self, backup_path: str | None = None) -> bool:
        """Restore Aurora from backup"""
        try:
            if not backup_path:
                backups = sorted(self.backup_dir.iterdir(), reverse=True)
                if not backups:
                    print("No backups found")
                    return False
                backup_path = backups[0]
            else:
                backup_path = Path(backup_path)

            print(f"Restoring from: {backup_path}")

            for dir_name in self.critical_dirs:
                src = backup_path / dir_name
                dst = Path(dir_name)

                if src.exists():
                    if dst.exists():
                        shutil.rmtree(dst)
                    shutil.copytree(src, dst)
                    print(f"  Restored {dir_name}")

            print("Aurora restored successfully")
            return True

        except Exception as e:
            print(f"Restore failed: {e}")
            return False

    def emergency_reset(self) -> bool:
        """Full emergency reset (last resort)"""
        try:
            print("EMERGENCY RESET INITIATED")
            print("This will reset Aurora to factory settings")

            confirm = input("Type 'CONFIRM' to proceed: ")
            if confirm != "CONFIRM":
                print("Reset cancelled")
                return False

            print("Clearing corrupted state...")
            state_files = [
                ".self_learning_state.json",
                ".aurora_diagnostics.json",
                ".aurora_healing_log.json",
                ".aurora_sessions.json",
            ]

            for state_file in state_files:
                try:
                    Path(state_file).unlink()
                    print(f"  Removed {state_file}")
                except FileNotFoundError:
                    pass
                except Exception as e:
                    print(f"  Could not remove {state_file}: {e}")

            print("Emergency reset complete")
            print("Aurora will reinitialize on next startup")
            return True

        except Exception as e:
            print(f"Reset failed: {e}")
            return False

    def health_report(self) -> dict:
        """Generate comprehensive recovery health report"""
        backups_available = 0
        latest_backup = None
        backup_integrity = "unknown"

        try:
            backups = list(self.backup_dir.iterdir())
            backups_available = len(backups)
            if backups:
                latest = sorted(backups, reverse=True)[0]
                latest_backup = str(latest)
                backup_integrity = self._verify_backup_integrity(latest)
        except Exception:
            pass

        critical_files = {
            "aurora_x": Path("aurora_x").exists(),
            "aurora_x/main.py": Path("aurora_x/main.py").exists(),
            "aurora_x/self_learn.py": Path("aurora_x/self_learn.py").exists(),
            "server": Path("server").exists(),
            "server/routes.ts": Path("server/routes.ts").exists(),
            "client": Path("client").exists(),
            "client/src/App.tsx": Path("client/src/App.tsx").exists(),
        }

        state_files = {
            ".self_learning_state.json": Path(".self_learning_state.json").exists(),
            ".aurora_diagnostics.json": Path(".aurora_diagnostics.json").exists(),
            ".aurora_healing_log.json": Path(".aurora_healing_log.json").exists(),
        }

        report = {
            "timestamp": datetime.now().isoformat(),
            "platform": sys.platform,
            "critical_files": critical_files,
            "state_files": state_files,
            "all_critical_present": all(critical_files.values()),
            "backups_available": backups_available,
            "latest_backup": latest_backup,
            "backup_integrity": backup_integrity,
            "backup_location": str(self.backup_dir),
            "recovery_ready": backups_available > 0 and backup_integrity == "valid",
        }
        return report

    def _verify_backup_integrity(self, backup_path: Path) -> str:
        """Verify backup integrity"""
        try:
            metadata_file = backup_path / "recovery_metadata.json"
            if not metadata_file.exists():
                return "missing_metadata"

            metadata = json.loads(metadata_file.read_text())

            for dir_name in metadata.get("critical_dirs", []):
                if not (backup_path / dir_name).exists():
                    return "incomplete"

            return "valid"
        except Exception as e:
            return f"error: {str(e)}"

    def preview_restore(self, backup_path: str | None = None) -> dict:
        """Preview what would be restored without actually restoring"""
        try:
            if not backup_path:
                backups = sorted(self.backup_dir.iterdir(), reverse=True)
                if not backups:
                    return {"error": "No backups found", "can_restore": False}
                backup_path = backups[0]
            else:
                backup_path = Path(backup_path)

            if not backup_path.exists():
                return {"error": "Backup path does not exist", "can_restore": False}

            preview = {
                "backup_path": str(backup_path),
                "can_restore": True,
                "directories_to_restore": [],
                "files_to_restore": [],
                "will_overwrite": [],
            }

            for dir_name in self.critical_dirs:
                src = backup_path / dir_name
                if src.exists():
                    preview["directories_to_restore"].append(dir_name)
                    if Path(dir_name).exists():
                        preview["will_overwrite"].append(dir_name)

            state_files = [
                ".self_learning_state.json",
                ".aurora_diagnostics.json",
                ".aurora_healing_log.json",
            ]

            for state_file in state_files:
                if (backup_path / state_file).exists():
                    preview["files_to_restore"].append(state_file)

            return preview

        except Exception as e:
            return {"error": str(e), "can_restore": False}

    def list_backups(self) -> list:
        """List all available backups"""
        backups = []
        try:
            for backup in sorted(self.backup_dir.iterdir(), reverse=True):
                metadata_file = backup / "recovery_metadata.json"
                if metadata_file.exists():
                    metadata = json.loads(metadata_file.read_text())
                    backups.append(
                        {
                            "path": str(backup),
                            "name": backup.name,
                            "timestamp": metadata.get("timestamp"),
                            "platform": metadata.get("platform"),
                        }
                    )
                else:
                    backups.append(
                        {
                            "path": str(backup),
                            "name": backup.name,
                            "timestamp": None,
                            "platform": None,
                        }
                    )
        except Exception:
            pass
        return backups


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Aurora Emergency Recovery System")
    parser.add_argument(
        "command",
        choices=["backup", "restore", "reset", "health", "list"],
        help="Recovery command to execute",
    )
    parser.add_argument("--backup-path", help="Path to backup (for restore)")

    args = parser.parse_args()

    recovery = AuroraRecoverySystem()

    if args.command == "backup":
        recovery.create_backup()
    elif args.command == "restore":
        recovery.restore_from_backup(args.backup_path)
    elif args.command == "reset":
        recovery.emergency_reset()
    elif args.command == "health":
        report = recovery.health_report()
        print(json.dumps(report, indent=2))
    elif args.command == "list":
        backups = recovery.list_backups()
        if backups:
            print(f"Found {len(backups)} backup(s):")
            for b in backups:
                print(f"  - {b['name']} ({b.get('timestamp', 'unknown')})")
        else:
            print("No backups found")


if __name__ == "__main__":
    main()
