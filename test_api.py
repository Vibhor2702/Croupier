import requests
import time

BASE_URL = "http://localhost:8000"

def wait_for_server():
    print("Waiting for server to start...")
    for _ in range(10):
        try:
            response = requests.get(BASE_URL)
            if response.status_code == 200:
                print("Server is up!")
                return True
        except requests.exceptions.ConnectionError:
            pass
        time.sleep(1)
    print("Server failed to start (or MongoDB is missing).")
    return False

def run_demo():
    if not wait_for_server():
        return

    print("\n--- 1. Create Organization ---")
    org_data = {
        "organization_name": "demo_corp",
        "email": "admin@demo.com",
        "password": "StrongPassword123"
    }
    try:
        resp = requests.post(f"{BASE_URL}/org/create", json=org_data)
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.json()}")
        if resp.status_code != 201:
            print("Failed to create org (maybe it already exists?)")
            # Try to login anyway if it exists
    except Exception as e:
        print(f"Error: {e}")

    print("\n--- 2. Admin Login ---")
    login_data = {
        "email": "admin@demo.com",
        "password": "StrongPassword123"
    }
    token = None
    try:
        resp = requests.post(f"{BASE_URL}/admin/login", json=login_data)
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            token = resp.json()["access_token"]
            print("Login Successful! Token received.")
        else:
            print(f"Login Failed: {resp.json()}")
            return
    except Exception as e:
        print(f"Error: {e}")
        return

    print("\n--- 3. Get Organization ---")
    try:
        resp = requests.get(f"{BASE_URL}/org/get/demo_corp")
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.json()}")
    except Exception as e:
        print(f"Error: {e}")

    print("\n--- 4. Update Organization ---")
    update_data = {
        "organization_name": "demo_global",
        "email": "newemail@demo.com"
    }
    headers = {"Authorization": f"Bearer {token}"}
    try:
        resp = requests.put(f"{BASE_URL}/org/update", json=update_data, headers=headers)
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.json()}")
    except Exception as e:
        print(f"Error: {e}")

    print("\n--- 5. Delete Organization ---")
    try:
        resp = requests.delete(f"{BASE_URL}/org/delete", headers=headers)
        print(f"Status: {resp.status_code}")
        if resp.status_code == 204:
            print("Organization deleted successfully (204 No Content)")
        else:
            print(f"Response: {resp.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run_demo()
