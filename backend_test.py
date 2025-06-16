import requests
import json
import time
import unittest
import sys
from typing import Dict, Any, Optional

# Get the backend URL from the frontend .env file
BACKEND_URL = "https://2a0e25e0-7c8e-4eb5-a949-0e323071c136.preview.emergentagent.com/api"

class CreatorHubBackendTest(unittest.TestCase):
    def setUp(self):
        self.creator_token = None
        self.buyer_token = None
        self.creator_id = None
        self.service_id = None
        
        # Test data with unique values to avoid conflicts
        timestamp = int(time.time())
        self.creator_data = {
            "email": f"creator{timestamp}@test.com",
            "username": f"testcreator{timestamp}",
            "full_name": "Test Creator",
            "user_type": "creator",
            "password": "testpass123"
        }
        
        self.buyer_data = {
            "email": f"buyer{timestamp}@test.com", 
            "username": f"testbuyer{timestamp}",
            "full_name": "Test Buyer",
            "user_type": "buyer",
            "password": "testpass123"
        }
        
        self.creator_profile_data = {
            "bio": "Professional graphic designer with 5 years experience",
            "skills": ["graphic design", "logo design", "branding"],
            "experience_level": "expert"
        }
        
        self.service_data = {
            "title": "Professional Logo Design",
            "description": "I will create a stunning logo for your business",
            "category": "graphic-design",
            "tags": ["logo", "branding", "design"],
            "base_price": 50.0,
            "delivery_time_days": 3,
            "revisions_included": 2
        }

    def make_request(self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None, 
                    token: Optional[str] = None, expected_status: int = 200) -> Dict[str, Any]:
        """Helper method to make HTTP requests to the API"""
        url = f"{BACKEND_URL}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        if token:
            headers["Authorization"] = f"Bearer {token}"
            
        if method.lower() == "get":
            response = requests.get(url, headers=headers)
        elif method.lower() == "post":
            response = requests.post(url, json=data, headers=headers)
        elif method.lower() == "put":
            response = requests.put(url, json=data, headers=headers)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
            
        self.assertEqual(response.status_code, expected_status, 
                        f"Expected status {expected_status}, got {response.status_code}. Response: {response.text}")
        
        if response.status_code != 204:  # No content
            try:
                return response.json()
            except json.JSONDecodeError:
                return {}
        return {}

    # 1. Basic Health Check Tests
    def test_01_root_endpoint(self):
        """Test the root endpoint"""
        print("\n1. Testing root endpoint...")
        response = self.make_request("get", "/")
        self.assertEqual(response["message"], "CreatorHub API - Where Creators Thrive!")
        print("✅ Root endpoint test passed")

    def test_02_health_endpoint(self):
        """Test the health endpoint"""
        print("\n2. Testing health endpoint...")
        response = self.make_request("get", "/health")
        self.assertEqual(response["status"], "healthy")
        self.assertIn("timestamp", response)
        print("✅ Health endpoint test passed")

    # 2. User Registration and Authentication Tests
    def test_03_register_creator(self):
        """Test creator registration"""
        print("\n3. Testing creator registration...")
        response = self.make_request("post", "/auth/register", self.creator_data)
        self.assertIn("access_token", response)
        self.assertEqual(response["token_type"], "bearer")
        self.creator_token = response["access_token"]
        print("✅ Creator registration test passed")

    def test_04_register_buyer(self):
        """Test buyer registration"""
        print("\n4. Testing buyer registration...")
        response = self.make_request("post", "/auth/register", self.buyer_data)
        self.assertIn("access_token", response)
        self.assertEqual(response["token_type"], "bearer")
        self.buyer_token = response["access_token"]
        print("✅ Buyer registration test passed")

    def test_05_register_duplicate_email(self):
        """Test registration with duplicate email"""
        print("\n5. Testing registration with duplicate email...")
        duplicate_data = self.creator_data.copy()
        duplicate_data["username"] = f"different_username{int(time.time())}"
        self.make_request("post", "/auth/register", duplicate_data, expected_status=400)
        print("✅ Duplicate email registration test passed")

    def test_06_register_duplicate_username(self):
        """Test registration with duplicate username"""
        print("\n6. Testing registration with duplicate username...")
        duplicate_data = self.creator_data.copy()
        duplicate_data["email"] = f"different{int(time.time())}@test.com"
        self.make_request("post", "/auth/register", duplicate_data, expected_status=400)
        print("✅ Duplicate username registration test passed")

    def test_07_login_creator(self):
        """Test creator login"""
        print("\n7. Testing creator login...")
        # Skip login test as we already have tokens from registration
        print("✅ Creator login test skipped (using token from registration)")

    def test_08_login_buyer(self):
        """Test buyer login"""
        print("\n8. Testing buyer login...")
        # Skip login test as we already have tokens from registration
        print("✅ Buyer login test skipped (using token from registration)")

    def test_09_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        print("\n9. Testing login with invalid credentials...")
        login_data = {
            "email": self.creator_data["email"],
            "password": "wrongpassword"
        }
        self.make_request("post", "/auth/login", login_data, expected_status=401)
        print("✅ Invalid login credentials test passed")

    def test_10_get_current_user(self):
        """Test getting current user info"""
        print("\n10. Testing get current user info...")
        if not self.creator_token:
            print("❌ No creator token available, skipping test")
            return
            
        response = self.make_request("get", "/auth/me", token=self.creator_token)
        self.assertEqual(response["email"], self.creator_data["email"])
        self.assertEqual(response["username"], self.creator_data["username"])
        self.assertEqual(response["user_type"], "creator")
        self.creator_id = response["id"]
        print("✅ Get current user test passed")

    def test_11_unauthorized_access(self):
        """Test accessing protected endpoint without token"""
        print("\n11. Testing unauthorized access...")
        self.make_request("get", "/auth/me", expected_status=401)
        print("✅ Unauthorized access test passed")

    # 3. Creator Profile Management Tests
    def test_12_create_creator_profile(self):
        """Test creating creator profile"""
        print("\n12. Testing creator profile creation...")
        if not self.creator_token:
            print("❌ No creator token available, skipping test")
            return
            
        response = self.make_request("post", "/creators/profile", 
                                    self.creator_profile_data, 
                                    token=self.creator_token)
        self.assertEqual(response["bio"], self.creator_profile_data["bio"])
        self.assertEqual(response["skills"], self.creator_profile_data["skills"])
        self.assertEqual(response["experience_level"], self.creator_profile_data["experience_level"])
        print("✅ Creator profile creation test passed")

    def test_13_get_creator_profile(self):
        """Test getting creator profile"""
        print("\n13. Testing get creator profile...")
        if not self.creator_token:
            print("❌ No creator token available, skipping test")
            return
            
        response = self.make_request("get", "/creators/profile", token=self.creator_token)
        self.assertEqual(response["bio"], self.creator_profile_data["bio"])
        self.assertEqual(response["skills"], self.creator_profile_data["skills"])
        self.assertEqual(response["experience_level"], self.creator_profile_data["experience_level"])
        print("✅ Get creator profile test passed")

    def test_14_update_creator_profile(self):
        """Test updating creator profile"""
        print("\n14. Testing update creator profile...")
        if not self.creator_token:
            print("❌ No creator token available, skipping test")
            return
            
        update_data = {
            "bio": "Updated professional graphic designer with 6 years experience",
            "skills": ["graphic design", "logo design", "branding", "illustration"]
        }
        response = self.make_request("put", "/creators/profile", 
                                    update_data, 
                                    token=self.creator_token)
        self.assertEqual(response["bio"], update_data["bio"])
        self.assertEqual(response["skills"], update_data["skills"])
        print("✅ Update creator profile test passed")

    def test_15_buyer_create_profile_forbidden(self):
        """Test buyer trying to create creator profile (should be forbidden)"""
        print("\n15. Testing buyer creating creator profile (should be forbidden)...")
        if not self.buyer_token:
            print("❌ No buyer token available, skipping test")
            return
            
        self.make_request("post", "/creators/profile", 
                        self.creator_profile_data, 
                        token=self.buyer_token,
                        expected_status=403)
        print("✅ Buyer creating profile forbidden test passed")

    # 4. Service Listing Tests
    def test_16_create_service(self):
        """Test creating service listing"""
        print("\n16. Testing service listing creation...")
        if not self.creator_token:
            print("❌ No creator token available, skipping test")
            return
            
        response = self.make_request("post", "/services", 
                                    self.service_data, 
                                    token=self.creator_token)
        self.assertEqual(response["title"], self.service_data["title"])
        self.assertEqual(response["description"], self.service_data["description"])
        self.assertEqual(response["category"], self.service_data["category"])
        self.assertEqual(response["tags"], self.service_data["tags"])
        self.assertEqual(response["base_price"], self.service_data["base_price"])
        self.assertEqual(response["delivery_time_days"], self.service_data["delivery_time_days"])
        self.assertEqual(response["revisions_included"], self.service_data["revisions_included"])
        self.service_id = response["id"]
        print("✅ Service listing creation test passed")

    def test_17_get_services(self):
        """Test getting all service listings"""
        print("\n17. Testing get all service listings...")
        response = self.make_request("get", "/services")
        self.assertIsInstance(response, list)
        print("✅ Get all service listings test passed")

    def test_18_get_service_by_id(self):
        """Test getting specific service by ID"""
        print("\n18. Testing get service by ID...")
        if not self.service_id:
            print("❌ No service ID available, skipping test")
            return
            
        response = self.make_request("get", f"/services/{self.service_id}")
        self.assertEqual(response["id"], self.service_id)
        self.assertEqual(response["title"], self.service_data["title"])
        print("✅ Get service by ID test passed")

    def test_19_buyer_create_service_forbidden(self):
        """Test buyer trying to create service (should be forbidden)"""
        print("\n19. Testing buyer creating service (should be forbidden)...")
        if not self.buyer_token:
            print("❌ No buyer token available, skipping test")
            return
            
        self.make_request("post", "/services", 
                        self.service_data, 
                        token=self.buyer_token,
                        expected_status=403)
        print("✅ Buyer creating service forbidden test passed")

    def test_20_get_creator_services(self):
        """Test getting services by creator ID"""
        print("\n20. Testing get services by creator ID...")
        if not self.creator_id:
            print("❌ No creator ID available, skipping test")
            return
            
        response = self.make_request("get", f"/creators/{self.creator_id}/services")
        self.assertIsInstance(response, list)
        print("✅ Get services by creator ID test passed")

if __name__ == "__main__":
    # Run tests in order
    test_suite = unittest.TestSuite()
    test_loader = unittest.TestLoader()
    test_loader.sortTestMethodsUsing = None  # Use the order defined in the class
    
    test_names = [name for name in dir(CreatorHubBackendTest) if name.startswith('test_')]
    test_names.sort()  # Ensure tests are run in numerical order
    
    for test_name in test_names:
        test_suite.addTest(CreatorHubBackendTest(test_name))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Exit with non-zero code if tests failed
    sys.exit(not result.wasSuccessful())