#!/usr/bin/env python3
"""
Tests for persistent learning seeds in Aurora-X
"""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

# Add aurora_x to path for import
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from aurora_x.learn import SeedStore


class TestSeedStore(unittest.TestCase):
    """Test SeedStore functionality."""

    def setUp(self):
        """Create a temporary directory for test files."""
        self.temp_dir = tempfile.mkdtemp()
        self.seed_path = Path(self.temp_dir) / "test_seeds.json"

    def tearDown(self):
        """Clean up temporary files."""
        if self.seed_path.exists():
            self.seed_path.unlink()
        if Path(self.temp_dir).exists():
            Path(self.temp_dir).rmdir()

    def test_initialization(self):
        """Test SeedStore initialization and default values."""
        store = SeedStore(path=str(self.seed_path))

        self.assertEqual(store.alpha, 0.2)
        self.assertEqual(store.drift_cap, 0.15)
        self.assertEqual(store.top_n, 10)
        self.assertTrue(self.seed_path.exists())

        # Check initial file content
        with open(self.seed_path) as f:
            data = json.load(f)
            self.assertIn("biases", data)
            self.assertIn("metadata", data)
            self.assertEqual(data["biases"], {})

    def test_persistence(self):
        """Test that biases persist across instances."""
        # Create and update a store
        store1 = SeedStore(path=str(self.seed_path))

        result = {"seed_key": "test_key_1", "score": 0.8, "success": True}
        store1.update(result)
        store1.save()

        # Load in a new store instance
        store2 = SeedStore(path=str(self.seed_path))

        # Check that the bias persisted
        bias = store2.get_bias("test_key_1")
        self.assertNotEqual(bias, 0.0)
        self.assertAlmostEqual(bias, 0.08, places=2)  # (0.8 - 0.5 + 0.1) * 0.2

    def test_empty_corpus_fallback(self):
        """Test behavior with no existing corpus data."""
        store = SeedStore(path=str(self.seed_path))

        # Should return 0.0 for unknown seeds
        bias = store.get_bias("unknown_key")
        self.assertEqual(bias, 0.0)

        # Summary should handle empty state
        summary = store.get_summary()
        self.assertEqual(summary["total_seeds"], 0)
        self.assertEqual(summary["avg_bias"], 0.0)

    def test_drift_cap(self):
        """Test that drift cap limits extreme changes."""
        store = SeedStore(path=str(self.seed_path), drift_cap=0.1)

        # First update
        result1 = {"seed_key": "drift_test", "score": 0.9, "success": True}
        store.update(result1)
        bias1 = store.get_bias("drift_test")

        # Second update with extreme score
        result2 = {"seed_key": "drift_test", "score": 0.0, "success": False}
        store.update(result2)
        bias2 = store.get_bias("drift_test")

        # Check that drift was capped
        drift = abs(bias2 - bias1)
        self.assertLessEqual(drift, 0.1)

    def test_deterministic_seeds(self):
        """Test that seed keys are deterministic."""
        store = SeedStore(path=str(self.seed_path))

        sig1 = "add(a: int, b: int) -> int"
        ctx1 = "Add two numbers"

        key1 = store.make_seed_key(sig1, ctx1)
        key2 = store.make_seed_key(sig1, ctx1)

        # Same inputs should produce same key
        self.assertEqual(key1, key2)

        # Different inputs should produce different keys
        key3 = store.make_seed_key(sig1, "Different context")
        self.assertNotEqual(key1, key3)

    def test_ema_update(self):
        """Test EMA (Exponential Moving Average) updates."""
        store = SeedStore(path=str(self.seed_path), alpha=0.3)

        # Series of updates
        updates = [
            {"seed_key": "ema_test", "score": 0.7, "success": True},  # 0.3
            {"seed_key": "ema_test", "score": 0.8, "success": True},  # 0.4
            {"seed_key": "ema_test", "score": 0.6, "success": False},  # 0.0
        ]

        for update in updates:
            store.update(update)

        final_bias = store.get_bias("ema_test")

        # Verify EMA calculation
        # Initial: 0
        # After 1st: 0 * 0.7 + (0.7 - 0.5 + 0.1) * 0.3 = 0.09
        # After 2nd: 0.09 * 0.7 + (0.8 - 0.5 + 0.1) * 0.3 = 0.063 + 0.12 = 0.183
        # After 3rd: 0.183 * 0.7 + (0.6 - 0.5 - 0.1) * 0.3 = 0.1281 + 0 = 0.1281
        self.assertAlmostEqual(final_bias, 0.1281, places=3)

    def test_top_n_limit(self):
        """Test that only top N biases are kept."""
        store = SeedStore(path=str(self.seed_path), top_n=3)

        # Add more than top_n biases
        for i in range(5):
            result = {
                "seed_key": f"key_{i}",
                "score": 0.5 + i * 0.1,  # Varying scores
                "success": True,
            }
            store.update(result)

        store.save()

        # Check that only top 3 are kept
        biases = store.get_biases()
        self.assertLessEqual(len(biases), 3)

    def test_summary_stats(self):
        """Test summary statistics generation."""
        store = SeedStore(path=str(self.seed_path))

        # Add some test data
        test_data = [
            {"seed_key": "key1", "score": 0.8, "success": True},
            {"seed_key": "key2", "score": 0.3, "success": False},
            {"seed_key": "key3", "score": 0.6, "success": True},
        ]

        for data in test_data:
            store.update(data)

        summary = store.get_summary()

        self.assertEqual(summary["total_seeds"], 3)
        self.assertGreater(summary["max_bias"], summary["min_bias"])
        self.assertEqual(summary["total_updates"], 3)
        self.assertIn("top_biases", summary)

    def test_reset_functionality(self):
        """Test reset clears all biases."""
        store = SeedStore(path=str(self.seed_path))

        # Add some data
        result = {"seed_key": "test", "score": 0.7, "success": True}
        store.update(result)

        # Reset
        store.reset()

        # Check that biases are cleared
        self.assertEqual(len(store.get_biases()), 0)
        self.assertEqual(store.get_bias("test"), 0.0)

    def test_environment_override(self):
        """Test that environment variable overrides default path."""
        custom_path = Path(self.temp_dir) / "custom_seeds.json"
        os.environ["AURORA_SEEDS_PATH"] = str(custom_path)

        try:
            from aurora_x.learn import get_seed_store

            store = get_seed_store()

            # Check that custom path was used
            self.assertEqual(Path(store.path), custom_path)
            self.assertTrue(custom_path.exists())

        finally:
            # Clean up environment
            del os.environ["AURORA_SEEDS_PATH"]
            if custom_path.exists():
                custom_path.unlink()


if __name__ == "__main__":
    unittest.main()
