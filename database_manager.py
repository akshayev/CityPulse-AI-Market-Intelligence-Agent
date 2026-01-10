# Database Manager Module for Market Agent
# Handles interactions with Supabase (Cloud) and Excel (Local)

import os
import pandas as pd
from supabase import create_client, Client
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple

class DatabaseManager:
    """
    Manages data storage and retrieval operations for the application.
    Supports dual-write to Supabase (Cloud PostgreSQL) and local Excel export.
    """
    
    def __init__(self, url: Optional[str] = None, key: Optional[str] = None):
        """
        Initializes the DatabaseManager.

        Args:
            url (Optional[str]): Supabase Project URL. Defaults to env var SUPABASE_URL.
            key (Optional[str]): Supabase API Key. Defaults to env var SUPABASE_KEY.
        """
        # Allow passing creds or grabbing from environment
        self.url = url or os.environ.get("SUPABASE_URL")
        self.key = key or os.environ.get("SUPABASE_KEY")
        self.client: Optional[Client] = None
        
        if self.url and self.key:
            try:
                self.client = create_client(self.url, self.key)
                print("[*] Connected to Supabase!")
            except Exception as e:
                print(f"[-] Supabase connection error: {e}")
        else:
            print("[!] Warning: Supabase credentials (SUPABASE_URL, SUPABASE_KEY) not found.")
            print("    Running in 'Offline Mode' (Excel Only).")

    def save_data(self, data_list: List[Dict[str, Any]], upsert: bool = True) -> Tuple[bool, str]:
        """
        Save data to Supabase (if connected).

        Args:
            data_list (List[Dict[str, Any]]): List of shop data dictionaries.
            upsert (bool): If True, updates existing records based on unique keys.

        Returns:
            Tuple[bool, str]: Success status and message.
        """
        if not data_list:
            return False, "No data to save"
            
        # 1. Save to Cloud (if applicable)
        if self.client:
            print(f"[*] Uploading {len(data_list)} records to Supabase...")
            try:
                # Assuming table name 'shops'
                if upsert:
                    self.client.table("shops").upsert(data_list).execute()
                else:
                    self.client.table("shops").insert(data_list).execute()
                print("[+] Cloud upload successful.")
            except Exception as e:
                print(f"[-] Cloud upload failed: {e}")
                return False, str(e)
        
        return True, "Success"

    def export_from_cloud_to_excel(self, filename: Optional[str] = None) -> Optional[str]:
        """
        Fetches all data from the Supabase 'shops' table and saves it to an Excel file.

        Args:
            filename (Optional[str]): Custom filename. Defaults to timestamped name.

        Returns:
            Optional[str]: The path to the created Excel file, or None if failed.
        """
        if not self.client:
            print("[-] Cannot export from cloud: No connection.")
            return None
            
        print("[*] Fetching data from Supabase...")
        try:
            # Fetch all rows 
            # Note: Supabase limits rows by default; massive datasets require pagination.
            response = self.client.table("shops").select("*").execute()
            data = response.data
            
            if not data:
                print("[-] Cloud DB is empty.")
                return None
                
            df = pd.DataFrame(data)
            
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"Cloud_Export_{timestamp}.xlsx"
                
            df.to_excel(filename, index=False)
            print(f"[+] Exported cloud data to {filename}")
            return filename
            
        except Exception as e:
            print(f"[-] Export failed: {e}")
            return None
