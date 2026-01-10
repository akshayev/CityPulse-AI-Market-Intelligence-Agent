# Scraper Module for Changanasherry Market Agent
# Handles data extraction via SerpApi and Selenium

import requests
import time
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from typing import List, Dict, Any, Optional

# =============================================================================
# CONSTANTS
# =============================================================================

SERPAPI_URL = "https://serpapi.com/search.json"

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def extract_shop_type(query: str) -> str:
    """
    Extracts the shop type from a search query string.

    Args:
        query (str): The search query (e.g., "textile shops in changanasherry").

    Returns:
        str: The extracted shop category (e.g., "Textile Shops").
    """
    words = query.split()
    if len(words) > 2 and "in" in words:
        return " ".join(words[:words.index("in")]).title()
    return query.title()

# =============================================================================
# OPTION 1: SERPAPI (RECOMMENDED)
# =============================================================================

def scrape_with_serpapi(api_key: str, queries: List[str], location_name: str) -> List[Dict[str, Any]]:
    """
    Scrapes shop data using the SerpApi Google Maps Engine.

    Args:
        api_key (str): Your SerpApi API Key.
        queries (List[str]): List of search queries.
        location_name (str): The target location name.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries, where each dictionary represents a shop.
    """
    print(f"[*] Scraping {len(queries)} categories in {location_name} using SerpApi...")
    
    shops_data: List[Dict[str, Any]] = []
    
    for query in queries:
        print(f"  - Searching for: {query}")
        try:
            params = {
                "q": query,
                "api_key": api_key,
                "engine": "google_maps",
                "type": "search",
            }
            
            response = requests.get(SERPAPI_URL, params=params, timeout=10)
            response.raise_for_status()
            results = response.json()
            
            if "local_results" in results:
                for place in results["local_results"]:
                    title = place.get("title", "N/A")
                    
                    # Avoid duplicates
                    if any(s['Shop Name'] == title for s in shops_data):
                        continue
                        
                    shop = {
                        "Shop Name": title,
                        "Shop Type": extract_shop_type(query),
                        "Rating": place.get("rating", "N/A"),
                        "Reviews": place.get("reviews", 0),
                        "Address": place.get("address", "N/A"),
                        "Phone": place.get("phone", "N/A"),
                        "Website": place.get("website", "N/A"),
                        "Open Status": place.get("open_state", "N/A"),
                        "Source": "SerpApi"
                    }
                    shops_data.append(shop)
            
            # Rate limiting
            time.sleep(1)
            
        except requests.exceptions.RequestException as e:
            print(f"Network error scraping {query}: {e}")
        except Exception as e:
            print(f"Error scraping {query}: {e}")
            
    return shops_data

# =============================================================================
# OPTION 2: SELENIUM (FREE FALLBACK)
# =============================================================================

def scrape_with_selenium(queries: List[str]) -> List[Dict[str, Any]]:
    """
    Scrapes shop data using Selenium WebDriver (Chrome).

    Args:
        queries (List[str]): List of search queries.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries representing shops.
    """
    print("[*] Scraping using Selenium (Google Maps)...")
    
    shops_data: List[Dict[str, Any]] = []
    
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    # options.add_argument("--headless") # Uncomment for headless mode
    
    driver = None
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    except Exception as e:
        print(f"Error initializing Chrome driver: {e}")
        return []

    try:
        for query in queries:
            url = f"https://www.google.com/maps/search/{query.replace(' ', '+')}"
            driver.get(url)
            time.sleep(5) # Wait for page load
            
            print(f"  - extracting results for {query}...")
            
            elements = driver.find_elements(By.CSS_SELECTOR, "div[role='article']")
            
            for elem in elements:
                try:
                    text = elem.text.split('\n')
                    if len(text) > 0:
                        name = text[0]
                        rating = "N/A"
                        shop_type = "N/A"
                        
                        if len(text) > 1:
                            line2 = text[1]
                            if str(line2)[0].isdigit() or str(line2)[0] == '(': 
                                rating = line2
                            else:
                                shop_type = line2
                        
                        shop = {
                            "Shop Name": name,
                            "Shop Type": shop_type,
                            "Rating": rating,
                            "Reviews": "N/A",
                            "Address": "Available on click", 
                            "Phone": "N/A",
                            "Website": "N/A",
                            "Open Status": "N/A", 
                            "Source": "Selenium"
                        }
                        shops_data.append(shop)
                except Exception:
                    continue
                    
    except Exception as e:
        print(f"Selenium runtime error: {e}")
    finally:
        if driver:
            driver.quit()
        
    return shops_data