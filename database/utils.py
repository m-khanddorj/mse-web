import pandas as pd
import os
from sqlalchemy.orm import Session
from contextlib import contextmanager

from . import connection, models, crud

def init_database():
    """
    Initialize the database by creating tables if they don't exist.
    """
    connection.init_db()

@contextmanager
def get_db_session():
    """
    Context manager for database sessions.
    
    Yields:
        Session: SQLAlchemy session
    """
    db = connection.SessionLocal()
    try:
        yield db
    finally:
        db.close()

def import_sample_data_to_db():
    """
    Import sample CSV files to the database.
    
    Returns:
        dict: Dictionary with stock symbols as keys and number of records imported as values
    """
    sample_dir = "sample_data"
    results = {}
    
    if not os.path.exists(sample_dir):
        return results
    
    # Get list of CSV files in the sample_data directory
    sample_files = [f for f in os.listdir(sample_dir) if f.endswith('.csv')]
    
    for file_name in sample_files:
        # Extract symbol from filename (remove .csv extension)
        symbol = file_name.split('.')[0]
        file_path = os.path.join(sample_dir, file_name)
        
        # Import data
        try:
            with get_db_session() as db:
                # Check if stock exists, create if not
                stock = crud.get_stock_by_symbol(db, symbol)
                if not stock:
                    stock = crud.create_stock(db, symbol=symbol)
                
                # Load CSV data
                df = pd.read_csv(file_path)
                
                # Convert date column
                if 'Date' in df.columns:
                    df['Date'] = pd.to_datetime(df['Date'])
                
                # Save to database
                records_added = crud.save_price_data_from_dataframe(db, stock.id, df)
                results[symbol] = records_added
        
        except Exception as e:
            print(f"Error importing {file_name}: {str(e)}")
            results[symbol] = str(e)
    
    return results

def load_data_from_db(symbol, start_date=None, end_date=None):
    """
    Load stock data from the database.
    
    Args:
        symbol (str): Stock symbol
        start_date (date, optional): Start date filter
        end_date (date, optional): End date filter
        
    Returns:
        pandas.DataFrame: DataFrame with stock price data, or None if not found
    """
    with get_db_session() as db:
        # Get stock by symbol
        stock = crud.get_stock_by_symbol(db, symbol)
        if not stock:
            return None
        
        # Get price data
        price_data = crud.get_stock_price_data(db, stock.id, start_date, end_date)
        if not price_data:
            return None
        
        # Convert to DataFrame
        df = crud.stock_price_data_to_dataframe(price_data)
        return df

def save_csv_data_to_db(symbol, df):
    """
    Save data from a CSV file to the database.
    
    Args:
        symbol (str): Stock symbol
        df (pandas.DataFrame): DataFrame with price data
        
    Returns:
        tuple: (success, message) - A tuple with a boolean indicating success and a message
    """
    try:
        with get_db_session() as db:
            # Check if stock exists, create if not
            stock = crud.get_stock_by_symbol(db, symbol)
            if not stock:
                stock = crud.create_stock(db, symbol=symbol)
            
            # Save data
            records_added = crud.save_price_data_from_dataframe(db, stock.id, df)
            return True, f"Successfully added {records_added} records for {symbol}"
    
    except Exception as e:
        return False, f"Error saving data: {str(e)}"

def get_available_symbols():
    """
    Get a list of stock symbols available in the database.
    
    Returns:
        list: List of stock symbols
    """
    with get_db_session() as db:
        stocks = crud.get_all_stocks(db)
        return [stock.symbol for stock in stocks]

def save_analysis_config(name, symbol, params):
    """
    Save an analysis configuration.
    
    Args:
        name (str): Analysis name
        symbol (str): Stock symbol
        params (dict): Analysis parameters
        
    Returns:
        tuple: (success, message) - A tuple with a boolean indicating success and a message
    """
    try:
        with get_db_session() as db:
            # Get stock by symbol
            stock = crud.get_stock_by_symbol(db, symbol)
            if not stock:
                return False, f"Stock {symbol} not found in database"
            
            # Save analysis
            analysis = crud.save_analysis(db, name, stock.id, params)
            return True, f"Analysis saved with ID {analysis.id}"
    
    except Exception as e:
        return False, f"Error saving analysis: {str(e)}"

def get_saved_analyses():
    """
    Get a list of saved analyses.
    
    Returns:
        list: List of saved analyses with stock information
    """
    with get_db_session() as db:
        analyses = crud.get_all_saved_analyses(db)
        results = []
        
        for analysis in analyses:
            stock = crud.get_stock_by_id(db, analysis.stock_id)
            if stock:
                results.append({
                    'id': analysis.id,
                    'name': analysis.name,
                    'symbol': stock.symbol,
                    'created_at': analysis.created_at
                })
        
        return results

def load_saved_analysis(analysis_id):
    """
    Load a saved analysis configuration.
    
    Args:
        analysis_id (int): Analysis ID
        
    Returns:
        tuple: (stock_symbol, params) or (None, error_message)
    """
    try:
        with get_db_session() as db:
            analysis = crud.get_saved_analysis(db, analysis_id)
            if not analysis:
                return None, f"Analysis with ID {analysis_id} not found"
            
            stock = crud.get_stock_by_id(db, analysis.stock_id)
            if not stock:
                return None, f"Stock with ID {analysis.stock_id} not found"
            
            # Extract parameters
            params = {
                'start_date': analysis.start_date,
                'end_date': analysis.end_date,
                'chart_type': analysis.chart_type,
                'show_ma': analysis.show_ma,
                'ma_periods': [int(x) for x in analysis.ma_periods.split(',')] if analysis.ma_periods else [],
                'show_rsi': analysis.show_rsi,
                'rsi_period': analysis.rsi_period,
                'show_macd': analysis.show_macd,
                'macd_fast': analysis.macd_fast,
                'macd_slow': analysis.macd_slow,
                'macd_signal': analysis.macd_signal,
                'show_bbands': analysis.show_bbands,
                'bbands_period': analysis.bbands_period,
                'bbands_std': analysis.bbands_std
            }
            
            return stock.symbol, params
    
    except Exception as e:
        return None, f"Error loading analysis: {str(e)}"