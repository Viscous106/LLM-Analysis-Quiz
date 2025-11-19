"""
Test client for the LLM Quiz Solver API.
Use this to test your deployment locally before the actual quiz.
"""

import requests
import json
import time
from typing import Dict, Any


def test_health_check(base_url: str = "http://localhost:8000") -> bool:
    """Test the health endpoint."""
    print("🏥 Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print(f"✅ Health check passed: {response.json()}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error connecting to server: {e}")
        return False


def test_invalid_json(base_url: str = "http://localhost:8000") -> bool:
    """Test that invalid JSON returns 400."""
    print("\n📝 Testing invalid JSON handling...")
    try:
        response = requests.post(
            f"{base_url}/quiz",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 400:
            print("✅ Invalid JSON correctly rejected (400)")
            return True
        else:
            print(f"❌ Expected 400, got {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_invalid_secret(
    base_url: str = "http://localhost:8000",
    email: str = "test@example.com"
) -> bool:
    """Test that invalid secret returns 403."""
    print("\n🔐 Testing invalid secret handling...")
    try:
        payload = {
            "email": email,
            "secret": "wrong-secret-12345",
            "url": "https://example.com/quiz-test"
        }
        response = requests.post(
            f"{base_url}/quiz",
            json=payload
        )
        if response.status_code == 403:
            print("✅ Invalid secret correctly rejected (403)")
            return True
        else:
            print(f"❌ Expected 403, got {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_valid_request(
    base_url: str = "http://localhost:8000",
    email: str = None,
    secret: str = None
) -> bool:
    """Test a valid quiz request."""
    print("\n✉️  Testing valid quiz request...")

    if not email or not secret:
        print("⚠️  Skipping valid request test (no credentials provided)")
        return True

    try:
        payload = {
            "email": email,
            "secret": secret,
            "url": "https://example.com/quiz-test"
        }
        response = requests.post(
            f"{base_url}/quiz",
            json=payload
        )

        if response.status_code == 200:
            result = response.json()
            print(f"✅ Valid request accepted (200): {result}")
            return True
        else:
            print(f"❌ Expected 200, got {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def run_all_tests(
    base_url: str = "http://localhost:8000",
    email: str = None,
    secret: str = None
):
    """Run all tests."""
    print("=" * 60)
    print("🧪 LLM Quiz Solver API Test Suite")
    print("=" * 60)
    print(f"Testing endpoint: {base_url}")
    print()

    results = []

    # Test 1: Health check
    results.append(("Health Check", test_health_check(base_url)))

    # Give server a moment
    time.sleep(0.5)

    # Test 2: Invalid JSON
    results.append(("Invalid JSON (400)", test_invalid_json(base_url)))

    # Test 3: Invalid Secret
    results.append(("Invalid Secret (403)", test_invalid_secret(base_url, email or "test@example.com")))

    # Test 4: Valid Request (optional)
    if email and secret:
        results.append(("Valid Request (200)", test_valid_request(base_url, email, secret)))

    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")

    print()
    print(f"Results: {passed}/{total} tests passed")
    print("=" * 60)

    if passed == total:
        print("🎉 All tests passed! Your API is ready.")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")

    return passed == total


if __name__ == "__main__":
    import sys
    import os
    from dotenv import load_dotenv

    # Load environment variables
    load_dotenv()

    # Get configuration
    base_url = os.getenv("TEST_BASE_URL", "http://localhost:8000")
    email = os.getenv("EMAIL")
    secret = os.getenv("SECRET")

    # Allow command-line override
    if len(sys.argv) > 1:
        base_url = sys.argv[1]

    # Run tests
    success = run_all_tests(base_url, email, secret)

    # Exit with appropriate code
    sys.exit(0 if success else 1)
