import sqlite3
import pandas as pd
import os

# 1. Define your Excel file name here
excel_filename = 'Beverages Datasets.xlsx' 

if not os.path.exists(excel_filename):
    print(f"Error: Could not find '{excel_filename}' in the current folder.")
else:
    print(f"Found {excel_filename}. Loading data...")
    
    # 2. Load the dataset into Pandas using read_excel instead of read_csv
    df = pd.read_excel(excel_filename)
    
    # 3. Connect to the local SQLite database
    conn = sqlite3.connect("enterprise_data.db")
    
    # 4. Write the data to a SQL table named 'sales_data'
    df.to_sql("sales_data", conn, if_exists="replace", index=False)
    
    print("Success! Data loaded into the 'sales_data' table.")
    conn.close()