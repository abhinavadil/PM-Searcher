#!/usr/bin/env python3
"""
PM-Searcher Streamlit App
Searches for LinkedIn profiles of Product Managers at Google who started in the last 4-6 months
"""

import streamlit as st
import pandas as pd
from serpapi import GoogleSearch
from datetime import datetime, timedelta
import os

# Page configuration
st.set_page_config(
    page_title="PM-Searcher",
    page_icon="🔍",
    layout="wide"
)

# Title
st.title("🔍 PM-Searcher")
st.markdown("Search for LinkedIn profiles of Product Managers at Google")

# Sidebar for API key
st.sidebar.header("Configuration")
api_key = st.sidebar.text_input(
    "SerpApi Key",
    type="password",
    help="Enter your SerpApi API key. Get one at https://serpapi.com/"
)

# Calculate date range for last 4-6 months
def get_date_range():
    """Calculate the date range for profiles started 4-6 months ago"""
    today = datetime.now()
    six_months_ago = today - timedelta(days=180)  # ~6 months
    four_months_ago = today - timedelta(days=120)  # ~4 months
    return four_months_ago, six_months_ago

def get_month_strings():
    """Get month strings for the last 4-6 months"""
    today = datetime.now()
    months = []
    for i in range(4, 7):  # 4, 5, 6 months ago
        month_date = today - timedelta(days=30 * i)
        month_str = month_date.strftime("%B %Y")  # e.g., "January 2024"
        months.append(month_str)
    return months

def run_search(api_key, month_str):
    """
    Search for LinkedIn profiles using SerpApi with specific month
    
    Args:
        api_key: SerpApi API key
        month_str: Month string in format "Month YYYY" (e.g., "January 2024")
    
    Returns:
        List of profile results
    """
    if not api_key:
        return []
    
    try:
        params = {
            "engine": "google",
            "q": f'site:linkedin.com/in/ "Product Manager" "Google" "Started {month_str}"',
            "api_key": api_key
        }
        search = GoogleSearch(params)
        return search.get_dict().get("organic_results", [])
    except Exception as e:
        st.error(f"Error searching for {month_str}: {str(e)}")
        return []

def search_linkedin_profiles(api_key, num_results=10):
    """
    Search for LinkedIn profiles across multiple months (4-6 months ago)
    
    Args:
        api_key: SerpApi API key
        num_results: Number of results per month (default: 10)
    
    Returns:
        List of profile dictionaries
    """
    if not api_key:
        st.error("Please enter your SerpApi key in the sidebar")
        return []
    
    all_profiles = []
    month_strings = get_month_strings()
    
    # Search for each month
    for month_str in month_strings:
        results = run_search(api_key, month_str)
        
        # Extract profile data from results
        for result in results:
            profile_data = {
                "Name": result.get("title", "N/A"),
                "LinkedIn URL": result.get("link", "N/A"),
                "Snippet": result.get("snippet", "N/A"),
                "Position": "Product Manager",
                "Company": "Google",
                "Started Month": month_str
            }
            all_profiles.append(profile_data)
    
    return all_profiles

# Main app logic
if api_key:
    st.sidebar.success("API key configured")
    
    # Search parameters
    st.sidebar.subheader("Search Parameters")
    num_results = st.sidebar.slider("Number of results", 10, 50, 10)
    
    # Date range info
    four_months, six_months = get_date_range()
    st.sidebar.info(
        f"Looking for profiles started between:\n"
        f"{four_months.strftime('%B %Y')} and {six_months.strftime('%B %Y')}"
    )
    
    # Search button
    if st.button("🔍 Search Profiles", type="primary"):
        with st.spinner("Searching for Product Manager profiles across multiple months..."):
            profiles = search_linkedin_profiles(api_key, num_results)
            
            if profiles:
                # Create DataFrame
                df = pd.DataFrame(profiles)
                
                # Display results
                st.success(f"Found {len(df)} profiles")
                st.dataframe(df, use_container_width=True)
                
                # Store in session state for download
                st.session_state['profiles_df'] = df
                
                # Download CSV button
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📥 Download CSV",
                    data=csv,
                    file_name=f"pm_profiles_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    type="primary"
                )
            else:
                st.warning("No profiles found. Try adjusting your search parameters.")
else:
    st.info("👈 Please enter your SerpApi key in the sidebar to begin searching")
    st.markdown("""
    ### How to get started:
    1. Sign up for a free account at [SerpApi](https://serpapi.com/)
    2. Get your API key from the dashboard
    3. Enter it in the sidebar
    4. Click "Search Profiles" to find Product Managers at Google
    """)

# Footer
st.markdown("---")
st.markdown(
    "<small>Note: This app searches for LinkedIn profiles. "
    "Manual verification may be needed to confirm start dates (4-6 months ago).</small>",
    unsafe_allow_html=True
)

