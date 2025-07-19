import MetaTrader5 as mt5
import pandas as pd
import numpy as np

def connect_to_mt5(login, password, server, path):
    """اتصال به MetaTrader 5 با اطلاعات ورودی."""
    if not mt5.initialize(path=path, login=login, password=password, server=server):
        raise RuntimeError("Unable to connect to MetaTrader 5")
    print("✅ Connected to MetaTrader 5")

def preparing_data_as_dataframe(symbol, timeframe, candle_num):
    """دریافت داده‌های قیمتی از MetaTrader 5 و تبدیل به دیتافریم."""
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, candle_num)
    if rates is None or len(rates) == 0:
        raise ValueError("Failed to retrieve data from MetaTrader 5")
    
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    return df.drop(columns=['tick_volume', 'spread', 'real_volume'])

def moving_average(df, period, method='SMA', apply_to='close'):
    """محاسبه میانگین متحرک (SMA، EMA، WMA) برای ستون مشخص."""
    if apply_to not in df.columns:
        raise ValueError(f"Column '{apply_to}' not found in DataFrame")

    if method == 'SMA':
        return df[apply_to].rolling(window=period).mean()
    elif method == 'EMA':
        return df[apply_to].ewm(span=period, adjust=True).mean()
    elif method == 'WMA':
        weights = pd.Series(range(1, period + 1))
        return df[apply_to].rolling(window=period).apply(
            lambda prices: (prices * weights).sum() / weights.sum(), raw=True
        )
    else:
        raise ValueError("Invalid method. Use 'SMA', 'EMA', or 'WMA'")

def adding_moving_averages(df, periods):
    """افزودن میانگین‌های متحرک (EMA) به دیتافریم برای دوره‌های مشخص."""
    for period in periods:
        column_name = f'MA_{period}'
        df[column_name] = round(moving_average(df, period=period, method='EMA', apply_to='close'), 3)
    return df

def macd(df, fast_period=12, slow_period=26, signal_period=9):
    """محاسبه MACD و خط سیگنال برای دوره‌های مشخص."""
    fast_ema = df['close'].ewm(span=fast_period, adjust=False).mean()
    slow_ema = df['close'].ewm(span=slow_period, adjust=False).mean()
    macd_line = fast_ema - slow_ema
    macd_signal = macd_line.ewm(span=signal_period, adjust=False).mean()

    df[f'macd_{fast_period}_{slow_period}_{signal_period}'] = macd_line
    df[f'macdS_{fast_period}_{slow_period}_{signal_period}'] = macd_signal
    return df[[f'macd_{fast_period}_{slow_period}_{signal_period}', 
               f'macdS_{fast_period}_{slow_period}_{signal_period}']]

def adding_macds(df):
    """افزودن MACD برای مجموعه‌ای از پارامترهای مختلف."""
    params = {
        "3_6_2": (3, 6, 2),
        "6_13_5": (6, 13, 5),
        "12_26_9": (12, 26, 9),
        "48_104_36": (48, 104, 36)
    }
    for key, (fast, slow, signal) in params.items():
        macd(df, fast_period=fast, slow_period=slow, signal_period=signal)
    return df

