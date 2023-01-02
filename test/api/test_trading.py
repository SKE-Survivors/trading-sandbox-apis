import json
import unittest
import requests

import rstr


class TestTrading(unittest.TestCase):
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
        requests.post(
            self.base_url + "/api/auth/signup",
            data=json.dumps(self.body),
            headers=self.headers,
        )
        resp = requests.post(
            self.base_url + "/api/auth/login",
            data=json.dumps({"email": self.email, "password": "ggmail"}),
            headers=self.headers,
        )
        self.token = resp.json()["MESSAGE"]["token"]

    def test_trade_order_endpoint_happy_path(self):
        order = {
            "status": "active",
            "flag": "buy",
            "pair_symbol": "btc-usdt",
            "input_amount": 200,
            "output_amount": 2,
        }
        resp = requests.post(
            self.base_url
            + "/api/trading/order?email="
            + self.email
            + "&token="
            + self.token,
            data=json.dumps(order),
            headers=self.headers,
        )
        self.assertEqual(resp.status_code, 201)
        resp_body = resp.json()
        self.assertEqual(resp_body["STATUS"], "SUCCESS")
        self.assertEqual(resp_body["MESSAGE"], "Create order successfully")
        resp = requests.get(self.base_url + "/api/info/orders")
        resp_body = resp.json()
        order = resp_body["MESSAGE"][-1]
        
        requests.delete(
            self.base_url
            + "/api/trading/order?email="
            + self.email
            + "&token="
            + self.token,
            data=json.dumps({"order_id": order["id"]}),
            headers=self.headers,
        )

    def test_delete_order_endpoint_happy_path(self):
        order = {
            "status": "active",
            "flag": "buy",
            "pair_symbol": "btc-usdt",
            "input_amount": 200,
            "output_amount": 2,
        }
        requests.post(
            self.base_url
            + "/api/trading/order?email="
            + self.email
            + "&token="
            + self.token,
            data=json.dumps(order),
            headers=self.headers,
        )
        resp = requests.get(self.base_url + "/api/info/orders")
        resp_body = resp.json()
        order = resp_body["MESSAGE"][-1]
        
        del_resp = requests.delete(
            self.base_url
            + "/api/trading/order?email="
            + self.email
            + "&token="
            + self.token,
            data=json.dumps({"order_id": order["id"]}),
            headers=self.headers,
        )
        self.assertEqual(del_resp.status_code, 200)
        del_resp_body = del_resp.json()
        self.assertEqual(del_resp_body["STATUS"], "SUCCESS")
        self.assertEqual(del_resp_body["MESSAGE"], "Cancel order Successfully")
        
    def test_order_endpoint_with_invalid_token(self):
        order = {
            "status": "active",
            "flag": "buy",
            "pair_symbol": "btc-usdt",
            "input_amount": 200,
            "output_amount": 2,
        }
        resp = requests.post(
            self.base_url
            + "/api/trading/order?email="
            + self.email,
            data=json.dumps(order),
            headers=self.headers,
        )
        self.assertEqual(resp.status_code, 400)
        resp_body = resp.json()
        self.assertEqual(resp_body["STATUS"], "FAILED")
        self.assertEqual(resp_body["MESSAGE"], "Missing argument: token")
        
    def test_order_endpoint_with_non_existing_user(self):
        resp = requests.post(
            self.base_url
            + "/api/trading/order?email=email@email.com"
            + "&token="
            + self.token,
            headers=self.headers,
        )
        self.assertEqual(resp.status_code, 400)

        resp_body = resp.json()
        self.assertEqual(resp_body["STATUS"], "FAILED")
        self.assertEqual(resp_body["MESSAGE"], "User does not exist")
        
    def test_order_endpoint_without_login(self):
        resp = requests.post(
            self.base_url
            + "/api/trading/order?email="
            + self.email
            + "&token=123",
            headers=self.headers,
        )
        self.assertEqual(resp.status_code, 400)
        resp_body = resp.json()
        self.assertEqual(resp_body["STATUS"], "FAILED")
        self.assertEqual(resp_body["MESSAGE"], "Permission denied")
        
    def test_delete_order_without_body(self):
        del_resp = requests.delete(
            self.base_url
            + "/api/trading/order?email="
            + self.email
            + "&token="
            + self.token,
            headers=self.headers,
        )
        self.assertEqual(del_resp.status_code, 400)
        del_resp_body = del_resp.json()
        self.assertEqual(del_resp_body["STATUS"], "FAILED")
        print(del_resp_body["MESSAGE"])
        self.assertEqual(del_resp_body["MESSAGE"], "Missing body")
    
    # order_id is required: คือกรณีมี field 'order_id' แต่ค่า blank
    # ถ้าไม่มี field ตั้งแต่ err แรกจะเป็น Missing body
    # นายจะให้เราแก้ก้ได้ (จะให้แก้ไงก้บอก -- แต่มันเป็นงี้หลายที่เลยอ่าา TTvTT)
    def test_delete_order_without_order_id(self):
        del_resp = requests.delete(
            self.base_url
            + "/api/trading/order?email="
            + self.email
            + "&token="
            + self.token,
            data=json.dumps({}),
            headers=self.headers,
        )
        self.assertEqual(del_resp.status_code, 400)
        del_resp_body = del_resp.json()
        self.assertEqual(del_resp_body["STATUS"], "FAILED")
        self.assertEqual(del_resp_body["MESSAGE"], "order_id is required")
    
    def test_delete_order_with_invalid_order_id(self):
        del_resp = requests.delete(
            self.base_url
            + "/api/trading/order?email="
            + self.email
            + "&token="
            + self.token,
            data=json.dumps({"order_id": 1923}),
            headers=self.headers,
        )
        self.assertEqual(del_resp.status_code, 400)
        del_resp_body = del_resp.json()
        self.assertEqual(del_resp_body["STATUS"], "FAILED")
        self.assertEqual(del_resp_body["MESSAGE"], "Order does not exist")
        
    def test_send_order_without_body(self):
        resp = requests.post(
            self.base_url
            + "/api/trading/order?email="
            + self.email
            + "&token="
            + self.token,
            headers=self.headers,
        )
        self.assertEqual(resp.status_code, 400)
        resp_body = resp.json()
        self.assertEqual(resp_body["STATUS"], "FAILED")
        self.assertEqual(resp_body["MESSAGE"], "Missing body")
    
    # error เดียวกับ test_delete_order_without_order_id (คิดว่านะ)
    def test_send_order_without_status(self):
        order = {
            "flag": "buy",
            "pair_symbol": "btc-usdt",
            "input_amount": 200,
            "output_amount": 2,
        }
        resp = requests.post(
            self.base_url
            + "/api/trading/order?email="
            + self.email
            + "&token="
            + self.token,
            data=json.dumps(order),
            headers=self.headers,
        )
        self.assertEqual(resp.status_code, 400)
        resp_body = resp.json()
        self.assertEqual(resp_body["STATUS"], "FAILED")
        self.assertEqual(resp_body["MESSAGE"], "status is required")
        
    # error เดียวกับ test_delete_order_without_order_id (คิดว่านะ)
    def test_send_order_without_flag(self):
        order = {
            "status": "finished",
            "pair_symbol": "btc-usdt",
            "input_amount": 200,
            "output_amount": 2,
        }
        resp = requests.post(
            self.base_url
            + "/api/trading/order?email="
            + self.email
            + "&token="
            + self.token,
            data=json.dumps(order),
            headers=self.headers,
        )
        self.assertEqual(resp.status_code, 400)
        resp_body = resp.json()
        self.assertEqual(resp_body["STATUS"], "FAILED")
        self.assertEqual(resp_body["MESSAGE"], "flag is required")

    # error เดียวกับ test_delete_order_without_order_id (คิดว่านะ)
    def test_send_order_without_pair_symbol(self):
        order = {
            "status": "finished",
            "flag": "buy",
            "input_amount": 200,
            "output_amount": 2,
        }
        resp = requests.post(
            self.base_url
            + "/api/trading/order?email="
            + self.email
            + "&token="
            + self.token,
            data=json.dumps(order),
            headers=self.headers,
        )
        self.assertEqual(resp.status_code, 400)
        resp_body = resp.json()
        self.assertEqual(resp_body["STATUS"], "FAILED")
        self.assertEqual(resp_body["MESSAGE"], "pair_symbol is required")
    
    # error เดียวกับ test_delete_order_without_order_id (คิดว่านะ)
    def test_send_order_without_input_amount(self):
        order = {
            "status": "finished",
            "flag": "buy",
            "pair_symbol": "btc-usdt",
            "output_amount": 2,
        }
        resp = requests.post(
            self.base_url
            + "/api/trading/order?email="
            + self.email
            + "&token="
            + self.token,
            data=json.dumps(order),
            headers=self.headers,
        )
        self.assertEqual(resp.status_code, 400)
        resp_body = resp.json()
        self.assertEqual(resp_body["STATUS"], "FAILED")
        self.assertEqual(resp_body["MESSAGE"], "input_amount is required")

    # error เดียวกับ test_delete_order_without_order_id (คิดว่านะ)
    def test_send_order_without_output_amount(self):
        order = {
            "status": "finished",
            "flag": "buy",
            "pair_symbol": "btc-usdt",
            "input_amount": 2,
        }
        resp = requests.post(
            self.base_url
            + "/api/trading/order?email="
            + self.email
            + "&token="
            + self.token,
            data=json.dumps(order),
            headers=self.headers,
        )
        self.assertEqual(resp.status_code, 400)
        resp_body = resp.json()
        self.assertEqual(resp_body["STATUS"], "FAILED")
        self.assertEqual(resp_body["MESSAGE"], "output_amount is required")
    
    def test_send_order_with_invalid_body(self):
        order = {
            "status": "AAA",
            "flag": "buy",
            "pair_symbol": "btc-usdt",
            "input_amount": 200,
            "output_amount": 2
        }
        resp = requests.post(
            self.base_url
            + "/api/trading/order?email="
            + self.email
            + "&token="
            + self.token,
            data=json.dumps(order),
            headers=self.headers,
        )
        self.assertEqual(resp.status_code, 400)
        resp_body = resp.json()
        self.assertEqual(resp_body["STATUS"], "FAILED")
        self.assertEqual(resp_body["MESSAGE"], "Create order failed: Invalid status")
        
    def test_trigger_happy_path(self):
        trigger = {
            "flag": "buy",
            "pair_symbol": "btc-usdt",
            "input_amount": 200,
            "output_amount": 2,
            "stop_price": 100
        }
        resp = requests.post(self.base_url
            + "/api/trading/trigger?email="
            + self.email
            + "&token="
            + self.token,
            data=json.dumps(trigger),
            headers=self.headers,)
        self.assertEqual(resp.status_code, 201)
        resp_body = resp.json()
        self.assertEqual(resp_body["STATUS"], "SUCCESS")
        self.assertEqual(resp_body["MESSAGE"], "Create trigger successfully")
        
    def test_trigger_endpoint_with_invalid_token(self):
        trigger = {
            "flag": "buy",
            "pair_symbol": "btc-usdt",
            "input_amount": 200,
            "output_amount": 2,
            "stop_price": 100
        }
        resp = requests.post(
            self.base_url
            + "/api/trading/trigger?email="
            + self.email,
            data=json.dumps(trigger),
            headers=self.headers,
        )
        self.assertEqual(resp.status_code, 400)
        resp_body = resp.json()
        self.assertEqual(resp_body["STATUS"], "FAILED")
        self.assertEqual(resp_body["MESSAGE"], "Missing argument: token")
        
    def test_trigger_endpoint_with_non_existing_user(self):
        resp = requests.post(
            self.base_url
            + "/api/trading/trigger?email=email@email.com"
            + "&token="
            + self.token,
            headers=self.headers,
        )
        self.assertEqual(resp.status_code, 400)

        resp_body = resp.json()
        self.assertEqual(resp_body["STATUS"], "FAILED")
        self.assertEqual(resp_body["MESSAGE"], "User does not exist")
        
    def test_trigger_endpoint_without_login(self):
        resp = requests.post(
            self.base_url
            + "/api/trading/trigger?email="
            + self.email
            + "&token=123",
            headers=self.headers,
        )
        self.assertEqual(resp.status_code, 400)
        resp_body = resp.json()
        self.assertEqual(resp_body["STATUS"], "FAILED")
        self.assertEqual(resp_body["MESSAGE"], "Permission denied")
    
    def test_send_trigger_without_body(self):
        resp = requests.post(
            self.base_url
            + "/api/trading/trigger?email="
            + self.email
            + "&token="
            + self.token,
            headers=self.headers,
        )
        self.assertEqual(resp.status_code, 400)
        resp_body = resp.json()
        self.assertEqual(resp_body["STATUS"], "FAILED")
        self.assertEqual(resp_body["MESSAGE"], "Missing body")
    
    # error เดียวกับ test_delete_order_without_order_id (คิดว่านะ)
    def test_send_trigger_without_stop_limit(self):
        trigger = {
            "flag": "buy",
            "pair_symbol": "btc-usdt",
            "input_amount": 200,
            "output_amount": 2,
        }
        resp = requests.post(
            self.base_url
            + "/api/trading/trigger?email="
            + self.email
            + "&token="
            + self.token,
            data=json.dumps(trigger),
            headers=self.headers,
        )
        self.assertEqual(resp.status_code, 400)
        resp_body = resp.json()
        self.assertEqual(resp_body["STATUS"], "FAILED")
        self.assertEqual(resp_body["MESSAGE"], "stop_limit is required")
        
    # error เดียวกับ test_delete_order_without_order_id (คิดว่านะ)
    def test_send_trigger_without_flag(self):
        trigger = {
            "pair_symbol": "btc-usdt",
            "input_amount": 200,
            "output_amount": 2,
            "stop_price": 100
        }
        resp = requests.post(
            self.base_url
            + "/api/trading/trigger?email="
            + self.email
            + "&token="
            + self.token,
            data=json.dumps(trigger),
            headers=self.headers,
        )
        self.assertEqual(resp.status_code, 400)
        resp_body = resp.json()
        self.assertEqual(resp_body["STATUS"], "FAILED")
        self.assertEqual(resp_body["MESSAGE"], "flag is required")

    # error เดียวกับ test_delete_order_without_order_id (คิดว่านะ)
    def test_send_trigger_without_pair_symbol(self):
        trigger = {
            "flag": "buy",
            "input_amount": 200,
            "output_amount": 2,
            "stop_price": 100
        }
        resp = requests.post(
            self.base_url
            + "/api/trading/trigger?email="
            + self.email
            + "&token="
            + self.token,
            data=json.dumps(trigger),
            headers=self.headers,
        )
        self.assertEqual(resp.status_code, 400)
        resp_body = resp.json()
        self.assertEqual(resp_body["STATUS"], "FAILED")
        self.assertEqual(resp_body["MESSAGE"], "pair_symbol is required")
    
    # error เดียวกับ test_delete_order_without_order_id (คิดว่านะ)
    def test_send_trigger_without_input_amount(self):
        trigger = {
            "flag": "buy",
            "pair_symbol": "btc-usdt",
            "output_amount": 2,
            "stop_price": 100
        }
        resp = requests.post(
            self.base_url
            + "/api/trading/trigger?email="
            + self.email
            + "&token="
            + self.token,
            data=json.dumps(trigger),
            headers=self.headers,
        )
        self.assertEqual(resp.status_code, 400)
        resp_body = resp.json()
        self.assertEqual(resp_body["STATUS"], "FAILED")
        self.assertEqual(resp_body["MESSAGE"], "input_amount is required")

    # error เดียวกับ test_delete_order_without_order_id (คิดว่านะ)
    def test_send_trigger_without_output_amount(self):
        trigger = {
            "flag": "buy",
            "pair_symbol": "btc-usdt",
            "input_amount": 200,
            "stop_price": 100
        }
        resp = requests.post(
            self.base_url
            + "/api/trading/trigger?email="
            + self.email
            + "&token="
            + self.token,
            data=json.dumps(trigger),
            headers=self.headers,
        )
        self.assertEqual(resp.status_code, 400)
        resp_body = resp.json()
        self.assertEqual(resp_body["STATUS"], "FAILED")
        self.assertEqual(resp_body["MESSAGE"], "output_amount is required")
    
    def test_send_trigger_with_invalid_body(self):
        trigger = {
            "flag": "AAA",
            "pair_symbol": "btc-usdt",
            "input_amount": 200,
            "output_amount": 2,
            "stop_price": 100
        }
        resp = requests.post(
            self.base_url
            + "/api/trading/trigger?email="
            + self.email
            + "&token="
            + self.token,
            data=json.dumps(trigger),
            headers=self.headers,
        )
        self.assertEqual(resp.status_code, 400)
        resp_body = resp.json()
        self.assertEqual(resp_body["STATUS"], "FAILED")
        self.assertEqual(resp_body["MESSAGE"], "Create trigger failed: Invalid flag")
    
