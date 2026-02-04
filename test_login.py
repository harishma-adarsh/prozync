"""
Test script to verify authentication is working correctly
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"

def test_signup():
    """Test user registration"""
    print("\n" + "="*50)
    print("TEST 1: User Signup")
    print("="*50)
    
    url = f"{BASE_URL}/auth/signup/"
    data = {
        "username": "testuser123",
        "email": "test123@example.com",
        "password": "testpass123",
        "full_name": "Test User"
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 201:
            print("✓ Signup successful!")
            return True
        elif 'already exists' in response.json().get('detail', '').lower():
            print("⚠ User already exists (this is OK for testing)")
            return True
        else:
            print("✗ Signup failed!")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_signin(username="testuser123", password="testpass123"):
    """Test user login"""
    print("\n" + "="*50)
    print("TEST 2: User Signin")
    print("="*50)
    
    url = f"{BASE_URL}/auth/signin/"
    data = {
        "username": username,
        "password": password
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✓ Signin successful!")
            return response.json().get('token')
        else:
            print("✗ Signin failed!")
            return None
    except Exception as e:
        print(f"✗ Error: {e}")
        return None


def test_profile_access(token):
    """Test accessing profile with token"""
    print("\n" + "="*50)
    print("TEST 3: Profile Access")
    print("="*50)
    
    if not token:
        print("✗ No token available, skipping test")
        return False
    
    url = f"{BASE_URL}/profiles/me/"
    headers = {
        "Authorization": f"Token {token}"
    }
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✓ Profile access successful!")
            return True
        else:
            print("✗ Profile access failed!")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_existing_users():
    """Test login with existing users"""
    print("\n" + "="*50)
    print("TEST 4: Existing Users Login")
    print("="*50)
    
    # Try with existing users (you may need to adjust credentials)
    existing_users = [
        {"username": "johndoe", "password": "unknown"},  # Will fail
        {"username": "developer10", "password": "unknown"},  # Will fail
    ]
    
    print("Testing with existing users (passwords unknown, will fail):")
    for user in existing_users:
        print(f"\n  Testing {user['username']}...")
        test_signin(user['username'], user['password'])


if __name__ == "__main__":
    print("\n" + "="*70)
    print(" PROZYNX AUTHENTICATION TEST SUITE")
    print("="*70)
    
    # Run tests
    test_signup()
    token = test_signin()
    test_profile_access(token)
    test_existing_users()
    
    print("\n" + "="*70)
    print(" TEST SUITE COMPLETED")
    print("="*70)
    print("\nNote: If you want to test existing users, you need to know their passwords")
    print("You can create a new user and test with that instead.\n")
