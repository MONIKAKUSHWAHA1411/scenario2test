def call_llm(prompt: str) -> dict:
    return {
        "functional": [
            {
                "id": "TC_FUNC_01",
                "title": "Verify product search returns relevant results",
                "raw_steps": [
                    "User searches for black hoodie",
                    "System displays results"
                ],
                "risk": "Search relevance impacts conversion"
            }
        ],
        "negative": [
            {
                "id": "TC_NEG_01",
                "title": "Verify payment failure with expired debit card",
                "raw_steps": [
                    "User proceeds to payment",
                    "User enters expired debit card"
                ],
                "risk": "Payment failure must not create order"
            }
        ],
        "api": []
    }
