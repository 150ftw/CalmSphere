import random
import string
from datetime import datetime, timedelta, timezone
import logging

logger = logging.getLogger(__name__)

def generate_otp(length=6):
    """Generate a random 6-digit OTP"""
    return ''.join(random.choices(string.digits, k=length))

def send_otp_email(email: str, otp: str, purpose: str = "login"):
    """
    Send OTP via email
    In production, integrate with SendGrid, AWS SES, or similar
    """
    try:
        # Simulate email sending
        logger.info(f"[EMAIL OTP] To: {email}, OTP: {otp}, Purpose: {purpose}")
        
        # TODO: Replace with actual email service
        # Example with SendGrid:
        # from sendgrid import SendGridAPIClient
        # from sendgrid.helpers.mail import Mail
        # message = Mail(
        #     from_email='noreply@calmsphere.ai',
        #     to_emails=email,
        #     subject=f'CalmSphere AI - Your OTP Code',
        #     html_content=f'<p>Your OTP code is: <strong>{otp}</strong></p><p>Valid for 10 minutes.</p>'
        # )
        # sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        # response = sg.send(message)
        
        return True
    except Exception as e:
        logger.error(f"Failed to send email OTP: {e}")
        return False

def send_otp_sms(phone_number: str, otp: str, purpose: str = "login"):
    """
    Send OTP via SMS
    In production, integrate with Twilio, MSG91, or similar
    """
    try:
        # Simulate SMS sending
        logger.info(f"[SMS OTP] To: {phone_number}, OTP: {otp}, Purpose: {purpose}")
        
        # TODO: Replace with actual SMS service
        # Example with Twilio:
        # from twilio.rest import Client
        # client = Client(os.environ.get('TWILIO_ACCOUNT_SID'), os.environ.get('TWILIO_AUTH_TOKEN'))
        # message = client.messages.create(
        #     body=f'Your CalmSphere AI OTP is: {otp}. Valid for 10 minutes.',
        #     from_=os.environ.get('TWILIO_PHONE_NUMBER'),
        #     to=phone_number
        # )
        
        # Example with MSG91 (India):
        # import requests
        # url = "https://api.msg91.com/api/v5/otp"
        # payload = {
        #     "template_id": os.environ.get('MSG91_TEMPLATE_ID'),
        #     "mobile": phone_number,
        #     "authkey": os.environ.get('MSG91_AUTH_KEY'),
        #     "otp": otp
        # }
        # response = requests.post(url, json=payload)
        
        return True
    except Exception as e:
        logger.error(f"Failed to send SMS OTP: {e}")
        return False

async def create_and_send_otp(db, user_id: str, email: str, phone_number: str, purpose: str = "login"):
    """
    Generate OTP, store in database, and send via email and SMS
    """
    otp_code = generate_otp()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)
    
    otp_doc = {
        "id": str(random.randint(100000, 999999)),
        "user_id": user_id,
        "otp_code": otp_code,
        "purpose": purpose,
        "expires_at": expires_at.isoformat(),
        "verified": False,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.otp_verifications.insert_one(otp_doc)
    
    # Send OTP via both channels
    email_sent = send_otp_email(email, otp_code, purpose)
    sms_sent = send_otp_sms(phone_number, otp_code, purpose)
    
    # TESTING MODE: Return OTP in response
    # TODO: Remove 'otp_code' from response in production
    return {
        "otp_sent": email_sent or sms_sent,
        "email_sent": email_sent,
        "sms_sent": sms_sent,
        "otp_id": otp_doc["id"],
        "otp_code": otp_code  # FOR TESTING ONLY - REMOVE IN PRODUCTION
    }

async def verify_otp(db, user_id: str, otp_code: str, purpose: str = "login"):
    """
    Verify OTP code
    """
    otp_record = await db.otp_verifications.find_one({
        "user_id": user_id,
        "otp_code": otp_code,
        "purpose": purpose,
        "verified": False
    })
    
    if not otp_record:
        return {"success": False, "message": "Invalid OTP code"}
    
    expires_at = datetime.fromisoformat(otp_record['expires_at'])
    if datetime.now(timezone.utc) > expires_at:
        return {"success": False, "message": "OTP expired"}
    
    # Mark as verified
    await db.otp_verifications.update_one(
        {"id": otp_record['id']},
        {"$set": {"verified": True}}
    )
    
    return {"success": True, "message": "OTP verified successfully"}
