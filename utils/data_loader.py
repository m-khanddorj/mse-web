import pandas as pd
from io import StringIO

def validate_csv_data(file_content):
    """
    Validate if the uploaded CSV file has the correct format for stock price data.
    
    Args:
        file_content (StringIO): File content as StringIO object
        
    Returns:
        tuple: (is_valid, message) - A tuple containing a boolean indicating if data is valid
               and a message explaining the reason if invalid
    """
    try:
        # Read the first few rows to validate format
        df = pd.read_csv(file_content, nrows=5)
        
        # Check for date column (could be 'Date' or 'date')
        date_col_found = False
        date_col_name = None
        
        if 'Date' in df.columns:
            date_col_found = True
            date_col_name = 'Date'
        elif 'date' in df.columns:
            date_col_found = True
            date_col_name = 'date'
            
        if not date_col_found:
            return False, "Missing 'Date' column in the CSV file."
        
        # Check for required price columns
        required_columns = ['Open', 'High', 'Low', 'Close']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            return False, f"Missing required columns: {', '.join(missing_columns)}"
        
        # Try to convert date column to datetime to make sure it's in a valid format
        try:
            pd.to_datetime(df[date_col_name])
        except Exception as e:
            return False, f"Date column format is invalid: {str(e)}"
            
        # File is valid if we get here
        return True, "CSV format is valid."
        
    except Exception as e:
        return False, f"Error validating CSV file: {str(e)}"


def load_csv_data(file_path):
    """
    Load stock price data from a CSV file.
    
    Args:
        file_path (str): Path to the CSV file
        
    Returns:
        pandas.DataFrame: DataFrame containing the stock price data
    """
    try:
        # Read the CSV file
        df = pd.read_csv(file_path)
        
        # Convert date column to datetime
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'])
        elif 'date' in df.columns:
            df['Date'] = pd.to_datetime(df['date'])
            df = df.drop('date', axis=1)
            
        # Sort by date
        if 'Date' in df.columns:
            df = df.sort_values('Date')
        
        return df
        
    except Exception as e:
        print(f"Error loading CSV file: {str(e)}")
        return None
