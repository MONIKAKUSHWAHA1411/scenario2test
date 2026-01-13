class ReviewAgent:
    def review(self, test_cases: dict) -> dict:
        reviewed = {}

        reviewed["functional"] = [
            {
                "id": "TC_FUNC_01",
                "title": "Verify product search returns relevant results",
                "gherkin": [
                    "Given the user is logged in and on the Amazon home page",
                    "When the user searches for 'black hoodie'",
                    "Then the search results page should load successfully",
                    "And relevant black hoodie products should be displayed",
                    "And each product should show name, price, image, and rating"
                ],
                "priority": "High",
                "test_type": "Functional",
                "notes": "Validates core discovery flow and search relevance"
            }
        ]

        reviewed["negative"] = [
            {
                "id": "TC_NEG_01",
                "title": "Verify payment failure with expired debit card",
                "gherkin": [
                    "Given the user has added a product to cart and selected a delivery address",
                    "And the user is on the payment page",
                    "When the user enters an expired debit card",
                    "And attempts to place the order",
                    "Then the payment should be declined",
                    "And a clear error message indicating card expiration should be shown",
                    "And no order should be created",
                    "And the cart contents should remain unchanged"
                ],
                "priority": "High",
                "test_type": "Negative",
                "notes": "Ensures payment failure does not cause data or order corruption"
            }
        ]

        reviewed["api"] = []

        return reviewed
