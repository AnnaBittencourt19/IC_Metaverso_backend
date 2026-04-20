#!/usr/bin/env python3
"""
Quick test to verify the API is working
"""
import subprocess
import time
import requests
import json

# Start server
print("🚀 Starting server...")
proc = subprocess.Popen(
    ["/Users/annabittencourt/projetos/IC_METAVERSO/metaverso/.venv/bin/python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"],
    cwd="/Users/annabittencourt/projetos/IC_METAVERSO/metaverso",
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

# Wait for server to start
time.sleep(5)

try:
    # Test health
    print("\n📊 Testing health endpoint...")
    resp = requests.get(
        "http://localhost:8000/api/v1/health",
        headers={"X-API-Key": "metaverso-secret-key-2026"}
    )
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.json()}")
    
    # Test ask
    print("\n🤔 Testing /ask endpoint...")
    resp = requests.post(
        "http://localhost:8000/api/v1/ask",
        json={"question": "O que é 6G?"},
        headers={"X-API-Key": "metaverso-secret-key-2026"}
    )
    print(f"Status: {resp.status_code}")
    if resp.status_code == 200:
        print("✅ SUCCESS - Got 200 OK")
        data = resp.json()
        print(f"Response keys: {data.keys()}")
        print(f"Confidence: {data.get('confidence')}")
        print(f"Docs used: {data.get('docs_used')}")
    else:
        print(f"❌ ERROR - Got {resp.status_code}")
        print(f"Response: {resp.json()}")
        
finally:
    print("\n🛑 Stopping server...")
    proc.terminate()
    proc.wait()
