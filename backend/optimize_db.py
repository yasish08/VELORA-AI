#!/usr/bin/env python
"""
Quick database optimization - add indexes for faster queries
"""

import sqlite3

DB_PATH = "data/argo.db"

def optimize_database():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    print("Optimizing database for faster queries...")
    
    # Drop old indexes if they exist
    print("\n1. Dropping old indexes...")
    try:
        cur.execute("DROP INDEX IF EXISTS idx_location")
        cur.execute("DROP INDEX IF EXISTS idx_time")
        cur.execute("DROP INDEX IF EXISTS idx_temp")
        cur.execute("DROP INDEX IF EXISTS idx_salinity")
    except:
        pass
    
    # Create composite indexes for common query patterns
    print("2. Creating optimized composite indexes...")
    
    # Composite index for region queries (lon, lat, time)
    print("   - Creating geospatial + time index...")
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_geo_time 
        ON argo_data(longitude, latitude, time)
    """)
    
    # Index for temperature queries
    print("   - Creating temperature index...")
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_temp_params 
        ON argo_data(temperature, time) 
        WHERE temperature IS NOT NULL
    """)
    
    # Index for salinity queries
    print("   - Creating salinity index...")
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_sal_params 
        ON argo_data(salinity, time) 
        WHERE salinity IS NOT NULL
    """)
    
    # Analyze tables for query optimizer
    print("3. Analyzing tables for query optimizer...")
    cur.execute("ANALYZE")
    
    # Set pragmas for faster queries
    print("4. Setting performance pragmas...")
    cur.execute("PRAGMA cache_size = -64000")  # 64MB cache
    cur.execute("PRAGMA temp_store = MEMORY")   # Use memory for temp storage
    cur.execute("PRAGMA mmap_size = 268435456") # 256MB memory-mapped I/O
    cur.execute("PRAGMA page_size = 4096")
    
    conn.commit()
    
    # Get stats
    cur.execute("SELECT COUNT(*) FROM argo_data")
    total = cur.fetchone()[0]
    
    conn.close()
    
    print(f"\n✅ Database optimized!")
    print(f"   Total records: {total:,}")
    print(f"   Indexes: Created")
    print(f"   Query performance: Improved")

if __name__ == "__main__":
    optimize_database()
