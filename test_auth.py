"""
Quick test script to verify authentication flow
"""
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse

def test_authentication():
    """Test the authentication flow"""
    
    # Create a test client
    client = Client()
    
    print("Testing AI Company Authentication Flow")
    print("=" * 50)
    
    # Test 1: Home page (should work without auth)
    print("\n1. Testing home page access...")
    response = client.get('/')
    print(f"   Home page status: {response.status_code}")
    if response.status_code == 200:
        print("   ✅ Home page accessible")
    else:
        print("   ❌ Home page failed")
    
    # Test 2: Login page access
    print("\n2. Testing login page access...")
    response = client.get('/login/')
    print(f"   Login page status: {response.status_code}")
    if response.status_code == 200:
        print("   ✅ Login page accessible")
    else:
        print("   ❌ Login page failed")
    
    # Test 3: Dashboard access (should redirect to login)
    print("\n3. Testing dashboard access (unauthenticated)...")
    response = client.get('/dashboard/')
    print(f"   Dashboard status: {response.status_code}")
    if response.status_code == 302:
        print("   ✅ Dashboard correctly redirects when not authenticated")
        print(f"   Redirect location: {response.get('Location', 'Not found')}")
    else:
        print("   ❌ Dashboard should redirect when not authenticated")
    
    # Test 4: Login with admin credentials
    print("\n4. Testing login with admin credentials...")
    login_data = {
        'username': 'admin',
        'password': 'admin123'
    }
    response = client.post('/login/', login_data)
    print(f"   Login POST status: {response.status_code}")
    
    if response.status_code == 302:
        print("   ✅ Login successful (redirected)")
        print(f"   Redirect location: {response.get('Location', 'Not found')}")
    else:
        print("   ❌ Login failed")
        return
    
    # Test 5: Dashboard access (authenticated)
    print("\n5. Testing dashboard access (authenticated)...")
    response = client.get('/dashboard/')
    print(f"   Dashboard status: {response.status_code}")
    if response.status_code == 200:
        print("   ✅ Dashboard accessible when authenticated")
    else:
        print("   ❌ Dashboard access failed even when authenticated")
    
    print("\n" + "=" * 50)
    print("Authentication test completed!")

if __name__ == '__main__':
    import os
    import sys
    import django
    
    # Setup Django
    sys.path.append('C:\\GPT4_PROJECTS\\agents_2\\ai_company')
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_company.settings')
    django.setup()
    
    test_authentication()
