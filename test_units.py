#!/usr/bin/env python3
"""
Test script for unit normalization in Aurora-X.
Tests the /api/units endpoint and physics solver with various unit inputs.
"""

import requests

from aurora_x.generators.solver import solve_text
from aurora_x.reasoners.units import (
    normalize_text,
    normalize_to_si,
    parse_value_with_unit,
)
from aurora_x.router.domain_router import classify_domain


def test_unit_parser():
    """Test the parse_value_with_unit function"""
    print("\n=== Testing Unit Parser ===")
    test_cases = [
        "7000 km",
        "5.972e24 kg",
        "1AU",
        "3.5 miles",
        "100 feet",
        "2.5 hours",
        "365 days",
        "1 solar_mass",
    ]

    for case in test_cases:
        value, unit = parse_value_with_unit(case)
        print(f"  '{case}' -> value={value}, unit={unit}")


def test_unit_normalization():
    """Test normalize_to_si function"""
    print("\n=== Testing Unit Normalization ===")
    test_cases = [
        (7000, "km", "distance"),
        (1, "AU", "distance"),
        (5.972e24, "kg", "mass"),
        (2, "tons", "mass"),
        (24, "hours", "time"),
        (1, "year", "time"),
        (100, "miles", "distance"),
        (10, "lbs", "mass"),
    ]

    for value, unit, unit_type in test_cases:
        result = normalize_to_si(value, unit, unit_type)
        print(f"  {value} {unit} -> {result['si_value']} {result['si_unit']} (factor: {result['conversion_factor']})")


def test_text_normalization():
    """Test normalize_text function"""
    print("\n=== Testing Text Normalization ===")
    test_texts = [
        "a=7000 km, M=5.972e24 kg",
        "orbital period a=1 AU M=2e30 kg",
        "distance is 100 miles and mass is 2 tons",
        "time=365 days, distance=384400 km",
    ]

    for text in test_texts:
        normalized = normalize_text(text)
        print(f"  Original: {text}")
        print(f"  Normalized: {normalized}")
        print()


def test_domain_router():
    """Test domain router with unit normalization"""
    print("\n=== Testing Domain Router ===")
    test_cases = [
        "orbital period a=7000 km M=5.972e24 kg",
        "orbital period a=1 AU M=2e30 kg",
        "differentiate 3x^2 + 2x + 5",
    ]

    for case in test_cases:
        intent = classify_domain(case)
        print(f"  Input: {case}")
        print(f"  Domain: {intent.domain}, Task: {intent.task}")
        if "a" in intent.payload:
            print(f"  Normalized a: {intent.payload.get('a')} m")
        if "M" in intent.payload:
            print(f"  Normalized M: {intent.payload.get('M')} kg")
        print()


def test_solver():
    """Test the complete solver with unit normalization"""
    print("\n=== Testing Complete Solver ===")
    test_cases = [
        "orbital period a=7000 km M=5.972e24 kg",  # Earth orbit with km
        "orbital period a=1 AU M=1.989e30 kg",  # Earth around Sun
        "orbital period a=384400 km M=5.972e24 kg",  # Moon around Earth
    ]

    for case in test_cases:
        print(f"\n  Problem: {case}")
        result = solve_text(case)
        if result.get("ok"):
            print(f"  Solution: Period = {result.get('period_s', 0)} seconds")
            if result.get("period_s"):
                period_hours = result["period_s"] / 3600
                period_days = period_hours / 24
                print(f"           = {period_hours:.2f} hours")
                print(f"           = {period_days:.2f} days")
        else:
            print(f"  Error: {result.get('err')}")


def test_api_units():
    """Test the /api/units endpoint"""
    print("\n=== Testing /api/units Endpoint ===")
    base_url = "http://localhost:5000/api/units"

    test_values = [
        "7000 km",
        "5.972e24 kg",
        "1 AU",
        "100 miles",
        "2.5 tons",
        "365 days",
        "3600 seconds",
    ]

    for value in test_values:
        try:
            response = requests.post(base_url, json={"value": value}, timeout=30)
            if response.status_code == 200:
                data = response.json()
                print(f"  {value} -> {data['si_value']} {data['si_unit']} (type: {data['unit_type']})")
            else:
                print(f"  {value} -> Error: {response.status_code}")
        except Exception as e:
            print(f"  {value} -> Connection error: {e}")


def test_api_solve():
    """Test the /api/solve endpoint with units"""
    print("\n=== Testing /api/solve Endpoint with Units ===")
    base_url = "http://localhost:5000/api/solve"

    test_problems = [
        {"problem": "orbital period a=7000 km M=5.972e24 kg"},
        {"prompt": "orbital period a=1 AU M=2e30 kg"},
        {"problem": "orbital period a=384400 kilometers M=5.972e24 kilograms"},
    ]

    for problem in test_problems:
        try:
            response = requests.post(base_url, json=problem, timeout=30)
            if response.status_code == 200:
                data = response.json()
                print(f"  Input: {problem}")
                if data.get("ok"):
                    print(f"  Result: Period = {data.get('period_s', 0):.2e} seconds")
                else:
                    print(f"  Error: {data}")
            else:
                print(f"  Error: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"  Connection error: {e}")


if __name__ == "__main__":
    print("Testing Aurora-X Unit Normalization System")
    print("=" * 50)

    # Test unit parsing and normalization functions
    test_unit_parser()
    test_unit_normalization()
    test_text_normalization()

    # Test domain router and solver
    test_domain_router()
    test_solver()

    # Test API endpoints (requires server to be running)
    print("\n" + "=" * 50)
    print("Testing API Endpoints (requires server on port 5000)")
    print("=" * 50)

    try:
        test_api_units()
        test_api_solve()
    except Exception as e:
        print(f"\nAPI tests skipped - server not running: {e}")

    print("\n" + "=" * 50)
    print("All tests completed!")
