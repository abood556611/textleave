import requests
import os
from config import Config


class OxaPayService:
    """Service for handling OxaPay cryptocurrency payments"""
    
    BASE_URL = "https://api.oxapay.com"
    
    def __init__(self):
        self.api_key = Config.OXAPAY_API_KEY
        self.merchant_id = os.getenv('OXAPAY_MERCHANT_ID', '')
    
    def create_invoice(self, amount, currency='USD', order_id=None, description=None):
        """
        Create a payment invoice
        
        Args:
            amount: Payment amount
            currency: Currency (USD, EUR, etc.)
            order_id: Unique order identifier
            description: Payment description
            
        Returns:
            dict with invoice data including payment URL
        """
        
        endpoint = f"{self.BASE_URL}/merchants/request"
        
        payload = {
            'merchant': self.merchant_id,
            'amount': amount,
            'currency': currency,
            'lifeTime': 30,  # Invoice lifetime in minutes
            'feePaidByPayer': 0,  # 0 = merchant pays, 1 = customer pays
            'underPaidCover': 2,  # Percentage allowed for underpayment
            'callbackUrl': f"{os.getenv('APP_URL', 'http://localhost:5000')}/api/payment/callback",
            'returnUrl': f"{os.getenv('APP_URL', 'http://localhost:5000')}/payment/success",
        }
        
        if order_id:
            payload['orderId'] = order_id
        
        if description:
            payload['description'] = description
        
        headers = {
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.post(endpoint, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error creating invoice: {e}")
            return None
    
    def verify_payment(self, track_id):
        """
        Verify payment status
        
        Args:
            track_id: OxaPay tracking ID
            
        Returns:
            dict with payment status
        """
        
        endpoint = f"{self.BASE_URL}/merchants/inquiry"
        
        payload = {
            'merchant': self.merchant_id,
            'trackId': track_id
        }
        
        headers = {
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.post(endpoint, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error verifying payment: {e}")
            return None
    
    def get_supported_networks(self):
        """Get list of supported blockchain networks"""
        return ['BSC', 'TRX', 'ETH', 'POLYGON', 'AVAX', 'BTC', 'LTC']
    
    def create_subscription_invoice(self, plan_type='monthly'):
        """
        Create invoice for subscription plan
        
        Args:
            plan_type: 'monthly' or 'yearly'
            
        Returns:
            Invoice data
        """
        
        amount = Config.MONTHLY_PRICE if plan_type == 'monthly' else Config.YEARLY_PRICE
        description = f"TextLeaf {plan_type.title()} Subscription"
        
        return self.create_invoice(
            amount=amount,
            currency='USD',
            description=description
        )


def create_payment_session(plan_type='monthly', user_id=None):
    """
    Helper function to create payment session
    
    Args:
        plan_type: 'monthly' or 'yearly'
        user_id: Optional user identifier
        
    Returns:
        Payment session data
    """
    
    service = OxaPayService()
    
    # Create invoice
    invoice = service.create_subscription_invoice(plan_type)
    
    if invoice and invoice.get('result') == 100:
        return {
            'success': True,
            'payment_id': invoice.get('trackId'),
            'payment_url': invoice.get('payLink'),
            'amount': Config.MONTHLY_PRICE if plan_type == 'monthly' else Config.YEARLY_PRICE,
            'currency': 'USD',
            'expires_at': invoice.get('expiredAt')
        }
    
    return {
        'success': False,
        'error': 'Failed to create payment session'
    }


def verify_payment_session(track_id):
    """
    Verify payment session
    
    Args:
        track_id: OxaPay tracking ID
        
    Returns:
        Verification result
    """
    
    service = OxaPayService()
    result = service.verify_payment(track_id)
    
    if result and result.get('result') == 100:
        status = result.get('status')
        
        return {
            'verified': status == 'Paid',
            'status': status,
            'amount': result.get('amount'),
            'currency': result.get('currency')
        }
    
    return {
        'verified': False,
        'error': 'Payment verification failed'
    }
