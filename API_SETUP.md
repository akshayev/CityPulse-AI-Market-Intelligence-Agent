# API Setup Instructions - SerpApi

## 🔑 Why Use SerpApi?

**Best Results Guaranteed:**
- ✅ Most accurate data
- ✅ Includes phone numbers, websites, hours
- ✅ Fastest scraping (3-5 seconds per query)
- ✅ No blocking issues
- ✅ Verified customer ratings
- ✅ Free tier available (100 requests/month)

---

## 📋 Step-by-Step Setup (2 minutes)

### Step 1: Sign Up

1. Go to: **https://serpapi.com/signup**
2. Click "Sign Up"
3. Enter your email
4. Verify email (check inbox/spam)
5. Create password
6. Click "Create Account"

### Step 2: Get Your API Key

1. After signup, you'll be on dashboard
2. Look for "API Key" section
3. Copy your key (looks like: `abc123def456ghi789...`)
4. Keep it safe!

### Step 3: Check Your Plan

1. Go to "Billing" section
2. Free plan: **100 requests/month**
3. Paid plans start at **$10/month** (10,000 requests)
4. No credit card needed for free tier

### Step 4: Use in Script

When you run:
```bash
python alappuzha_scraper.py
```

Choose option **1** when prompted, then paste your API key.

---

## 🧪 Test Your API Key

### Quick Test (Optional):

```python
import requests

api_key = "YOUR_API_KEY_HERE"  # Replace with your key
url = "https://api.serpapi.com/search"

params = {
    "q": "coffee shops in alappuzha",
    "location": "Alappuzha, Kerala",
    "api_key": api_key,
    "engine": "google_maps"
}

response = requests.get(url, params=params)
results = response.json()

print(f"Found {len(results.get('place_results', []))} shops")
```

If you see shops, your API key works! ✅

---

## 💰 Understanding Quotas

### Free Plan (100 requests/month):
```
100 requests ÷ 10 shop types = ~10 results per type
Perfect for: Testing, small datasets, learning

Example queries (uses 10 requests):
- general stores alappuzha
- textile shops alappuzha
- electronics shops alappuzha
- pharmacies alappuzha
- cosmetics shops alappuzha
- grocery stores alappuzha
- restaurants alappuzha
- hardware shops alappuzha
- jewellery shops alappuzha
- clothing stores alappuzha
```

### Paid Plans:
```
$10/month = 10,000 requests
- Can run 1,000 different queries
- Perfect for: Comprehensive data, regular updates
- 333 requests per day

$50/month = 100,000 requests
- Can run 10,000 different queries
- Perfect for: Large-scale scraping, production
- 3,333 requests per day
```

---

## 🔒 Security Best Practices

### ❌ DON'T:
```python
# ❌ Bad: API key visible in code
api_key = "abc123def456ghi789"
url = f"https://api.serpapi.com/search?api_key={api_key}"
```

### ✅ DO:
```python
# ✅ Good: Use environment variables
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('SERPAPI_KEY')

if not api_key:
    print("Error: SERPAPI_KEY not found in .env file")
    exit()
```

### Setup .env File:

1. Create file `.env` in your project folder
2. Add this line:
   ```
   SERPAPI_KEY=your_actual_key_here
   ```
3. Add to `.gitignore`:
   ```
   .env
   *.pyc
   __pycache__/
   ```

### Modified Script Usage:
```bash
pip install python-dotenv
```

Then your script will safely read the key from `.env`

---

## 📊 API Response Example

When you use SerpApi, you get structured JSON data:

```json
{
  "place_results": [
    {
      "title": "Kerala Textile Store",
      "rating": 4.5,
      "review_count": 127,
      "address": "Main Road, Alappuzha, Kerala",
      "phone": "+91-9487654321",
      "website": "https://keralatextiles.com",
      "hours": "10:00 AM - 9:00 PM",
      "type": "Textile shop"
    },
    {
      "title": "Tech Hub Electronics",
      "rating": 4.8,
      "review_count": 213,
      "address": "Market Street, Alappuzha",
      "phone": "+91-9876543210",
      "website": "https://techhub.in",
      "hours": "10:00 AM - 8:30 PM",
      "type": "Electronics store"
    }
    // ... more results
  ],
  "search_parameters": {
    "q": "shops in alappuzha",
    "engine": "google_maps"
  }
}
```