def calculate_macd_ranges(df, macd_cols='def', limit_zones=7):
    """محاسبه محدوده‌های MACD و شناسایی اکسترمم‌ها."""
    params = {
        "low2": ['macd_3_6_2', 'macdS_3_6_2'],
        "low1": ['macd_6_13_5', 'macdS_6_13_5'],
        "def": ['macd_12_26_9', 'macdS_12_26_9'],
        "high": ['macd_48_104_36', 'macdS_48_104_36'],
    }
    
    if macd_cols not in params:
        raise ValueError(f"Invalid macd_cols: '{macd_cols}'. Choose from: 'low2', 'low1', 'def', 'high'.")
    
    selected_columns = ['time', 'open', 'high', 'close', 'low'] + params[macd_cols]
    df = df[selected_columns].copy()
    
    macd_col = df.columns[5]
    df['macd_sign'] = np.where(df[macd_col] >= 0, 'positive', 'negative')
    df['range_extreme'] = np.nan
    df['macd_extreme'] = np.nan
    df['range_number'] = np.nan
    df['time_extreme'] = pd.NaT

    current_sign = df['macd_sign'].iloc[-1]
    range_number = 1
    start_index = len(df) - 1
    
    for i in range(len(df) - 2, -1, -1):
        if df['macd_sign'].iloc[i] != current_sign:
            range_df = df.iloc[i+1:start_index+1]
            
            if current_sign == 'positive':
                price_extreme = range_df['high'].max()
                macd_extreme = range_df[macd_col].max()
                time_extreme = range_df.loc[range_df['high'].idxmax(), 'time']
            else:
                price_extreme = range_df['low'].min()
                macd_extreme = range_df[macd_col].min()
                time_extreme = range_df.loc[range_df['low'].idxmin(), 'time']
            
            df.loc[i+1:start_index, 'range_extreme'] = price_extreme
            df.loc[i+1:start_index, 'macd_extreme'] = macd_extreme
            df.loc[i+1:start_index, 'range_number'] = range_number
            df.loc[i+1:start_index, 'time_extreme'] = time_extreme
            
            current_sign = df['macd_sign'].iloc[i]
            start_index = i
            range_number += 1
    
    range_df = df.iloc[:start_index+1]
    if current_sign == 'positive':
        price_extreme = range_df['high'].max()
        macd_extreme = range_df[macd_col].max()
        time_extreme = range_df.loc[range_df['high'].idxmax(), 'time']
    else:
        price_extreme = range_df['low'].min()
        macd_extreme = range_df[macd_col].min()
        time_extreme = range_df.loc[range_df['low'].idxmin(), 'time']
    df.loc[:start_index, 'range_extreme'] = price_extreme
    df.loc[:start_index, 'macd_extreme'] = macd_extreme
    df.loc[:start_index, 'range_number'] = range_number
    df.loc[:start_index, 'time_extreme'] = time_extreme

    filtered_df = df[df['range_number'] <= limit_zones]
    unique_df = filtered_df.drop_duplicates(subset=['range_extreme', 'macd_extreme', 'range_number'], keep='first')
    return unique_df[['range_extreme', 'macd_extreme', 'range_number', 'time_extreme']]

def detect_divergence(df, check_for="Bearish_Divergence"):
    """تشخیص واگرایی‌های منظم و مخفی."""
    if len(df) < 6:
        return "No Divergence"

    df_copy = df.copy()
    if check_for == "Bearish_Divergence" and df_copy['macd_extreme'].iloc[-1] < 0:
        df_copy = df_copy[:-1]
    elif check_for == "Bullish_Divergence" and df_copy['macd_extreme'].iloc[-1] > 0:
        df_copy = df_copy[:-1]

    regular_divergence_bearish = None
    if (df_copy['macd_extreme'].iloc[-1] > 0 and df_copy['macd_extreme'].iloc[-3] > 0 and
        df_copy['range_extreme'].iloc[-1] > df_copy['range_extreme'].iloc[-3] and
        df_copy['macd_extreme'].iloc[-1] < df_copy['macd_extreme'].iloc[-3]):
        regular_divergence_bearish = "Bearish Regular Divergence"

    regular_divergence_bullish = None
    if (df_copy['macd_extreme'].iloc[-1] < 0 and df_copy['macd_extreme'].iloc[-3] < 0 and
        df_copy['range_extreme'].iloc[-1] < df_copy['range_extreme'].iloc[-3] and
        df_copy['macd_extreme'].iloc[-1] > df_copy['macd_extreme'].iloc[-3]):
        regular_divergence_bullish = "Bullish Regular Divergence"

    hidden_divergence_bullish = None
    hidden_divergence_bearish = None
    if len(df_copy) >= 6:
        if ((df_copy['macd_extreme'].iloc[-2] < 0 and df_copy['macd_extreme'].iloc[-4] < 0 and
             df_copy['range_extreme'].iloc[-2] > df_copy['range_extreme'].iloc[-4] and
             df_copy['macd_extreme'].iloc[-2] < df_copy['macd_extreme'].iloc[-4]) or
            (df_copy['macd_extreme'].iloc[-2] < 0 and df_copy['macd_extreme'].iloc[-6] < 0 and
             df_copy['range_extreme'].iloc[-2] > df_copy['range_extreme'].iloc[-6] and
             df_copy['macd_extreme'].iloc[-2] < df_copy['macd_extreme'].iloc[-6])):
            hidden_divergence_bullish = "Bullish Hidden Divergence"

        if ((df_copy['macd_extreme'].iloc[-2] > 0 and df_copy['macd_extreme'].iloc[-4] > 0 and
             df_copy['range_extreme'].iloc[-2] < df_copy['range_extreme'].iloc[-4] and
             df_copy['macd_extreme'].iloc[-2] > df_copy['macd_extreme'].iloc[-4]) or
            (df_copy['macd_extreme'].iloc[-2] > 0 and df_copy['macd_extreme'].iloc[-6] > 0 and
             df_copy['range_extreme'].iloc[-2] < df_copy['range_extreme'].iloc[-6] and
             df_copy['macd_extreme'].iloc[-2] > df_copy['macd_extreme'].iloc[-6])):
            hidden_divergence_bearish = "Bearish Hidden Divergence"

    divergences = [d for d in [regular_divergence_bearish, regular_divergence_bullish,
                               hidden_divergence_bullish, hidden_divergence_bearish] if d]
    return " and ".join(divergences) if divergences else "No Divergence"

