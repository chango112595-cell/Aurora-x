#!/usr/bin/env python3
"""
Tests for adaptive learning scheduler in Aurora-X
"""

import sys
import unittest
from pathlib import Path

# Add aurora_x to path for import
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from aurora_x.learn.adaptive import AdaptiveBiasScheduler, AdaptiveConfig, BiasStat


class TestAdaptiveBiasScheduler(unittest.TestCase):
    """Test AdaptiveBiasScheduler functionality."""

    def test_exploit_choice(self):
        """Test exploitation chooses highest value candidate."""
        cfg = AdaptiveConfig(epsilon=0.0, decay=1.0, cooldown_iters=0, seed=1)
        s = AdaptiveBiasScheduler(cfg)

        # Manually set stats
        s.stats['a'] = BiasStat(value=1.0, wins=0, losses=0, last_used_iter=-1)
        s.stats['b'] = BiasStat(value=0.1, wins=0, losses=0, last_used_iter=-1)

        # Should choose 'a' since it has higher value and epsilon=0
        self.assertEqual(s.choose(['a', 'b']), 'a')

    def test_decay_applies(self):
        """Test that decay is applied on tick."""
        s = AdaptiveBiasScheduler()
        s.reward('x', True, magnitude=1.0)
        v1 = s.stats['x'].value
        s.tick()
        self.assertLess(s.stats['x'].value, v1)

    def test_exploration_mode(self):
        """Test exploration with epsilon=1.0."""
        cfg = AdaptiveConfig(epsilon=1.0, decay=1.0, seed=42)
        s = AdaptiveBiasScheduler(cfg)

        # With epsilon=1.0, should always explore randomly
        s.stats['a'] = BiasStat(value=10.0)
        s.stats['b'] = BiasStat(value=0.1)

        # Should sometimes choose 'b' despite lower value
        choices = [s.choose(['a', 'b']) for _ in range(100)]
        self.assertIn('b', choices)

    def test_cooldown_mechanism(self):
        """Test cooldown prevents immediate reuse."""
        cfg = AdaptiveConfig(epsilon=0.0, cooldown_iters=3, seed=1)
        s = AdaptiveBiasScheduler(cfg)

        s.stats['a'] = BiasStat(value=1.0, last_used_iter=5)
        s.stats['b'] = BiasStat(value=0.5, last_used_iter=-1)

        # At iteration 7, 'a' is still in cooldown (5 + 3 > 7)
        s.iteration = 7
        self.assertEqual(s.choose(['a', 'b']), 'b')

        # At iteration 8, 'a' is out of cooldown
        s.iteration = 8
        self.assertEqual(s.choose(['a', 'b']), 'a')

    def test_reward_updates(self):
        """Test reward updates stats correctly."""
        s = AdaptiveBiasScheduler()

        # Reward success
        s.reward('key1', True, magnitude=1.0)
        self.assertGreater(s.stats['key1'].value, 0)
        self.assertEqual(s.stats['key1'].wins, 1)
        self.assertEqual(s.stats['key1'].losses, 0)

        # Punish failure
        s.reward('key2', False, magnitude=1.0)
        self.assertLess(s.stats['key2'].value, 0)
        self.assertEqual(s.stats['key2'].wins, 0)
        self.assertEqual(s.stats['key2'].losses, 1)

    def test_history_tracking(self):
        """Test that history is tracked correctly."""
        s = AdaptiveBiasScheduler()

        s.reward('test_key', True, magnitude=0.5)
        s.reward('test_key', False, magnitude=0.3)

        # Check history contains entries
        self.assertEqual(len(s.history), 2)
        self.assertEqual(s.history[0][1], 'test_key')
        self.assertEqual(s.history[1][1], 'test_key')

    def test_summary_top_k(self):
        """Test summary returns top K biases."""
        cfg = AdaptiveConfig(top_k=3)
        s = AdaptiveBiasScheduler(cfg)

        # Add multiple keys with different values
        for i in range(5):
            s.reward(f'key{i}', i % 2 == 0, magnitude=float(i))

        summary = s.summary()
        self.assertLessEqual(len(summary), 3)

    def test_sparkline_generation(self):
        """Test sparkline visual generation."""
        s = AdaptiveBiasScheduler()

        # Create history with ups and downs
        s.reward('test', True, magnitude=1.0)
        s.reward('test', True, magnitude=1.0)
        s.reward('test', False, magnitude=1.0)
        s.reward('test', True, magnitude=1.0)

        sparkline = s.sparkline('test', width=4)
        self.assertEqual(len(sparkline), 4)
        self.assertIn('▁', sparkline)  # Should have low point

    def test_max_drift_limit(self):
        """Test that max_drift_per_iter is respected."""
        cfg = AdaptiveConfig(max_drift_per_iter=0.05)
        s = AdaptiveBiasScheduler(cfg)

        # Try to apply large magnitude
        s.reward('test', True, magnitude=10.0)

        # Should be capped at max_drift_per_iter
        self.assertLessEqual(s.stats['test'].value, 0.05)

    def test_load_dump_roundtrip(self):
        """Test load/dump preserves state."""
        s1 = AdaptiveBiasScheduler()

        # Create some state
        s1.reward('key1', True, magnitude=0.8)
        s1.reward('key2', False, magnitude=0.5)

        # Dump and load into new scheduler
        data = s1.dump()

        s2 = AdaptiveBiasScheduler()
        s2.load(data)

        # Check values preserved
        self.assertAlmostEqual(s2.stats['key1'].value, s1.stats['key1'].value, places=5)
        self.assertAlmostEqual(s2.stats['key2'].value, s1.stats['key2'].value, places=5)


if __name__ == "__main__":
    unittest.main()
