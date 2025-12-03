"""
Payment flow utilities. Implement your gateway integration here.
"""
import os
import hmac
import hashlib
from dotenv import load_dotenv

load_dotenv()

PAYMENT_SECRET = os.getenv('PAYMENT_SECRET', 'changeme')
PAYMENT_GATEWAY_URL = os.getenv('PAYMENT_GATEWAY_URL', 'https://payments.example.com')


async def generate_payment_link(owner_id: int, plan: str) -> str:
    """
    Generate a payment link for the given owner and plan.
    
    Replace this with your actual payment gateway integration:
    - Stripe: Use stripe.checkout.Session.create()
    - Razorpay: Use razorpay.order.create()
    - PayPal: Use paypal.orders.create()
    
    Args:
        owner_id: Telegram user ID of the owner
        plan: Subscription plan (basic/premium)
    
    Returns:
        Payment URL string
    """
    # Generate a simple signature for verification
    data = f"{owner_id}:{plan}:{PAYMENT_SECRET}"
    signature = hashlib.sha256(data.encode()).hexdigest()[:16]
    
    # Mock payment link - replace with real gateway
    return f"{PAYMENT_GATEWAY_URL}/pay?owner={owner_id}&plan={plan}&sig={signature}"


async def validate_payment_notification(data: dict) -> bool:
    """
    Validate incoming payment webhook notification.
    
    Replace with your gateway's signature verification:
    - Stripe: stripe.Webhook.construct_event()
    - Razorpay: razorpay.utility.verify_webhook_signature()
    
    Args:
        data: Webhook payload dictionary
    
    Returns:
        True if valid, False otherwise
    """
    received_sig = data.get('signature', '')
    owner_id = data.get('owner_id', '')
    plan = data.get('plan', '')
    
    # Recreate signature
    expected_data = f"{owner_id}:{plan}:{PAYMENT_SECRET}"
    expected_sig = hashlib.sha256(expected_data.encode()).hexdigest()[:16]
    
    return hmac.compare_digest(received_sig, expected_sig)


async def process_successful_payment(owner_id: int, plan: str) -> bool:
    """
    Process a successful payment - activate subscription.
    
    Args:
        owner_id: Telegram user ID
        plan: Plan that was purchased
    
    Returns:
        True if processed successfully
    """
    import datetime
    from database import AsyncSessionLocal, Owner
    from sqlalchemy import select
    
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Owner).where(Owner.telegram_id == owner_id)
        )
        owner = result.scalars().first()
        
        if not owner:
            return False
        
        owner.plan = plan
        if plan == 'premium':
            owner.subscription_expires = datetime.datetime.utcnow() + datetime.timedelta(days=30)
        
        await session.commit()
        return True


def get_plan_price(plan: str) -> float:
    """Get price for a subscription plan."""
    prices = {
        'basic': 0.0,
        'premium': 9.99,
        'enterprise': 29.99
    }
    return prices.get(plan, 0.0)
