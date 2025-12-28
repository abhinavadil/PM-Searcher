import streamlit as st
from serpapi import GoogleSearch
import pandas as pd
import datetime
import re
import urllib.parse

st.set_page_config(page_title="PM Hire Finder + Auto-Note", page_icon="🔍", layout="wide")

# --- CUSTOM MESSAGE LOGIC ---
def generate_note(template, name, company, month, year):
    # Basic personalization logic
    note = template.replace("{Name}", name).replace("{Company}", company)
    note = note.replace("{Month}", month).replace("{Year}", str(year))
    return note[:300] # LinkedIn limit is 300 characters

# --- SIDEBAR: TEMPLATE BUILDER ---
st.sidebar.header("1. Connection Note Template")
default_template = "Hi {Name}, noticed you recently joined {Company} as a PM (congrats on the {Month} start!). Would love to connect and follow your journey there."
user_template = st.sidebar.text_area("Customize Note (use {Name}, {Company}, {Month})", 
                                    value=default_template, 
                                    help="Max 300 chars. Placeholders will auto-fill.")
st.sidebar.caption(f"Length: {len(user_template)}/300 chars")

st.sidebar.divider()
st.sidebar.header("2. Search Parameters")
target_company = st.sidebar.text_input("Target Company", value="Google")
target_title = st.sidebar.text_input("Job Title", value="Product Manager")
all_months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
selected_months = st.sidebar.multiselect("Months Joined", options=all_months, default=["August", "September"])
selected_year = st.sidebar.selectbox("Year Joined", options=[2024, 2025], index=1)

# --- GOOGLE SEARCH API KEY ---
if "SERPAPI_KEY" in st.secrets:
    api_key = st.secrets["SERPAPI_KEY"]
else:
    api_key = st.sidebar.text_input("SerpApi Key:", type="password")

# --- MAIN UI ---
st.title("🔍 New Hire Finder & Outreach Tool")

if st.button("🚀 Find New Hires"):
    if not api_key:
        st.error("Please enter your SerpApi Key.")
    else:
        all_results = []
        with st.status("Searching LinkedIn...", expanded=True) as status:
            for month in selected_months:
                query = f'site:linkedin.com/in/ "{target_title}" "{target_company}" "Started {month} {selected_year}"'
                try:
                    search = GoogleSearch({"engine": "google", "q": query, "api_key": api_key, "num": 10})
                    results = search.get_dict().get("organic_results", [])
                    for r in results:
                        name = r.get("title").split("-")[0].strip()
                        # Clean name (remove emojis or titles)
                        name = name.split(",")[0].split("|")[0].strip()
                        
                        personalized_note = generate_note(user_template, name, target_company, month, selected_year)
                        
                        all_results.append({
                            "Name": name,
                            "Joined": f"{month} {selected_year}",
                            "Note": personalized_note,
                            "Profile Link": r.get("link")
                        })
                except Exception as e:
                    st.error(f"Search error: {e}")
            status.update(label="Search complete!", state="complete")

        if all_results:
            df = pd.DataFrame(all_results).drop_duplicates(subset=['Profile Link'])
            
            st.write("### Found Candidates")
            st.info("💡 **Workflow:** Click 'Copy Note' then click 'LinkedIn' to paste your message in the invite box.")

            # Displaying results in a clean custom list instead of a basic table
            for index, row in df.iterrows():
                col1, col2, col3 = st.columns([1, 3, 1])
                with col1:
                    st.markdown(f"**{row['Name']}**")
                    st.caption(row['Joined'])
                with col2:
                    st.code(row['Note'], language=None)
                    st.caption("💡 Click the copy button above the code box, then click LinkedIn link below")
                with col3:
                    st.markdown(f"[🔗 Open LinkedIn]({row['Profile Link']})")
                    st.caption("Paste note in connection request")
                st.divider()
        else:
            st.warning("No profiles found. Try broading your search or changing months.")

# --- HELP SECTION ---
with st.expander("Pro-Tip: How to send the invite fast"):
    st.write("""
    1. Click the **📋 Copy Note** button next to a person.
    2. Click **🔗 Open LinkedIn** to go to their profile.
    3. On LinkedIn, click **'Connect'**.
    4. Click **'Add a note'**.
    5. Press **Cmd+V** (Paste) and hit **Send**.
    """)
