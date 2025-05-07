import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

def create_price_chart(data, chart_type='Line', ma_periods=None):
    """
    Create a price chart with optional moving averages and Bollinger Bands.
    
    Args:
        data (pandas.DataFrame): DataFrame with price data
        chart_type (str): Chart type ('Line' or 'Candlestick')
        ma_periods (list): List of periods for moving averages
        
    Returns:
        plotly.graph_objects.Figure: Plotly figure object
    """
    if 'Date' not in data.columns:
        return go.Figure()
    
    # Create figure
    fig = go.Figure()
    
    # Add price data based on chart type
    if chart_type == 'Line':
        fig.add_trace(
            go.Scatter(
                x=data['Date'],
                y=data['Close'],
                name='Close Price',
                line=dict(color='royalblue', width=2)
            )
        )
    else:  # Candlestick
        fig.add_trace(
            go.Candlestick(
                x=data['Date'],
                open=data['Open'],
                high=data['High'],
                low=data['Low'],
                close=data['Close'],
                name='Price'
            )
        )
    
    # Add Bollinger Bands if available
    if all(col in data.columns for col in ['BB_Upper', 'BB_Middle', 'BB_Lower']):
        # Add upper band
        fig.add_trace(
            go.Scatter(
                x=data['Date'],
                y=data['BB_Upper'],
                name='Upper Bollinger Band',
                line=dict(color='rgba(250, 128, 114, 0.7)', width=1, dash='dot'),
                hoverinfo='skip'
            )
        )
        
        # Add middle band (SMA)
        fig.add_trace(
            go.Scatter(
                x=data['Date'],
                y=data['BB_Middle'],
                name='Middle Bollinger Band',
                line=dict(color='rgba(128, 128, 128, 0.7)', width=1, dash='dot'),
                hoverinfo='skip'
            )
        )
        
        # Add lower band
        fig.add_trace(
            go.Scatter(
                x=data['Date'],
                y=data['BB_Lower'],
                name='Lower Bollinger Band',
                line=dict(color='rgba(173, 216, 230, 0.7)', width=1, dash='dot'),
                hoverinfo='skip',
                fill='tonexty',
                fillcolor='rgba(173, 216, 230, 0.1)'
            )
        )
    
    # Add Moving Averages
    colors = ['red', 'orange', 'green', 'purple', 'brown', 'pink']
    
    if ma_periods:
        for i, period in enumerate(ma_periods):
            col_name = f'MA_{period}'
            if col_name in data.columns:
                color = colors[i % len(colors)]
                fig.add_trace(
                    go.Scatter(
                        x=data['Date'],
                        y=data[col_name],
                        name=f'{period}-day MA',
                        line=dict(color=color, width=1.5)
                    )
                )
    
    # Update layout
    fig.update_layout(
        title='Stock Price Chart',
        xaxis_title='Date',
        yaxis_title='Price',
        legend_title='Legend',
        xaxis_rangeslider_visible=False,
        height=500
    )
    
    fig.update_xaxes(
        rangeslider_visible=False,
        rangebreaks=[
            # Hide weekends
            dict(bounds=["sat", "mon"])
        ]
    )
    
    return fig


def create_volume_chart(data):
    """
    Create a volume chart.
    
    Args:
        data (pandas.DataFrame): DataFrame with volume data
        
    Returns:
        plotly.graph_objects.Figure: Plotly figure object
    """
    if 'Date' not in data.columns or 'Volume' not in data.columns:
        return go.Figure()
    
    # Create figure
    fig = go.Figure()
    
    # Add volume bars
    fig.add_trace(
        go.Bar(
            x=data['Date'],
            y=data['Volume'],
            name='Volume',
            marker=dict(color='rgba(58, 71, 80, 0.6)')
        )
    )
    
    # Update layout
    fig.update_layout(
        title='Trading Volume',
        xaxis_title='Date',
        yaxis_title='Volume',
        height=300
    )
    
    fig.update_xaxes(
        rangeslider_visible=False,
        rangebreaks=[
            # Hide weekends
            dict(bounds=["sat", "mon"])
        ]
    )
    
    return fig


def create_indicator_chart(data, main_line, secondary_line=None, histogram=None, 
                          y_min=None, y_max=None, reference_levels=None):
    """
    Create a chart for technical indicators.
    
    Args:
        data (pandas.DataFrame): DataFrame with indicator data
        main_line (str): Column name for the main line
        secondary_line (str, optional): Column name for the secondary line
        histogram (str, optional): Column name for histogram data
        y_min (float, optional): Minimum y-axis value
        y_max (float, optional): Maximum y-axis value
        reference_levels (list, optional): List of reference levels to draw on chart
        
    Returns:
        plotly.graph_objects.Figure: Plotly figure object
    """
    if 'Date' not in data.columns or main_line not in data.columns:
        return go.Figure()
    
    # Create figure
    fig = go.Figure()
    
    # Add main line
    fig.add_trace(
        go.Scatter(
            x=data['Date'],
            y=data[main_line],
            name=main_line,
            line=dict(color='blue', width=1.5)
        )
    )
    
    # Add secondary line if provided
    if secondary_line and secondary_line in data.columns:
        fig.add_trace(
            go.Scatter(
                x=data['Date'],
                y=data[secondary_line],
                name=secondary_line,
                line=dict(color='red', width=1.5)
            )
        )
    
    # Add histogram if provided
    if histogram and histogram in data.columns:
        colors = ['green' if val >= 0 else 'red' for val in data[histogram]]
        fig.add_trace(
            go.Bar(
                x=data['Date'],
                y=data[histogram],
                name=histogram,
                marker=dict(color=colors)
            )
        )
    
    # Add reference levels if provided
    if reference_levels:
        for level in reference_levels:
            fig.add_shape(
                type="line",
                x0=data['Date'].iloc[0],
                y0=level,
                x1=data['Date'].iloc[-1],
                y1=level,
                line=dict(
                    color="rgba(0, 0, 0, 0.5)",
                    width=1,
                    dash="dash",
                )
            )
    
    # Update layout
    title = main_line
    if secondary_line:
        title += f" and {secondary_line}"
    
    fig.update_layout(
        title=title,
        xaxis_title='Date',
        yaxis_title='Value',
        height=300
    )
    
    # Set y-axis range if provided
    if y_min is not None and y_max is not None:
        fig.update_yaxes(range=[y_min, y_max])
    
    fig.update_xaxes(
        rangeslider_visible=False,
        rangebreaks=[
            # Hide weekends
            dict(bounds=["sat", "mon"])
        ]
    )
    
    return fig
