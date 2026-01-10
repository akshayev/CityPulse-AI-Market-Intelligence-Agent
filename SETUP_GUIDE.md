# Alappuzha Shops Data Scraper - Complete Setup Guide

## Overview
This Python script scrapes shop data from Alappuzha with accurate ratings, shop types, and contact information. The data is automatically organized and exported to a formatted Excel file.

## Installation & Setup

### Step 1: Install Python
Download Python 3.8+ from: https://www.python.org/downloads/

### Step 2: Install Required Libraries
Open Command Prompt/Terminal and run:

```bash
pip install selenium beautifulsoup4 pandas openpyxl requests webdriver-manager
```

Or if you want to install from requirements.txt:

```bash
pip install -r requirements.txt
```

**requirements.txt content:**

```text
selenium==4.15.2
beautifulsoup4==4.12.2
pandas==2.1.3
openpyxl==3.1.2
requests==2.31.0
webdriver-manager==4.0.1
```

## Configuration & Usage

### Option 1: Using SerpApi (RECOMMENDED - Most Accurate)
**Advantages:**
- ✅ Most accurate data with verified ratings
- ✅ Includes phone numbers, websites, hours
- ✅ Faster scraping
- ✅ No blocking issues

**Steps:**
1. Go to https://serpapi.com
2. Sign up (Free account gives 100 requests/month)
3. Copy your API key from the dashboard
4. Run the script and enter your API key when prompted

**Command:**
```bash
python alappuzha_scraper.py
```
Then select option 1 and paste your API key.

### Option 2: Using Selenium (No API Key Required)
**Advantages:**
- ✅ No API key needed
- ✅ Uses browser automation
- ✅ Can scrape directly from Google Maps

**Disadvantages:**
- Slower than API
- Requires more system resources
- May get rate limited

**Command:**
```bash
python alappuzha_scraper.py
```
Select option 2

### Option 3: Using JustDial (Limited Data)
**Advantages:**
- Local business directory
- Has ratings and reviews

**Disadvantages:**
- Often blocked by JustDial
- Limited data extraction
- Not recommended - Use option 1 or 2 instead

### Option 4: Combined Approach (Best Results)
Scrapes from multiple sources for comprehensive coverage.
