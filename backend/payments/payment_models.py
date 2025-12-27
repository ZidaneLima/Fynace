from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PaymentRequest(BaseModel):
    title: str
    unit_price: float
    quantity: int = 1
    email: str
    success_url: str
    failure_url: str
    pending_url: str
    external_reference: str

class PaymentResponse(BaseModel):
    id: str
    init_point: str
    external_reference: str
    status: str

class WebhookRequest(BaseModel):
    topic: str
    resource_id: str
    action: str
    api_version: str
    date_created: datetime
    user_id: str
    live_mode: bool
    type: str
    received_by: str
    application_id: Optional[str] = None
    merchant_order_id: Optional[str] = None
    preference_id: Optional[str] = None