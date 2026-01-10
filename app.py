# Streamlit Dashboard for Changanasherry Market Agent
# Visualizes retail data and provides AI-driven market analysis

import streamlit as st
import pandas as pd
import plotly.express as px
import os
import glob
from dotenv import load_dotenv
from typing import Optional

# Local modules
from market_analyst import analyze_market_data

# Load environment variables
load_dotenv()

# Page Configuration
st.set_page_config(page_title="Market Intelligence Dashboard", layout="wide")

def load_data(file_path: str) -> pd.DataFrame:
    """
    Loads Excel data into a Pandas DataFrame.
    
    Args:
        file_path (str): Path to the .xlsx file.
        
    Returns:
        pd.DataFrame: Loaded data.
    """
    return pd.read_excel(file_path)

def main() -> None:
    """Main function for the Streamlit Dashboard."""
    
    st.title("🏙️ CityPulse AI: Changanasherry")
    st.markdown("Automated insights from retail data.")

    # Sidebar - Configuration
    st.sidebar.header("Configuration")
    
    # Auto-load key from secrets (Cloud) or env vars (Local)
    default_key = ""
    if "GEMINI_KEY" in st.secrets:
        default_key = st.secrets["GEMINI_KEY"]
    elif os.getenv("GEMINI_KEY"):
        default_key = os.getenv("GEMINI_KEY")
        
    api_key = st.sidebar.text_input("Gemini API Key", value=default_key, type="password")

    # File Selector Logic
    files = glob.glob("*.xlsx")
    
    if not files:
        st.warning("No data found. Run the scraper pipeline first!")
        return

    # Default to the most recent file
    latest_file = max(files, key=os.path.getctime)
    selected_file = st.sidebar.selectbox("Select Dataset", files, index=files.index(latest_file))
    
    if selected_file:
        df = load_data(selected_file)
        
        # --- KEY METRICS ---
        st.subheader("📊 Key Metrics")
        col1, col2, col3 = st.columns(3)
        
        total_shops = len(df)
        
        # Calculate Average Rating safely
        if 'Rating' in df.columns:
            valid_ratings = df[df['Rating'] != 'N/A']['Rating']
            # Convert to numeric, coercing errors to NaN
            valid_ratings = pd.to_numeric(valid_ratings, errors='coerce').dropna()
            avg_rating = valid_ratings.mean() if not valid_ratings.empty else 0.0
        else:
            avg_rating = 0.0
            
        # Determine Dominant Category safely
        if 'Shop Type' in df.columns and not df['Shop Type'].empty:
            top_category = df['Shop Type'].mode()[0]
        else:
            top_category = "N/A"
        
        col1.metric("Total Shops Scraped", total_shops)
        col2.metric("Average Rating", f"{avg_rating:.2f}")
        col3.metric("Dominant Category", top_category)
        
        # --- CHARTS ---
        col_charts1, col_charts2 = st.columns(2)
        
        with col_charts1:
            st.markdown("### Shop Distribution")
            if 'Shop Type' in df.columns:
                fig_cat = px.pie(df, names='Shop Type', title="Shops by Category", hole=0.4)
                st.plotly_chart(fig_cat, use_container_width=True)
            else:
                st.info("No 'Shop Type' column found.")
            
        with col_charts2:
            st.markdown("### Rating Analysis")
            if 'Rating' in df.columns:
                # Filter valid ratings for histogram
                current_valid_ratings = df[df['Rating'] != 'N/A'].copy()
                current_valid_ratings['Rating'] = pd.to_numeric(current_valid_ratings['Rating'], errors='coerce')
                
                fig_hist = px.histogram(
                    current_valid_ratings, 
                    x="Rating", 
                    nbins=10, 
                    title="Rating Distribution", 
                    color_discrete_sequence=['#4CAF50']
                )
                st.plotly_chart(fig_hist, use_container_width=True)
            else:
                st.info("No 'Rating' column found.")
            
        # --- AI ANALYSIS ---
        st.divider()
        st.subheader("🤖 AI Market Analyst")
        
        if st.button("Generate Intelligence Report"):
            if not api_key:
                st.error("Please enter a Gemini API Key in the sidebar or .env file.")
            else:
                with st.spinner("Analyzing market patterns..."):
                    report = analyze_market_data(api_key, selected_file)
                    st.success("Analysis Complete")
                    st.markdown(report)
                    
        # --- RAW DATA ---
        st.divider()
        with st.expander("📂 View Raw Data"):
            st.dataframe(df)

if __name__ == "__main__":
    main()
