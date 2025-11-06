"""
Quick script to verify Amadeus credentials and test token acquisition.
Run this from the project root to check your .env configuration.
"""
import os
import sys
import httpx
import asyncio
from dotenv import load_dotenv

# Load .env file
print("\n📋 Loading environment...")
load_dotenv()

# Get credentials
client_id = os.getenv("AMADEUS_CLIENT_ID")
client_secret = os.getenv("AMADEUS_CLIENT_SECRET")
base_url = os.getenv("AMADEUS_BASE_URL", "https://test.api.amadeus.com")

print("\n🔑 Configured credentials:")
print(f"Client ID: {client_id[:4]}...{client_id[-4:] if client_id and len(client_id) > 8 else 'not set'}")
print(f"Client Secret: {client_secret[:4]}...{client_secret[-4:] if client_secret and len(client_secret) > 8 else 'not set'}")
print(f"Base URL: {base_url}")

async def test_token():
    """Attempt to get an Amadeus token and print detailed results."""
    if not client_id or not client_secret:
        print("\n❌ Missing credentials in .env file!")
        print("Please ensure you have AMADEUS_CLIENT_ID and AMADEUS_CLIENT_SECRET set.")
        return False
        
    url = f"{base_url}/v1/security/oauth2/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret
    }
    
    print(f"\n📡 Requesting token from: {url}")
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            print("📤 Sending request...")
            resp = await client.post(url, headers=headers, data=data)
            
            print(f"\n📥 Response status: {resp.status_code}")
            print(f"📄 Response headers: {dict(resp.headers)}")
            print(f"📝 Response body: {resp.text[:500]}...")  # truncate long responses
            
            if resp.status_code == 200:
                token_data = resp.json()
                if "access_token" in token_data:
                    print("\n✅ Successfully obtained token!")
                    print(f"Token type: {token_data.get('token_type')}")
                    print(f"Expires in: {token_data.get('expires_in')} seconds")
                    return True
            elif resp.status_code == 401:
                print("\n❌ Authentication failed (401)")
                print("This usually means your client_id or client_secret is incorrect.")
                print("Double check that:")
                print("1. You're using the correct API key pair")
                print("2. The credentials are properly copied (no extra spaces)")
                print("3. You're using the test environment credentials if using test.api.amadeus.com")
            else:
                print(f"\n❌ Unexpected status code: {resp.status_code}")
            return False
    except Exception as e:
        print(f"\n💥 Error during request: {e}")
        return False

if __name__ == "__main__":
    print("\n🔍 Testing Amadeus token acquisition...")
    result = asyncio.run(test_token())
    print("\n" + "="*60)
    if not result:
        sys.exit(1)