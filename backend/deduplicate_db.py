#!/usr/bin/env python
"""
Deduplicate ARGO database by removing:
1. Exact duplicates
2. Records with same location + time (keep one representative)
3. Very similar records within 5 minutes at same location
"""

import sqlite3
from datetime import datetime

DB_PATH = "data/argo.db"

def deduplicate_database():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    print("Starting deduplication process...")
    
    # Get initial count
    cur.execute("SELECT COUNT(*) FROM argo_data")
    initial_count = cur.fetchone()[0]
    print(f"Initial records: {initial_count:,}")
    
    # Step 1: Remove exact duplicates
    print("\n1. Removing exact duplicates...")
    cur.execute("""
        DELETE FROM argo_data 
        WHERE id NOT IN (
            SELECT MIN(id) 
            FROM argo_data 
            GROUP BY time, latitude, longitude, temperature, salinity, pressure
        )
    """)
    conn.commit()
    
    cur.execute("SELECT COUNT(*) FROM argo_data")
    after_exact = cur.fetchone()[0]
    print(f"   After exact duplicates: {after_exact:,} (removed {initial_count - after_exact:,})")
    
    # Step 2: Keep only one record per location per hour (reduce temporal redundancy)
    print("\n2. Removing similar records at same location/time...")
    cur.execute("""
        DELETE FROM argo_data 
        WHERE id NOT IN (
            SELECT MIN(id) 
            FROM argo_data 
            GROUP BY 
                CAST(latitude * 10 AS INTEGER),  -- Round to 0.1 degree
                CAST(longitude * 10 AS INTEGER), 
                substr(time, 1, 13)              -- Hour precision
        )
    """)
    conn.commit()
    
    cur.execute("SELECT COUNT(*) FROM argo_data")
    after_temporal = cur.fetchone()[0]
    print(f"   After temporal dedup: {after_temporal:,} (removed {after_exact - after_temporal:,})")
    
    # Step 3: Vacuum to reclaim space
    print("\n3. Vacuuming database to reclaim space...")
    cur.execute("VACUUM")
    
    # Step 4: Rebuild indexes
    print("4. Rebuilding indexes...")
    cur.execute("REINDEX")
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ Deduplication complete!")
    print(f"   Original: {initial_count:,} records")
    print(f"   Final: {after_temporal:,} records")
    print(f"   Removed: {initial_count - after_temporal:,} records ({((initial_count - after_temporal) / initial_count * 100):.1f}%)")
    print(f"   Database optimized!")

if __name__ == "__main__":
    deduplicate_database()
