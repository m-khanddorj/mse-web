from sqlalchemy.orm import Session
import pandas as pd
from datetime import date, datetime
from typing import List, Optional, Dict, Any, Union

from . import models

def get_stock_by_symbol(db: Session, symbol: str):
    """
    Get a stock by its symbol.
    
    Args:
        db (Session): Database session
        symbol (str): Stock symbol
        
    Returns:
        models.Stock: Stock object if found, None otherwise
    """
    return db.query(models.Stock).filter(models.Stock.symbol == symbol).first()

def get_stock_by_id(db: Session, stock_id: int):
    """
    Get a stock by its ID.
    
    Args:
        db (Session): Database session
        stock_id (int): Stock ID
        
    Returns:
        models.Stock: Stock object if found, None otherwise
    """
    return db.query(models.Stock).filter(models.Stock.id == stock_id).first()

def get_all_stocks(db: Session, skip: int = 0, limit: int = 100):
    """
    Get all stocks with pagination.
    
    Args:
        db (Session): Database session
        skip (int): Number of records to skip
        limit (int): Maximum number of records to return
        
    Returns:
        List[models.Stock]: List of stocks
    """
    return db.query(models.Stock).offset(skip).limit(limit).all()

def create_stock(db: Session, symbol: str, name: Optional[str] = None, description: Optional[str] = None):
    """
    Create a new stock.
    
    Args:
        db (Session): Database session
        symbol (str): Stock symbol
        name (Optional[str]): Stock name
        description (Optional[str]): Stock description
        
    Returns:
        models.Stock: Created stock object
    """
    stock = models.Stock(symbol=symbol, name=name, description=description)
    db.add(stock)
    db.commit()
    db.refresh(stock)
    return stock

def get_stock_price_data(db: Session, stock_id: int, start_date: Optional[date] = None, end_date: Optional[date] = None):
    """
    Get price data for a stock with optional date range.
    
    Args:
        db (Session): Database session
        stock_id (int): Stock ID
        start_date (Optional[date]): Start date for filter
        end_date (Optional[date]): End date for filter
        
    Returns:
        List[models.StockPrice]: List of stock price data
    """
    query = db.query(models.StockPrice).filter(models.StockPrice.stock_id == stock_id)
    
    if start_date:
        query = query.filter(models.StockPrice.date >= start_date)
    
    if end_date:
        query = query.filter(models.StockPrice.date <= end_date)
    
    return query.order_by(models.StockPrice.date).all()

def stock_price_data_to_dataframe(price_data: List[models.StockPrice]) -> pd.DataFrame:
    """
    Convert a list of StockPrice objects to a pandas DataFrame.
    
    Args:
        price_data (List[models.StockPrice]): List of stock price data
        
    Returns:
        pd.DataFrame: DataFrame with price data
    """
    data = {
        'Date': [item.date for item in price_data],
        'Open': [item.open for item in price_data],
        'High': [item.high for item in price_data],
        'Low': [item.low for item in price_data],
        'Close': [item.close for item in price_data]
    }
    
    # Add Volume if available
    if all(item.volume is not None for item in price_data):
        data['Volume'] = [item.volume for item in price_data]
    
    # Add Adjusted Close if available
    if all(item.adjusted_close is not None for item in price_data):
        data['Adjusted Close'] = [item.adjusted_close for item in price_data]
    
    df = pd.DataFrame(data)
    return df

def save_price_data_from_dataframe(db: Session, stock_id: int, df: pd.DataFrame):
    """
    Save price data from a pandas DataFrame to the database.
    
    Args:
        db (Session): Database session
        stock_id (int): Stock ID
        df (pd.DataFrame): DataFrame with price data
        
    Returns:
        int: Number of records added
    """
    # Ensure DataFrame has required columns
    required_columns = ['Date', 'Open', 'High', 'Low', 'Close']
    if not all(col in df.columns for col in required_columns):
        raise ValueError(f"DataFrame must contain all required columns: {required_columns}")
    
    # Ensure Date column is datetime
    if not pd.api.types.is_datetime64_any_dtype(df['Date']):
        df['Date'] = pd.to_datetime(df['Date'])
    
    # Get existing dates for this stock to avoid duplicates
    existing_dates = {
        row[0] for row in db.query(models.StockPrice.date).filter(models.StockPrice.stock_id == stock_id).all()
    }
    
    records_added = 0
    
    for _, row in df.iterrows():
        date_value = row['Date'].date() if isinstance(row['Date'], datetime) else row['Date']
        
        # Skip if this date already exists
        if date_value in existing_dates:
            continue
        
        # Create new price record
        price_data = models.StockPrice(
            stock_id=stock_id,
            date=date_value,
            open=float(row['Open']),
            high=float(row['High']),
            low=float(row['Low']),
            close=float(row['Close']),
            volume=float(row['Volume']) if 'Volume' in row and not pd.isna(row['Volume']) else None,
            adjusted_close=float(row['Adjusted Close']) if 'Adjusted Close' in row and not pd.isna(row['Adjusted Close']) else None
        )
        
        db.add(price_data)
        records_added += 1
    
    # Commit if any records were added
    if records_added > 0:
        db.commit()
    
    return records_added

def save_analysis(db: Session, name: str, stock_id: int, params: Dict[str, Any]):
    """
    Save an analysis configuration.
    
    Args:
        db (Session): Database session
        name (str): Analysis name
        stock_id (int): Stock ID
        params (Dict[str, Any]): Analysis parameters
        
    Returns:
        models.SavedAnalysis: Saved analysis object
    """
    analysis = models.SavedAnalysis(
        name=name,
        stock_id=stock_id,
        start_date=params.get('start_date'),
        end_date=params.get('end_date'),
        chart_type=params.get('chart_type'),
        show_ma=params.get('show_ma', False),
        ma_periods=','.join(map(str, params.get('ma_periods', []))) if 'ma_periods' in params else None,
        show_rsi=params.get('show_rsi', False),
        rsi_period=params.get('rsi_period'),
        show_macd=params.get('show_macd', False),
        macd_fast=params.get('macd_fast'),
        macd_slow=params.get('macd_slow'),
        macd_signal=params.get('macd_signal'),
        show_bbands=params.get('show_bbands', False),
        bbands_period=params.get('bbands_period'),
        bbands_std=params.get('bbands_std')
    )
    
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    return analysis

def get_all_saved_analyses(db: Session, skip: int = 0, limit: int = 100):
    """
    Get all saved analyses with pagination.
    
    Args:
        db (Session): Database session
        skip (int): Number of records to skip
        limit (int): Maximum number of records to return
        
    Returns:
        List[models.SavedAnalysis]: List of saved analyses
    """
    return db.query(models.SavedAnalysis).offset(skip).limit(limit).all()

def get_saved_analysis(db: Session, analysis_id: int):
    """
    Get a saved analysis by ID.
    
    Args:
        db (Session): Database session
        analysis_id (int): Analysis ID
        
    Returns:
        models.SavedAnalysis: Saved analysis object if found, None otherwise
    """
    return db.query(models.SavedAnalysis).filter(models.SavedAnalysis.id == analysis_id).first()

def delete_saved_analysis(db: Session, analysis_id: int):
    """
    Delete a saved analysis.
    
    Args:
        db (Session): Database session
        analysis_id (int): Analysis ID
        
    Returns:
        bool: True if deleted, False otherwise
    """
    analysis = db.query(models.SavedAnalysis).filter(models.SavedAnalysis.id == analysis_id).first()
    if not analysis:
        return False
    
    db.delete(analysis)
    db.commit()
    return True