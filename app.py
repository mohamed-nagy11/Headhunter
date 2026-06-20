import streamlit as st
import pandas as pd
import os
from main import run_full_pipeline

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
    target_location = st.text_input(
        "Geographical boundary:", 
        placeholder="e.g., Egypt, Remote, San Francisco"
    )

st.divider()

# 4. Action Button & Pipeline Execution
if st.button("🚀 Start AI Sourcing Pipeline", type="primary", use_container_width=True):
    
    if not raw_jd or not target_location:
        st.warning("⚠️ Please provide both a Job Description and a Target Location before starting.")
    else:
        # Use st.status to show a cool loading animation while the backend works
        with st.status("Executing AI Pipeline (This may take a minute)...", expanded=True) as status:
            st.write("🧠 Initializing Groq Query Agent...")
            st.write("🔍 Sourcing candidates via Renidly API...")
            st.write("⚖️ Enriching profiles and semantic ranking...")
            
            # Call your actual backend function!
            try:
                candidates, excel_path = run_full_pipeline(raw_jd=raw_jd, target_location=target_location)
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