Our script automatically extracts and formats this data into Excel!

---

## 🔄 Request/Response Cycle

```
Your Script
    ↓
SerpApi API
    ↓ (Queries Google Maps)
Google Maps
    ↓ (Returns results)
SerpApi API
    ↓ (Parses as JSON)
Your Script
    ↓ (Processes data)
Excel File
```

Each request = 1 API call (counts against your quota)

---

## ⚠️ Common Issues

### Issue: "Invalid API key"
**Solution:**
1. Copy key again carefully
2. Remove extra spaces
3. Regenerate key from dashboard if needed

### Issue: "Quota exceeded"
**Solution:**
1. Wait until next month (free plan)
2. Upgrade to paid plan
3. Use Selenium method instead (no API needed)

### Issue: "Connection timeout"
**Solution:**
1. Check internet connection
2. Try again after 10 seconds
3. Check SerpApi status: https://serpapi.com/status

### Issue: "No results returned"
**Solution:**
1. Check query spelling
2. Try simpler query like "shops alappuzha"
3. Verify location name (Kerala spelling)

---

## 📈 Monitoring Your Usage

### Check Quota:
1. Login to SerpApi dashboard
2. See "Requests used this month"
3. Click "Billing" for detailed breakdown
4. Track usage by date and engine

### Upgrade When Needed:
1. Go to "Billing" section
2. Click "Upgrade Plan"
3. Choose plan ($10, $50, $100+)
4. Add payment method
5. Instant activation!

---

## 🎯 Optimization Tips

### Reduce API Calls:
```python
# ❌ Bad: 100 API calls for 100 shops
for shop_id in range(1, 101):
    query = f"shop {shop_id} alappuzha"
    # Separate API call each time!

# ✅ Good: 1 API call for all shops
query = "shops alappuzha"
# Single API call returns multiple results!
```

### Batch Processing:
```python
# ✅ Good: Process multiple queries efficiently
shop_types = [
    "general stores",
    "textile shops",
    "electronics shops",
    # ... more types
]

for shop_type in shop_types:
    query = f"{shop_type} alappuzha"
    # 1 API call per type
```

### Cache Results:
```python
# ✅ Good: Save results to avoid re-scraping
import json

results = load_from_cache('shops_cache.json')
if not results:
    results = scrape_with_serpapi(api_key)
    save_to_cache('shops_cache.json', results)

# Next run uses cached data!
```

---

## 🔗 Useful Links

- **SerpApi Docs:** https://serpapi.com/docs
- **Google Maps API:** https://maps.google.com
- **API Key Dashboard:** https://serpapi.com/dashboard
- **Status Page:** https://serpapi.com/status
- **Support:** https://serpapi.com/support

---

## 💡 Pro Tips

1. **Free accounts reset monthly** - January 1st, February 1st, etc.
2. **Save API key securely** - Use .env file, not in code
3. **Test with small queries first** - Save quota for production
4. **Monitor usage regularly** - Check dashboard weekly
5. **Keep script efficient** - Reduce unnecessary API calls
6. **Use caching** - Avoid duplicate requests
7. **Set request limits** - Batch similar queries together

---

## ✅ Verification Checklist

Before running the main script:

- [ ] SerpApi account created
- [ ] API key copied
- [ ] API key tested (optional)
- [ ] .env file created (optional but recommended)
- [ ] requirements.txt installed
- [ ] No Python errors when importing
- [ ] Internet connection working
- [ ] API quota checked

---

**You're all set! 🎉**

Run the scraper anytime:
```bash
python alappuzha_scraper.py
```

Choose option 1 when prompted and paste your API key.

Need help? Check PROJECT_SUMMARY.md or SETUP_GUIDE.md
