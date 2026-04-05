"""
ArgoFloats CSV to SQLite Converter
Converts the large ARGO CSV into an indexed SQLite database for efficient querying
"""

import sqlite3
import pandas as pd
import os
from datetime import datetime

DB_PATH = 'data/argo.db'
CSV_PATH = 'data/ArgoFloats_6d62_a128_cc74.csv'

def create_database():
    """Create SQLite database from CSV in chunks"""
    
    print(f"Starting conversion... {datetime.now().strftime('%H:%M:%S')}")
    
    # Remove existing database
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"Removed existing database")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create table with proper schema
    cursor.execute("""
        CREATE TABLE argo_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            time TEXT NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            pressure REAL,
            temperature REAL,
            salinity REAL,
            platform_number TEXT
        )
    """)
    
    # Read and insert in chunks
    chunk_size = 50000
    total_rows = 0
    
    print(f"Reading CSV and loading into database...")
    print(f"File: {CSV_PATH}")
    
    try:
        # Read CSV with correct headers (row 0 is header, row 1 is units, data starts at row 2)
        for chunk_idx, chunk in enumerate(pd.read_csv(
            CSV_PATH, 
            skiprows=1,  # Skip units row
            chunksize=chunk_size,
            dtype={
                'time': str,
                'latitude': float,
                'longitude': float,
                'pres': float,
                'temp': float,
                'psal': float,
                'platform_number': str
            }
        )):
            # Rename columns to match table schema
            chunk.columns = ['time', 'latitude', 'longitude', 'pressure', 
                           'temperature', 'salinity', 'platform_number']
            
            # Drop rows with NaN in critical columns
            chunk = chunk.dropna(subset=['time', 'latitude', 'longitude'])
            
            # Insert into database
            chunk.to_sql('argo_data', conn, if_exists='append', index=False)
            
            total_rows += len(chunk)
            
            if (chunk_idx + 1) % 10 == 0:
                print(f"  Processed {total_rows:,} rows... ({datetime.now().strftime('%H:%M:%S')})")
        
        # Create indexes for faster queries
        print(f"\nCreating indexes...")
        cursor.execute("CREATE INDEX idx_latitude ON argo_data(latitude)")
        cursor.execute("CREATE INDEX idx_longitude ON argo_data(longitude)")
        cursor.execute("CREATE INDEX idx_time ON argo_data(time)")
        cursor.execute("CREATE INDEX idx_platform ON argo_data(platform_number)")
        cursor.execute("CREATE INDEX idx_temp ON argo_data(temperature)")
        cursor.execute("CREATE INDEX idx_sal ON argo_data(salinity)")
        
        conn.commit()
        
        # Get statistics
        stats = cursor.execute("SELECT COUNT(*) FROM argo_data").fetchone()[0]
        print(f"\n✅ Database created successfully!")
        print(f"   Total records: {stats:,}")
        print(f"   Database size: {os.path.getsize(DB_PATH) / 1024 / 1024 / 1024:.2f} GB")
        print(f"   Location: {os.path.abspath(DB_PATH)}")
        
        # Sample query
        sample = cursor.execute(
            "SELECT COUNT(*) FROM argo_data WHERE temperature > 20 AND salinity > 34"
        ).fetchone()[0]
        print(f"   Sample query: {sample:,} records with temp > 20°C and salinity > 34")
        
    except Exception as e:
        print(f"❌ Error during conversion: {e}")
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    create_database()
    print(f"\nDone! {datetime.now().strftime('%H:%M:%S')}")
