"""
Affiliate Link Tracker for Umrah Deal Finder
Converts regular booking URLs to affiliate links with your tracking codes
"""

import os
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse


class AffiliateTracker:
    """
    Manages affiliate tracking codes for various booking platforms
    """

    def __init__(self):
        # Load affiliate IDs from environment variables
        self.affiliate_codes = {
            # Booking.com
            "booking.com": {
                "param": "aid",
                "value": os.getenv("BOOKING_AFFILIATE_ID", ""),
                "label_param": "label",
                "label_value": "madinagpt-umrah"
            },

            # Agoda
            "agoda.com": {
                "param": "cid",
                "value": os.getenv("AGODA_AFFILIATE_ID", ""),
            },

            # Hotels.com
            "hotels.com": {
                "param": "affiliateId",
                "value": os.getenv("HOTELS_AFFILIATE_ID", ""),
            },

            # Expedia
            "expedia.com": {
                "param": "affid",
                "value": os.getenv("EXPEDIA_AFFILIATE_ID", ""),
            },

            # Skyscanner (redirect through your tracking)
            "skyscanner.com": {
                "redirect": True,
                "tracking_url": os.getenv("SKYSCANNER_TRACKING_URL", ""),
            },

            # Kayak
            "kayak.com": {
                "param": "a",
                "value": os.getenv("KAYAK_AFFILIATE_ID", ""),
            },

            # Google Flights (no direct affiliate, redirect to partner)
            "google.com/flights": {
                "redirect": True,
                "fallback_partner": "skyscanner.com"
            },

            # Islamic/Umrah booking sites
            "almosafer.com": {
                "param": "ref",
                "value": os.getenv("ALMOSAFER_PARTNER_ID", ""),
            },

            "seera.sa": {
                "param": "partner",
                "value": os.getenv("SEERA_PARTNER_ID", ""),
            },

            "halalbooking.com": {
                "param": "ref",
                "value": os.getenv("HALALBOOKING_AFFILIATE_ID", ""),
            },

            # Travelpayouts (unified tracking)
            "travelpayouts": {
                "marker": os.getenv("TRAVELPAYOUTS_MARKER", "madinagpt"),
                "redirect_base": "https://tp.media/click"
            }
        }

    def add_affiliate_code(self, url: str, deal_type: str = "hotel") -> str:
        """
        Add affiliate tracking code to a booking URL

        Args:
            url: Original booking URL from Perplexity
            deal_type: Type of deal (hotel, flight, package)

        Returns:
            URL with affiliate tracking code added
        """

        if not url or url == "#":
            return url

        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()

            # Check if we have affiliate setup for this domain
            affiliate_config = None
            for site, config in self.affiliate_codes.items():
                if site in domain:
                    affiliate_config = config
                    break

            if not affiliate_config:
                # No affiliate program for this site, return original URL
                print(f"⚠️ No affiliate config for {domain}")
                return url

            # Handle redirect-based tracking (Skyscanner, etc.)
            if affiliate_config.get("redirect"):
                tracking_url = affiliate_config.get("tracking_url")
                if tracking_url:
                    # Encode original URL in tracking redirect
                    return f"{tracking_url}?url={url}"
                else:
                    return url

            # Handle parameter-based tracking (Booking.com, Agoda, etc.)
            param = affiliate_config.get("param")
            value = affiliate_config.get("value")

            if not value:
                print(f"⚠️ Affiliate ID not set for {domain}")
                return url

            # Parse existing query parameters
            query_params = parse_qs(parsed.query)

            # Add affiliate parameter
            query_params[param] = [value]

            # Add label/additional tracking if specified
            if "label_param" in affiliate_config:
                query_params[affiliate_config["label_param"]] = [affiliate_config["label_value"]]

            # Rebuild URL with affiliate code
            new_query = urlencode(query_params, doseq=True)
            tracked_url = urlunparse((
                parsed.scheme,
                parsed.netloc,
                parsed.path,
                parsed.params,
                new_query,
                parsed.fragment
            ))

            print(f"✅ Added affiliate tracking to {domain}")
            return tracked_url

        except Exception as e:
            print(f"❌ Error adding affiliate code: {e}")
            return url

    def get_commission_info(self, domain: str) -> dict:
        """
        Get commission information for a booking platform

        Returns:
            dict: Commission rate, status, etc.
        """

        commission_rates = {
            "booking.com": {"rate": "3-4%", "type": "per_booking", "payout": "Net 30"},
            "agoda.com": {"rate": "5-7%", "type": "per_booking", "payout": "Net 30"},
            "expedia.com": {"rate": "3-5%", "type": "per_booking", "payout": "Net 60"},
            "almosafer.com": {"rate": "10-15%", "type": "per_booking", "payout": "Net 30"},
            "skyscanner.com": {"rate": "Variable", "type": "CPC/CPA", "payout": "Net 60"},
        }

        for site, info in commission_rates.items():
            if site in domain.lower():
                return info

        return {"rate": "Unknown", "type": "Unknown", "payout": "Unknown"}


# Global instance
affiliate_tracker = AffiliateTracker()


def track_booking_click(deal: dict, user_id: str = None) -> dict:
    """
    Track when a user clicks on a booking URL
    Log for analytics and commission tracking

    Args:
        deal: The deal object with booking_url
        user_id: Optional user identifier

    Returns:
        dict: Tracking information
    """

    original_url = deal.get("booking_url", "")
    tracked_url = affiliate_tracker.add_affiliate_code(original_url, deal.get("deal_type", "hotel"))

    # TODO: Log click to database for analytics
    click_data = {
        "user_id": user_id,
        "original_url": original_url,
        "tracked_url": tracked_url,
        "deal_name": deal.get("hotel_name") or deal.get("flight_airline"),
        "price": deal.get("price"),
        "provider": deal.get("provider"),
        "timestamp": "2025-11-02"  # Use actual timestamp
    }

    print(f"📊 Tracked booking click: {click_data['deal_name']} - ${click_data['price']}")

    return {
        "tracked_url": tracked_url,
        "click_id": "click_" + str(hash(tracked_url))[:8]
    }
