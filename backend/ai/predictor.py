"""
Predictor module
Performs time series prediction on ocean data
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from typing import Dict, List, Optional

class OceanPredictor:
    def __init__(self):
        self.model = LinearRegression()
    
    def predict_trend(self, data: pd.DataFrame, parameter: str, future_years: int = 5) -> Dict:
        """
        Predict future trends based on historical data
        
        Args:
            data: DataFrame with time series data
            parameter: Parameter to predict (temperature, salinity, etc.)
            future_years: Number of years to predict into the future
            
        Returns:
            Dictionary with predictions and trend analysis
        """
        
        if data.empty or parameter not in data.columns:
            return {
                "success": False,
                "message": "Insufficient data for prediction"
            }
        
        # Prepare data
        data = data.dropna(subset=[parameter])
        
        if len(data) < 2:
            return {
                "success": False,
                "message": "Need at least 2 data points for prediction"
            }
        
        # Extract years and values
        X = data['year'].values.reshape(-1, 1)
        y = data[parameter].values
        
        # Fit model
        self.model.fit(X, y)
        
        # Make predictions
        last_year = int(X[-1][0])
        future_years_array = np.array(range(last_year + 1, last_year + future_years + 1)).reshape(-1, 1)
        predictions = self.model.predict(future_years_array)
        
        # Calculate trend
        slope = self.model.coef_[0]
        trend = "increasing" if slope > 0 else "decreasing"
        
        # Calculate confidence
        r_squared = self.model.score(X, y)
        
        return {
            "success": True,
            "predictions": [
                {"year": int(year[0]), "value": float(pred)}
                for year, pred in zip(future_years_array, predictions)
            ],
            "trend": trend,
            "slope": float(slope),
            "r_squared": float(r_squared),
            "confidence": "high" if r_squared > 0.8 else "medium" if r_squared > 0.5 else "low"
        }
    
    def detect_anomalies(self, data: pd.DataFrame, parameter: str) -> List[Dict]:
        """
        Detect anomalies in the data using statistical methods
        
        Args:
            data: DataFrame with time series data
            parameter: Parameter to check for anomalies
            
        Returns:
            List of anomaly points
        """
        
        if data.empty or parameter not in data.columns:
            return []
        
        values = data[parameter].dropna()
        
        if len(values) < 3:
            return []
        
        # Use z-score method
        mean = values.mean()
        std = values.std()
        
        anomalies = []
        
        for idx, row in data.iterrows():
            if pd.notna(row[parameter]):
                z_score = abs((row[parameter] - mean) / std) if std > 0 else 0
                
                if z_score > 2.5:  # 2.5 standard deviations
                    anomalies.append({
                        "year": row['year'],
                        "value": float(row[parameter]),
                        "z_score": float(z_score),
                        "severity": "high" if z_score > 3 else "medium"
                    })
        
        return anomalies
    
    def calculate_statistics(self, data: pd.DataFrame, parameter: str) -> Dict:
        """
        Calculate basic statistics for the parameter
        """
        
        if data.empty or parameter not in data.columns:
            return {}
        
        values = data[parameter].dropna()
        
        if len(values) == 0:
            return {}
        
        return {
            "mean": float(values.mean()),
            "median": float(values.median()),
            "std": float(values.std()),
            "min": float(values.min()),
            "max": float(values.max()),
            "count": int(len(values))
        }
