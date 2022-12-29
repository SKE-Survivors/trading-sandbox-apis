import json
import unittest

import requests
import rstr


class TestInfo(unittest.TestCase):
    base_url = "http://localhost:3000"
    pairs = [
        "btc-usdt",
        "eth-usdt",
        "eth-btc",
        "bnb-usdt",
        "bnb-btc",
        "xrp-usdt",
        "xrp-btc",
        "bnb-eth",
        "xrp-bnb",
        "xrp-eth",
    ]

    def test_get_pairs_endpoint(self):
        resp = requests.get(self.base_url + "/api/info/pairs")
        self.assertEqual(resp.status_code, 200)

        resp_body = resp.json()
        self.assertEqual(resp_body["STATUS"], "SUCCESS")
        self.assertEqual(resp_body["MESSAGE"], self.pairs)
        
    def test_get_orders_endpoint(self):
        resp = requests.get(self.base_url + "/api/info/orders")
        self.assertEqual(resp.status_code, 200)

        resp_body = resp.json()
        self.assertEqual(resp_body["STATUS"], "SUCCESS")
        
