"""
CLI Tool Template Generator for T08 Intent Router
Generates Python CLI applications with argparse
"""


def render_cli(name: str, brief: str, fields: dict) -> str:
    """
    Generate a CLI tool Python script based on intent

    Args:
        name: Tool name (e.g., 'hash_files', 'file_manager')
        brief: Brief description of what the tool does
        fields: Additional fields from intent classification

    Returns:
        Complete Python CLI script as string
    """

    # Check if this is a hash files request
    is_hash_tool = any(word in brief.lower() for word in ["hash", "md5", "sha", "checksum"])

    if is_hash_tool:
        return _render_hash_cli(name, brief)
    else:
        return _render_generic_cli(name, brief)


def _render_hash_cli(name: str, brief: str) -> str:
    """Generate a file hashing CLI tool"""
    return f'''#!/usr/bin/env python3
"""
{brief}

A command-line tool for computing file hashes using various algorithms.
Supports MD5, SHA1, SHA256, and SHA512 hashing algorithms.

Usage examples:
    python {name}.py file1.txt                    # Default SHA256
    python {name}.py -a md5 file1.txt file2.txt   # MD5 hash
    python {name}.py -a sha512 *.py               # SHA512 for all Python files
    python {name}.py -r /path/to/directory        # Recursive directory hashing
"""

import argparse
import hashlib
import os
import sys
from pathlib import Path
from typing import List, Optional

# Try to import colorama for colored output
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    HAS_COLOR = True
except ImportError:
    HAS_COLOR = False
    # Define dummy color constants
    class Fore:
        GREEN = YELLOW = RED = CYAN = RESET = ''
    class Style:
        BRIGHT = RESET_ALL = ''


def compute_hash(filepath: Path, algorithm: str = 'sha256') -> Optional[str]:
    """
    Compute hash of a file using specified algorithm

    Args:
        filepath: Path to the file
        algorithm: Hash algorithm (md5, sha1, sha256, sha512)

    Returns:
        Hex digest string or None if error
    """
    try:
        hash_obj = hashlib.new(algorithm)

        # Read file in chunks for memory efficiency
        with open(filepath, 'rb') as f:
            while chunk := f.read(8192):
                hash_obj.update(chunk)

        return hash_obj.hexdigest()
    except (IOError, OSError) as e:
        print(f"{{Fore.RED}}Error reading {{filepath}}: {{e}}{{Fore.RESET}}")
        return None
    except ValueError as e:
        print(f"{{Fore.RED}}Invalid algorithm '{{algorithm}}': {{e}}{{Fore.RESET}}")
        return None


def process_files(files: List[str], algorithm: str, recursive: bool = False) -> int:
    """
    Process list of files/patterns and compute hashes

    Args:
        files: List of file paths or patterns
        algorithm: Hash algorithm to use
        recursive: Whether to process directories recursively

    Returns:
        Number of files successfully processed
    """
    processed = 0

    for file_pattern in files:
        path = Path(file_pattern)

        if path.is_dir():
            if recursive:
                # Process directory recursively
                pattern = '**/*' if recursive else '*'
                for file_path in path.glob(pattern):
                    if file_path.is_file():
                        if hash_value := compute_hash(file_path, algorithm):
                            print(f"{{Fore.GREEN}}{{algorithm.upper():8}}{{Fore.RESET}} "
                                  f"{{hash_value}}  {{Fore.CYAN}}{{file_path}}{{Fore.RESET}}")
                            processed += 1
            else:
                print(f"{{Fore.YELLOW}}Skipping directory: {{path}} (use -r for recursive){{Fore.RESET}}")
        elif path.is_file():
            # Process single file
            if hash_value := compute_hash(path, algorithm):
                print(f"{{Fore.GREEN}}{{algorithm.upper():8}}{{Fore.RESET}} "
                      f"{{hash_value}}  {{Fore.CYAN}}{{path}}{{Fore.RESET}}")
                processed += 1
        else:
            # Try as glob pattern
            matches = list(Path('.').glob(file_pattern))
            if matches:
                for file_path in matches:
                    if file_path.is_file():
                        if hash_value := compute_hash(file_path, algorithm):
                            print(f"{{Fore.GREEN}}{{algorithm.upper():8}}{{Fore.RESET}} "
                                  f"{{hash_value}}  {{Fore.CYAN}}{{file_path}}{{Fore.RESET}}")
                            processed += 1
            else:
                print(f"{{Fore.YELLOW}}No files found matching: {{file_pattern}}{{Fore.RESET}}")

    return processed


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="{brief}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s document.pdf                     # SHA256 hash of document.pdf
  %(prog)s -a md5 *.txt                     # MD5 hashes for all .txt files
  %(prog)s -a sha512 -r /home/user/docs     # SHA512 recursive directory scan
  %(prog)s file1.txt file2.txt file3.txt    # Multiple files at once

Supported algorithms: md5, sha1, sha256 (default), sha512
        """
    )

    parser.add_argument(
        'files',
        nargs='+',
        help='Files or patterns to hash'
    )

    parser.add_argument(
        '-a', '--algorithm',
        choices=['md5', 'sha1', 'sha256', 'sha512'],
        default='sha256',
        help='Hash algorithm to use (default: sha256)'
    )

    parser.add_argument(
        '-r', '--recursive',
        action='store_true',
        help='Process directories recursively'
    )

    parser.add_argument(
        '-v', '--version',
        action='version',
        version='%(prog)s 1.0.0'
    )

    args = parser.parse_args()

    # Process files
    print(f"{{Fore.CYAN}}{{Style.BRIGHT}}Computing {{args.algorithm.upper()}} hashes...{{Style.RESET_ALL}}")
    processed = process_files(args.files, args.algorithm, args.recursive)

    # Summary
    print(f"\\n{{Fore.GREEN}}Processed {{processed}} file(s){{Fore.RESET}}")

    # Exit with error if no files processed
    sys.exit(0 if processed > 0 else 1)


if __name__ == '__main__':
    main()
'''


