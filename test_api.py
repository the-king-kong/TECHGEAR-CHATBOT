"""
Test script for the TechGear Chatbot API

Tests all API endpoints with curl and requests library
"""

import requests
import json
import time
import subprocess
import sys
import os

print("\n" + "="*70)
print("🧪 TESTING TECHGEAR CHATBOT API")
print("="*70)

# Base URL for the API
BASE_URL = "http://localhost:8000"

# Test 1: Health check
print("\n✅ TEST 1: GET /health")
print("-" * 70)
try:
    response = requests.get(f"{BASE_URL}/health", timeout=5)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 2: Welcome endpoint
print("\n✅ TEST 2: GET /")
print("-" * 70)
try:
    response = requests.get(f"{BASE_URL}/", timeout=5)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 3: Chat endpoint - Product question
print("\n✅ TEST 3: POST /chat - Product Query")
print("-" * 70)
query_1 = "What is the price of SmartWatch Pro X?"
payload_1 = {"query": query_1}
print(f"Query: {query_1}")
try:
    response = requests.post(f"{BASE_URL}/chat", json=payload_1, timeout=10)
    print(f"Status Code: {response.status_code}")
    result = response.json()
    print(f"Response:")
    print(json.dumps(result, indent=2))
except Exception as e:
    print(f"❌ Error: {e}")

# Test 4: Chat endpoint - Returns question
print("\n✅ TEST 4: POST /chat - Returns Query")
print("-" * 70)
query_2 = "Can I return items within 7 days?"
payload_2 = {"query": query_2}
print(f"Query: {query_2}")
try:
    response = requests.post(f"{BASE_URL}/chat", json=payload_2, timeout=10)
    print(f"Status Code: {response.status_code}")
    result = response.json()
    print(f"Response:")
    print(json.dumps(result, indent=2))
except Exception as e:
    print(f"❌ Error: {e}")

# Test 5: Chat endpoint - General question
print("\n✅ TEST 5: POST /chat - General Query")
print("-" * 70)
query_3 = "Tell me a joke"
payload_3 = {"query": query_3}
print(f"Query: {query_3}")
try:
    response = requests.post(f"{BASE_URL}/chat", json=payload_3, timeout=10)
    print(f"Status Code: {response.status_code}")
    result = response.json()
    print(f"Response:")
    print(json.dumps(result, indent=2))
except Exception as e:
    print(f"❌ Error: {e}")

# Test 6: Empty query (should fail)
print("\n✅ TEST 6: POST /chat - Empty Query (Error Case)")
print("-" * 70)
payload_4 = {"query": ""}
print(f"Query: (empty)")
try:
    response = requests.post(f"{BASE_URL}/chat", json=payload_4, timeout=10)
    print(f"Status Code: {response.status_code}")
    result = response.json()
    print(f"Response:")
    print(json.dumps(result, indent=2))
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "="*70)
print("✅ API TESTING COMPLETE")
print("="*70)
