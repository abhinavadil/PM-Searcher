import streamlit as st
from serpapi import GoogleSearch
import pandas as pd
import datetime
import re

st.set_page_config(page_title="PM Outreach & Job Navigator", page_icon="🚀", layout="wide")

# --- 1. TOP 30 COMPANIES & CAREER LINKS ---
# Mapping the top 30 tech companies to their direct PM job search URLs
TOP_PM_COMPANIES = {
    "Google": "https://careers.google.com/jobs/results/?q=\"Product Manager\"",
    "Meta": "https://www.metacareers.com/jobs/?q=Product%20Manager",
    "Amazon": "https://www.amazon.jobs/en/search?base_query=Product+Manager",
    "Apple": "https://jobs.apple.com/en-us/search?search=Product%20Manager",
    "Microsoft": "https://careers.microsoft.com/us/en/search-results?keywords=Product%20Manager",
    "Netflix": "https://jobs.netflix.com/search?q=Product%20Manager",
    "Stripe": "https://stripe.com/jobs/search?q=Product+Manager",
    "Airbnb": "https://careers.airbnb.com/results/?q=Product%20Manager",
    "NVIDIA": "https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite?q=Product+Manager",
    "OpenAI": "https://openai.com/careers/search?q=Product+Manager",
    "Uber": "https://www.uber.com/careers/list/?keywords=Product%20Manager",
    "Salesforce": "https://salesforce.wd1.myworkdayjobs.com/External_Career_Site?q=Product+Manager",
    "Snowflake": "https://careers.snowflake.com/us/en/search-results?keywords=Product+Manager",
    "Adobe": "https://adobe.wd5.myworkdayjobs.com/external_experienced?q=Product+Manager",
    "Spotify": "https://www.lifeatspotify.com/jobs?q=Product+Manager",
    "Atlassian": "https://www.atlassian.com/company/careers/all-jobs?search=Product%20Manager",
    "Roblox": "https://careers.roblox.com/jobs?q=Product%20Manager",
    "HubSpot": "https://www.hubspot.com/careers/jobs?query=Product%20Manager",
    "Notion": "https://www.notion.so/about/jobs",
    "Figma": "https://www.figma.com/careers/",
    "Databricks": "https://www.databricks.com/company/careers/open-positions?q=Product%20Manager",
    "Palantir": "https://www.palantir.com/careers/jobs/",
    "DoorDash": "https://careers.doordash.com/browse-jobs?keywords=Product%20Manager",
    "Instacart": "https://instacart.careers/jobs/?q=Product%20Manager",
    "Pinterest": "https://www.pinterestcareers.com/en/jobs/?search=Product%20Manager",
    "Coinbase": "https://www.coinbase.com/careers/positions?q=Product%20Manager",
    "ByteDance (TikTok)": "https://jobs.bytedance.com/en/position?keywords=Product%20Manager",
    "Tesla": "https://www.tesla.com/careers/search/?query=Product%20Manager",
    "LinkedIn": "https://www.linkedin.com/company/linkedin/jobs/?keywords=Product%20Manager",
    "Zoom": "https://careers.zoom.us/home?q=Product%20Manager"
}

# --- HELPER FUNCTIONS ---
def generate_note(template, name, company, month, year):
    # Basic personalization logic
    note = template.replace("{Name}", name).replace("{Company}", company)
    note = note.replace("{Month}", month).replace("{Year}", str(year))
    return note[:300] # LinkedIn limit is 300 characters

# --- SIDEBAR NAVIGATOR ---
st.sidebar.title("🛠 PM Toolbox")
tab_choice = st.sidebar.radio("Go to:", ["Find New Hires (Networking)", "PM Job Board (Applying)"])

# --- TAB 1: NEW HIRE SEARCH ---
if tab_choice == "Find New Hires (Networking)":
    st.title("🔍 New Hire Networking")
    
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
                st.info("💡 **Workflow:** Click the copy button on the code box, then click LinkedIn link to paste your message in the invite box.")

                # Displaying results in a clean custom list instead of a basic table
                for index, row in df.iterrows():
                    col1, col2, col3 = st.columns([1, 3, 1])
                    with col1:
                        st.markdown(f"**{row['Name']}**")
                        st.caption(row['Joined'])
                    with col2:
                        st.code(row['Note'], language=None)
                        st.caption("💡 Click the copy button above, then click LinkedIn link below")
                    with col3:
                        st.markdown(f"[🔗 Open LinkedIn]({row['Profile Link']})")
                        st.caption("Paste note in connection request")
                    st.divider()
            else:
                st.warning("No profiles found. Try broadening your search or changing months.")

    # --- HELP SECTION ---
    with st.expander("Pro-Tip: How to send the invite fast"):
        st.write("""
        1. Click the **copy button** on the code box next to a person.
        2. Click **🔗 Open LinkedIn** to go to their profile.
        3. On LinkedIn, click **'Connect'**.
        4. Click **'Add a note'**.
        5. Press **Cmd+V** (Paste) and hit **Send**.
        """)
    
    st.info("💡 Switch to the 'PM Job Board' tab in the sidebar to see live openings at top companies.")

# --- TAB 2: JOB BOARD NAVIGATOR ---
else:
    st.title("💼 PM Job Board Navigator")
    st.write("Quickly jump to the Product Manager career pages of the top 30 tech companies.")

    # Create a clean grid for the companies
    cols = st.columns(3)
    
    # Sort companies alphabetically
    sorted_companies = sorted(TOP_PM_COMPANIES.keys())

    for i, company in enumerate(sorted_companies):
        with cols[i % 3]:
            st.markdown(f"### {company}")
            career_url = TOP_PM_COMPANIES[company]
            # Big button-like link
            st.link_button(f"View PM Jobs at {company}", career_url, use_container_width=True)
            st.write("") # Spacer

    st.divider()
    st.subheader("💡 Tips for these sites:")
    st.markdown("""
    - **Workday/Lever/Greenhouse:** Many of these companies use these platforms. The links above are designed to trigger their internal search engines.
    - **Referrals:** If you found a new hire in the other tab, ask them for a referral *before* applying through these links!
    - **Filters:** Most links are pre-filtered for 'Product Manager', but you may need to select your preferred location (e.g., 'Remote' or 'San Francisco') manually.
    """)
