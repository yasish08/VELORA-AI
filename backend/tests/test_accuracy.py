"""
Prediction Accuracy Test Suite
Tests the OceanPredictor model accuracy using train-test splits and cross-validation
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pandas as pd
import numpy as np
import sqlite3
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from ai.predictor import OceanPredictor
import warnings
warnings.filterwarnings('ignore')

# Database path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(SCRIPT_DIR, "..", "data", "argo.db")

# Test configuration
REGION_BOUNDS = {
    "Indian Ocean": (20, 120, -60, 23),
    "Pacific Ocean": (120, 180, -60, 60),
    "Atlantic Ocean": (-100, 0, -60, 60),
    "Arctic Ocean": (-180, 180, 60, 90),
}

TRAIN_YEARS = (2020, 2024)  # Training data
TEST_YEARS = (2025, 2026)    # Test data (held out)

def get_db_connection():
    """Get SQLite connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_yearly_data(region: str, parameter: str, start_year: int, end_year: int):
    """Extract yearly averaged data for a region and parameter"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    lon_min, lon_max, lat_min, lat_max = REGION_BOUNDS[region]
    
    query = f"""
        SELECT 
            CAST(substr(time, 1, 4) AS INTEGER) AS year,
            AVG({parameter}) AS avg_value
        FROM argo_data
        WHERE 
            longitude >= ? AND longitude <= ? 
            AND latitude >= ? AND latitude <= ?
            AND substr(time, 1, 4) >= ?
            AND substr(time, 1, 4) <= ?
            AND {parameter} IS NOT NULL
        GROUP BY CAST(substr(time, 1, 4) AS INTEGER)
        ORDER BY year ASC
    """
    
    cur.execute(query, (lon_min, lon_max, lat_min, lat_max, str(start_year), str(end_year)))
    rows = cur.fetchall()
    conn.close()
    
    df = pd.DataFrame([{"year": row["year"], parameter: row["avg_value"]} for row in rows])
    return df

def test_train_test_split(region: str, parameter: str):
    """Test prediction accuracy using train-test split"""
    print(f"\n{'='*70}")
    print(f"Testing {region} - {parameter.upper()}")
    print(f"{'='*70}")
    
    # Get training data
    train_df = get_yearly_data(region, parameter, TRAIN_YEARS[0], TRAIN_YEARS[1])
    
    if len(train_df) < 3:
        print(f"❌ Insufficient training data ({len(train_df)} years)")
        return None
    
    print(f"📊 Training data: {TRAIN_YEARS[0]}-{TRAIN_YEARS[1]} ({len(train_df)} years)")
    print(f"   Mean: {train_df[parameter].mean():.3f}, Std: {train_df[parameter].std():.3f}")
    
    # Get test data
    test_df = get_yearly_data(region, parameter, TEST_YEARS[0], TEST_YEARS[1])
    
    if len(test_df) < 1:
        print(f"❌ No test data available")
        return None
    
    print(f"📊 Test data: {TEST_YEARS[0]}-{TEST_YEARS[1]} ({len(test_df)} years)")
    print(f"   Mean: {test_df[parameter].mean():.3f}, Std: {test_df[parameter].std():.3f}")
    
    # Train predictor
    predictor = OceanPredictor()
    pred_result = predictor.predict_trend(train_df, parameter, future_years=len(test_df))
    
    if not pred_result.get("success"):
        print(f"❌ Prediction failed: {pred_result.get('message')}")
        return None
    
    # Extract predictions
    predictions = pred_result["predictions"]
    pred_years = [p["year"] for p in predictions]
    pred_values = np.array([p["value"] for p in predictions])
    
    # Match test data to prediction years
    test_years = test_df["year"].values
    test_values = test_df[parameter].values
    
    # Filter predictions to only test years that exist
    matched_preds = []
    matched_actuals = []
    for test_year, test_val in zip(test_years, test_values):
        if test_year in pred_years:
            idx = pred_years.index(test_year)
            matched_preds.append(pred_values[idx])
            matched_actuals.append(test_val)
    
    if len(matched_preds) == 0:
        print(f"❌ No overlapping years between predictions and test data")
        return None
    
    matched_preds = np.array(matched_preds)
    matched_actuals = np.array(matched_actuals)
    
    # Calculate metrics
    mae = mean_absolute_error(matched_actuals, matched_preds)
    rmse = np.sqrt(mean_squared_error(matched_actuals, matched_preds))
    r2 = r2_score(matched_actuals, matched_preds) if len(matched_actuals) > 1 else None
    
    # Calculate percentage error
    mape = np.mean(np.abs((matched_actuals - matched_preds) / matched_actuals)) * 100
    
    print(f"\n📈 Prediction Results:")
    print(f"   R² (training): {pred_result['r_squared']:.3f}")
    print(f"   Confidence: {pred_result['confidence']}")
    print(f"   Slope: {pred_result['slope']:.4f} per year")
    
    print(f"\n✅ Test Set Accuracy:")
    print(f"   MAE:  {mae:.4f} {'°C' if parameter == 'temperature' else 'PSU'}")
    print(f"   RMSE: {rmse:.4f} {'°C' if parameter == 'temperature' else 'PSU'}")
    if r2 is not None:
        print(f"   R²:   {r2:.3f}")
    print(f"   MAPE: {mape:.2f}%")
    
    print(f"\n📋 Year-by-Year Comparison:")
    print(f"{'Year':<8} {'Actual':<12} {'Predicted':<12} {'Error':<12}")
    print("-" * 48)
    for i, year in enumerate(test_years):
        if year in pred_years:
            idx = pred_years.index(year)
            actual = matched_actuals[i]
            predicted = matched_preds[i]
            error = actual - predicted
            print(f"{year:<8} {actual:<12.4f} {predicted:<12.4f} {error:+12.4f}")
    
    return {
        "region": region,
        "parameter": parameter,
        "mae": mae,
        "rmse": rmse,
        "r2": r2,
        "mape": mape,
        "train_r2": pred_result['r_squared'],
        "confidence": pred_result['confidence'],
        "n_train": len(train_df),
        "n_test": len(matched_actuals)
    }

def rolling_window_test(region: str, parameter: str, window_size: int = 4):
    """Test using rolling window approach (more robust)"""
    print(f"\n{'='*70}")
    print(f"Rolling Window Test: {region} - {parameter.upper()}")
    print(f"Window size: {window_size} years, forecast: 1 year ahead")
    print(f"{'='*70}")
    
    # Get all data
    all_data = get_yearly_data(region, parameter, 2020, 2026)
    
    if len(all_data) < window_size + 1:
        print(f"❌ Insufficient data for rolling window ({len(all_data)} years)")
        return None
    
    predictor = OceanPredictor()
    errors = []
    
    print(f"\n📋 Rolling Window Results:")
    print(f"{'Train Years':<20} {'Test Year':<12} {'Actual':<12} {'Predicted':<12} {'Error':<12}")
    print("-" * 72)
    
    # Rolling window
    for i in range(len(all_data) - window_size):
        train_window = all_data.iloc[i:i+window_size]
        test_point = all_data.iloc[i+window_size]
        
        # Train and predict
        pred_result = predictor.predict_trend(train_window, parameter, future_years=1)
        
        if pred_result.get("success") and len(pred_result["predictions"]) > 0:
            predicted_value = pred_result["predictions"][0]["value"]
            actual_value = test_point[parameter]
            error = actual_value - predicted_value
            errors.append(error)
            
            train_years = f"{train_window['year'].iloc[0]}-{train_window['year'].iloc[-1]}"
            print(f"{train_years:<20} {test_point['year']:<12} {actual_value:<12.4f} {predicted_value:<12.4f} {error:+12.4f}")
    
    if len(errors) == 0:
        print(f"❌ No successful predictions")
        return None
    
    errors = np.array(errors)
    mae = np.mean(np.abs(errors))
    rmse = np.sqrt(np.mean(errors**2))
    
    print(f"\n✅ Rolling Window Accuracy:")
    print(f"   MAE:  {mae:.4f} {'°C' if parameter == 'temperature' else 'PSU'}")
    print(f"   RMSE: {rmse:.4f} {'°C' if parameter == 'temperature' else 'PSU'}")
    print(f"   Windows tested: {len(errors)}")
    
    return {
        "region": region,
        "parameter": parameter,
        "mae": mae,
        "rmse": rmse,
        "n_windows": len(errors)
    }

def run_full_test_suite():
    """Run comprehensive accuracy tests"""
    print("\n" + "="*70)
    print("VELORA AI - PREDICTION ACCURACY TEST SUITE")
    print("="*70)
    print(f"Test Date: February 21, 2026")
    print(f"Training Period: {TRAIN_YEARS[0]}-{TRAIN_YEARS[1]}")
    print(f"Test Period: {TEST_YEARS[0]}-{TEST_YEARS[1]}")
    print("="*70)
    
    # Test regions and parameters
    test_configs = [
        ("Indian Ocean", "temperature"),
        ("Indian Ocean", "salinity"),
        ("Pacific Ocean", "temperature"),
        ("Atlantic Ocean", "temperature"),
    ]
    
    results = []
    
    # Train-test split tests
    print("\n" + "🔬 TRAIN-TEST SPLIT TESTS")
    for region, parameter in test_configs:
        result = test_train_test_split(region, parameter)
        if result:
            results.append(result)
    
    # Rolling window tests
    print("\n\n" + "🔄 ROLLING WINDOW TESTS")
    for region, parameter in test_configs[:2]:  # Test subset for speed
        rolling_window_test(region, parameter, window_size=4)
    
    # Summary
    if results:
        print("\n" + "="*70)
        print("📊 SUMMARY STATISTICS")
        print("="*70)
        
        df_results = pd.DataFrame(results)
        
        print(f"\nOverall Performance (Train-Test Split):")
        print(f"  Average MAE:  {df_results['mae'].mean():.4f}")
        print(f"  Average RMSE: {df_results['rmse'].mean():.4f}")
        print(f"  Average R²:   {df_results['r2'].mean():.3f}")
        print(f"  Average MAPE: {df_results['mape'].mean():.2f}%")
        
        print(f"\nConfidence Distribution:")
        print(df_results['confidence'].value_counts())
        
        print(f"\nBest Performance (Lowest MAE):")
        best = df_results.loc[df_results['mae'].idxmin()]
        print(f"  {best['region']} - {best['parameter']}: MAE = {best['mae']:.4f}")
        
        print(f"\nWorst Performance (Highest MAE):")
        worst = df_results.loc[df_results['mae'].idxmax()]
        print(f"  {worst['region']} - {worst['parameter']}: MAE = {worst['mae']:.4f}")
    
    print("\n" + "="*70)
    print("✅ TEST SUITE COMPLETE")
    print("="*70)
    print("\nRecommendations:")
    print("  • Use predictions with R² > 0.8 for high confidence")
    print("  • Typical accuracy: ±0.05-0.15°C, ±0.01-0.03 PSU")
    print("  • Best for 2-5 year forecasts, not extreme events")
    print(f"  • For details, see PREDICTION_ACCURACY.md")
    print("="*70 + "\n")

if __name__ == "__main__":
    run_full_test_suite()
