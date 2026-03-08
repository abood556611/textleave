import requests
import os
from config import Config


class OxaPayService:
    """Service for handling OxaPay cryptocurrency payments"""
    
    BASE_URL = "https://api.oxapay.com/v1"
    
    def __init__(self):
        self.merchant_api_key = Config.OXAPAY_API_KEY
    
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
        
        endpoint = f"{self.BASE_URL}/payment/invoice"
        
        payload = {
            'amount': amount,
            'currency': currency,
            'lifetime': 30,  # Invoice lifetime in minutes
            'fee_paid_by_payer': 0,  # 0 = merchant pays, 1 = customer pays
            'under_paid_coverage': 2,  # Percentage allowed for underpayment
            'callback_url': f"{os.getenv('APP_URL', 'http://localhost:5000')}/api/payment/callback",
            'return_url': f"{os.getenv('APP_URL', 'http://localhost:5000')}/payment/success",
        }
        
        if order_id:
            payload['order_id'] = order_id
        
        if description:
            payload['description'] = description
        
        headers = {
            'Content-Type': 'application/json',
            'merchant_api_key': self.merchant_api_key
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
        
        endpoint = f"{self.BASE_URL}/payment/info"
        
        payload = {
            'track_id': track_id
        }
        
        headers = {
            'Content-Type': 'application/json',
            'merchant_api_key': self.merchant_api_key
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
    
    if invoice and invoice.get('status') == 200:
        data = invoice.get('data', {})
        return {
            'success': True,
            'payment_id': data.get('track_id'),
            'payment_url': data.get('payment_url'),
            'amount': Config.MONTHLY_PRICE if plan_type == 'monthly' else Config.YEARLY_PRICE,
            'currency': 'USD',
            'expires_at': data.get('expired_at')
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
    
    if result and result.get('status') == 200:
        data = result.get('data', {})
        status = data.get('status')
        
        return {
            'verified': status == 'Paid',
            'status': status,
            'amount': data.get('amount'),
            'currency': data.get('currency')
        }
    
    return {
        'verified': False,
        'error': 'Payment verification failed'
    }
