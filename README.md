# MACD Divergence Detection

This repository contains Python code for detecting MACD (Moving Average Convergence Divergence) divergences in financial time series data. The code provides functions to calculate MACD ranges, identify local peaks and troughs, and detect both regular and hidden bullish and bearish divergences. It is designed to work with financial datasets containing OHLC (Open, High, Low, Close) prices and MACD indicators.

## Features
- **MACD Range Calculation**: Identifies price and MACD extremes within specified zones, based on MACD sign changes or a maximum candle count.
- **Divergence Detection**: Detects regular and hidden bullish/bearish divergences using MACD and price data.
- **Flexible MACD Parameters**: Supports multiple MACD configurations (e.g., 3-6-2, 6-13-5, 12-26-9, 48-104-36).
- **Local Extrema Detection**: Identifies local peaks and troughs in prolonged MACD ranges for detailed analysis.
- **Multi-Timeframe Analysis**: Supports checking divergences across different timeframes for more robust signals.

## Key Functions
1. **calculate_macd_ranges**: Segments the data into ranges based on MACD sign changes and calculates price and MACD extremes.
2. **detect_divergence**: Analyzes the data for regular and hidden divergences, either bullish or bearish.
3. **check_divergence_conditions**: Combines multiple timeframe analyses to confirm divergence signals.
4. **find_local_extremes**: Detects local peaks and troughs within long MACD ranges.
5. **calculate_macd_ranges_with_extremes**: Enhanced version of range calculation that includes local extrema detection for prolonged ranges.

## Requirements
- Python 3.x
- Libraries: `numpy`, `pandas`

## Usage
1. Ensure your input DataFrame contains the required columns: `time`, `open`, `high`, `low`, `close`, and MACD-related columns (e.g., `macd_12_26_9`, `macdS_12_26_9`).
2. Use the `check_divergence` function to detect divergences with customizable parameters:
   ```python
   result = check_divergence(df, check_for="Bearish_Divergence", macd_cols="def", limit_zones=7)
   print("Divergence Result:", result)
