class ReviewAgent:
    def review(self, test_cases: dict) -> dict:
        reviewed = {}

        # ---------- Functional ----------
        reviewed["functional"] = test_cases.get("functional", [])
        reviewed["negative"] = test_cases.get("negative", [])

        # ---------- API (QA-refined) ----------
        reviewed["api"] = []

        for api_case in test_cases.get("api", []):
            if "payment" in api_case["title"].lower():
                reviewed["api"].append({
                    "id": "TC_API_01",
                    "title": "Verify payment API rejects expired debit card",
                    "endpoint": "POST /api/payments/charge",
                    "assertions": [
                        "Payment response indicates failure",
                        "No transaction ID is generated",
                        "Order status remains PAYMENT_PENDING"
                    ],
                    "priority": "High",
                    "test_type": "API",
                    "notes": "Prevents invalid payments from creating orders"
                })

            if "order" in api_case["title"].lower():
                reviewed["api"].append({
                    "id": "TC_API_02",
                    "title": "Verify order is not created when payment fails",
                    "endpoint": "POST /api/orders",
                    "assertions": [
                        "Order creation request is rejected",
                        "No order ID is generated",
                        "Cart remains active"
                    ],
                    "priority": "High",
                    "test_type": "API",
                    "notes": "Ensures order creation is atomic"
                })

        return reviewed
