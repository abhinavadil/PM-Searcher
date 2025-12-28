import streamlit as st
from serpapi import GoogleSearch
import pandas as pd
import datetime
import re

st.set_page_config(page_title="Professional Hire Finder Pro", page_icon="🕵️‍♂️", layout="wide")

# --- REGEX HELPERS ---
def extract_emails(text):
    if not text: return ""
    email_regex = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = re.findall(email_regex, text)
    return ", ".join(list(set(emails)))

def extract_phones(text):
    if not text: return ""
    # Simple regex for common phone formats
    phone_regex = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    phones = re.findall(phone_regex, text)
    return ", ".join(list(set(phones)))

# --- SECRET HANDLING ---
if "SERPAPI_KEY" in st.secrets:
    api_key = st.secrets["SERPAPI_KEY"]
else:
    api_key = st.sidebar.text_input("SerpApi Key:", type="password")

# --- SIDEBAR INPUTS ---
st.sidebar.header("Search Parameters")
target_company = st.sidebar.text_input("Target Company", value="Google")
target_title = st.sidebar.text_input("Job Title", value="Product Manager")

all_months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
current_year = datetime.datetime.now().year
selected_months = st.sidebar.multiselect("Months Joined", options=all_months, default=["August", "September"])
selected_year = st.sidebar.selectbox("Year Joined", options=[current_year, current_year-1], index=0)

st.sidebar.divider()
st.sidebar.header("Deep Search Options")
find_contacts = st.sidebar.checkbox("Try to find public emails/phones", value=False, help="Will add contact keywords to search. Low success rate but free.")

# --- MAIN UI ---
st.title("🕵️‍♂️ Professional Hire Finder + Contact Finder")

if st.button("Run Search"):
    if not api_key:
        st.error("Please provide a SerpApi Key.")
    elif not selected_months:
        st.warning("Please select at least one month.")
    else:
        all_results = []
        
        with st.status("Searching LinkedIn profiles...", expanded=True) as status:
            for month in selected_months:
                status.write(f"Querying {month} {selected_year}...")
                
                # BASE QUERY
                query = f'site:linkedin.com/in/ "{target_title}" "{target_company}" "Started {month} {selected_year}"'
                
                # ENHANCED CONTACT QUERY
                if find_contacts:
                    # Adding common public email patterns
                    query += ' ("@gmail.com" OR "@google.com" OR "contact me" OR "email")'
                
                try:
                    search = GoogleSearch({
                        "engine": "google", "q": query, "api_key": api_key, "num": 10
                    })
                    results = search.get_dict().get("organic_results", [])
                    
                    for r in results:
                        snippet_text = r.get("snippet", "")
                        found_email = extract_emails(snippet_text)
                        found_phone = extract_phones(snippet_text)
                        
                        all_results.append({
                            "Name": r.get("title").split("-")[0].strip(),
                            "Joined": f"{month} {selected_year}",
                            "Email Found": found_email if found_email else "Not public",
                            "Phone Found": found_phone if found_phone else "Not public",
                            "Profile Link": r.get("link"),
                            "Snippet": snippet_text
                        })
                except Exception as e:
                    st.error(f"Error: {e}")
            
            status.update(label="Search complete!", state="complete", expanded=False)

        if all_results:
            df = pd.DataFrame(all_results).drop_duplicates(subset=['Profile Link'])
            st.success(f"Found {len(df)} potential matches!")
            
            # Highlight columns with found emails
            st.dataframe(
                df, 
                column_config={
                    "Profile Link": st.column_config.LinkColumn("LinkedIn"),
                    "Email Found": st.column_config.TextColumn("📧 Email", help="Extracted from public snippet"),
                },
                use_container_width=True
            )
            
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Results", csv, f"{target_company}_contacts.csv", "text/csv")
        else:
            st.warning("No results. Try turning off 'Deep Search' if you get zero results.")
