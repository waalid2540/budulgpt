"""
Alert Service for Umrah Deal Finder
Handles Email, WhatsApp, and SMS notifications
"""

import os
from typing import Optional
import httpx
from twilio.rest import Client

# Environment variables
RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
RESEND_API_URL = "https://api.resend.com/emails"

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")
TWILIO_SMS_NUMBER = os.getenv("TWILIO_SMS_NUMBER", "")


async def send_email_alert(
    to_email: str,
    search_name: str,
    deal_info: dict,
    alert_type: str = "price_drop"
) -> bool:
    """
    Send email alert using Resend API

    Args:
        to_email: Recipient email address
        search_name: Name of the saved search
        deal_info: Dictionary with deal details
        alert_type: Type of alert (price_drop, new_deal)

    Returns:
        bool: True if sent successfully
    """
    if not RESEND_API_KEY:
        print("⚠️ RESEND_API_KEY not set, skipping email")
        return False

    # Build email content
    if alert_type == "price_drop":
        subject = f"🔔 Price Drop Alert: {search_name}"
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #059669 0%, #047857 100%); padding: 30px; text-align: center;">
                <h1 style="color: white; margin: 0;">🕋 Umrah Deal Alert!</h1>
                <p style="color: #d1fae5; margin-top: 10px;">Price Drop on "{search_name}"</p>
            </div>

            <div style="padding: 30px; background: #f9fafb;">
                <h2 style="color: #047857;">💰 Great News! Price Dropped!</h2>

                <div style="background: white; padding: 20px; border-radius: 12px; margin: 20px 0; border-left: 4px solid #059669;">
                    <h3 style="margin-top: 0; color: #1f2937;">{deal_info.get('hotel_name') or deal_info.get('flight_airline', 'Deal')}</h3>
                    <p style="font-size: 24px; color: #059669; font-weight: bold; margin: 10px 0;">
                        ${deal_info.get('price')} {deal_info.get('currency', 'USD')}
                    </p>

                    {f"<p><strong>Location:</strong> {deal_info.get('location')}</p>" if deal_info.get('location') else ""}
                    {f"<p><strong>Rating:</strong> {'⭐' * int(deal_info.get('rating', 0))}</p>" if deal_info.get('rating') else ""}
                    {f"<p><strong>Provider:</strong> {deal_info.get('provider')}</p>" if deal_info.get('provider') else ""}

                    <a href="{deal_info.get('booking_url', '#')}"
                       style="display: inline-block; background: #059669; color: white; padding: 12px 30px;
                              text-decoration: none; border-radius: 8px; margin-top: 15px; font-weight: bold;">
                        Book Now →
                    </a>
                </div>

                <p style="color: #6b7280; font-size: 14px; margin-top: 20px;">
                    🤖 This alert was sent by MadinaGPT Umrah Deal Finder.
                    <br>You're receiving this because you set up price alerts for "{search_name}".
                </p>

                <p style="color: #6b7280; font-size: 12px; margin-top: 10px;">
                    Manage your alerts: <a href="https://madinagpt.com/umrah-deals/dashboard" style="color: #059669;">Dashboard</a>
                </p>
            </div>
        </body>
        </html>
        """
    else:  # new_deal
        subject = f"🆕 New Deal Found: {search_name}"
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); padding: 30px; text-align: center;">
                <h1 style="color: white; margin: 0;">🕋 New Umrah Deal!</h1>
                <p style="color: #dbeafe; margin-top: 10px;">Match found for "{search_name}"</p>
            </div>

            <div style="padding: 30px; background: #f9fafb;">
                <h2 style="color: #2563eb;">✨ New Deal Matching Your Criteria!</h2>

                <div style="background: white; padding: 20px; border-radius: 12px; margin: 20px 0; border-left: 4px solid #3b82f6;">
                    <h3 style="margin-top: 0; color: #1f2937;">{deal_info.get('hotel_name') or deal_info.get('flight_airline', 'Deal')}</h3>
                    <p style="font-size: 24px; color: #2563eb; font-weight: bold; margin: 10px 0;">
                        ${deal_info.get('price')} {deal_info.get('currency', 'USD')}
                    </p>

                    {f"<p><strong>Location:</strong> {deal_info.get('location')}</p>" if deal_info.get('location') else ""}
                    {f"<p><strong>Rating:</strong> {'⭐' * int(deal_info.get('rating', 0))}</p>" if deal_info.get('rating') else ""}

                    <a href="{deal_info.get('booking_url', '#')}"
                       style="display: inline-block; background: #2563eb; color: white; padding: 12px 30px;
                              text-decoration: none; border-radius: 8px; margin-top: 15px; font-weight: bold;">
                        View Deal →
                    </a>
                </div>

                <p style="color: #6b7280; font-size: 14px; margin-top: 20px;">
                    🤖 MadinaGPT found this deal for you!
                </p>
            </div>
        </body>
        </html>
        """

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                RESEND_API_URL,
                headers={
                    "Authorization": f"Bearer {RESEND_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "from": "MadinaGPT Alerts <noreply@madinagpt.com>",
                    "to": [to_email],
                    "subject": subject,
                    "html": html_content
                },
                timeout=10.0
            )

            if response.status_code == 200:
                print(f"✅ Email sent to {to_email}")
                return True
            else:
                print(f"❌ Email failed: {response.status_code} - {response.text}")
                return False

    except Exception as e:
        print(f"❌ Email error: {str(e)}")
        return False


