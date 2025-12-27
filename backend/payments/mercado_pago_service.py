import mercadopago
import os
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

class MercadoPagoService:
    def __init__(self):
        self.access_token = os.getenv("MERCADOPAGO_ACCESS_TOKEN")
        if not self.access_token:
            raise ValueError("MERCADOPAGO_ACCESS_TOKEN environment variable is required")
        self.sdk = mercadopago.SDK(self.access_token)

    def create_preference(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a Mercado Pago preference for payment
        """
        try:
            preference_data = {
                "items": [
                    {
                        "title": payment_data.get("title", "Premium Plan"),
                        "quantity": payment_data.get("quantity", 1),
                        "unit_price": float(payment_data.get("unit_price", 0)),
                        "currency_id": "BRL"
                    }
                ],
                "payer": {
                    "email": payment_data.get("email", "")
                },
                "back_urls": {
                    "success": payment_data.get("success_url", ""),
                    "failure": payment_data.get("failure_url", ""),
                    "pending": payment_data.get("pending_url", "")
                },
                "auto_return": "approved",
                "external_reference": payment_data.get("external_reference", ""),
                "notification_url": f"{os.getenv('BASE_URL', 'http://localhost:8000')}/pagamentos/webhook"
            }
            
            preference_response = self.sdk.preference().create(preference_data)
            return preference_response["response"]
        except Exception as e:
            raise Exception(f"Error creating Mercado Pago preference: {str(e)}")

    def get_payment_status(self, payment_id: str) -> Dict[str, Any]:
        """
        Get payment status by payment ID
        """
        try:
            payment_response = self.sdk.payment().get(payment_id)
            return payment_response["response"]
        except Exception as e:
            raise Exception(f"Error getting payment status: {str(e)}")

    def validate_webhook(self, topic: str, resource_id: str) -> Dict[str, Any]:
        """
        Validate webhook notification from Mercado Pago
        """
        try:
            if topic == "payment":
                payment_info = self.get_payment_status(resource_id)
                return payment_info
            else:
                raise Exception(f"Unsupported topic: {topic}")
        except Exception as e:
            raise Exception(f"Error validating webhook: {str(e)}")