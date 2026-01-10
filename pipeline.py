# Pipeline Controller Module for Changanasherry Market Agent
# Orchestrates the Scraping -> Data Engineering -> AI Analysis workflow

import os
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from typing import List, Optional

# Local Modules
# Note: 'scraper' module replaces the old 'alappuzha_scraper'
from scraper import scrape_with_serpapi, scrape_with_selenium
from database_manager import DatabaseManager
from market_analyst import analyze_market_data

# Load environment variables
load_dotenv()

def clear_screen() -> None:
    """Clears the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner() -> None:
    """Prints the application banner."""
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║   🛒  CITYPULSE AI - PIPELINE CONTROLLER             ║
    ╠══════════════════════════════════════════════════════════╣
    ║   [1] Run Full Cycle (Scrape -> Store -> Analyze)        ║
    ║   [2] Quick Scrape (Excel Only)                          ║
    ║   [3] Generate AI Report from Existing Data              ║
    ║   [4] Export Cloud Data to Excel                         ║
    ║   [Q] Quit                                               ║
    ╚══════════════════════════════════════════════════════════╝
    """)

def check_quota(estimated_usage: int) -> bool:
    """
    Displays a quota warning and asks for user confirmation.

    Args:
        estimated_usage (int): Number of API calls to be made.

    Returns:
        bool: True if confirmed, False otherwise.
    """
    print(f"\n[!] ⚠️  QUOTA WARNING: This action will consume ~{estimated_usage} searches.")
    confirm = input("    Proceed? (y/n): ").strip().lower()
    return confirm == 'y'

def run_pipeline() -> None:
    """
    Main loop for the pipeline controller CLI.
    """
    clear_screen()
    print_banner()
    
    # --- Configuration ---
    # Load from environment variables (Priority) or Input (Fallback)
    serp_key: str = os.getenv("SERPAPI_KEY") or input("Enter SerpApi Key (Press Enter to use existing from env): ").strip()
    gemini_key: str = os.getenv("GEMINI_KEY") or input("Enter Gemini API Key (For Analysis): ").strip()
    supabase_url: str = os.getenv("SUPABASE_URL") or input("Enter Supabase URL (Optional): ").strip()
    supabase_key: str = os.getenv("SUPABASE_KEY") or input("Enter Supabase Key (Optional): ").strip()
    
    if not serp_key:
        print("[!] Warning: No SerpApi Key provided. Option 1 will fail.")
        serp_key = ""

    db_manager = DatabaseManager(supabase_url, supabase_key)
    
    while True:
        choice = input("\nSelect Action: ").strip().lower()
        
        if choice == 'q':
            print("Goodbye!")
            break
            
        elif choice == '1':
            # --- FULL CYCLE ---
            location = input("\n[?] Target Location (e.g. Changanasherry): ").strip()
            category = input("[?] Target Category (e.g. Gyms). Leave empty for defaults: ").strip()
            
            # Quota Check and Query Construction
            queries: List[str] = []
            if category:
                queries = [f"{category} in {location}"]
                if not check_quota(1): continue
            else:
                base_categories = ["general stores", "textile shops", "electronics shops", "restaurants"] 
                queries = [f"{cat} in {location}" for cat in base_categories]
                if not check_quota(len(queries)): continue
            
            # 1. Scrape
            scraped_data = scrape_with_serpapi(serp_key, queries, location)
            
            if scraped_data:
                # 2. Store
                db_manager.save_data(scraped_data)
                
                # 3. Export to Excel (for Analyst)
                excel_file = f"{location}_{datetime.now().strftime('%Y%m%d')}.xlsx"
                pd.DataFrame(scraped_data).to_excel(excel_file, index=False)
                print(f"[+] Data saved locally to {excel_file}")
                
                # 4. Analyze
                if gemini_key:
                    analyze_market_data(gemini_key, excel_file)
                else:
                    print("[-] Skipping AI Analysis (No Gemini Key provided)")
                    
        elif choice == '3':
            # --- AI REPORT ONLY ---
            if not gemini_key:
                print("[-] Need Gemini Key to run analysis!")
                continue
                
            files = [f for f in os.listdir('.') if f.endswith('.xlsx')]
            if not files:
                print("[-] No valid Excel files found to analyze.")
                continue
                
            print("\nAvailable Files:")
            for i, f in enumerate(files):
                print(f"{i+1}. {f}")
                
            try:
                file_idx = int(input("Select file number: ")) - 1
                if 0 <= file_idx < len(files):
                    analyze_market_data(gemini_key, files[file_idx])
                else:
                    print("[-] Invalid selection.")
            except ValueError:
                print("[-] Invalid input.")

        elif choice == '4':
             # --- EXPORT FROM CLOUD ---
             db_manager.export_from_cloud_to_excel()

if __name__ == "__main__":
    run_pipeline()
