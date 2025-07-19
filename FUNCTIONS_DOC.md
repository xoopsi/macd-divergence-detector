# 🧠 Function Documentation – MACD Divergence Detection

This document provides a detailed explanation of all functions used in the MACD-based price divergence detection project. The goal is to identify **regular** and **hidden** bullish/bearish divergences using historical market data.

---

## 📌 1. `calculate_macd_ranges(df, macd_cols='def', limit_zones=7)`

### Description:
Detects ranges where MACD stays positive or negative and extracts price and MACD extremes in those zones.

### Parameters:
- `df` (DataFrame): Historical price data.
- `macd_cols` (str): MACD configuration. Options:
  - `'low2'`: MACD(3,6,2)
  - `'low1'`: MACD(6,13,5)
  - `'def'`: MACD(12,26,9) (default)
  - `'high'`: MACD(48,104,36)
- `limit_zones` (int): Maximum number of MACD ranges to extract (must be ≥ 7).

### Returns:
DataFrame with:
- `range_extreme`: Extreme price in the MACD range
- `macd_extreme`: Corresponding MACD extreme
- `range_number`: Zone number
- `time_extreme`: Timestamp of the extreme

---

## 📌 2. `detect_divergence(df, check_for="Bearish_Divergence")`

### Description:
Analyzes the two most recent MACD-price extremes to detect regular or hidden divergences.

### Parameters:
- `df` (DataFrame): Output from `calculate_macd_ranges`.
- `check_for` (str): Type of divergence to detect:
  - `"Bearish_Divergence"`
  - `"Bullish_Divergence"`

### Returns:
String result:
- `"Bearish Regular Divergence"`
- `"Bullish Regular Divergence"`
- `"Bearish Hidden Divergence"`
- `"Bullish Hidden Divergence"`
- or `"No Divergence"`

---

## 📌 3. `check_divergence_conditions(df, lower_TF_df, divergence_type="Bearish")`

### Description:
Checks multiple MACD configurations across both main and lower timeframes to confirm divergence signals.

### Parameters:
- `df` (DataFrame): Main timeframe data.
- `lower_TF_df` (DataFrame): Lower timeframe data.
- `divergence_type` (str): `"Bearish"` or `"Bullish"`.

### Returns:
- `True` if at least one valid divergence is detected.
- `False` otherwise.

---

## 📌 4. `check_divergence(df, check_for="Bearish_Divergence", macd_cols='def', limit_zones=7)`

### Description:
Wrapper function that combines `calculate_macd_ranges` and `detect_divergence`.

### Parameters:
- `df` (DataFrame): Price + MACD data.
- `check_for` (str): `"Bearish_Divergence"` or `"Bullish_Divergence"`.
- `macd_cols` (str): MACD configuration.
- `limit_zones` (int): Range limit (≥ 7).

### Returns:
- Divergence result string from `detect_divergence`.

---

## 📌 5. `find_local_extremes(df, macd_col, price_col, min_candles=2)`

### Description:
Detects local MACD peaks and troughs within longer MACD segments.

### Parameters:
- `df` (DataFrame): Data with MACD and price columns.
- `macd_col` (str): Column name of MACD.
- `price_col` (str): Column name of price (usually `'high'` or `'low'`).
- `min_candles` (int): Minimum number of candles separating each local extreme.

### Returns:
DataFrame with:
- `time`: Timestamp of the extreme
- `macd_extreme`: Value of MACD at the peak/trough
- `price_extreme`: Price at that point
- `type`: `'peak'` or `'trough'`

---

## 📌 6. `calculate_macd_ranges_with_extremes(df, macd_cols='def', limit_zones=7, max_candle_count=50)`

### Description:
Advanced version of `calculate_macd_ranges` with built-in support for detecting local MACD extremes in long MACD segments.

### Parameters:
- `df` (DataFrame): Input market data.
- `macd_cols` (str): MACD config string (`'low2'`, `'low1'`, `'def'`, `'high'`)
- `limit_zones` (int): Limit on the number of MACD ranges
- `max_candle_count` (int): Max length of MACD segment before extracting local peaks/troughs

### Returns:
Tuple:
1. Processed DataFrame with range and MACD extremes
2. DataFrame of local extremes: `time`, `macd_extreme`, `price_extreme`, `type`

---

## 📊 Supported MACD Configurations

| Name     | MACD Settings  |
|----------|----------------|
| `low2`   | 3-6-2          |
| `low1`   | 6-13-5         |
| `def`    | 12-26-9        |
| `high`   | 48-104-36      |

---

## 🧪 Example Usage

```python
from divergence import check_divergence

result = check_divergence(df, check_for="Bullish_Divergence", macd_cols="low1", limit_zones=7)
print(result)  # Example: Bullish Regular Divergence
