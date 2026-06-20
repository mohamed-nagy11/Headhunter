import streamlit as st
import pandas as pd
import os
import pycountry
from main import run_full_pipeline

# Generate mapping from pycountry (sorted alphabetically)
country_map = {country.name: country.alpha_2.lower() for country in sorted(pycountry.countries, key=lambda x: x.name)}

# 1. Page Configuration
st.set_page_config(
    page_title="AI Headhunter Agent", 
    page_icon="🕵️‍♂️", 
    layout="wide"
)

# 2. Main Header
st.title("🕵️‍♂️ AI HR Headhunter Agent")
st.markdown("Automate your candidate sourcing, enrichment, and semantic ranking in seconds.")
st.divider()

# 3. Input Section
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("1. Job Requirements")
    raw_jd = st.text_area(
        "Paste the Job Description or core requirements here:", 
        height=150, 
        placeholder="e.g., Looking for a Senior Python Developer with 5+ years of experience in FastAPI, Docker, and AWS."
    )

with col2:
    st.subheader("2. Target Location")
    target_country_names = st.multiselect(
        "Search and select target countries:", 
        options=list(country_map.keys()),
        placeholder="e.g., Egypt, United Arab Emirates"
    )
    limit = st.slider(
        "Search limit per country:",
        min_value=1,
        max_value=100,
        value=5,
        step=1,
        help="The maximum number of candidate profiles to source from each country."
    )

st.divider()

# 4. Action Button & Pipeline Execution
if st.button("🚀 Start AI Sourcing Pipeline", type="primary", use_container_width=True):
    
    if not raw_jd or not target_country_names:
        st.warning("⚠️ Please provide both a Job Description and at least one Target Location before starting.")
    else:
        # Use st.status to show a cool loading animation while the backend works
        with st.status("Executing AI Pipeline (This may take a minute)...", expanded=True) as status:
            st.write("🧠 Initializing Groq Query Agent...")
            st.write("🔍 Sourcing candidates via Renidly API...")
            st.write("⚖️ Enriching profiles and semantic ranking...")
            
            # Call your actual backend function!
            try:
                iso_codes = [country_map[name] for name in target_country_names]
                candidates, excel_path = run_full_pipeline(
                    raw_jd=raw_jd, 
                    target_country_names=target_country_names, 
                    target_iso_codes=iso_codes,
                    limit=limit
                )
                status.update(label="Pipeline Complete!", state="complete", expanded=False)
                success = True
            except Exception as e:
                status.update(label=f"Pipeline Failed: {e}", state="error", expanded=False)
                success = False

        # 5. Display Results
        if success and candidates:
            st.success(f"Successfully sourced and ranked {len(candidates)} candidates!")
            
            # Display the interactive dataframe on the website
            st.subheader("📊 Shortlist Results")
            df = pd.DataFrame(candidates)
            
            # We configure the dataframe to make URLs clickable
            st.dataframe(
                df, 
                use_container_width=True,
                column_config={
                    "Profile URL": st.column_config.LinkColumn("Profile URL")
                }
            )
            
            # 6. Provide the Excel Download Button
            if os.path.exists(excel_path):
                with open(excel_path, "rb") as file:
                    st.download_button(
                        label="📥 Download Excel Report",
                        data=file,
                        file_name="Headhunter_Shortlist.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
        elif success and not candidates:
            st.error("The search completed, but no candidates matched those specific criteria.")