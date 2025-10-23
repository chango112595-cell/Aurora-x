#!/usr/bin/env python3
"""
build a command line tool for file processing

A command-line tool with common utility functions.
Extensible template for building CLI applications.

Usage examples:
    python build_a_command_line_tool_fo.py info                  # Show system information
    python build_a_command_line_tool_fo.py process file.txt      # Process a file
    python build_a_command_line_tool_fo.py --verbose run         # Run with verbose output
"""

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path

# Try to import colorama for colored output
try:
    from colorama import Fore, Style, init

    init(autoreset=True)
    HAS_COLOR = True
except ImportError:
    HAS_COLOR = False

    class Fore:
        GREEN = YELLOW = RED = CYAN = MAGENTA = RESET = ""

    class Style:
        BRIGHT = DIM = RESET_ALL = ""


class CLI:
    """Main CLI application class"""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose

    def log(self, message: str, level: str = "info"):
        """Log a message with color coding based on level"""
        timestamp = datetime.now().strftime("%H:%M:%S")

        colors = {
            "info": Fore.CYAN,
            "success": Fore.GREEN,
            "warning": Fore.YELLOW,
            "error": Fore.RED,
            "debug": Fore.MAGENTA,
        }

        color = colors.get(level, "")

        if level == "debug" and not self.verbose:
            return

        print(f"{color}[{timestamp}] {message}{Fore.RESET}")

    def cmd_info(self, args):
        """Display system and environment information"""
        self.log("System Information", "info")
        print(f"  Python: {sys.version.split()[0]}")
        print(f"  Platform: {sys.platform}")
        print(f"  Current Dir: {os.getcwd()}")
        print(f"  User: {os.environ.get('USER', 'unknown')}")
        self.log("Command completed successfully", "success")
        return 0

    def cmd_process(self, args):
        """Process files based on input"""
        if not args.input:
            self.log("No input file specified", "error")
            return 1

        input_path = Path(args.input)

        if not input_path.exists():
            self.log(f"File not found: {input_path}", "error")
            return 1

        self.log(f"Processing: {input_path}", "info")

        # Example processing logic
        try:
            with open(input_path) as f:
                lines = f.readlines()
                self.log(f"Read {len(lines)} lines", "debug")

            # Process the data (example: count words)
            total_words = sum(len(line.split()) for line in lines)

            print(f"\n{Style.BRIGHT}File Statistics:{Style.RESET_ALL}")
            print(f"  Lines: {len(lines)}")
            print(f"  Words: {total_words}")
            print(f"  Size: {input_path.stat().st_size} bytes")

            self.log("Processing completed", "success")
            return 0

        except Exception as e:
            self.log(f"Error processing file: {e}", "error")
            return 1

    def cmd_run(self, args):
        """Run the main application logic"""
        self.log("Starting application...", "info")

        # Example task execution
        tasks = args.tasks or ["default_task"]

        for i, task in enumerate(tasks, 1):
            self.log(f"Running task {i}/{len(tasks)}: {task}", "debug")
            print(f"  {Fore.GREEN}✓{Fore.RESET} Task '{task}' completed")

        self.log("All tasks completed successfully", "success")
        return 0


def main():
    """Main entry point for the CLI"""
    parser = argparse.ArgumentParser(
        description="build a command line tool for file processing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")

    parser.add_argument("--version", action="version", version="%(prog)s 1.0.0")

    # Subcommands
    subparsers = parser.add_subparsers(title="Commands", dest="command", help="Available commands")

    # Info command
    subparsers.add_parser("info", help="Display system information")

    # Process command
    process_parser = subparsers.add_parser("process", help="Process input files")
    process_parser.add_argument("input", help="Input file to process")

    # Run command
    run_parser = subparsers.add_parser("run", help="Run the application")
    run_parser.add_argument("-t", "--tasks", nargs="*", help="Tasks to execute")

    args = parser.parse_args()

    # Create CLI instance
    cli = CLI(verbose=args.verbose)

    # Route to appropriate command
    if not args.command:
        parser.print_help()
        return 1

    commands = {"info": cli.cmd_info, "process": cli.cmd_process, "run": cli.cmd_run}

    handler = commands.get(args.command)
    if handler:
        return handler(args)
    else:
        cli.log(f"Unknown command: {args.command}", "error")
        return 1


if __name__ == "__main__":
    sys.exit(main())
