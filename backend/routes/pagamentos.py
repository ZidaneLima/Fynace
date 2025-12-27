from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import Dict, Any
from ..auth_utils import get_current_user
from ..payments.mercado_pago_service import MercadoPagoService
from ..payments.payment_models import PaymentRequest, PaymentResponse
from supabase import Client
from ..database.database_service import get_supabase_client
import logging

router = APIRouter(prefix="/pagamentos", tags=["pagamentos"])

logger = logging.getLogger(__name__)

@router.post("/criar", response_model=PaymentResponse)
async def criar_pagamento(
    payment_request: PaymentRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Create a new payment preference with Mercado Pago
    """
    try:
        # Ensure the email in the request matches the authenticated user's email
        if payment_request.email != current_user.get('email'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment email must match authenticated user's email"
            )
        
        # Add user_id to external_reference to track the payment
        external_reference = f"{current_user.get('id')}-{payment_request.external_reference}"
        
        # Prepare payment data
        payment_data = {
            "title": payment_request.title,
            "unit_price": payment_request.unit_price,
            "quantity": payment_request.quantity,
            "email": payment_request.email,
            "success_url": payment_request.success_url,
            "failure_url": payment_request.failure_url,
            "pending_url": payment_request.pending_url,
            "external_reference": external_reference
        }
        
        # Initialize Mercado Pago service
        mercado_pago_service = MercadoPagoService()
        
        # Create preference
        preference = mercado_pago_service.create_preference(payment_data)
        
        # Update user profile to indicate payment initiation
        supabase.table('user_profiles').upsert({
            'user_id': current_user.get('id'),
            'plano': 'free',  # Will be updated by webhook when payment is approved
            'pagamento_status': 'initiated',
            'pagamento_id': str(preference.get('id', '')),
            'created_at': 'now()',
            'updated_at': 'now()'
        }).execute()
        
        # Return the init_point for frontend redirection
        return PaymentResponse(
            id=preference['id'],
            init_point=preference['init_point'],
            external_reference=external_reference,
            status="initiated"
        )
    
    except Exception as e:
        logger.error(f"Error creating payment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_ERROR,
            detail=f"Error creating payment: {str(e)}"
        )


@router.post("/webhook")
async def webhook_handler(request: Request):
    """
    Handle Mercado Pago webhook notifications
    """
    from ..payments.webhook import handle_webhook
    return await handle_webhook(request)


@router.get("/status/{payment_id}")
async def get_payment_status(
    payment_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Get payment status by payment ID
    """
    try:
        # Initialize Mercado Pago service
        mercado_pago_service = MercadoPagoService()
        
        # Get payment status from Mercado Pago
        payment_info = mercado_pago_service.get_payment_status(payment_id)
        
        # Verify that this payment belongs to the current user
        external_reference = payment_info.get('external_reference', '')
        user_id_from_ref = external_reference.split('-')[0] if '-' in external_reference else external_reference
        
        if user_id_from_ref != current_user.get('id'):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this payment"
            )
        
        # Update user profile based on payment status
        payment_status = payment_info.get('status', 'pending')
        plan = 'premium' if payment_status == 'approved' else 'free'
        
        # Update user profile in Supabase
        supabase.table('user_profiles').update({
            'plano': plan,
            'pagamento_status': payment_status,
            'updated_at': 'now()'
        }).eq('user_id', current_user.get('id')).execute()
        
        return {
            "payment_id": payment_id,
            "status": payment_status,
            "plan": plan,
            "external_reference": external_reference
        }
    
    except Exception as e:
        logger.error(f"Error getting payment status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_ERROR,
            detail=f"Error getting payment status: {str(e)}"
        )