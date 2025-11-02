# 💰 Umrah Deal Finder - Affiliate Commission Guide

## Overview

The MadinaGPT Umrah Deal Finder uses **Perplexity AI** to search the entire web for Umrah deals, then automatically adds **YOUR affiliate tracking codes** to booking links so you earn commission when users book.

---

## How It Works

### 1. **Perplexity Searches the Web** 🔍
- Perplexity AI searches ALL major booking sites in real-time
- No need for individual APIs from Booking.com, Expedia, etc.
- Returns current prices, availability, and booking URLs

### 2. **We Add Your Affiliate Codes** 💵
- System automatically injects YOUR affiliate tracking codes into URLs
- When users click "Book Now", they go through YOUR affiliate link
- You earn commission on every booking

### 3. **User Books, You Earn** ✅
- User completes booking on partner site
- Partner tracks the sale through your affiliate code
- You receive commission (3-15% depending on partner)

---

## Commission Rates by Platform

| Platform | Commission Rate | Payout Terms | Umrah-Friendly? |
|----------|----------------|--------------|-----------------|
| **Booking.com** | 3-4% | Net 30 days | ✅ Yes |
| **Agoda** | 5-7% | Net 30 days | ✅ Yes |
| **Hotels.com** | 3-5% | Net 60 days | ✅ Yes |
| **Expedia** | 3-5% | Net 60 days | ✅ Yes |
| **Almosafer** | 10-15% | Net 30 days | ✅✅ **BEST for Umrah** |
| **Seera** | 10-15% | Net 30 days | ✅✅ **BEST for Umrah** |
| **HalalBooking** | 5-8% | Net 30 days | ✅✅ **BEST for Umrah** |
| **Skyscanner** | Variable (CPC/CPA) | Net 60 days | ⚠️ Mixed |

---

## Step-by-Step Setup

### **Option 1: Travelpayouts (EASIEST - RECOMMENDED FOR BEGINNERS)** ⭐

Travelpayouts is an **aggregator** that gives you access to multiple affiliate programs through ONE platform.

#### Setup:
1. **Sign up**: https://www.travelpayouts.com
2. **Choose programs**: Enable Booking.com, Agoda, Hotels.com, Aviasales (flights)
3. **Get your marker**: Copy your unique marker code (e.g., `madinagpt`)
4. **Add to .env**:
   ```bash
   TRAVELPAYOUTS_MARKER=your_marker_here
   ```

#### Why Travelpayouts?
✅ One platform for multiple booking sites
✅ Single payout for all commissions
✅ Easy tracking dashboard
✅ No need to manage multiple affiliate accounts
✅ Commission rates: 3-7%

---

### **Option 2: Direct Affiliate Programs (HIGHER COMMISSIONS)**

Sign up directly with each booking platform for potentially higher commissions and more control.

#### A. **Booking.com Affiliate Partner Program**
1. **Sign up**: https://www.booking.com/affiliate-program
2. **Get approved**: Usually takes 1-2 business days
3. **Get your AID**: Copy your affiliate ID (e.g., `123456`)
4. **Add to .env**:
   ```bash
   BOOKING_AFFILIATE_ID=123456
   ```

#### B. **Agoda YCS (Your Commission Source)**
1. **Sign up**: https://ycs.agoda.com
2. **Get CID**: Copy your affiliate CID
3. **Add to .env**:
   ```bash
   AGODA_AFFILIATE_ID=your_cid_here
   ```

#### C. **Almosafer Partnership** (HIGHEST COMMISSIONS for Umrah) 🌙
1. **Contact**: partnerships@almosafer.com
2. **Mention**: You have an Umrah travel platform (MadinaGPT)
3. **Negotiate**: 10-15% commission (higher than general travel)
4. **Get partner ID**: Add to `.env`:
   ```bash
   ALMOSAFER_PARTNER_ID=your_partner_id_here
   ```

#### D. **Seera Partnership** (Saudi Arabia-based)
1. **Contact**: https://www.seera.sa/en/partnerships
2. **Negotiate**: 10-15% for Umrah bookings
3. **Add to .env**:
   ```bash
   SEERA_PARTNER_ID=your_partner_id_here
   ```

---

### **Option 3: Islamic Travel Aggregators** 🕋

These platforms specialize in Muslim travel and often have better Umrah deals + higher commissions.

#### HalalBooking Affiliate Program
1. **Sign up**: https://www.halalbooking.com/affiliate
2. **Commission**: 5-8%
3. **Add to .env**:
   ```bash
   HALALBOOKING_AFFILIATE_ID=your_ref_code_here
   ```

---

## Configuration (.env file)

Add these to your `/Users/yussufabdi/madinagpt/backend/.env` file:

```bash
# ============================================
# AFFILIATE TRACKING
# ============================================

# Booking.com
BOOKING_AFFILIATE_ID=123456

# Agoda
AGODA_AFFILIATE_ID=your_cid_here

# Hotels.com
HOTELS_AFFILIATE_ID=your_id_here

# Expedia
EXPEDIA_AFFILIATE_ID=your_id_here

# Skyscanner
SKYSCANNER_TRACKING_URL=https://skyscanner.net/g/aff?id=YOUR_ID

# Islamic/Umrah Sites (HIGHEST COMMISSIONS)
ALMOSAFER_PARTNER_ID=your_partner_id
SEERA_PARTNER_ID=your_partner_id
HALALBOOKING_AFFILIATE_ID=your_ref_code

# Travelpayouts (EASIEST - RECOMMENDED)
TRAVELPAYOUTS_MARKER=madinagpt
```

