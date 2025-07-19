import numpy as np
import pandas as pd



def calculate_macd_ranges(df, macd_cols='def', limit_zones=7):
    """
    mocd_cols = ["low2 = 3-6-2", "low1 = 6-13-5", "def = 12-26-9", "high = 48-104-36"]
    limit_zones >= 7
    """
    params = {
        "low2": ['macd_3_6_2', 'macdS_3_6_2'],
        "low1": ['macd_6_13_5', 'macdS_6_13_5'],
        "def": ['macd_12_26_9', 'macdS_12_26_9'],
        "high": ['macd_48_104_36', 'macdS_48_104_36'],
    }
    
    if macd_cols not in params:
        raise ValueError(f"Invalid macd_cols value: '{macd_cols}'. Please choose one of the following options: 'low2', 'low1', 'def', 'high'.")
    
    selected_columns = ['time', 'open', 'high', 'close', 'low'] + params[macd_cols]
    df = df[selected_columns].copy()
    
    macd_col = df.columns[5] 

    df['macd_sign'] = np.where(df[macd_col] >= 0, 'positive', 'negative')
    df['range_extreme'] = np.nan
    df['macd_extreme'] = np.nan
    df['range_number'] = np.nan
    df['time_extreme'] = pd.NaT  # ستون جدید برای ذخیره زمان اکسترمم

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
    # Check if the dataframe has at least 6 rows
    if len(df) < 6:
        # Instead of raising an error, return "No Divergence" if there is insufficient data
        return "No Divergence"

    # Create a copy of df to avoid modifying the original dataframe
    df_copy = df.copy()

    # بررسی شرط‌ها و حذف ردیف آخر در صورت برقرار بودن شرایط
    if check_for == "Bearish_Divergence" and df_copy['macd_extreme'].iloc[-1] < 0:
        df_copy = df_copy[:-1]  # حذف ردیف آخر
    elif check_for == "Bullish_Divergence" and df_copy['macd_extreme'].iloc[-1] > 0:
        df_copy = df_copy[:-1]  # حذف ردیف آخر

    # Bearish Regular Divergence between two recent peaks
    if (df_copy['macd_extreme'].iloc[-1] > 0 and df_copy['macd_extreme'].iloc[-3] > 0 and
        df_copy['range_extreme'].iloc[-1] > df_copy['range_extreme'].iloc[-3] and
        df_copy['macd_extreme'].iloc[-1] < df_copy['macd_extreme'].iloc[-3]):
        regular_divergence_bearish = "Bearish Regular Divergence"
    else:
        regular_divergence_bearish = None

    # Bullish Regular Divergence between two recent troughs
    if (df_copy['macd_extreme'].iloc[-1] < 0 and df_copy['macd_extreme'].iloc[-3] < 0 and
        df_copy['range_extreme'].iloc[-1] < df_copy['range_extreme'].iloc[-3] and
        df_copy['macd_extreme'].iloc[-1] > df_copy['macd_extreme'].iloc[-3]):
        regular_divergence_bullish = "Bullish Regular Divergence"
    else:
        regular_divergence_bullish = None

    # Check for sufficient rows for hidden divergence analysis
    if len(df_copy) >= 6:
        # Bullish Hidden Divergence
        if ((df_copy['macd_extreme'].iloc[-2] < 0 and df_copy['macd_extreme'].iloc[-4] < 0 and
             df_copy['range_extreme'].iloc[-2] > df_copy['range_extreme'].iloc[-4] and
             df_copy['macd_extreme'].iloc[-2] < df_copy['macd_extreme'].iloc[-4]) or
            (df_copy['macd_extreme'].iloc[-2] < 0 and df_copy['macd_extreme'].iloc[-6] < 0 and
             df_copy['range_extreme'].iloc[-2] > df_copy['range_extreme'].iloc[-6] and
             df_copy['macd_extreme'].iloc[-2] < df_copy['macd_extreme'].iloc[-6])):
            hidden_divergence_bullish = "Bullish Hidden Divergence"
        else:
            hidden_divergence_bullish = None

        # Bearish Hidden Divergence
        if ((df_copy['macd_extreme'].iloc[-2] > 0 and df_copy['macd_extreme'].iloc[-4] > 0 and
             df_copy['range_extreme'].iloc[-2] < df_copy['range_extreme'].iloc[-4] and
             df_copy['macd_extreme'].iloc[-2] > df_copy['macd_extreme'].iloc[-4]) or
            (df_copy['macd_extreme'].iloc[-2] > 0 and df_copy['macd_extreme'].iloc[-6] > 0 and
             df_copy['range_extreme'].iloc[-2] < df_copy['range_extreme'].iloc[-6] and
             df_copy['macd_extreme'].iloc[-2] > df_copy['macd_extreme'].iloc[-6])):
            hidden_divergence_bearish = "Bearish Hidden Divergence"
        else:
            hidden_divergence_bearish = None
    else:
        hidden_divergence_bullish = None
        hidden_divergence_bearish = None

    # Compile all results
    divergences = [d for d in [regular_divergence_bearish, regular_divergence_bullish,
                               hidden_divergence_bullish, hidden_divergence_bearish] if d]

    # Return results or indicate no divergence
    return " and ".join(divergences) if divergences else "No Divergence"