async def send_whatsapp_alert(
    to_phone: str,
    search_name: str,
    deal_info: dict,
    alert_type: str = "price_drop"
) -> bool:
    """
    Send WhatsApp alert using Twilio API

    Args:
        to_phone: Recipient phone number (format: +1234567890)
        search_name: Name of the saved search
        deal_info: Dictionary with deal details
        alert_type: Type of alert (price_drop, new_deal)

    Returns:
        bool: True if sent successfully
    """
    if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
        print("⚠️ Twilio credentials not set, skipping WhatsApp")
        return False

    # Format phone number for WhatsApp
    if not to_phone.startswith("whatsapp:"):
        to_phone = f"whatsapp:{to_phone}"

    # Build message content
    if alert_type == "price_drop":
        emoji = "📉"
        message = f"""🕋 *Umrah Price Drop Alert!*

{emoji} Great news for "{search_name}"!

*{deal_info.get('hotel_name') or deal_info.get('flight_airline', 'Deal')}*

💰 *${deal_info.get('price')} {deal_info.get('currency', 'USD')}*

"""
    else:  # new_deal
        emoji = "✨"
        message = f"""🕋 *New Umrah Deal Found!*

{emoji} Perfect match for "{search_name}"!

*{deal_info.get('hotel_name') or deal_info.get('flight_airline', 'Deal')}*

💰 *${deal_info.get('price')} {deal_info.get('currency', 'USD')}*

"""

    if deal_info.get('location'):
        message += f"📍 {deal_info['location']}\n"
    if deal_info.get('rating'):
        message += f"⭐ {deal_info['rating']} stars\n"
    if deal_info.get('provider'):
        message += f"🔗 via {deal_info['provider']}\n"

    message += f"\n🔗 Book: {deal_info.get('booking_url', 'madinagpt.com/umrah-deals')}"
    message += "\n\n🤖 Sent by MadinaGPT"

    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

        message_obj = client.messages.create(
            from_=TWILIO_WHATSAPP_NUMBER,
            to=to_phone,
            body=message
        )

        print(f"✅ WhatsApp sent to {to_phone}: {message_obj.sid}")
        return True

    except Exception as e:
        print(f"❌ WhatsApp error: {str(e)}")
        return False


async def send_sms_alert(
    to_phone: str,
    search_name: str,
    deal_info: dict,
    alert_type: str = "price_drop"
) -> bool:
    """
    Send SMS alert using Twilio API

    Args:
        to_phone: Recipient phone number (format: +1234567890)
        search_name: Name of the saved search
        deal_info: Dictionary with deal details
        alert_type: Type of alert (price_drop, new_deal)

    Returns:
        bool: True if sent successfully
    """
    if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN or not TWILIO_SMS_NUMBER:
        print("⚠️ Twilio SMS credentials not set, skipping SMS")
        return False

    # Build short message for SMS (160 chars limit)
    deal_name = deal_info.get('hotel_name') or deal_info.get('flight_airline', 'Deal')
    price = deal_info.get('price')

    if alert_type == "price_drop":
        message = f"🕋 Price Drop! {search_name}: {deal_name} - ${price}. Book: madinagpt.com/umrah-deals"
    else:
        message = f"🕋 New Deal! {search_name}: {deal_name} - ${price}. View: madinagpt.com/umrah-deals"

    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

        message_obj = client.messages.create(
            from_=TWILIO_SMS_NUMBER,
            to=to_phone,
            body=message
        )

        print(f"✅ SMS sent to {to_phone}: {message_obj.sid}")
        return True

    except Exception as e:
        print(f"❌ SMS error: {str(e)}")
        return False


async def send_alert(
    user_email: Optional[str],
    user_phone: Optional[str],
    search_name: str,
    deal_info: dict,
    alert_type: str = "price_drop",
    send_email: bool = True,
    send_whatsapp: bool = False,
    send_sms: bool = False
) -> dict:
    """
    Send alerts through multiple channels

    Returns:
        dict: Status of each channel
    """
    results = {
        "email": False,
        "whatsapp": False,
        "sms": False
    }

    # Send email
    if send_email and user_email:
        results["email"] = await send_email_alert(user_email, search_name, deal_info, alert_type)

    # Send WhatsApp
    if send_whatsapp and user_phone:
        results["whatsapp"] = await send_whatsapp_alert(user_phone, search_name, deal_info, alert_type)

    # Send SMS
    if send_sms and user_phone:
        results["sms"] = await send_sms_alert(user_phone, search_name, deal_info, alert_type)

    return results
