import numpy as np
import pandas as pd

def calculate_moving_average(data, window):
    """
    Calculate Simple Moving Average (SMA) for a given data series.
    
    Args:
        data (pandas.Series): Price data
        window (int): Window size for moving average
        
    Returns:
        pandas.Series: Moving average values
    """
    return data.rolling(window=window).mean()


def calculate_rsi(data, window=14):
    """
    Calculate Relative Strength Index (RSI).
    
    Args:
        data (pandas.Series): Price data
        window (int): RSI period/window
        
    Returns:
        pandas.Series: RSI values
    """
    # Calculate price changes
    delta = data.diff()
    
    # Create gain (positive) and loss (negative) Series
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    
    # Calculate average gain and loss over the specified period
    avg_gain = gain.rolling(window=window).mean()
    avg_loss = loss.rolling(window=window).mean()
    
    # Calculate the relative strength (RS)
    rs = avg_gain / avg_loss
    
    # Calculate RSI
    rsi = 100 - (100 / (1 + rs))
    
    return rsi


def calculate_macd(data, fast_period=12, slow_period=26, signal_period=9):
    """
    Calculate Moving Average Convergence Divergence (MACD).
    
    Args:
        data (pandas.Series): Price data
        fast_period (int): Fast EMA period
        slow_period (int): Slow EMA period
        signal_period (int): Signal line EMA period
        
    Returns:
        tuple: (MACD line, Signal line, Histogram)
    """
    # Calculate fast and slow EMAs
    ema_fast = data.ewm(span=fast_period, adjust=False).mean()
    ema_slow = data.ewm(span=slow_period, adjust=False).mean()
    
    # Calculate MACD line
    macd_line = ema_fast - ema_slow
    
    # Calculate signal line (EMA of MACD line)
    signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
    
    # Calculate histogram (MACD line - Signal line)
    histogram = macd_line - signal_line
    
    return macd_line, signal_line, histogram


def calculate_bollinger_bands(data, window=20, num_std=2):
    """
    Calculate Bollinger Bands.
    
    Args:
        data (pandas.Series): Price data
        window (int): Window/period for moving average
        num_std (int): Number of standard deviations for bands
        
    Returns:
        tuple: (Upper band, Middle band, Lower band)
    """
    # Calculate middle band (simple moving average)
    middle_band = data.rolling(window=window).mean()
    
    # Calculate standard deviation
    std = data.rolling(window=window).std()
    
    # Calculate upper and lower bands
    upper_band = middle_band + (std * num_std)
    lower_band = middle_band - (std * num_std)
    
    return upper_band, middle_band, lower_band


def calculate_atr(high, low, close, window=14):
    """
    Calculate Average True Range (ATR).
    
    Args:
        high (pandas.Series): High prices
        low (pandas.Series): Low prices
        close (pandas.Series): Close prices
        window (int): Window/period for ATR
        
    Returns:
        pandas.Series: ATR values
    """
    # Calculate True Range
    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())
    
    tr = pd.DataFrame({
        'tr1': tr1,
        'tr2': tr2,
        'tr3': tr3
    }).max(axis=1)
    
    # Calculate ATR
    atr = tr.rolling(window=window).mean()
    
    return atr
