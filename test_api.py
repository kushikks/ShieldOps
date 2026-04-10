#!/usr/bin/env python3
"""Quick API test script"""
import requests
import json

BASE_URL = "http://localhost:5000"

print("=" * 50)
print("ShieldOps API Testing")
print("=" * 50)

# Test 1: Health Check
print("\n1. Testing Health Endpoint...")
response = requests.get(f"{BASE_URL}/health")
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")

# Test 2: Simulation
print("\n2. Testing Simulation Endpoint...")
payload = {
    "disaster_type": "flood",
    "severity": 7,
    "population": 50000
}
response = requests.post(f"{BASE_URL}/api/simulate", json=payload)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")

# Test 3: History
print("\n3. Testing History Endpoint...")
response = requests.get(f"{BASE_URL}/api/history")
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")

print("\n" + "=" * 50)
print("✅ All API tests completed!")
print("=" * 50)
