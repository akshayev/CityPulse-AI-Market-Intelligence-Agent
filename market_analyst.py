# Market Analysis Module for Changanasherry Market Agent
# Handles AI analysis via Google Gemini and Report Generation

import google.generativeai as genai
import pandas as pd
import os
import json
from fpdf import FPDF
from datetime import datetime
from typing import Optional, Dict, Any, Union

class PDFReport(FPDF):
    """
    Custom PDF class extending FPDF to add Header and Footer.
    """
    def header(self) -> None:
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Market Intelligence Report', 0, 1, 'C')
        self.ln(10)

    def footer(self) -> None:
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def generate_json_output(analysis_text: str, raw_data_summary: str) -> str:
    """
    Generates a structured JSON output file containing the analysis and data summary.

    Args:
        analysis_text (str): The AI-generated analysis text.
        raw_data_summary (str): The raw data context used for analysis.

    Returns:
        str: The filename of the generated JSON report.
    """
    output = {
        "timestamp": datetime.now().isoformat(),
        "analysis": analysis_text,
        "data_summary": raw_data_summary
    }
    
    filename = f"Market_Analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(output, f, indent=4)
        
    print(f"[+] JSON Report saved to: {filename}")
    return filename

def generate_pdf_report(analysis_text: str, raw_data_summary: str) -> str:
    """
    Generates a professionally formatted PDF report.

    Args:
        analysis_text (str): The AI-generated analysis text.
        raw_data_summary (str): The raw data context used for analysis.

    Returns:
        str: The filename of the generated PDF report.
    """
    pdf = PDFReport()
    pdf.add_page()
    
    # Meta Info
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=1, align='L')
    pdf.ln(10)
    
    # Analysis Section
    pdf.set_font("Arial", 'B', size=14)
    pdf.cell(200, 10, txt="AI Analysis", ln=1, align='L')
    pdf.set_font("Arial", size=11)
    
    # Sanitize text for FPDF (Latin-1 encoding limit)
    safe_text = analysis_text.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 10, txt=safe_text)
    pdf.ln(10)
    
    # Data Summary Section
    pdf.set_font("Arial", 'B', size=14)
    pdf.cell(200, 10, txt="Data Summary", ln=1, align='L')
    pdf.set_font("Courier", size=10)
    
    safe_data = raw_data_summary.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 10, txt=safe_data)
    
    filename = f"Market_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf.output(filename)
    
    print(f"[+] PDF Report saved to: {filename}")
    return filename

def analyze_market_data(api_key: str, excel_file: str) -> str:
    """
    Analyzes shop data using Google Gemini AI.

    Args:
        api_key (str): Google Gemini API Key.
        excel_file (str): Path to the Excel file containing shop data.

    Returns:
        str: The raw text of the AI analysis.
    """
    print(f"[*] Analyzing {excel_file} with Gemini AI...")
    
    # 1. Configure Gemini
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-pro')
    
    # 2. Load Data
    try:
        df = pd.read_excel(excel_file)
    except Exception as e:
        return f"Error reading file: {e}"
        
    # 3. Summarize Data Context
    total_shops = len(df)
    
    # Handle empty or malformed data gracefully
    if 'Shop Type' in df.columns:
        categories = df['Shop Type'].value_counts().to_string()
    else:
        categories = "N/A"
        
    if 'Rating' in df.columns and not df.empty:
        top_rated = df[df['Rating'] != 'N/A'].sort_values(by='Rating', ascending=False).head(5)[['Shop Name', 'Rating']].to_string()
    else:
        top_rated = "N/A"
    
    data_context = f"""
    Total Shops scraped: {total_shops}
    
    Category Breakdown:
    {categories}
    
    Top Rated Shops:
    {top_rated}
    """ 
    
    # 4. Construct Prompt
    prompt = f"""
    Act as a Market Intelligence Analyst. 
    Here is a summary of retail data scraped from the city:
    
    {data_context}
    
    Please provide a comprehensive market analysis report.
    Include:
    1. Executive Summary
    2. Category Density Analysis (Which businesses are oversaturated?)
    3. Opportunity Gaps (What businesses are missing?)
    4. Strategic Recommendations for a new investor.
    
    Format the output clearly with headers.
    """
        
    # 5. Generate Response
    print("    Sending prompt to Gemini... (This may take a few seconds)")
    try:
        response = model.generate_content(prompt)
        analysis_text = response.text
        
        # 6. Generate Outputs (Side Effects)
        generate_json_output(analysis_text, data_context)
        generate_pdf_report(analysis_text, data_context)
        
        return analysis_text
        
    except Exception as e:
        return f"AI Error: {e}"
