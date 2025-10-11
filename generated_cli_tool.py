#!/usr/bin/env python3
"""
create a CLI tool to hash files

A command-line tool for computing file hashes using various algorithms.
Supports MD5, SHA1, SHA256, and SHA512 hashing algorithms.

Usage examples:
    python create_a_cli_tool_to_hash_fi.py file1.txt                    # Default SHA256
    python create_a_cli_tool_to_hash_fi.py -a md5 file1.txt file2.txt   # MD5 hash
    python create_a_cli_tool_to_hash_fi.py -a sha512 *.py               # SHA512 for all Python files
    python create_a_cli_tool_to_hash_fi.py -r /path/to/directory        # Recursive directory hashing
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
        print(f"{Fore.RED}Error reading {filepath}: {e}{Fore.RESET}")
        return None
    except ValueError as e:
        print(f"{Fore.RED}Invalid algorithm '{algorithm}': {e}{Fore.RESET}")
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
                            print(f"{Fore.GREEN}{algorithm.upper():8}{Fore.RESET} "
                                  f"{hash_value}  {Fore.CYAN}{file_path}{Fore.RESET}")
                            processed += 1
            else:
                print(f"{Fore.YELLOW}Skipping directory: {path} (use -r for recursive){Fore.RESET}")
        elif path.is_file():
            # Process single file
            if hash_value := compute_hash(path, algorithm):
                print(f"{Fore.GREEN}{algorithm.upper():8}{Fore.RESET} "
                      f"{hash_value}  {Fore.CYAN}{path}{Fore.RESET}")
                processed += 1
        else:
            # Try as glob pattern
            matches = list(Path('.').glob(file_pattern))
            if matches:
                for file_path in matches:
                    if file_path.is_file():
                        if hash_value := compute_hash(file_path, algorithm):
                            print(f"{Fore.GREEN}{algorithm.upper():8}{Fore.RESET} "
                                  f"{hash_value}  {Fore.CYAN}{file_path}{Fore.RESET}")
                            processed += 1
            else:
                print(f"{Fore.YELLOW}No files found matching: {file_pattern}{Fore.RESET}")
    
    return processed


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="create a CLI tool to hash files",
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
    print(f"{Fore.CYAN}{Style.BRIGHT}Computing {args.algorithm.upper()} hashes...{Style.RESET_ALL}")
    processed = process_files(args.files, args.algorithm, args.recursive)
    
    # Summary
    print(f"\n{Fore.GREEN}Processed {processed} file(s){Fore.RESET}")
    
    # Exit with error if no files processed
    sys.exit(0 if processed > 0 else 1)


if __name__ == '__main__':
    main()