def _render_generic_cli(name: str, brief: str) -> str:
    """Generate a generic CLI tool template"""
    return f'''#!/usr/bin/env python3
"""
{brief}

A command-line tool with common utility functions.
Extensible template for building CLI applications.

Usage examples:
    python {name}.py info                  # Show system information
    python {name}.py process file.txt      # Process a file
    python {name}.py --verbose run         # Run with verbose output
"""

import argparse
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Optional, List

# Try to import colorama for colored output
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    HAS_COLOR = True
except ImportError:
    HAS_COLOR = False
    class Fore:
        GREEN = YELLOW = RED = CYAN = MAGENTA = RESET = ''
    class Style:
        BRIGHT = DIM = RESET_ALL = ''


class CLI:
    """Main CLI application class"""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose

    def log(self, message: str, level: str = 'info'):
        """Log a message with color coding based on level"""
        timestamp = datetime.now().strftime('%H:%M:%S')

        colors = {{
            'info': Fore.CYAN,
            'success': Fore.GREEN,
            'warning': Fore.YELLOW,
            'error': Fore.RED,
            'debug': Fore.MAGENTA
        }}

        color = colors.get(level, '')

        if level == 'debug' and not self.verbose:
            return

        print(f"{{color}}[{{timestamp}}] {{message}}{{Fore.RESET}}")

    def cmd_info(self, args):
        """Display system and environment information"""
        self.log("System Information", "info")
        print(f"  Python: {{sys.version.split()[0]}}")
        print(f"  Platform: {{sys.platform}}")
        print(f"  Current Dir: {{os.getcwd()}}")
        print(f"  User: {{os.environ.get('USER', 'unknown')}}")
        self.log("Command completed successfully", "success")
        return 0

    def cmd_process(self, args):
        """Process files based on input"""
        if not args.input:
            self.log("No input file specified", "error")
            return 1

        input_path = Path(args.input)

        if not input_path.exists():
            self.log(f"File not found: {{input_path}}", "error")
            return 1

        self.log(f"Processing: {{input_path}}", "info")

        # Example processing logic
        try:
            with open(input_path, 'r') as f:
                lines = f.readlines()
                self.log(f"Read {{len(lines)}} lines", "debug")

            # Process the data (example: count words)
            total_words = sum(len(line.split()) for line in lines)

            print(f"\\n{{Style.BRIGHT}}File Statistics:{{Style.RESET_ALL}}")
            print(f"  Lines: {{len(lines)}}")
            print(f"  Words: {{total_words}}")
            print(f"  Size: {{input_path.stat().st_size}} bytes")

            self.log("Processing completed", "success")
            return 0

        except Exception as e:
            self.log(f"Error processing file: {{e}}", "error")
            return 1

    def cmd_run(self, args):
        """Run the main application logic"""
        self.log("Starting application...", "info")

        # Example task execution
        tasks = args.tasks or ["default_task"]

        for i, task in enumerate(tasks, 1):
            self.log(f"Running task {{i}}/{{len(tasks)}}: {{task}}", "debug")
            print(f"  {{Fore.GREEN}}{{Fore.RESET}} Task '{{task}}' completed")

        self.log("All tasks completed successfully", "success")
        return 0


def main():
    """Main entry point for the CLI"""
    parser = argparse.ArgumentParser(
        description="{brief}",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )

    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 1.0.0'
    )

    # Subcommands
    subparsers = parser.add_subparsers(
        title='Commands',
        dest='command',
        help='Available commands'
    )

    # Info command
    info_parser = subparsers.add_parser(
        'info',
        help='Display system information'
    )

    # Process command
    process_parser = subparsers.add_parser(
        'process',
        help='Process input files'
    )
    process_parser.add_argument(
        'input',
        help='Input file to process'
    )

    # Run command
    run_parser = subparsers.add_parser(
        'run',
        help='Run the application'
    )
    run_parser.add_argument(
        '-t', '--tasks',
        nargs='*',
        help='Tasks to execute'
    )

    args = parser.parse_args()

    # Create CLI instance
    cli = CLI(verbose=args.verbose)

    # Route to appropriate command
    if not args.command:
        parser.print_help()
        return 1

    commands = {{
        'info': cli.cmd_info,
        'process': cli.cmd_process,
        'run': cli.cmd_run
    }}

    handler = commands.get(args.command)
    if handler:
        return handler(args)
    else:
        cli.log(f"Unknown command: {{args.command}}", "error")
        return 1


if __name__ == '__main__':
    sys.exit(main())
'''