---

## How Affiliate Tracking Works in Code

### Backend Flow:
1. **Perplexity searches** → Returns deals with regular URLs
2. **Affiliate tracker intercepts** → Adds your tracking codes
3. **User sees tracked URL** → Clicks "Book Now"
4. **Booking completed** → Commission tracked to you

### Example:
```
Original URL from Perplexity:
https://booking.com/hotel/makkah-clock-tower

After affiliate tracking:
https://booking.com/hotel/makkah-clock-tower?aid=123456&label=madinagpt-umrah
                                            ^^^^^^^^ YOUR affiliate code
```

---

## Testing Your Affiliate Links

### 1. **Start the backend**:
```bash
cd /Users/yussufabdi/madinagpt/backend
python -m uvicorn app.main:app --reload
```

### 2. **Check the logs**:
When you search for deals, you'll see:
```
✅ Added affiliate tracking to booking.com
✅ Added affiliate tracking to agoda.com
⚠️ No affiliate config for google.com/flights
```

### 3. **Inspect URLs**:
- Open browser developer tools (F12)
- Search for deals
- Click "Book Now" and check the URL
- Verify your affiliate code is present

---

## Recommended Strategy

### **Phase 1: Start Simple** (Week 1)
1. Sign up for **Travelpayouts** only
2. Add your `TRAVELPAYOUTS_MARKER` to `.env`
3. Test with a few searches
4. Verify commissions are tracking

### **Phase 2: Add Direct Programs** (Week 2-4)
1. Apply to **Booking.com** affiliate program
2. Apply to **Agoda YCS**
3. Add affiliate IDs to `.env`
4. Higher commissions start flowing

### **Phase 3: Umrah Specialists** (Month 2+)
1. Contact **Almosafer** for partnership (10-15% commission)
2. Contact **Seera** for partnership
3. Sign up for **HalalBooking** affiliate
4. **BEST COMMISSIONS** for Umrah-specific bookings

---

## Expected Earnings Example

### Scenario: 100 bookings per month

| Platform | Bookings | Avg Booking | Commission Rate | Your Earnings |
|----------|----------|-------------|-----------------|---------------|
| Booking.com | 40 | $800 | 4% | $1,280 |
| Agoda | 20 | $600 | 6% | $720 |
| Almosafer | 30 | $1,200 | 12% | $4,320 |
| Seera | 10 | $1,000 | 12% | $1,200 |
| **TOTAL** | **100** | - | - | **$7,520/mo** |

**Annual projection**: $90,240/year (before Masjid donation)

After 50% donation to Masjid Madina: **$45,120/year to you + $45,120 to Masjid** 💚

---

## Compliance & Best Practices

### ✅ DO:
- Disclose affiliate relationships (add to Terms of Service)
- Track conversions in analytics
- Test affiliate links regularly
- Monitor commission reports monthly

### ❌ DON'T:
- Click your own affiliate links (violates TOS)
- Promise specific prices (Perplexity shows real-time data)
- Use misleading marketing
- Violate partner program terms

---

## Tracking & Analytics

The system logs all affiliate clicks to help you track performance:

```python
📊 Tracked booking click: Makkah Clock Tower - $450
📊 Tracked booking click: Emirates Flight - $890
```

### Recommended Dashboard:
- **Travelpayouts Dashboard**: All-in-one tracking
- **Booking.com Partner Center**: Detailed hotel booking analytics
- **Google Analytics**: Track user behavior before booking

---

## Troubleshooting

### "⚠️ Affiliate ID not set for booking.com"
**Solution**: Add your affiliate ID to `.env`:
```bash
BOOKING_AFFILIATE_ID=your_id_here
```

### "⚠️ No affiliate config for example.com"
**Solution**: The site doesn't have affiliate setup yet. Either:
1. Add config to `affiliate_tracker.py`
2. Or the site doesn't offer affiliate programs

### No commissions showing up
**Check**:
1. Affiliate IDs are correct in `.env`
2. You've been approved by affiliate programs
3. Cookies are enabled (needed for tracking)
4. 30-60 day delay for commission reporting

---

## Support

For affiliate program support:
- **Travelpayouts**: support@travelpayouts.com
- **Booking.com**: affiliaterelations@booking.com
- **Almosafer**: partnerships@almosafer.com
- **MadinaGPT**: Your development team

---

## Summary

✅ **Perplexity finds all deals** (no individual APIs needed)
✅ **Automatic affiliate tracking** (your codes added to all URLs)
✅ **Multiple commission sources** (Booking.com, Agoda, Almosafer, etc.)
✅ **Higher commissions for Umrah** (10-15% from Islamic travel sites)
✅ **Support Masjid Madina** (50% of earnings)

**Start with Travelpayouts → Add direct programs → Focus on Umrah specialists for best results!**

Barakallahu feekum! 🌙
