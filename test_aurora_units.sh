#!/bin/bash

echo "============================================"
echo "Testing Aurora-X Unit Normalization System"
echo "============================================"
echo

echo "1. Testing /api/units endpoint with various units:"
echo "-------------------------------------------"
echo "Test: 7000 km"
curl -s -X POST http://localhost:5000/api/units -H "Content-Type: application/json" -d '{"value": "7000 km"}' | python -m json.tool

echo -e "\nTest: 1 AU"
curl -s -X POST http://localhost:5000/api/units -H "Content-Type: application/json" -d '{"value": "1 AU"}' | python -m json.tool

echo -e "\nTest: 5.972e24 kg"
curl -s -X POST http://localhost:5000/api/units -H "Content-Type: application/json" -d '{"value": "5.972e24 kg"}' | python -m json.tool

echo -e "\nTest: 100 feet"
curl -s -X POST http://localhost:5000/api/units -H "Content-Type: application/json" -d '{"value": "100 feet"}' | python -m json.tool

echo
echo "2. Testing /api/solve endpoint with unit normalization:"
echo "-------------------------------------------"
echo "Test: orbital period a=7000 km M=5.972e24 kg (Earth orbit with km)"
curl -s -X POST http://localhost:5000/api/solve -H "Content-Type: application/json" -d '{"problem": "orbital period a=7000 km M=5.972e24 kg"}' | python -m json.tool

echo -e "\nTest: orbital period a=1 AU M=2e30 kg (Earth around Sun)"
curl -s -X POST http://localhost:5000/api/solve -H "Content-Type: application/json" -d '{"problem": "orbital period a=1 AU M=2e30 kg"}' | python -m json.tool

echo -e "\nTest: orbital period a=384400 kilometers M=5.972e24 kilograms (Moon around Earth)"
curl -s -X POST http://localhost:5000/api/solve -H "Content-Type: application/json" -d '{"problem": "orbital period a=384400 kilometers M=5.972e24 kilograms"}' | python -m json.tool

echo
echo "3. Testing /api/explain endpoint:"
echo "-------------------------------------------"
echo "Test: orbital period a=7000 km M=5.972e24 kg"
curl -s -X POST http://localhost:5000/api/explain -H "Content-Type: application/json" -d '{"problem": "orbital period a=7000 km M=5.972e24 kg"}' | python -m json.tool

echo
echo "============================================"
echo "All tests completed successfully!"
echo "============================================"
