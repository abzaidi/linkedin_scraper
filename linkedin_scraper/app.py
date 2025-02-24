import streamlit as st
import subprocess
import json
import os
import time
import pandas as pd
import signal

# Configure the Streamlit page layout
st.set_page_config(page_title="Scraper Dashboard", layout="wide")

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Select Scraper", ["Google Jobs Scraper", "LinkedIn Post Scraper", "LinkedIn Job Scraper"])


PROCESS_FILE = "scraper_process.json"

def save_process_id(spider_name, pid):
    """Save the PID of the Scrapy process."""
    processes = {}
    if os.path.exists(PROCESS_FILE):
        with open(PROCESS_FILE, "r") as f:
            processes = json.load(f)
    processes[spider_name] = pid
    with open(PROCESS_FILE, "w") as f:
        json.dump(processes, f)

def get_process_id(spider_name):
    """Retrieve the Scrapy process PID from the file."""
    if os.path.exists(PROCESS_FILE):
        with open(PROCESS_FILE, "r") as f:
            processes = json.load(f)
        return processes.get(spider_name)
    return None

def stop_scraping(spider_name):
    """Stop the Scrapy process for a given spider."""
    pid = get_process_id(spider_name)
    if pid:
        try:
            os.kill(pid, signal.SIGTERM)
            st.warning(f"{spider_name} scraping process stopped!")
        except ProcessLookupError:
            st.error("No running process found.")
    else:
        st.error("No active scraping process.")


# ======================== GOOGLE JOBS SCRAPER PAGE ========================
if page == "Google Jobs Scraper":
    st.title("Google Jobs Scraper")

    # User input for job keywords
    keywords = st.text_area("Enter job keywords (comma-separated)", "Python Developer, Django, Remote, London")

    # User input for scroll count
    scrolls = st.slider("Number of Scrolls", min_value=0, max_value=10, value=3)

    if "google_jobs_running" not in st.session_state:
        st.session_state.google_jobs_running = False

    # Start Scraping Button
    if st.button("Start Scraping"):
        st.write("Scraping in progress... Please wait.")

        # Convert user input into a Scrapy-friendly format
        formatted_keywords = keywords.split(",")  
        formatted_keywords = [kw.strip() for kw in formatted_keywords]  

        # Set environment variables (to avoid modifying the Spider code)
        os.environ["SCRAPER_KEYWORDS"] = ",".join(formatted_keywords)
        os.environ["SCRAPER_SCROLLS"] = str(scrolls)

        # Run Scrapy Spider
        process = subprocess.run(["scrapy", "crawl", "google_jobs"], capture_output=True, text=True)
        save_process_id("google_jobs", process.pid)
        st.session_state.google_jobs_running = True
        # Wait for the scraper to finish
        time.sleep(5)

        # Fetch latest scraped CSV file
        files = os.listdir("data")
        csv_files = [f for f in files if f.endswith(".csv")]
        
        if csv_files:
            latest_file = max(csv_files, key=lambda f: os.path.getctime(os.path.join("data", f)))
            csv_path = os.path.join("data", latest_file)

            st.success("Scraping completed successfully!")
            
            # Display results as a table
            df = pd.read_csv(csv_path)
            st.write("### Scraped Job Listings")
            st.dataframe(df)

            # Download Button
            with open(csv_path, "rb") as file:
                st.download_button(
                    label="📥 Download CSV",
                    data=file,
                    file_name="scraped_jobs.csv",
                    mime="text/csv"
                )
        else:
            st.error("No data files found!")
    if st.session_state.google_jobs_running:
        if st.button("Stop Scraping"):
            stop_scraping("google_jobs")

