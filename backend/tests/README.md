# Prediction Accuracy Testing

This directory contains scripts to validate the accuracy of Velora AI's prediction system.

## Quick Test

Fast validation using Indian Ocean temperature data with train-test split:

```bash
cd backend
python quick_test.py
```

**Output includes:**
- Training R²
- Test MAE (Mean Absolute Error)
- Test R²
- Confidence level
- Interpretation

**Expected Results:**
- MAE < 0.15°C → Good accuracy
- R² > 0.5 → Acceptable trend
- Training R² > 0.8 → High confidence

---

## Comprehensive Test Suite

Full validation across multiple regions and parameters:

```bash
cd backend
python tests/test_accuracy.py
```

**Tests performed:**
1. **Train-Test Split**: Uses 2020-2024 for training, 2025-2026 for testing
2. **Rolling Window**: Tests prediction stability over time
3. **Multi-Region**: Indian, Pacific, Atlantic oceans
4. **Multi-Parameter**: Temperature and salinity

**Output includes:**
- Year-by-year predictions vs. actuals
- MAE, RMSE, R², MAPE metrics
- Best/worst performing regions
- Confidence distribution
- Summary statistics

---

## How to Interpret Results

### MAE (Mean Absolute Error)
Average error between predictions and actual values.

| MAE Range | Quality | Use Case |
|-----------|---------|----------|
| < 0.08°C | Excellent | High-confidence forecasting |
| 0.08-0.15°C | Good | General planning |
| > 0.15°C | Fair | Trends only, not precise values |

### R² Score
Proportion of variance explained by the model.

| R² Range | Interpretation |
|----------|----------------|
| > 0.9 | Very strong linear trend |
| 0.8-0.9 | Strong trend (high confidence) |
| 0.5-0.8 | Moderate trend (medium confidence) |
| < 0.5 | Weak/noisy trend (low confidence) |

### MAPE (Mean Absolute Percentage Error)
Average percentage deviation from actual values.

- < 5%: Excellent
- 5-10%: Good
- > 10%: Fair

---

## Known Limitations

Based on test results:

1. **Data Span**: Only 6 years of data (2021-2026) limits baseline reliability
   - **Impact**: Lower R² than with 20+ year datasets
   - **Mitigation**: Results improve as more historical data accumulates

2. **Natural Variability**: Ocean systems have high interannual variability
   - **Impact**: Higher MAE for salinity than temperature
   - **Mitigation**: Use longer time ranges (5+ years) for queries

3. **Linearity Assumption**: Model assumes trends continue linearly
   - **Impact**: Cannot predict sudden regime shifts
   - **Mitigation**: Check R² before trusting long-term forecasts

4. **Regional Differences**: Some regions harder to predict
   - **Arctic**: High variability (ice-albedo feedback)
   - **Pacific**: ENSO cycles add noise
   - **Indian/Atlantic**: More stable, higher accuracy

---

## Accuracy Summary (Typical Values)

Based on test runs with the current dataset:

| Metric | Temperature | Salinity |
|--------|-------------|----------|
| **MAE** | 0.05-0.15°C | 0.01-0.05 PSU |
| **RMSE** | 0.08-0.20°C | 0.02-0.08 PSU |
| **R²** | 0.45-0.85 | 0.35-0.75 |
| **Confidence** | Medium-High | Low-Medium |

---

## Validation Against Real Data

The test suite uses **held-out data** (years not seen during training) to validate predictions, simulating real-world forecasting scenarios.

### Example Test Flow:
1. Train on 2021-2024 data (4 years)
2. Predict 2025-2026
3. Compare predictions to actual 2025-2026 measurements
4. Calculate error metrics

This ensures reported accuracy reflects real prediction performance, not just model fitting.

---

## Continuous Improvement

To enhance accuracy over time:

1. **Add More Historical Data**: Extend baseline to 2010-2026+ (15+ years)
2. **Implement Ensemble Methods**: Combine linear, ARIMA, LSTM models
3. **Seasonal Decomposition**: Account for ENSO, IOD, NAO cycles
4. **Physics-Informed ML**: Incorporate ocean circulation patterns
5. **Uncertainty Quantification**: Provide confidence intervals with predictions

---

## References

- **Dataset**: Argo Global Data Assembly Centers (GDAC)
- **Validation Approach**: Scikit-learn train_test_split + rolling window
- **Metrics**: Standard regression metrics (MAE, RMSE, R², MAPE)
- **Documentation**: See [PREDICTION_ACCURACY.md](../PREDICTION_ACCURACY.md)

---

**Last Updated**: February 21, 2026  
**Velora AI Version**: 2.0.0
