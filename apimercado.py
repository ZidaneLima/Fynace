"""
Legacy Mercado Pago API file - DO NOT USE in production
This file exists for reference only. Use the new payment system in backend/payments/
"""
import mercadopago
import os
from dotenv import load_dotenv

load_dotenv()

# Get access token from environment variable
access_token = os.getenv("MERCADOPAGO_ACCESS_TOKEN")
if not access_token:
    raise ValueError("MERCADOPAGO_ACCESS_TOKEN environment variable is required")

sdk = mercadopago.SDK(access_token)

payment_data = {
    "items": [
        {   "id": "1",
            "title": "Teste",
            "quantity": 1,
            "currency_id": "BRL",
            "unit_price": 20
        }
    ],
    "back_urls": {
		"success": "https://test.com/success",
		"failure": "https://test.com/failure",
		"pending": "https://test.com/pending",
	},
    "auto_return": "all",
}
result = sdk.preference().create(payment_data)
payment = result["response"]
print(payment)
