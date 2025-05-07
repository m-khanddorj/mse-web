from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from .connection import Base

class Stock(Base):
    """
    Stock model representing a stock/ticker
    """
    __tablename__ = "stocks"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    price_data = relationship("StockPrice", back_populates="stock", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Stock(symbol='{self.symbol}', name='{self.name}')>"

class StockPrice(Base):
    """
    StockPrice model representing daily price data for a stock
    """
    __tablename__ = "stock_prices"
    
    id = Column(Integer, primary_key=True, index=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False)
    date = Column(Date, nullable=False, index=True)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    adjusted_close = Column(Float, nullable=True)
    volume = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    stock = relationship("Stock", back_populates="price_data")
    
    # Composite unique constraint to prevent duplicate date entries for a stock
    __table_args__ = (
        {'sqlite_autoincrement': True},
    )
    
    def __repr__(self):
        return f"<StockPrice(stock='{self.stock.symbol if self.stock else None}', date='{self.date}', close={self.close})>"

class SavedAnalysis(Base):
    """
    SavedAnalysis model to store user analysis configurations
    """
    __tablename__ = "saved_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    chart_type = Column(String(20), nullable=True)  # Line or Candlestick
    show_ma = Column(Boolean, default=False)
    ma_periods = Column(String(100), nullable=True)  # Store as comma-separated values
    show_rsi = Column(Boolean, default=False)
    rsi_period = Column(Integer, nullable=True)
    show_macd = Column(Boolean, default=False)
    macd_fast = Column(Integer, nullable=True)
    macd_slow = Column(Integer, nullable=True)
    macd_signal = Column(Integer, nullable=True)
    show_bbands = Column(Boolean, default=False)
    bbands_period = Column(Integer, nullable=True)
    bbands_std = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<SavedAnalysis(name='{self.name}', stock_id={self.stock_id})>"