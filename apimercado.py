import mercadopago
sdk = mercadopago.SDK("EST-7430204721093650-122118-477d0da502a318df08aa635161754e42-467461530")

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
