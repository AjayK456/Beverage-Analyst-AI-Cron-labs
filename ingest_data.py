import pandas as pd
import sqlite3
import os

# 1. Configuration
EXCEL_FILE = "Beverages Datasets.xlsx"
DB_FILE = "enterprise_data.db"

def load_excel_to_sqlite():
    if not os.path.exists(EXCEL_FILE):
        print(f"Error: {EXCEL_FILE} not found in the folder!")
        return

    print(f"Reading {EXCEL_FILE}...")
    # Load all sheets into a dictionary of DataFrames
    excel_data = pd.read_excel(EXCEL_FILE, sheet_name=None)
    
    # Connect to (or create) the database
    conn = sqlite3.connect(DB_FILE)
    
    for sheet_name, df in excel_data.items():
        # Clean sheet names for SQL (replace spaces with underscores)
        table_name = sheet_name.lower().replace(" ", "_")
        
        # Write to SQL
        df.to_sql(table_name, conn, if_exists="replace", index=False)
        print(f"✅ Loaded sheet '{sheet_name}' into table '{table_name}' ({len(df)} rows)")

    conn.close()
    print("\nDatabase updated successfully with your beverage data!")

if __name__ == "__main__":
    load_excel_to_sqlite()