from locust import HttpUser, task, between
import json
import random

class LoadTestUser(HttpUser):
    """
    Simulates user behavior for load testing.
    Includes registration and login tasks.
    """
    wait_time = between(1, 2)  # Delay between user tasks to simulate real usage patterns

    def on_start(self):
        """
        Initialize data for user registration and login.
        Generates unique user-specific test data on startup.
        """
        self.unique_user_id = random.randint(1000, 9999)  # Unique identifier for this test user

        # Test data for user registration
        self.registration_payload = {
            "fullName": f"Test User {self.unique_user_id}",
            "userName": f"user{self.unique_user_id}",
            "email": f"user{self.unique_user_id}@test.com",
            "password": "securepassword123",
            "phone": f"987654{self.unique_user_id}"
        }

        # Test data for user login
        self.login_payload = {
            "userName": f"user{self.unique_user_id}",
            "email": f"user{self.unique_user_id}@test.com",
            "password": "securepassword123"
        }

    @task(2)
    def register_user(self):
        """
        Simulates user registration by sending POST requests to the /register endpoint.
        Verifies successful registration or handles already registered scenarios.
        """
        with self.client.post(
            "/register",
            data=self.registration_payload,
            catch_response=True
        ) as response:
            try:
                response_data = response.json()
                if response_data.get("msg") in ["User Registered", "Email already Exists"]:
                    response.success()
                else:
                    response.failure(f"Unexpected registration response: {response_data}")
            except json.JSONDecodeError:
                response.failure("Received invalid JSON from registration endpoint")
            except Exception as error:
                response.failure(f"Unexpected error during registration: {str(error)}")

    @task(3)
    def login_user(self):
        """
        Simulates user login by sending POST requests to the /login endpoint.
        Verifies successful login or handles incorrect credentials scenarios.
        """
        with self.client.post(
            "/login",
            data=self.login_payload,
            catch_response=True
        ) as response:
            try:
                response_data = response.json()
                if "token" in response_data or response_data.get("msg") == "Incorrect email or password":
                    response.success()
                else:
                    response.failure(f"Unexpected login response: {response_data}")
            except json.JSONDecodeError:
                response.failure("Received invalid JSON from login endpoint")
            except Exception as error:
                response.failure(f"Unexpected error during login: {str(error)}")


class StressTestUser(LoadTestUser):
    """
    Specialized user class for stress testing with reduced wait times.
    Simulates a high load on the login endpoint with randomized user data.
    """
    wait_time = between(0.1, 0.5)  # Shorter delay to apply more pressure on the system

    @task(1)
    def perform_stress_login(self):
        """
        Sends randomized login attempts to stress test the /login endpoint.
        Evaluates the system's ability to handle high volumes of requests.
        """
        random_id = random.randint(1000, 9999)  # Generate a random user ID for stress testing
        stress_login_payload = {
            "userName": f"user{random_id}",
            "email": f"user{random_id}@test.com",
            "password": "securepassword123"
        }

        with self.client.post(
            "/login",
            data=stress_login_payload,
            catch_response=True
        ) as response:
            try:
                response_data = response.json()
                if "token" in response_data or response_data.get("msg") == "Incorrect email or password":
                    response.success()
                else:
                    response.failure(f"Unexpected stress login response: {response_data}")
            except json.JSONDecodeError:
                response.failure("Received invalid JSON from stress login endpoint")
            except Exception as error:
                response.failure(f"Unexpected error during stress login: {str(error)}")


def describe_load_test_scenario():
    """
    Load Testing Scenario:
    - Tests user registration and login under normal conditions.
    - Ensures the system can handle simultaneous user interactions.
    """
    pass


def describe_stress_test_scenario():
    """
    Stress Testing Scenario:
    - Simulates a high volume of login attempts.
    - Verifies the system's ability to manage heavy traffic and fail gracefully.
    """
    pass
