#!/usr/bin/env python
import sqlite3

conn = sqlite3.connect("data/argo.db")
cur = conn.cursor()

# Get a sample time value
cur.execute("SELECT time FROM argo_data LIMIT 1")
sample_time = cur.fetchone()[0]
print(f"Sample time value: '{sample_time}'")
print(f"Type: {type(sample_time)}")

# Check year extraction method
if sample_time:
    print(f"Extracted year with substr: {sample_time[:4]}")
    
# Count records for different year patterns
print("\nRecords by year pattern:")
for year in ["2020", "2021", "2022", "2023", "2024"]:
    cur.execute("SELECT COUNT(*) FROM argo_data WHERE time LIKE ?", (year + "%",))
    count = cur.fetchone()[0]
    if count > 0:
        print(f"  {year}: {count:,}")

# Check year range with substr
cur.execute("SELECT MIN(substr(time, 1, 4)), MAX(substr(time, 1, 4)) FROM argo_data")
min_year, max_year = cur.fetchone()
print(f"\nYear range (using substr): {min_year} to {max_year}")

conn.close()
