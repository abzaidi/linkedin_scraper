
# Web Scraper

This repository contains three scrapers:

- Google Jobs Scraper
- Linkedin Post Scraper
- Linkedin Jobs Scraper
## Run Locally

Clone the project

```bash
  git clone https://github.com/abzaidi/linkedin_scraper.git
```

Go to the project directory

```bash
  cd linkedin_scraper
```

Create a virtual environment using

```bash
  python -m venv venv
```

Activate the environment using

```bash
  venv\Scripts\activate
```

Install the packages using

```bash
  pip install -r requirements.txt
```

- create a .env file in the root directory

Then download the chrome driver from this link


```bash
  https://googlechromelabs.github.io/chrome-for-testing/#stable
```

- Make sure the driver matches your google chrome version and then download for you operating system.

- Unzip the chrome driver and move the .exe file in your root directory of the scraper

Now go to


```bash
  cd linkedin_scraper
```

Run the server:

```bash
  streamlit run app.py
```

The server will run.
