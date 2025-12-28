import streamlit as st
from serpapi import GoogleSearch
import pandas as pd
import datetime

st.set_page_config(page_title="Google PM New Hire Finder", page_icon="🔍")

# --- SECRET HANDLING ---
# This checks if the key exists in secrets.toml (local) or Streamlit Cloud (web)
if "SERPAPI_KEY" in st.secrets:
    api_key = st.secrets["SERPAPI_KEY"]
else:
    # Fallback: if no secret is found, show the sidebar input
    api_key = st.sidebar.text_input("SerpApi Key not found in secrets. Enter here:", type="password")

st.title("🔍 Google PM New Hire Finder")
st.write("Targeting folks who joined Google in the last 4-6 months.")

def get_target_months():
    # Calculate 4-6 months ago dynamically
    today = datetime.datetime.now()
    months = []
    for i in range(4, 7):  # 4, 5, 6 months ago
        month_date = today - datetime.timedelta(days=30 * i)
        month_str = month_date.strftime("%B %Y")
        months.append(month_str)
    return months

if st.button("Search for New Hires"):
    if not api_key:
        st.error("Please provide a SerpApi Key via secrets.toml or the sidebar.")
    else:
        target_months = get_target_months()
        all_results = []
        
        with st.spinner('Searching LinkedIn via Google...'):
            for month in target_months:
                # Optimized query for LinkedIn's "Started [Month] [Year]" format
                query = f'site:linkedin.com/in/ "Product Manager" "Google" "Started {month}"'
                
                search = GoogleSearch({
                    "engine": "google",
                    "q": query,
                    "api_key": api_key,
                    "num": 10
                })
                
                results = search.get_dict().get("organic_results", [])
                for r in results:
                    all_results.append({
                        "Name": r.get("title").split("-")[0].strip(),
                        "Started": month,
                        "Profile": r.get("link"),
                        "Snippet": r.get("snippet")
                    })

        if all_results:
            df = pd.DataFrame(all_results)
            st.success(f"Found {len(df)} profiles!")
            st.dataframe(df)
            
            # Download link
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("Download Results", csv, "google_new_pms.csv", "text/csv")
        else:
            st.warning("No results found. Note: Google indexing can take time for very recent hires.")
