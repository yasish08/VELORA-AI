"""
Quick Accuracy Test
Simple script to verify prediction accuracy with minimal output
Run: python quick_test.py
"""

import sys
import os

# Add parent directory to path for imports
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

import pandas as pd
import numpy as np
import sqlite3
from sklearn.metrics import mean_absolute_error, r2_score
from ai.predictor import OceanPredictor
import warnings
warnings.filterwarnings('ignore')

# Get database path relative to this script
DB_PATH = os.path.join(SCRIPT_DIR, "data", "argo.db")

def get_indian_ocean_temp_data():
    """Get Indian Ocean temperature data"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    query = """
        SELECT 
            CAST(substr(time, 1, 4) AS INTEGER) AS year,
            AVG(temperature) AS avg_value
        FROM argo_data
        WHERE 
            longitude >= 20 AND longitude <= 120 
            AND latitude >= -60 AND latitude <= 23
            AND temperature IS NOT NULL
        GROUP BY CAST(substr(time, 1, 4) AS INTEGER)
        ORDER BY year ASC
    """
    
    cur.execute(query)
    rows = cur.fetchall()
    conn.close()
    
    return pd.DataFrame([{"year": row["year"], "temperature": row["avg_value"]} for row in rows])

def quick_test():
    print("\n" + "="*60)
    print("⚡ VELORA AI - QUICK ACCURACY TEST")
    print("="*60)
    
    # Get data
    data = get_indian_ocean_temp_data()
    
    if len(data) < 5:
        print("❌ Insufficient data")
        return
    
    print(f"✓ Loaded {len(data)} years of data ({data['year'].min()}-{data['year'].max()})")
    
    # Split: train on first 80%, test on last 20%
    split_idx = int(len(data) * 0.8)
    train = data.iloc[:split_idx]
    test = data.iloc[split_idx:]
    
    print(f"✓ Train: {len(train)} years | Test: {len(test)} years")
    
    # Train predictor
    predictor = OceanPredictor()
    result = predictor.predict_trend(train, "temperature", future_years=len(test))
    
    if not result.get("success"):
        print(f"❌ Prediction failed")
        return
    
    # Get predictions for test years
    pred_years = [p["year"] for p in result["predictions"]]
    pred_values = [p["value"] for p in result["predictions"]]
    
    # Match with actual test data
    actual_values = []
    matched_preds = []
    
    for _, row in test.iterrows():
        if row["year"] in pred_years:
            idx = pred_years.index(row["year"])
            actual_values.append(row["temperature"])
            matched_preds.append(pred_values[idx])
    
    if len(actual_values) == 0:
        print("❌ No matching test data")
        return
    
    # Calculate metrics
    mae = mean_absolute_error(actual_values, matched_preds)
    r2 = r2_score(actual_values, matched_preds) if len(actual_values) > 1 else 0
    
    print(f"\n📊 Results:")
    print(f"   Training R²:     {result['r_squared']:.3f}")
    print(f"   Test MAE:        {mae:.4f} °C")
    print(f"   Test R²:         {r2:.3f}")
    print(f"   Confidence:      {result['confidence']}")
    
    print(f"\n💡 Interpretation:")
    if mae < 0.08:
        print(f"   ✅ Excellent accuracy (MAE < 0.08°C)")
    elif mae < 0.15:
        print(f"   ✓ Good accuracy (MAE < 0.15°C)")
    else:
        print(f"   ⚠️  Higher uncertainty (MAE > 0.15°C)")
    
    if result['r_squared'] > 0.8:
        print(f"   ✅ Strong linear trend (R² > 0.8)")
    elif result['r_squared'] > 0.5:
        print(f"   ✓ Moderate trend (R² > 0.5)")
    else:
        print(f"   ⚠️  Weak trend (R² < 0.5)")
    
    print("\n" + "="*60)
    print("✅ TEST COMPLETE")
    print("="*60)
    print("\nFor detailed testing, run: python tests/test_accuracy.py")
    print("="*60 + "\n")

if __name__ == "__main__":
    quick_test()
