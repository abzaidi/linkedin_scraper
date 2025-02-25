import streamlit as st
import subprocess
import os
import time
import pandas as pd
import signal

st.set_page_config(page_title="Scraper Dashboard", layout="wide")

st.sidebar.title("Navigation")
page = st.sidebar.radio("Select Scraper", ["Google Jobs Scraper", "LinkedIn Post Scraper", "LinkedIn Job Scraper"])


# ======================== GOOGLE JOBS SCRAPER PAGE ========================
if page == "Google Jobs Scraper":
    st.title("Google Jobs Scraper")

    keywords = st.text_area("Enter job keywords (comma-separated)", "Python Developer, Django, Remote, London")

    scrolls = st.slider("Number of Scrolls", min_value=0, max_value=10, value=3)


    if st.button("Start Scraping"):
        st.write("Scraping in progress... Please wait.")

        formatted_keywords = keywords.split(",")  
        formatted_keywords = [kw.strip() for kw in formatted_keywords]  

        os.environ["SCRAPER_KEYWORDS"] = ",".join(formatted_keywords)
        os.environ["SCRAPER_SCROLLS"] = str(scrolls)

        process = subprocess.run(["scrapy", "crawl", "google_jobs"], capture_output=True, text=True)

        time.sleep(5)

        files = os.listdir("data")
        csv_files = [f for f in files if f.endswith(".csv")]
        
        if csv_files:
            latest_file = max(csv_files, key=lambda f: os.path.getctime(os.path.join("data", f)))
            csv_path = os.path.join("data", latest_file)

            st.success("Scraping completed successfully!")
            
            df = pd.read_csv(csv_path)
            st.write("### Scraped Job Listings")
            st.dataframe(df)

            with open(csv_path, "rb") as file:
                st.download_button(
                    label="📥 Download CSV",
                    data=file,
                    file_name="scraped_jobs.csv",
                    mime="text/csv"
                )
            
            try:
                os.remove(csv_path)
            except Exception as e:
                st.error(f"Error deleting file: {e}")
        else:
            st.error("No data files found!")

# ======================== LINKEDIN POST SCRAPER PAGE ========================
elif page == "LinkedIn Post Scraper":
    st.title("LinkedIn Post Scraper")

    linkedin_keywords = st.text_area("Enter search keywords (comma-separated)", "Python Developer, Jobs, Remote")

    linkedin_scrolls = st.slider("Number of Scrolls", min_value=0, max_value=10, value=2)

    session_id = st.text_input("Enter your LinkedIn Session ID (li_at)", "YOUR_SESSION_ID_HERE", type="password")

    if st.button("Start Scraping"):
        st.write("Scraping in progress... Please wait.")

        formatted_keywords = linkedin_keywords.split(",")  
        formatted_keywords = [kw.strip() for kw in formatted_keywords]  

        os.environ["LINKEDIN_KEYWORDS"] = ",".join(formatted_keywords)
        os.environ["LINKEDIN_SCROLLS"] = str(linkedin_scrolls)
        os.environ["LINKEDIN_SESSION_ID"] = session_id

  
        process = subprocess.run(["scrapy", "crawl", "linkedin_post"], capture_output=True, text=True)

        time.sleep(5)

        files = os.listdir("data")
        csv_files = [f for f in files if f.endswith(".csv")]
        
        if csv_files:
            latest_file = max(csv_files, key=lambda f: os.path.getctime(os.path.join("data", f)))
            csv_path = os.path.join("data", latest_file)

            st.success("Scraping completed successfully!")
            
            df = pd.read_csv(csv_path)
            st.write("### Scraped LinkedIn Posts")
            st.dataframe(df)

            with open(csv_path, "rb") as file:
                st.download_button(
                    label="📥 Download CSV",
                    data=file,
                    file_name="linkedin_posts.csv",
                    mime="text/csv"
                )
            
            try:
                os.remove(csv_path)
            except Exception as e:
                st.error(f"Error deleting file: {e}")
        else:
            st.error("No data files found!")
    

# ======================== LINKEDIN JOB SCRAPER PAGE ========================
elif page == "LinkedIn Job Scraper":
    st.title("LinkedIn Job Scraper")

    job_keywords = st.text_area("Enter job keywords (comma-separated)", "Python Developer, Django")
    location = st.text_input("Enter job location", "United States")
    session_id = st.text_input("Enter your LinkedIn Session ID (li_at)", "YOUR_SESSION_ID_HERE", type="password")

    date_posted_options = ["Past 24 hours", "Past Week", "Past Month", "Any Time"]
    selected_date_posted = st.selectbox("Date Posted", date_posted_options, index=0)

    experience_level_options = ["Internship", "Entry Level", "Associate", "Mid Senior Level", "Director", "Executive", "Any Level"]
    selected_experience_levels = st.multiselect("Experience Level (Select multiple if needed)", experience_level_options, default=[])

    job_type_options = ["On Site", "Remote", "Hybrid", "Any Level"]
    selected_job_types = st.multiselect("Job Type (Select multiple if needed)", job_type_options, default=[])

    if st.button("Start Scraping"):
        st.write("Scraping in progress... Please wait.")

        os.environ["LINKEDIN_JOB_KEYWORDS"] = ",".join(job_keywords.split(","))
        os.environ["LINKEDIN_JOB_LOCATION"] = location
        os.environ["LINKEDIN_JOB_SESSION_ID"] = session_id
        os.environ["LINKEDIN_JOB_DATE_POSTED"] = selected_date_posted.lower()
        os.environ["LINKEDIN_JOB_EXPERIENCE_LEVELS"] = ",".join(selected_experience_levels)
        os.environ["LINKEDIN_JOB_TYPES"] = ",".join(selected_job_types)

        process = subprocess.run(["scrapy", "crawl", "linkedin_job"], capture_output=True, text=True)
        
        
        time.sleep(5)

        files = os.listdir("data")
        csv_files = [f for f in files if f.endswith(".csv")]

        if csv_files:
            latest_file = max(csv_files, key=lambda f: os.path.getctime(os.path.join("data", f)))
            csv_path = os.path.join("data", latest_file)

            st.success("Scraping completed successfully!")
            df = pd.read_csv(csv_path)
            st.dataframe(df)

            with open(csv_path, "rb") as file:
                st.download_button("📥 Download CSV", data=file, file_name="linkedin_jobs.csv", mime="text/csv")
            
            try:
                os.remove(csv_path)
            except Exception as e:
                st.error(f"Error deleting file: {e}")
        else:
            st.error("No data files found!")
    