# Streamlit Dashboard for CityPulse AI
# Visualizes retail data, runs live scrapes, and provides AI-driven market analysis

import streamlit as st
import pandas as pd
import plotly.express as px
import os
import glob
from datetime import datetime
from dotenv import load_dotenv
from typing import Optional, List

# Local modules

from scraper import scrape_with_serpapi, scrape_with_selenium
from database_manager import DatabaseManager

# Load environment variables
load_dotenv()

# Page Configuration
st.set_page_config(page_title="CityPulse AI: Market Intelligence", layout="wide", page_icon="🏙️")

def load_data(file_path: str) -> pd.DataFrame:
    """Loads Excel data into a Pandas DataFrame."""
    try:
        return pd.read_excel(file_path)
    except Exception as e:
        st.error(f"Error loading file: {e}")
        return pd.DataFrame()

def main() -> None:
    """Main function for the Streamlit Dashboard."""
    
    st.title("🏙️ CityPulse AI")
    st.markdown("### Real-time Market Intelligence Agent")

    # Sidebar - Configuration
    st.sidebar.header("🔌 Configuration")
    
    # -------------------------------------------------------------------------
    # SECRETS MANAGEMENT
    # -------------------------------------------------------------------------
    # We attempt to load secrets from Streamlit Cloud's `st.secrets` first.
    # If falling back to local run, we check environment variables (.env).
    # This checks prevents crashes on local machines without secrets.toml.
    
    default_gemini_key = ""
    default_serp_key = ""
    
    # helper for safely accessing secrets
    def get_secret(key_name):
        try:
            return st.secrets[key_name] if key_name in st.secrets else os.getenv(key_name)
        except:
            return os.getenv(key_name)

    default_serp_key = get_secret("SERPAPI_KEY") or ""
    
    # Allow user to override keys in the UI (good for demos)
    api_key_serp = st.sidebar.text_input("SerpApi Key", value=default_serp_key, type="password")
    
    supabase_url = get_secret("SUPABASE_URL")
    supabase_key = get_secret("SUPABASE_KEY")

    # --- SECTION 1: LIVE SCRAPER ---
    with st.expander("🔍 **Start New Scrape**", expanded=True):
        col_city, col_type = st.columns(2)
        with col_city:
            target_city = st.text_input("Target City", placeholder="e.g. Kochi")
        with col_type:
            target_category = st.text_input("Category (Optional)", placeholder="e.g. Textil Shops. Leave empty for Full Scan.")
            
        use_serp = st.checkbox("Use SerpApi (Fast & Accurate)", value=True, help="Requires API Key. Uncheck for Selenium (Slower).")
        
        if st.button("🚀 Launch Agent"):
            if not target_city:
                st.warning("Please enter a City Name.")
            else:
                with st.spinner(f"Agent is scanning {target_city}... This may take a moment."):
                    # 1. Define Queries
                    queries = []
                    if target_category:
                        queries = [f"{target_category} in {target_city}"]
                    else:
                        base_categories = ["Supermarkets", "Textile Shops", "Electronics Stores", "Restaurants", "Gyms"] 
                        queries = [f"{cat} in {target_city}" for cat in base_categories]
                    
                    # 2. Run Scraper
                    scraped_data = []
                    if use_serp:
                        if not api_key_serp:
                            st.error("SerpApi Key missing!")
                        else:
                            scraped_data = scrape_with_serpapi(api_key_serp, queries, target_city)
                    else:
                        # Fallback to Selenium
                        st.info("Using local browser (Selenium)...")
                        scraped_data = scrape_with_selenium(queries)
                        
                    # 3. Save & Process
                    if scraped_data:
                        # Save Local
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"{target_city}_{timestamp}.xlsx"
                        pd.DataFrame(scraped_data).to_excel(filename, index=False)
                        
                        # Save Cloud
                        db = DatabaseManager(supabase_url, supabase_key)
                        db.save_data(scraped_data)
                        
                        # UPDATE SESSION STATE (Critical for Privacy)
                        st.session_state['scraped_data'] = pd.DataFrame(scraped_data)
                        
                        st.success(f"Success! Found {len(scraped_data)} shops. Data saved to {filename}")
                        # Rerun to update the dashboard below immediately
                        st.rerun() 
                    else:
                        st.error("No data found or scraping failed.")

    st.divider()

    # --- SECTION 2: ANALYSIS DASHBOARD ---
    
    # Check Session State instead of File System
    if 'scraped_data' not in st.session_state or st.session_state['scraped_data'].empty:
        st.info("👋 Welcome! The dashboard is empty. Use the **'Start New Scrape'** section above to launch the agent.")
        st.caption("Your search results will appear here properly isolated to your session.")
        return

    # Load data from memory
    df = st.session_state['scraped_data']
    selected_file = "Live_Session_Data" # Placeholder name for display logic

    tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "🗺️ Map Analysis", "💼 Lead Generator"])
    
    # --- TAB 1: DASHBOARD ---
    with tab1:
        st.subheader(f"Insights for: Current Session")
        
        col1, col2, col3 = st.columns(3)
        
        total_shops = len(df)
        
        # Calculate Average Rating safely
        avg_rating = 0.0
        if 'Rating' in df.columns:
            valid_ratings = df[df['Rating'] != 'N/A']['Rating']
            valid_ratings = pd.to_numeric(valid_ratings, errors='coerce').dropna()
            if not valid_ratings.empty:
                avg_rating = valid_ratings.mean()
            
        # Determine Highest Rated Category
        top_category = "N/A"
        if 'Shop Type' in df.columns and 'Rating' in df.columns:
            cat_ratings = df[df['Rating'] != 'N/A'].copy()
            cat_ratings['Rating'] = pd.to_numeric(cat_ratings['Rating'], errors='coerce')
            if not cat_ratings.empty:
                best_cat = cat_ratings.groupby('Shop Type')['Rating'].mean().idxmax()
                top_rating = cat_ratings.groupby('Shop Type')['Rating'].mean().max()
                top_category = f"{best_cat} ({top_rating:.1f}⭐)"
        
        col1.metric("Total Shops Scraped", total_shops)
        col2.metric("Average Rating", f"{avg_rating:.2f}")
        col3.metric("Best Rated Sector", top_category)
        
        # Charts
        col_charts1, col_charts2 = st.columns(2)
        with col_charts1:
            if 'Shop Type' in df.columns:
                fig_cat = px.pie(df, names='Shop Type', title="Category Distribution (Sampled)", hole=0.4)
                st.plotly_chart(fig_cat, use_container_width=True)
        with col_charts2:
            if 'Rating' in df.columns:
                current_valid_ratings = df[df['Rating'] != 'N/A'].copy()
                current_valid_ratings['Rating'] = pd.to_numeric(current_valid_ratings['Rating'], errors='coerce')
                fig_hist = px.histogram(current_valid_ratings, x="Rating", nbins=10, title="Rating Distribution", color_discrete_sequence=['#4CAF50'])
                st.plotly_chart(fig_hist, use_container_width=True)
        
        # Market Intelligence
        st.divider()
        st.subheader("⚡ Instant Market Intelligence")
        
        if st.button("Generate Market Analysis"):
            with st.spinner("Analyzing data patterns..."):
                # Recalculate for report (ensuring scope)
                cat_ratings = df[df['Rating'] != 'N/A'].copy()
                cat_ratings['Rating'] = pd.to_numeric(cat_ratings['Rating'], errors='coerce')
                best_sector = "N/A"
                best_rating = 0.0
                if not cat_ratings.empty:
                    best_sector = cat_ratings.groupby('Shop Type')['Rating'].mean().idxmax()
                    best_rating = cat_ratings.groupby('Shop Type')['Rating'].mean().max()
                
                df['Reviews'] = pd.to_numeric(df['Reviews'], errors='coerce').fillna(0)
                most_reviews = "N/A"
                total_reviews = 0
                if not df.empty:
                    most_reviews = df.groupby('Shop Type')['Reviews'].sum().idxmax()
                    total_reviews = df.groupby('Shop Type')['Reviews'].sum().max()
                
                counts = df['Shop Type'].value_counts()
                rare_sector = "N/A"
                if not counts.empty:
                    rare_sector = counts.idxmin()
                
                report = f"""
                ### 📢 Executive Summary
                Based on the {total_shops} businesses analyzed in **this session**:
                #### 🏆 Top Performer: {best_sector}
                *   **Average Rating:** {best_rating:.1f}/5.0
                #### 🔥 Most Popular: {most_reviews}
                *   **Total Online Reviews:** {int(total_reviews)}
                #### 💎 Niche Opportunity: {rare_sector}
                *   **Low Competition:** Only {counts.min() if not counts.empty else 0} shops found.
                """
                st.markdown(report)
                st.success("Analysis Complete")

    # --- TAB 2: MAP ---
    with tab2:
        st.subheader("📍 Business Locations")
        if 'latitude' in df.columns and 'longitude' in df.columns:
            map_df = df.dropna(subset=['latitude', 'longitude'])
            if not map_df.empty:
                st.map(map_df)
                st.caption(f"Showing {len(map_df)} locations based on SerpApi data.")
            else:
                st.warning("No GPS coordinates available in this dataset. (Try running a new scrape with SerpApi)")
        else:
            st.info("GPS columns missing. Please run a new scrape to capture location data.")

    # --- TAB 3: LEADS ---
    with tab3:
        st.subheader("🎯 Lead Generation (Missing Digital Presence)")
        st.caption("Businesses with missing Website or Phone are high-potential leads for Digital Marketing services.")
        
        # 1. Standardize missing values
        df_leads = df.copy()
        df_leads['Website'] = df_leads['Website'].fillna("N/A").astype(str).str.strip()
        df_leads['Phone'] = df_leads['Phone'].fillna("N/A").astype(str).str.strip()
        
        # 2. Filter rows where Website OR Phone is "N/A" or "nan" or empty
        leads_mask = (
            (df_leads['Website'] == 'N/A') | 
            (df_leads['Website'] == 'nan') | 
            (df_leads['Website'] == '') |
            (df_leads['Phone'] == 'N/A') | 
            (df_leads['Phone'] == 'nan') | 
            (df_leads['Phone'] == '')
        )
        
        leads_df = df[leads_mask] # Use original DF to preserve other columns if needed
        
        if leads_df.empty:
            st.info("Good news! All businesses in this dataset have a Website and Phone number. (Or the data is fully populated).")
        else:
            st.metric("Potential Leads Found", len(leads_df))
            st.dataframe(leads_df)
            
            csv = leads_df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Leads (CSV)", csv, "potential_leads.csv", "text/csv")
        
    # --- RAW DATA ---
    st.divider()
    with st.expander("📂 View Raw Data"):
        st.dataframe(df)

if __name__ == "__main__":
    main()
