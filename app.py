import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
from utils.data_processor import load_data, get_unique_values, filter_data, calculate_market_indicators
from utils.visualization import create_sales_trend_chart, create_indicator_chart

# Page config
st.set_page_config(
    page_title="Automotive Market Analysis Dashboard",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Define the color scheme
colors = {
    "primary": "#1E88E5",
    "success": "#43A047",
    "accent": "#FFC107",
    "background": "#FAFAFA",
    "text": "#212121"
}

# Initialize session state for filters
if 'filters' not in st.session_state:
    st.session_state.filters = {}

def main():
    # Header
    st.title("🚗 Automotive Market Analysis Dashboard")
    st.markdown("### Comprehensive automotive sales data analysis and visualization")
    
    # Load data
    data = load_data()
    
    # Check if data exists
    if data is None:
        st.error("No data found. Please ensure your data file exists at 'data/automotive_sales.csv'")
        st.markdown("""
        ## Data Requirements
        
        This dashboard expects a CSV file at `data/automotive_sales.csv` with columns like:
        
        - **date**: The sales date (format: YYYY-MM-DD)
        - **brand**: Car manufacturer/brand
        - **model**: Car model
        - **sales_count**: Number of cars sold
        - **price**: Car price
        - **region**: Geographic region of sale
        - **vehicle_type**: Type of vehicle (e.g., SUV, Sedan)
        - **fuel_type**: Fuel type (e.g., Gasoline, Electric)
        - **year**: Model year
        
        Please upload your data to this location to use the dashboard.
        """)
        return
    
    # Sidebar for filters
    with st.sidebar:
        st.header("Filters")
        
        # Date range filter if date column exists
        if 'date' in data.columns:
            min_date = data['date'].min().date()
            max_date = data['date'].max().date()
            date_range = st.date_input(
                "Date Range",
                [min_date, max_date],
                min_value=min_date,
                max_value=max_date
            )
            
            if len(date_range) == 2:
                start_date, end_date = date_range
                data = data[(data['date'].dt.date >= start_date) & (data['date'].dt.date <= end_date)]
        
        # Brand filter
        if 'brand' in data.columns:
            brand_options = ['All'] + get_unique_values(data, 'brand')
            selected_brands = st.multiselect("Brand", brand_options, default="All")
            
            if 'All' not in selected_brands and selected_brands:
                st.session_state.filters['brand'] = selected_brands
            else:
                if 'brand' in st.session_state.filters:
                    del st.session_state.filters['brand']
        
        # Year filter
        if 'year' in data.columns:
            year_options = ['All'] + [str(year) for year in get_unique_values(data, 'year')]
            selected_years = st.multiselect("Year", year_options, default="All")
            
            if 'All' not in selected_years and selected_years:
                st.session_state.filters['year'] = [int(year) for year in selected_years if year != 'All']
            else:
                if 'year' in st.session_state.filters:
                    del st.session_state.filters['year']
        
        # Region filter
        if 'region' in data.columns:
            region_options = ['All'] + get_unique_values(data, 'region')
            selected_regions = st.multiselect("Region", region_options, default="All")
            
            if 'All' not in selected_regions and selected_regions:
                st.session_state.filters['region'] = selected_regions
            else:
                if 'region' in st.session_state.filters:
                    del st.session_state.filters['region']
        
        # Vehicle type filter
        if 'vehicle_type' in data.columns:
            vehicle_type_options = ['All'] + get_unique_values(data, 'vehicle_type')
            selected_vehicle_types = st.multiselect("Vehicle Type", vehicle_type_options, default="All")
            
            if 'All' not in selected_vehicle_types and selected_vehicle_types:
                st.session_state.filters['vehicle_type'] = selected_vehicle_types
            else:
                if 'vehicle_type' in st.session_state.filters:
                    del st.session_state.filters['vehicle_type']
        
        # Apply all filters
        filtered_data = filter_data(data, st.session_state.filters)
        
        # Reset filters button
        if st.button("Reset Filters"):
            st.session_state.filters = {}
            st.rerun()
        
        st.write("---")
        st.markdown("### About")
        st.markdown("""
        This dashboard provides comprehensive analysis of automotive sales data.
        Navigate through the pages to explore different aspects of the market.
        
        **Pages:**
        - Home: Overview and Key Metrics
        - Sales Trends: Time Series Analysis
        - Brand Performance: Competitive Analysis
        - Price Analysis: Distribution and Trends
        - Geographic Insights: Regional Analysis
        - Export Data: Download Analytics
        """)
    
    # Main area - Overview Dashboard
    
    # Apply filters
    filtered_data = filter_data(data, st.session_state.filters)
    
    # Calculate market indicators
    indicators = calculate_market_indicators(filtered_data)
    
    # Key metrics row
    st.subheader("Key Market Indicators")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Sales",
            value=f"{indicators['total_sales']:,}",
            delta=None
        )
    
    with col2:
        st.metric(
            label="Average Price",
            value=f"${indicators['avg_price']:,.2f}",
            delta=f"{indicators['price_trend']:.1f}%" if indicators['price_trend'] != 0 else None
        )
    
    with col3:
        st.metric(
            label="Sales Growth",
            value=f"{indicators['sales_growth']:.1f}%",
            delta=None
        )
    
    with col4:
        st.metric(
            label="Top Brand",
            value=indicators['top_brand'],
            delta=None
        )
    
    st.markdown("---")
    
    # Sales Trend Chart
    st.subheader("Recent Sales Trends")
    
    # Check if we have the necessary columns for a trend chart
    if 'date' in filtered_data.columns and 'sales_count' in filtered_data.columns:
        # Group by date
        sales_trend_data = filtered_data.groupby(filtered_data['date'].dt.date)['sales_count'].sum().reset_index()
        sales_trend_data.columns = ['date', 'sales_count']
        
        # Create and display chart
        sales_chart = create_sales_trend_chart(
            sales_trend_data,
            x_col='date',
            y_col='sales_count',
            title='Daily Sales Trend'
        )
        st.plotly_chart(sales_chart, use_container_width=True)
    else:
        st.warning("Unable to generate sales trend chart. Required columns not found in data.")
    
    # Two column layout for additional charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Brand Market Share")
        if 'brand' in filtered_data.columns:
            from utils.visualization import create_market_share_chart
            
            market_share_chart = create_market_share_chart(
                filtered_data,
                category_col='brand',
                value_col='sales_count' if 'sales_count' in filtered_data.columns else None,
                title='Brand Market Share'
            )
            st.plotly_chart(market_share_chart, use_container_width=True)
        else:
            st.warning("Brand information not available in data.")
    
    with col2:
        st.subheader("Price Distribution")
        if 'price' in filtered_data.columns:
            from utils.visualization import create_price_distribution_chart
            
            price_dist_chart = create_price_distribution_chart(
                filtered_data,
                price_col='price',
                title='Price Distribution'
            )
            st.plotly_chart(price_dist_chart, use_container_width=True)
        else:
            st.warning("Price information not available in data.")
    
    st.markdown("---")
    
    # Bottom section with additional insight
    st.subheader("Additional Insights")
    
    if 'vehicle_type' in filtered_data.columns and 'sales_count' in filtered_data.columns:
        from utils.visualization import create_brand_performance_chart
        
        vehicle_type_chart = create_brand_performance_chart(
            filtered_data,
            brand_col='vehicle_type',
            value_col='sales_count',
            title='Sales by Vehicle Type'
        )
        st.plotly_chart(vehicle_type_chart, use_container_width=True)
    elif 'vehicle_type' in filtered_data.columns:
        from utils.visualization import create_brand_performance_chart
        
        # If no sales_count column, we'll just count rows
        vehicle_type_data = filtered_data['vehicle_type'].value_counts().reset_index()
        vehicle_type_data.columns = ['vehicle_type', 'count']
        
        vehicle_type_chart = create_brand_performance_chart(
            vehicle_type_data,
            brand_col='vehicle_type',
            value_col='count',
            title='Count by Vehicle Type'
        )
        st.plotly_chart(vehicle_type_chart, use_container_width=True)
    else:
        st.info("Navigate to other pages using the sidebar to explore more detailed analyses.")

if __name__ == "__main__":
    main()
