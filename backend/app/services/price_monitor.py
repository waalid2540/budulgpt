"""
Background Price Monitoring Service for Umrah Deal Finder
Checks saved searches every 6 hours and sends alerts for price drops
"""

import asyncio
from datetime import datetime, timedelta
from typing import List, Dict
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.services.alerts import send_alert


class PriceMonitor:
    """
    Background service that monitors saved searches for price changes
    """

    def __init__(self):
        self.check_interval_hours = int(os.getenv("ALERT_CHECK_INTERVAL", "6"))
        self.price_drop_threshold = 0.10  # 10% price drop triggers alert
        self.running = False

    async def check_saved_search(self, saved_search: Dict) -> None:
        """
        Check a single saved search for new deals or price drops

        Args:
            saved_search: Dictionary containing search criteria and user info
        """

        search_criteria = saved_search.get("search_criteria", {})
        user_email = saved_search.get("user_email")
        user_phone = saved_search.get("user_phone")
        search_name = saved_search.get("search_name", "Your Umrah Search")
        last_best_price = saved_search.get("best_price", float('inf'))

        # Get alert preferences
        alert_email = saved_search.get("alert_email", True)
        alert_whatsapp = saved_search.get("alert_whatsapp", False)
        alert_sms = saved_search.get("alert_sms", False)

        try:
            # Import here to avoid circular imports
            from app.api.v1.umrah_deals import search_umrah_deals_with_perplexity, UmrahSearchRequest

            # Convert search criteria dict to UmrahSearchRequest
            search_request = UmrahSearchRequest(**search_criteria)

            # Search for new deals
            deals = await search_umrah_deals_with_perplexity(search_request)

            if not deals:
                print(f"⚠️ No deals found for search: {search_name}")
                return

            # Find the best (lowest) price
            best_deal = min(deals, key=lambda d: d.get("price", float('inf')))
            current_best_price = best_deal.get("price", float('inf'))

            # Check if there's a significant price drop
            if current_best_price < last_best_price * (1 - self.price_drop_threshold):
                print(f"🔔 Price drop detected for '{search_name}': ${last_best_price} → ${current_best_price}")

                # Send price drop alert
                await send_alert(
                    user_email=user_email if alert_email else None,
                    user_phone=user_phone if (alert_whatsapp or alert_sms) else None,
                    search_name=search_name,
                    deal_info=best_deal,
                    alert_type="price_drop",
                    send_email=alert_email,
                    send_whatsapp=alert_whatsapp,
                    send_sms=alert_sms
                )

                # TODO: Update best_price in database
                print(f"✅ Alert sent to {user_email or user_phone}")

            elif current_best_price < last_best_price:
                # Small price improvement, but not enough to trigger alert
                print(f"💰 Small price improvement for '{search_name}': ${last_best_price} → ${current_best_price}")
                # TODO: Update best_price in database silently

            else:
                print(f"📊 No price change for '{search_name}': ${current_best_price}")

        except Exception as e:
            print(f"❌ Error checking search '{search_name}': {str(e)}")

    async def check_all_saved_searches(self) -> None:
        """
        Check all saved searches in the database
        """

        print(f"🔍 Starting price check at {datetime.now()}")

        # TODO: Fetch all saved searches from database
        # For now, this is a placeholder
        saved_searches = []

        # Mock example for testing (remove when database is connected)
        if os.getenv("DEBUG_MODE") == "true":
            saved_searches = [
                {
                    "id": "search_test_1",
                    "search_name": "Makkah 5-star Budget",
                    "user_email": os.getenv("TEST_EMAIL", "test@example.com"),
                    "user_phone": os.getenv("TEST_PHONE"),
                    "alert_email": True,
                    "alert_whatsapp": False,
                    "alert_sms": False,
                    "best_price": 500,
                    "search_criteria": {
                        "search_type": "hotels",
                        "destination": "Makkah",
                        "budget_min": 0,
                        "budget_max": 600,
                        "hotel_rating": 5,
                        "distance_from_haram": 2.0,
                        "duration_nights": 7
                    }
                }
            ]

        if not saved_searches:
            print("ℹ️ No saved searches to check")
            return

        # Check each saved search
        for saved_search in saved_searches:
            await self.check_saved_search(saved_search)
            # Small delay between checks to avoid rate limits
            await asyncio.sleep(2)

        print(f"✅ Completed price check at {datetime.now()}")

    async def start_monitoring(self) -> None:
        """
        Start the background monitoring loop
        Runs every N hours (default: 6 hours)
        """

        self.running = True
        print(f"🚀 Price monitoring started - checking every {self.check_interval_hours} hours")

        while self.running:
            try:
                await self.check_all_saved_searches()

                # Wait for the next check interval
                next_check = datetime.now() + timedelta(hours=self.check_interval_hours)
                print(f"⏰ Next check scheduled at: {next_check.strftime('%Y-%m-%d %H:%M:%S')}")

                await asyncio.sleep(self.check_interval_hours * 3600)

            except Exception as e:
                print(f"❌ Error in monitoring loop: {str(e)}")
                # Wait 5 minutes before retrying on error
                await asyncio.sleep(300)

    def stop_monitoring(self) -> None:
        """
        Stop the background monitoring loop
        """
        self.running = False
        print("🛑 Price monitoring stopped")


# Global monitor instance
price_monitor = PriceMonitor()


async def start_price_monitoring():
    """
    Start the background price monitoring service
    Call this from your FastAPI startup event
    """
    await price_monitor.start_monitoring()


async def stop_price_monitoring():
    """
    Stop the background price monitoring service
    Call this from your FastAPI shutdown event
    """
    price_monitor.stop_monitoring()


# For manual testing
if __name__ == "__main__":
    print("🧪 Testing Price Monitor...")
    asyncio.run(price_monitor.check_all_saved_searches())