# ======================== LINKEDIN POST SCRAPER PAGE ========================
elif page == "LinkedIn Post Scraper":
    st.title("LinkedIn Post Scraper")

    # User input for LinkedIn keywords
    linkedin_keywords = st.text_area("Enter search keywords (comma-separated)", "Python Developer, Jobs, Remote")

    # User input for scroll count
    linkedin_scrolls = st.slider("Number of Scrolls", min_value=0, max_value=10, value=2)

    # User input for LinkedIn session ID
    session_id = st.text_input("Enter your LinkedIn Session ID (li_at)", "YOUR_SESSION_ID_HERE", type="password")

    if "linkedin_post_running" not in st.session_state:
        st.session_state.linkedin_post_running = False
    # Start Scraping Button
    if st.button("Start Scraping"):
        st.write("Scraping in progress... Please wait.")

        # Convert user input into a Scrapy-friendly format
        formatted_keywords = linkedin_keywords.split(",")  
        formatted_keywords = [kw.strip() for kw in formatted_keywords]  

        # Set environment variables (to avoid modifying the Spider code)
        os.environ["LINKEDIN_KEYWORDS"] = ",".join(formatted_keywords)
        os.environ["LINKEDIN_SCROLLS"] = str(linkedin_scrolls)
        os.environ["LINKEDIN_SESSION_ID"] = session_id

        # Run Scrapy Spider
        process = subprocess.run(["scrapy", "crawl", "linkedin_post"], capture_output=True, text=True)
        save_process_id("linkedin_post", process.pid)
        st.session_state.linkedin_post_running = True
        # Wait for the scraper to finish
        time.sleep(5)

        # Fetch latest scraped CSV file
        files = os.listdir("data")
        csv_files = [f for f in files if f.endswith(".csv")]
        
        if csv_files:
            latest_file = max(csv_files, key=lambda f: os.path.getctime(os.path.join("data", f)))
            csv_path = os.path.join("data", latest_file)

            st.success("Scraping completed successfully!")
            
            # Display results as a table
            df = pd.read_csv(csv_path)
            st.write("### Scraped LinkedIn Posts")
            st.dataframe(df)

            # Download Button
            with open(csv_path, "rb") as file:
                st.download_button(
                    label="📥 Download CSV",
                    data=file,
                    file_name="linkedin_posts.csv",
                    mime="text/csv"
                )
        else:
            st.error("No data files found!")
    
    if st.session_state.linkedin_post_running:
        if st.button("Stop Scraping"):
            stop_scraping("linkedin_post")

# ======================== LINKEDIN JOB SCRAPER PAGE ========================
elif page == "LinkedIn Job Scraper":
    st.title("LinkedIn Job Scraper")

    # Input fields
    job_keywords = st.text_area("Enter job keywords (comma-separated)", "Python Developer, Django")
    location = st.text_input("Enter job location", "United States")
    session_id = st.text_input("Enter your LinkedIn Session ID (li_at)", "YOUR_SESSION_ID_HERE", type="password")

    # Dropdowns for filtering
    date_posted_options = ["Past 24 hours", "Past Week", "Past Month", "Any Time"]
    selected_date_posted = st.selectbox("Date Posted", date_posted_options, index=0)

    experience_level_options = ["Internship", "Entry Level", "Associate", "Mid Senior Level", "Director", "Executive", "Any Level"]
    selected_experience_levels = st.multiselect("Experience Level (Select multiple if needed)", experience_level_options, default=[])

    job_type_options = ["On Site", "Remote", "Hybrid", "Any Level"]
    selected_job_types = st.multiselect("Job Type (Select multiple if needed)", job_type_options, default=[])

    if "linkedin_job_running" not in st.session_state:
        st.session_state.linkedin_job_running = False
    # Start Scraping Button
    if st.button("Start Scraping"):
        st.write("Scraping in progress... Please wait.")

        os.environ["LINKEDIN_JOB_KEYWORDS"] = ",".join(job_keywords.split(","))
        os.environ["LINKEDIN_JOB_LOCATION"] = location
        os.environ["LINKEDIN_JOB_SESSION_ID"] = session_id
        os.environ["LINKEDIN_JOB_DATE_POSTED"] = selected_date_posted.lower()
        os.environ["LINKEDIN_JOB_EXPERIENCE_LEVELS"] = ",".join(selected_experience_levels)
        os.environ["LINKEDIN_JOB_TYPES"] = ",".join(selected_job_types)

        process = subprocess.run(["scrapy", "crawl", "linkedin_job"], capture_output=True, text=True)
        save_process_id("linkedin_job", process.pid)
        st.session_state.linkedin_job_running = True
        
        
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
        else:
            st.error("No data files found!")
    
    if st.session_state.linkedin_job_running:
        if st.button("Stop Scraping"):
            stop_scraping("linkedin_job")