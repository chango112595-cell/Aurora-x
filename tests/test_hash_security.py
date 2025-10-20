#!/usr/bin/env python3
"""
Tests to verify secure hash algorithms are used throughout the codebase.
"""

import hashlib
import sys
import unittest
from pathlib import Path

# Add aurora_x to path for import
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from aurora_x.spec.parser_nl import _hash
from aurora_x.learn import SeedStore


class TestHashSecurity(unittest.TestCase):
    """Test that secure hash algorithms (SHA-256) are used."""

    def test_parser_nl_uses_sha256(self):
        """Test that parser_nl._hash uses SHA-256."""
        test_text = "test string"
        expected = hashlib.sha256(test_text.encode("utf-8")).hexdigest()[:8]
        actual = _hash(test_text)
        self.assertEqual(actual, expected)

    def test_seed_store_uses_sha256(self):
        """Test that SeedStore.make_seed_key uses SHA-256."""
        import tempfile
        temp_dir = tempfile.mkdtemp()
        seed_path = Path(temp_dir) / "test_seeds.json"
        
        try:
            store = SeedStore(path=str(seed_path))
            
            # Test that make_seed_key produces SHA-256 hash
            func_sig = "def test() -> None"
            context = "test context"
            combined = f"{func_sig}:{context}"
            expected = hashlib.sha256(combined.encode()).hexdigest()[:16]
            actual = store.make_seed_key(func_sig, context)
            
            self.assertEqual(actual, expected)
        finally:
            # Cleanup
            if seed_path.exists():
                seed_path.unlink()
            if Path(temp_dir).exists():
                Path(temp_dir).rmdir()

    def test_no_md5_in_parser_nl(self):
        """Verify MD5 is not used in parser_nl.py."""
        parser_nl_path = Path(__file__).resolve().parents[1] / "aurora_x/spec/parser_nl.py"
        with open(parser_nl_path) as f:
            content = f.read()
        self.assertNotIn("hashlib.md5", content)

    def test_no_sha1_in_parser_nl(self):
        """Verify SHA1 is not used in parser_nl.py."""
        parser_nl_path = Path(__file__).resolve().parents[1] / "aurora_x/spec/parser_nl.py"
        with open(parser_nl_path) as f:
            content = f.read()
        self.assertNotIn("hashlib.sha1", content)

    def test_no_md5_in_seeds(self):
        """Verify MD5 is not used in seeds.py."""
        seeds_path = Path(__file__).resolve().parents[1] / "aurora_x/learn/seeds.py"
        with open(seeds_path) as f:
            content = f.read()
        self.assertNotIn("hashlib.md5", content)

    def test_no_md5_in_ci_gate(self):
        """Verify MD5 is not used in ci_gate.py."""
        ci_gate_path = Path(__file__).resolve().parents[1] / "aurora_x/checks/ci_gate.py"
        with open(ci_gate_path) as f:
            content = f.read()
        self.assertNotIn("hashlib.md5", content)

    def test_no_md5_in_serve_addons(self):
        """Verify MD5 is not used in serve_addons.py."""
        serve_addons_path = Path(__file__).resolve().parents[1] / "aurora_x/serve_addons.py"
        with open(serve_addons_path) as f:
            content = f.read()
        self.assertNotIn("hashlib.md5", content)


if __name__ == "__main__":
    unittest.main()