def check_divergence_conditions(df, lower_tf_df, divergence_type="Bearish"):
    """بررسی شرایط واگرایی در تایم‌فریم‌های مختلف."""
    divergence_types = ["Bearish", "Bullish"]
    check_for = f"{divergence_type}_Divergence"
    
    expected_results = [
        f"{divergence_type} Regular Divergence",
        f"{divergence_type} Regular Divergence and {divergence_types[1 if divergence_type == 'Bearish' else 0]} Hidden Divergence"
    ]

    conditions = [
        calculate_macd_ranges(df, macd_cols='def', limit_zones=7),
        calculate_macd_ranges(df, macd_cols='low1', limit_zones=7),
        calculate_macd_ranges(lower_tf_df, macd_cols='def', limit_zones=7),
        calculate_macd_ranges(lower_tf_df, macd_cols='low1', limit_zones=7)
    ]

    for condition in conditions:
        divergence_result = detect_divergence(condition, check_for=check_for)
        if divergence_result in expected_results:
            return True
    return False

if __name__ == "__main__":
    # اتصال به MetaTrader 5
    connect_to_mt5(
        login=111111,
        password="222222",
        server="MT5 Server",
        path="C:/Program Files/MT5/terminal64.exe"
    )

    # تاریخ هدف
    target_end_time = pd.to_datetime("2025-07-16 17:30:00")

    # دریافت و فیلتر داده‌های تایم‌فریم M30
    df = preparing_data_as_dataframe("GBPUSD", mt5.TIMEFRAME_M30, 2000)
    df = df[df['time'] <= target_end_time]
    if len(df) > 2000:
        df = df.iloc[-2000:]
    elif len(df) < 2000:
        print(f"Warning: Only {len(df)} rows available instead of 2000.")

    main_df = adding_moving_averages(df, [15, 30, 60, 240])
    main_df = adding_macds(main_df)
    print("Main DataFrame (M30):")
    print(main_df.tail())

    # دریافت و پردازش تایم‌فریم‌های پایین‌تر
    lower1_timeframe = mt5.TIMEFRAME_M15
    lower2_timeframe = mt5.TIMEFRAME_M5

    lower1_df = preparing_data_as_dataframe("GBPUSD", lower1_timeframe, 3500)
    lower1_df = lower1_df[lower1_df['time'] <= target_end_time]
    lower1_df = adding_moving_averages(lower1_df, [15, 30, 60, 240])
    lower1_df = adding_macds(lower1_df)

    lower2_df = preparing_data_as_dataframe("GBPUSD", lower2_timeframe, 5000)
    lower2_df = lower2_df[lower2_df['time'] <= target_end_time]
    lower2_df = adding_moving_averages(lower2_df, [15, 30, 60, 240])
    lower2_df = adding_macds(lower2_df)

    # بررسی واگرایی
    if (check_divergence_conditions(main_df, lower1_df, "Bearish") or
            check_divergence_conditions(lower1_df, lower2_df, "Bearish")):
        print("Divergence is OK")
    else:
        print("No Divergence")

    # بستن اتصال MetaTrader 5
    mt5.shutdown()