def check_divergence_conditions(df, lower_TF_df, divergence_type="Bearish"):
    """
    بررسی واگرایی با توجه به نوع ورودی
    
    پارامترها:
    df (DataFrame): داده‌های اصلی تایم فریم بالا
    lower_TF_df (DataFrame): داده‌های تایم فریم پایین‌تر
    divergence_type (str): نوع واگرایی، می‌تواند "Bearish" یا "Bullish" باشد
    
    خروجی:
    bool: اگر حداقل یکی از شرایط واگرایی برقرار باشد، مقدار True برمی‌گرداند و در غیر این صورت False
    """
    # انواع واگرایی‌های موجود
    divergence_types = ["Bearish", "Bullish"]
    check_for = f"{divergence_type}_Divergence"
    
    # تنظیم نتایج مورد انتظار بر اساس نوع واگرایی
    if divergence_type == divergence_types[0]:  # Bearish
        expected_results = [
            f"{divergence_types[0]} Regular Divergence", 
            f"{divergence_types[0]} Regular Divergence and {divergence_types[1]} Hidden Divergence"
        ]
    else:  # Bullish
        expected_results = [
            f"{divergence_types[1]} Regular Divergence", 
            f"{divergence_types[1]} Regular Divergence and {divergence_types[0]} Hidden Divergence"
        ]

    # محاسبه واگرایی برای شرایط مختلف
    conditions = [
        calculate_macd_ranges(df, macd_cols='def', limit_zones=7),
        calculate_macd_ranges(df, macd_cols='low1', limit_zones=7),
        calculate_macd_ranges(lower_TF_df, macd_cols='def', limit_zones=7),
        calculate_macd_ranges(lower_TF_df, macd_cols='low1', limit_zones=7)
    ]

    # بررسی هر شرط و ارزیابی نتیجه
    for condition in conditions:
        divergence_result = detect_divergence(condition, check_for=check_for)
        if divergence_result in expected_results:
            return True  # حداقل یکی از شرایط درست است

    return False  # هیچ شرطی برقرار نیست







def check_divergence(df, check_for = "Bearish_Divergence", macd_cols='def', limit_zones=7):
    """
    check_for = ["Bearish_Divergence", "Bullish_Divergence"]
    mocd_cols = ["low2 = 3-6-2", "low1 = 6-13-5", "def = 12-26-9", "high = 48-104-36"]
    limit_zones >= 7
    """
    df1 = calculate_macd_ranges(df, macd_cols = macd_cols, limit_zones = limit_zones)
    result = detect_divergence(df1, check_for = check_for)
    return result


# /////// Advanced

def find_local_extremes(df, macd_col, price_col, min_candles=2):
    """
    این تابع نقاط بیشینه و کمینه محلی در یک محدوده طولانی MACD را برمی‌گرداند.
    ورودی‌ها:
        - df: دیتافریم شامل ستون MACD و قیمت
        - macd_col: نام ستون MACD
        - price_col: نام ستون قیمت (high یا low بسته به جهت MACD)
        - min_candles: تعداد حداقل کندل‌هایی که باید بین قله‌ها و دره‌ها فاصله باشد (برای صاف‌کردن)
    خروجی:
        - یک دیتافریم شامل زمان، مقدار MACD و قیمت در قله‌ها و دره‌ها
    """
    extremes = []
    
    # بررسی روند تغییرات MACD برای شناسایی قله‌ها و دره‌ها
    for i in range(min_candles, len(df) - min_candles):
        # بررسی قله محلی
        if df[macd_col].iloc[i] > df[macd_col].iloc[i - min_candles] and df[macd_col].iloc[i] > df[macd_col].iloc[i + min_candles]:
            extremes.append({
                'time': df['time'].iloc[i],
                'macd_extreme': df[macd_col].iloc[i],
                'price_extreme': df[price_col].iloc[i],
                'type': 'peak'
            })
        
        # بررسی دره محلی
        elif df[macd_col].iloc[i] < df[macd_col].iloc[i - min_candles] and df[macd_col].iloc[i] < df[macd_col].iloc[i + min_candles]:
            extremes.append({
                'time': df['time'].iloc[i],
                'macd_extreme': df[macd_col].iloc[i],
                'price_extreme': df[price_col].iloc[i],
                'type': 'trough'
            })

    # تبدیل لیست به دیتافریم برای خروجی
    extremes_df = pd.DataFrame(extremes)
    return extremes_df[['time', 'macd_extreme', 'price_extreme', 'type']]



