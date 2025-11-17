import pandas as pd

def find_pattern(df, jump_threshold=2.0):
    patterns = []
    
    df = df.copy()
    df['change'] = df['price'].pct_change() * 100
    
    # 1. Find sharp rising patterns (above threshold)
    big_jumps = df[df['change'] > jump_threshold]
    if len(big_jumps) > 0:
        patterns.append(f"Sharp rises (>{jump_threshold}%): {len(big_jumps)} times")
        max_jump = df['change'].max()
        patterns.append(f"Max increase: {max_jump:.2f}%")
    
    # 2. Find sharp falling patterns
    big_drops = df[df['change'] < -jump_threshold]
    if len(big_drops) > 0:
        patterns.append(f"Sharp drops (<-{jump_threshold}%): {len(big_drops)} times")
        min_drop = df['change'].min()
        patterns.append(f"Max decrease: {min_drop:.2f}%")
    
    # 3. Volatility patterns by time period
    try:
        time_vols = [
            ['00:00', '03:00'],
            ['03:00', '06:00'],
            ['06:00', '09:00'],
            ['09:00', '12:00'],
            ['12:00', '15:00'],
            ['15:00', '18:00'],
            ['18:00', '21:00'],
            ['21:00', '23:59'],
        ]
        for vol in time_vols:
            period_vol = df.between_time(vol[0], vol[1])['change'].std()
            patterns.append(f"Volatility ({vol[0]} - {vol[1]}): {period_vol:.2f}%")

    except:
        # If time filtering fails, calculate overall volatility
        overall_vol = df['change'].std()
        patterns.append(f"Overall volatility: {overall_vol:.2f}%")
    
    # 4. Price trend
    price_change = ((df['price'].iloc[-1] - df['price'].iloc[0]) / df['price'].iloc[0]) * 100
    patterns.append(f"Total price change: {price_change:.2f}%")
    
    return patterns

