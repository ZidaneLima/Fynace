import logging
from fastapi import Request, HTTPException, status
from supabase import Client
from ..payments.mercado_pago_service import MercadoPagoService
from ..database.database_service import get_supabase_client

logger = logging.getLogger(__name__)

async def handle_webhook(request: Request):
    """
    Handle Mercado Pago webhook notifications
    """
    try:
        # Get the JSON payload from the request
        payload = await request.json()
        
        # Extract webhook data
        topic = payload.get('topic')
        resource_id = payload.get('resource_id')
        
        if not topic or not resource_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing topic or resource_id in webhook payload"
            )
        
        # Initialize Mercado Pago service
        mercado_pago_service = MercadoPagoService()
        
        # Validate the webhook data
        payment_info = mercado_pago_service.validate_webhook(topic, resource_id)
        
        # Connect to Supabase
        supabase: Client = get_supabase_client()
        
        # Update user profile based on payment status
        external_reference = payment_info.get('external_reference')
        if external_reference:
            # Extract user_id from external_reference (format: user_id-payment_id)
            user_id = external_reference.split('-')[0] if '-' in external_reference else external_reference
            
            # Get payment status
            payment_status = payment_info.get('status', 'pending')
            mercado_pago_payment_id = payment_info.get('id')
            
            # Determine plan based on payment status
            if payment_status == 'approved':
                plan = 'premium'
            elif payment_status in ['cancelled', 'refunded', 'charged_back']:
                plan = 'free'
            else:
                plan = 'free'  # Default to free for pending, in_process, etc.
            
            # Update user profile in Supabase
            response = supabase.table('user_profiles').update({
                'plano': plan,
                'pagamento_status': payment_status,
                'pagamento_id': str(mercado_pago_payment_id),
                'updated_at': 'now()'
            }).eq('user_id', user_id).execute()
            
            logger.info(f"Webhook processed successfully for user {user_id}. Payment status: {payment_status}")
            return {"status": "success", "message": "Webhook processed successfully"}
        else:
            logger.warning(f"No external_reference found in payment info: {payment_info}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No external_reference found in payment information"
            )
    
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_ERROR,
            detail=f"Error processing webhook: {str(e)}"
        )