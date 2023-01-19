import json
import unittest

import requests
import rstr

class TestAuth(unittest.TestCase):
    base_url = "http://localhost:3000"
    headers = {"Content-Type": "application/json"}
    email = f'{rstr.xeger("[A-Z][a-z]{3,5}")}@gmail.com'
    body = {
        "email": email,
        "username": "gmail",
        "password": "ggmail",
        "confirm-password": "ggmail",
    }
    token = ""

    @classmethod
    def setUpClass(self) -> None:
        self.sec_email = f'{rstr.xeger("[A-Z][a-z]{3,5}")}@gmail.com'
        body = {
            "email": self.sec_email,
            "username": "emailer",
            "password": "eemail",
            "confirm-password": "eemail",
        }
        requests.post(
            self.base_url + "/api/auth/signup",
            data=json.dumps(body),
            headers=self.headers,
        )

    def test_signup_happy_path(self):
        resp = requests.post(
            self.base_url + "/api/auth/signup",
            data=json.dumps(self.body),
            headers=self.headers,
        )
        self.assertEqual(resp.status_code, 201)

        resp_body = resp.json()
        self.assertEqual(resp_body["STATUS"], "SUCCESS")
        self.assertEqual(resp_body["MESSAGE"], "Registration Successfully")

    def test_signup_with_invalid_email(self):
        body = {
            "email": None,
            "username": "gmail",
            "password": "ggmail",
            "confirm-password": "ggmail",
        }
        resp = requests.post(
            self.base_url + "/api/auth/signup",
            data=json.dumps(body),
            headers=self.headers,
        )
        self.assertEqual(resp.status_code, 400)

        resp_body = resp.json()
        self.assertEqual(resp_body["STATUS"], "FAILED")
        self.assertEqual(resp_body["MESSAGE"], "Email is required")

    def test_signup_with_invalid_password(self):
        body = {
            "email": "test2gmail@gmail.com",
            "username": "gmail",
            "password": None,
            "confirm-password": "ggmail",
        }
        resp = requests.post(
            self.base_url + "/api/auth/signup",
            data=json.dumps(body),
            headers=self.headers,
        )
        self.assertEqual(resp.status_code, 400)

        resp_body = resp.json()
        self.assertEqual(resp_body["STATUS"], "FAILED")
        self.assertEqual(resp_body["MESSAGE"], "Password is required")

    def test_signup_with_invalid_confirm_password(self):
        body = {
            "email": "test2gmail@gmail.com",
            "username": "gmail",
            "password": "password",
            "confirm-password": "ggmail",
        }
        resp = requests.post(
            self.base_url + "/api/auth/signup",
            data=json.dumps(body),
            headers=self.headers,
        )
        self.assertEqual(resp.status_code, 400)

        resp_body = resp.json()
        self.assertEqual(resp_body["STATUS"], "FAILED")
        self.assertEqual(resp_body["MESSAGE"], "Confirm password mismatch")

    def test_signup_user_already_exist(self):
        resp = requests.post(
            self.base_url + "/api/auth/signup",
            data=json.dumps(self.body),
            headers=self.headers,
        )
        self.assertEqual(resp.status_code, 400)

        resp_body = resp.json()
        self.assertEqual(resp_body["STATUS"], "FAILED")
        self.assertEqual(resp_body["MESSAGE"], "User already exist")

    def test_email_validation_error(self):
        body = {
            "email": 123,
            "username": "gmail",
            "password": "ggmail",
            "confirm-password": "ggmail",
        }
        resp = requests.post(
            self.base_url + "/api/auth/signup",
            data=json.dumps(body),
            headers=self.headers,
        )

        self.assertEqual(resp.status_code, 400)
        resp_body = resp.json()
        self.assertEqual(resp_body["STATUS"], "FAILED")
        self.assertEqual(
            resp_body["MESSAGE"],
            "Registration failed: ValidationError (User:123) (StringField only accepts string values: ['email'])",
        )

        body = {
            "email": "aaaaa",
            "username": "gmail",
            "password": "ggmail",
            "confirm-password": "ggmail",
        }
        resp = requests.post(
            self.base_url + "/api/auth/signup",
            data=json.dumps(body),
            headers=self.headers,
        )

        self.assertEqual(resp.status_code, 400)
        resp_body = resp.json()
        self.assertEqual(resp_body["STATUS"], "FAILED")
        self.assertEqual(
            resp_body["MESSAGE"],
            "Registration failed: ValidationError (User:aaaaa) (Invalid email address: aaaaa: ['email'])",
        )

    def test_login_happy_path(self):
        body = {"email": self.sec_email, "password": "eemail"}
        resp = requests.post(
            self.base_url + "/api/auth/login",
            data=json.dumps(body),
            headers=self.headers,
        )
        self.assertEqual(resp.status_code, 201)

        resp_body = resp.json()
        self.assertEqual(resp_body["STATUS"], "SUCCESS")
        self.token = resp_body["MESSAGE"]["token"]

    def test_login_with_invalid_email(self):
        body = {"email": None, "password": "eemail"}
        resp = requests.post(
            self.base_url + "/api/auth/login",
            data=json.dumps(body),
            headers=self.headers,
        )
        self.assertEqual(resp.status_code, 400)

        resp_body = resp.json()
        self.assertEqual(resp_body["STATUS"], "FAILED")
        self.assertEqual(resp_body["MESSAGE"], "Email is required")

    def test_login_with_invalid_password(self):
        body = {"email": "testemail@email.com", "password": None}
        resp = requests.post(
            self.base_url + "/api/auth/login",
            data=json.dumps(body),
            headers=self.headers,
        )
        self.assertEqual(resp.status_code, 400)

        resp_body = resp.json()
        self.assertEqual(resp_body["STATUS"], "FAILED")
        self.assertEqual(resp_body["MESSAGE"], "Password is required")

    def test_login_with_non_existing_user(self):
        body = {"email": "notexist@email.com", "password": "eeeee"}
        resp = requests.post(
            self.base_url + "/api/auth/login",
            data=json.dumps(body),
            headers=self.headers,
        )
        self.assertEqual(resp.status_code, 400)

        resp_body = resp.json()
        self.assertEqual(resp_body["STATUS"], "FAILED")
        self.assertEqual(resp_body["MESSAGE"], "User does not exist")

    def test_login_with_wrong_password(self):
        body = {"email": self.sec_email, "password": "wrong_password"}
        resp = requests.post(
            self.base_url + "/api/auth/login",
            data=json.dumps(body),
            headers=self.headers,
        )
        self.assertEqual(resp.status_code, 400)

        resp_body = resp.json()
        self.assertEqual(resp_body["STATUS"], "FAILED")
        self.assertEqual(resp_body["MESSAGE"], "Wrong password")

    def test_logout_happy_path(self):
        body = {"email": self.sec_email, "password": "eemail"}
        resp = requests.post(
            self.base_url + "/api/auth/login",
            data=json.dumps(body),
            headers=self.headers,
        )
        resp_body = resp.json()

        resp_logout = requests.get(
            self.base_url
            + "/api/auth/logout?email="
            + self.sec_email
            + "&token="
            + resp_body["MESSAGE"]["token"],
            headers=self.headers,
        )
        self.assertEqual(resp_logout.status_code, 200)

        resp_logout_body = resp_logout.json()
        self.assertEqual(resp_logout_body["STATUS"], "SUCCESS")
        self.assertEqual(resp_logout_body["MESSAGE"], "Logout successfully")

    def test_logout_with_non_existing_user(self):
        resp_logout = requests.get(
            self.base_url + "/api/auth/logout?email=fake@email.com&token=123",
            headers=self.headers,
        )
        self.assertEqual(resp_logout.status_code, 400)

        resp_logout_body = resp_logout.json()
        self.assertEqual(resp_logout_body["STATUS"], "FAILED")
        self.assertEqual(resp_logout_body["MESSAGE"], "User does not exist")

    def test_user_endpoint_get_user_data_happy_path(self):
        resp = requests.get(self.base_url + "/api/auth/user?email=" + self.email)
        resp_body = resp.json()
        self.assertEqual(resp_body["STATUS"], "SUCCESS")
        self.assertEqual(
            resp_body["data"],
            {
                "email": self.email,
                "username": "gmail",
                "wallet": {"usdt": 500.0,"btc": 500.0,"eth": 0,"bnb": 0,"xrp": 0},
                "available_wallet": {"usdt": 500.0,"btc": 500.0,"eth": 0,"bnb": 0,"xrp": 0},
                "orders": [],
                "triggers": [],
            },
        )

    def test_user_endpoint_with_invalid_email(self):
        resp = requests.get(self.base_url + "/api/auth/user")
        self.assertEqual(resp.status_code, 400)

        resp_body = resp.json()
        self.assertEqual(resp_body["STATUS"], "FAILED")
        self.assertEqual(resp_body["MESSAGE"], "Email is required")

    def test_user_endpoint_with_non_existing_user(self):
        resp = requests.get(self.base_url + "/api/auth/user?email=notexist@email.com")
        self.assertEqual(resp.status_code, 400)

        resp_body = resp.json()
        self.assertEqual(resp_body["STATUS"], "FAILED")
        self.assertEqual(resp_body["MESSAGE"], "User does not exist")

    def test_user_endpoint_update_data_happy_path(self):
        resp = requests.post(
            self.base_url + "/api/auth/login",
            data=json.dumps({"email": self.sec_email, "password": "eemail"}),
            headers=self.headers,
        )
        resp_body = resp.json()

        body = {
            "username": "newusername",
            "password": "eemail",
            "confirm-password": "eemail",
        }
        update_resp = requests.put(
            self.base_url
            + "/api/auth/user?email="
            + self.sec_email
            + "&token="
            + resp_body["MESSAGE"]["token"],
            data=json.dumps(body),
            headers=self.headers,
        )
        self.assertEqual(update_resp.status_code, 201)
        update_resp_body = update_resp.json()
        self.assertEqual(update_resp_body["STATUS"], "SUCCESS")
        self.assertEqual(update_resp_body["MESSAGE"], "Update user "+self.sec_email)

    def test_user_endpoint_with_invalid_token(self):
        update_resp = requests.put(
            self.base_url
            + "/api/auth/user?email="
            + self.sec_email,
            data={},
            headers=self.headers,
        )
        self.assertEqual(update_resp.status_code, 400)
        update_resp_body = update_resp.json()
        self.assertEqual(update_resp_body["STATUS"], "FAILED")
        self.assertEqual(update_resp_body["MESSAGE"], "Missing argument: token")
        
    def test_user_endpoint_with_missing_body(self):
        resp = requests.post(
            self.base_url + "/api/auth/login",
            data=json.dumps({"email": self.sec_email, "password": "eemail"}),
            headers=self.headers,
        )
        resp_body = resp.json()
        
        update_resp = requests.put(
            self.base_url
            + "/api/auth/user?email="
            + self.sec_email
            + "&token="
            + resp_body["MESSAGE"]["token"],
            headers=self.headers,
        )
        self.assertEqual(update_resp.status_code, 400)
        update_resp_body = update_resp.json()
        self.assertEqual(update_resp_body["STATUS"], "FAILED")
        self.assertEqual(update_resp_body["MESSAGE"], "Missing body")
        
    def test_user_endpoint_without_login(self):
        update_resp = requests.put(
            self.base_url
            + "/api/auth/user?email="
            + self.sec_email
            + "&token=123",
            data=json.dumps({"a": 1}),
            headers=self.headers,
        )
        self.assertEqual(update_resp.status_code, 400)
        update_resp_body = update_resp.json()
        self.assertEqual(update_resp_body["STATUS"], "FAILED")
        self.assertEqual(update_resp_body["MESSAGE"], "Permission denied")
        
    def test_user_endpoint_invalid_body(self):
        resp = requests.post(
            self.base_url + "/api/auth/login",
            data=json.dumps({"email": self.sec_email, "password": "eemail"}),
            headers=self.headers,
        )
        resp_body = resp.json()

        body = {
            "username": "newusername",
            "password": "1qaz",
        }
        update_resp = requests.put(
            self.base_url
            + "/api/auth/user?email="
            + self.sec_email
            + "&token="
            + resp_body["MESSAGE"]["token"],
            data=json.dumps(body),
            headers=self.headers,
        )
        self.assertEqual(update_resp.status_code, 400)
        update_resp_body = update_resp.json()
        self.assertEqual(update_resp_body["STATUS"], "FAILED")
        self.assertEqual(update_resp_body["MESSAGE"], "Confirm-password is required")
        
    def test_user_endpoint_invalid_confirm_password(self):
        resp = requests.post(
            self.base_url + "/api/auth/login",
            data=json.dumps({"email": self.sec_email, "password": "eemail"}),
            headers=self.headers,
        )
        resp_body = resp.json()

        body = {
            "username": "newusername",
            "password": "1qaz",
            "confirm-password": "1111"
        }
        update_resp = requests.put(
            self.base_url
            + "/api/auth/user?email="
            + self.sec_email
            + "&token="
            + resp_body["MESSAGE"]["token"],
            data=json.dumps(body),
            headers=self.headers,
        )
        self.assertEqual(update_resp.status_code, 400)
        update_resp_body = update_resp.json()
        self.assertEqual(update_resp_body["STATUS"], "FAILED")
        self.assertEqual(update_resp_body["MESSAGE"], "Confirm password mismatch")

    def test_user_endpoint_delete_user_happy_path(self):
        body = {
            "email": "test@email.com",
            "username": "emailer",
            "password": "eemail",
            "confirm-password": "eemail",
        }
        requests.post(
            self.base_url + "/api/auth/signup",
            data=json.dumps(body),
            headers=self.headers,
        )
        resp = requests.post(
            self.base_url + "/api/auth/login",
            data=json.dumps({"email": "test@email.com", "password": "eemail"}),
            headers=self.headers,
        )
        resp_body = resp.json()
        del_resp =requests.delete(
            self.base_url
            + "/api/auth/user?email=test@email.com"
            + "&token="
            + resp_body["MESSAGE"]["token"]
        )
        del_resp_body = del_resp.json()
        self.assertEqual(del_resp.status_code, 201)
        self.assertEqual(del_resp_body["STATUS"], "SUCCESS")
        self.assertEqual(del_resp_body["MESSAGE"], "Delete user test@email.com")

    @classmethod
    def tearDownClass(self) -> None:
        resp = requests.post(
            self.base_url + "/api/auth/login",
            data=json.dumps({"email": self.sec_email, "password": "eemail"}),
            headers=self.headers,
        )
        resp_body = resp.json()
        requests.delete(
            self.base_url
            + "/api/auth/user?email="
            + self.sec_email
            + "&token="
            + resp_body["MESSAGE"]["token"]
        )
        
        resp = requests.post(
            self.base_url + "/api/auth/login",
            data=json.dumps({"email": self.email, "password": "ggmail"}),
            headers=self.headers,
        )
        resp_body = resp.json()
        requests.delete(
            self.base_url
            + "/api/auth/user?email="
            + self.email
            + "&token="
            + resp_body["MESSAGE"]["token"]
        )