import numpy as np
import pandas as pd

def calculate_macd_ranges_with_extremes(df, macd_cols='def', limit_zones=7, max_candle_count=50):
    """
    تابع اصلی که با رسیدن به 50 کندل، قله و دره‌های مکدی را شناسایی می‌کند
    """
    params = {
        "low2": ['macd_3_6_2', 'macdS_3_6_2'],
        "low1": ['macd_6_13_5', 'macdS_6_13_5'],
        "def": ['macd_12_26_9', 'macdS_12_26_9'],
        "high": ['macd_48_104_36', 'macdS_48_104_36'],
    }

    if macd_cols not in params:
        raise ValueError(f"Invalid macd_cols value: '{macd_cols}'. Please choose one of the following options: 'low2', 'low1', 'def', 'high'.")

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
    candle_count = 0
    all_extremes = []  # لیست برای ذخیره قله‌ها و دره‌ها

    for i in range(len(df) - 2, -1, -1):
        candle_count += 1

        # اگر تغییر علامت داشتیم یا به محدودیت کندل رسیدیم
        if df['macd_sign'].iloc[i] != current_sign or candle_count >= max_candle_count:
            range_df = df.iloc[i+1:start_index+1]
            
            if current_sign == 'positive':
                price_extreme = range_df['high'].max()
                macd_extreme = range_df[macd_col].max()
                time_extreme = range_df.loc[range_df['high'].idxmax(), 'time']
                price_col = 'high'
            else:
                price_extreme = range_df['low'].min()
                macd_extreme = range_df[macd_col].min()
                time_extreme = range_df.loc[range_df['low'].idxmin(), 'time']
                price_col = 'low'

            df.loc[i+1:start_index, 'range_extreme'] = price_extreme
            df.loc[i+1:start_index, 'macd_extreme'] = macd_extreme
            df.loc[i+1:start_index, 'range_number'] = range_number
            df.loc[i+1:start_index, 'time_extreme'] = time_extreme

            # ارسال داده‌ها به تابع کمکی اگر تعداد کندل‌ها از حد مجاز بیشتر بود
            if candle_count >= max_candle_count:
                extremes_df = find_local_extremes(range_df, macd_col, price_col)
                all_extremes.append(extremes_df)

            current_sign = df['macd_sign'].iloc[i]
            start_index = i
            range_number += 1
            candle_count = 0  # Reset candle count for new range

    # آخرین محدوده
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

    # در صورت وجود محدوده بلند، شناسایی قله‌ها و دره‌ها
    if len(range_df) >= max_candle_count:
        extremes_df = find_local_extremes(range_df, macd_col, price_col)
        all_extremes.append(extremes_df)

    # تجمیع تمامی قله‌ها و دره‌ها
    all_extremes_df = pd.concat(all_extremes, ignore_index=True) if all_extremes else pd.DataFrame()

    # خروجی نهایی
    return df, all_extremes_df[['time', 'macd_extreme', 'price_extreme', 'type']]



if __name__ == "__main__":
    # نمونه‌ای از داده‌ها برای آزمایش
    data = {
        'time': pd.date_range(start="2024-10-11", periods=20, freq='H'),  # افزایش تعداد سطرها به 20
        'open': np.random.random(20) * 100,
        'high': np.random.random(20) * 100 + 50,
        'low': np.random.random(20) * 100,
        'close': np.random.random(20) * 100,
        'macd_12_26_9': np.random.randn(20),
        'macdS_12_26_9': np.random.randn(20)
    }
    df = pd.DataFrame(data)
    
    # فراخوانی تابع check_divergence و نمایش نتیجه
    check_for = "Bearish_Divergence"
    macd_cols = 'def'
    limit_zones = 7
    
    result = check_divergence(df, check_for=check_for, macd_cols=macd_cols, limit_zones=limit_zones)
    print("Divergence Result:", result)  
