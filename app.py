import streamlit as st
from serpapi import GoogleSearch
import pandas as pd
import datetime

st.set_page_config(page_title="Professional Hire Finder", page_icon="🕵️‍♂️", layout="wide")

# --- SECRET HANDLING ---
if "SERPAPI_KEY" in st.secrets:
    api_key = st.secrets["SERPAPI_KEY"]
else:
    api_key = st.sidebar.text_input("SerpApi Key:", type="password", help="Get your key at serpapi.com")

# --- SIDEBAR INPUTS ---
st.sidebar.header("Search Parameters")
target_company = st.sidebar.text_input("Target Company", value="Google")
target_title = st.sidebar.text_input("Job Title", value="Product Manager")

# Month Selection
all_months = [
    "January", "February", "March", "April", "May", "June", 
    "July", "August", "September", "October", "November", "December"
]
current_year = datetime.datetime.now().year
selected_months = st.sidebar.multiselect("Months Joined", options=all_months, default=["August", "September"])
selected_year = st.sidebar.selectbox("Year Joined", options=[current_year, current_year-1], index=0)

# --- MAIN UI ---
st.title("🕵️‍♂️ Professional Hire Finder")
st.write(f"Searching for **{target_title}s** who joined **{target_company}** in **{', '.join(selected_months)} {selected_year}**.")

if st.button("Run Search"):
    if not api_key:
        st.error("Please provide a SerpApi Key.")
    elif not selected_months:
        st.warning("Please select at least one month.")
    else:
        all_results = []
        
        # We use a status container to show progress
        with st.status("Searching LinkedIn profiles...", expanded=True) as status:
            for month in selected_months:
                status.write(f"Querying {month} {selected_year}...")
                
                # Dynamic Query Builder
                # Logic: site:linkedin.com/in/ "Title" "Company" "Started Month Year"
                query = f'site:linkedin.com/in/ "{target_title}" "{target_company}" "Started {month} {selected_year}"'
                
                try:
                    search = GoogleSearch({
                        "engine": "google",
                        "q": query,
                        "api_key": api_key,
                        "num": 10  # Top 10 results per month
                    })
                    
                    results = search.get_dict().get("organic_results", [])
                    
                    for r in results:
                        all_results.append({
                            "Name": r.get("title").split("-")[0].strip(),
                            "Company": target_company,
                            "Title": target_title,
                            "Joined": f"{month} {selected_year}",
                            "Profile Link": r.get("link"),
                            "Snippet": r.get("snippet")
                        })
                except Exception as e:
                    st.error(f"Search failed for {month}: {e}")
            
            status.update(label="Search complete!", state="complete", expanded=False)

        # --- DISPLAY RESULTS ---
        if all_results:
            df = pd.DataFrame(all_results)
            
            # Clean up: Remove duplicates if any
            df = df.drop_duplicates(subset=['Profile Link'])
            
            st.success(f"Found {len(df)} potential matches!")
            
            # Make links clickable in the dataframe
            st.dataframe(
                df, 
                column_config={
                    "Profile Link": st.column_config.LinkColumn("LinkedIn Profile")
                },
                use_container_width=True
            )
            
            # Download CSV
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Results as CSV",
                data=csv,
                file_name=f"{target_company}_new_hires.csv",
                mime="text/csv",
            )
        else:
            st.warning("No results found. LinkedIn profiles sometimes take weeks to be indexed by Google.")

# --- INSTRUCTIONS ---
with st.expander("How this works"):
    st.info("""
    1. This app uses 'Google Dorking' to find public LinkedIn profiles.
    2. It specifically looks for the string **'Started [Month] [Year]'** which appears when someone updates their LinkedIn experience.
    3. Note: If a user has a 'Private' profile or has blocked search engines, they will not appear here.
    """)
