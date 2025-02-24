import scrapy
import undetected_chromedriver as uc
from scrapy.http import HtmlResponse
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import urllib.parse
import time
import random
import os

class LinkedInJobSpider(scrapy.Spider):
    name = "linkedin_job"
    allowed_domains = ["linkedin.com"]

    DATE_POSTED_OPTIONS = {
        "past 24 hours": "r86400",
        "past week": "r604800",
        "past month": "r2592000",
        "any time": "",
    }

    EXPERIENCE_LEVEL_OPTIONS = {
        "internship": "1",
        "entry level": "2",
        "associate": "3",
        "mid senior level": "4",
        "director": "5",
        "executive": "6",
        "any level": ""
    }

    JOB_TYPE_OPTIONS = {
        "on site": "1",
        "remote": "2",
        "hybrid": "3",
        "any level": ""
    }

    def __init__(self, *args, **kwargs):
        super(LinkedInJobSpider, self).__init__(*args, **kwargs)

        # ✅ Get values dynamically from environment variables (set by Streamlit UI)
        self.KEYWORDS = os.getenv("LINKEDIN_JOB_KEYWORDS", "Python Developer").split(",")
        self.LOCATION = os.getenv("LINKEDIN_JOB_LOCATION", "United States")
        self.SESSION_ID = os.getenv("LINKEDIN_JOB_SESSION_ID", "")
        self.DATE_POSTED = os.getenv("LINKEDIN_JOB_DATE_POSTED", "past 24 hours").lower()
        self.EXPERIENCE_LEVELS = os.getenv("LINKEDIN_JOB_EXPERIENCE_LEVELS", "").split(",")
        self.JOB_TYPES = os.getenv("LINKEDIN_JOB_TYPES", "").split(",")

        # ✅ Ensure session ID is properly passed
        self.COOKIES = {'li_at': self.SESSION_ID}

        # ✅ Generate the URL dynamically
        self.start_urls = [self.build_linkedin_jobs_url(self.KEYWORDS, self.LOCATION, self.DATE_POSTED, self.EXPERIENCE_LEVELS, self.JOB_TYPES)]
        self.scraped_urls = set()


    # SESSION_ID = 'AQEDAVfxB5UFTrdQAAABlR5UOzwAAAGVQmC_PFYAf7CMEwRIp0SZD_EYgPT5w_GcspTCtgoHGUKwvaz4dyXVYm75ojI9WZORnfC4_RBOcT4k5hE-iPouB12jPIuzT9ZZc8AloYTacnU1sKTuIxJetAhw'

    def build_linkedin_jobs_url(self, keywords, location, date_posted, experience_levels, job_types):
        """Builds a LinkedIn Jobs Search URL dynamically based on user inputs."""
        base_url = "https://www.linkedin.com/jobs/search/?"

        formatted_keywords = ", ".join([f"{keyword}" for keyword in keywords])
        encoded_keywords = urllib.parse.quote(formatted_keywords)
        encoded_location = urllib.parse.quote(location)

        # ✅ Get selected filters dynamically
        date_posted_value = self.DATE_POSTED_OPTIONS.get(date_posted, "")
        experience_level_values = ",".join([self.EXPERIENCE_LEVEL_OPTIONS.get(level.lower(), "") for level in experience_levels if level.lower() in self.EXPERIENCE_LEVEL_OPTIONS])
        job_type_values = ",".join([self.JOB_TYPE_OPTIONS.get(jt.lower(), "") for jt in job_types if jt.lower() in self.JOB_TYPE_OPTIONS])

        # ✅ Construct the LinkedIn Jobs search URL with filters
        params = {
            "keywords": encoded_keywords,
            "location": encoded_location,
            "f_TPR": date_posted_value,
            "f_E": experience_level_values,
            "f_WT": job_type_values,
        }

        # ✅ Remove empty parameters
        params = {k: v for k, v in params.items() if v}

        return base_url + "&".join([f"{k}={v}" for k, v in params.items()])


    custom_settings = {
        'FEEDS': {
            'data/%(name)s_%(time)s.json': {'format': 'json'},
            'data/%(name)s_%(time)s.csv': {'format': 'csv'},
        },
    }

    # COOKIES = {
    #     'li_at': SESSION_ID,
    # }


    def start_requests(self):
        """ Start requests with LinkedIn session cookies. """
        for url in self.start_urls:
            yield scrapy.Request(
                url=url,
                cookies=self.COOKIES,
                callback=self.parse
            )

    def parse(self, response):
        """ Load LinkedIn job search results with Selenium, paginate through pages, and extract job URLs. """
        
        sleep_time = random.uniform(3, 5)
        
        options = uc.ChromeOptions()
        options.binary_location = "/usr/bin/google-chrome"
        driver = uc.Chrome(options=options)

        driver.maximize_window()

        driver.delete_all_cookies()

        driver.get("https://www.linkedin.com")
        time.sleep(sleep_time) 

        for name, value in self.COOKIES.items():
            driver.add_cookie({"name": name, "value": value})

        time.sleep(sleep_time) 

        driver.get(response.url)
        time.sleep(sleep_time) 

        page = 1 
        last_page = None 
        self.all_job_urls = set()

        while True:  
            self.logger.info(f"Extracting job listings from page {page}")

            self.scroll_to_load_jobs(driver, max_scrolls=10)

            wait = WebDriverWait(driver, 10)
            try:
                wait.until(EC.presence_of_element_located((By.XPATH, '//li//a[contains(@class, "job-card-container__link")]')))
            except:
                self.logger.info("Timeout: No job links found within 15 seconds.")

            search_page_html = driver.page_source

            new_response = HtmlResponse(url=response.url, body=search_page_html, encoding='utf-8')

            job_urls = new_response.xpath('//a[contains(@class, "job-card-container__link")]/@href').getall()
            
            print(f"Extracted {len(job_urls)} job URLs from page {page}")

            absolute_job_urls = [
                f"https://www.linkedin.com{url}" if url.startswith("/") else url for url in job_urls
            ]

            random.shuffle(absolute_job_urls)

            self.all_job_urls.update(absolute_job_urls)

            print(f"Extracted {len(job_urls)} job URLs from page {page}")
            self.logger.info(f"Total unique job URLs collected so far: {len(self.all_job_urls)}")

            for job_url in absolute_job_urls:
                yield scrapy.Request(
                    url=job_url,
                    cookies=self.COOKIES,
                    callback=self.parse_job_page
                )
                
            try:
                pagination_buttons = driver.find_elements(By.XPATH, '//button[contains(@aria-label, "Page ")]')
                last_page_button = pagination_buttons[-1]

                if last_page is None: 
                    last_page = int(last_page_button.get_attribute("aria-label").split("Page ")[1])

                if page >= last_page: 
                    print("Reached the last page, stopping pagination.")
                    break

                next_page_number = page + 1
                next_page_button = driver.find_element(By.XPATH, f'//button[@aria-label="Page {next_page_number}"]')
                driver.execute_script("arguments[0].click();", next_page_button)
                
                time.sleep(random.uniform(3, 6))

                page += 1

            except Exception as e:
                print(f"No more pages found or error navigating pages: {e}")
                break 
        
        print(f"✅ Total job URLs extracted across all pages: {len(self.all_job_urls)}")
        self.logger.info(f"✅ Final total job URLs: {len(self.all_job_urls)}")

        driver.quit()



    def parse_job_page(self, response):
        """ Load LinkedIn job detail page with Selenium, extract data, and save response as HTML. """

        self.scraped_urls.add(response.url)

        if response.status != 200:
            self.logger.warning(f"Skipping job {response.url} due to response status {response.status}")
            return

        sleep_time = random.uniform(3, 5)

        options = uc.ChromeOptions()
        options.binary_location = "/usr/bin/google-chrome"
        driver = uc.Chrome(options=options)

        driver.get("https://www.linkedin.com")

        time.sleep(sleep_time) 
        for name, value in self.COOKIES.items():
            driver.add_cookie({"name": name, "value": value})

        time.sleep(sleep_time) 

        driver.get(response.url)

        time.sleep(sleep_time) 

        self.human_scroll(driver)
        self.human_mouse_movements(driver)

        wait = WebDriverWait(driver, 10)
        try:
            wait.until(EC.presence_of_element_located((By.XPATH, '//div[@class="job-view-layout jobs-details"]')))
        except:
            self.logger.info("Timeout: No job title found.")
        
        time.sleep(sleep_time) 

        job_page_html = driver.page_source

        try:
            job_title = driver.find_element(By.XPATH, '//div[@class="t-14 artdeco-card"]//h1').text.strip()
        except:
            job_title = None

        try:
            company_name = driver.find_element(By.XPATH, '//div[@class="job-details-jobs-unified-top-card__company-name"]//a').text.strip()
        except:
            company_name = None

        try:
            location = driver.find_element(By.XPATH, '//div[@class="job-details-jobs-unified-top-card__primary-description-container"]//div//span[1]').text.strip()
        except:
            location = None

        try:
            time_posted_elements = driver.find_elements(By.XPATH, '//div[@class="job-details-jobs-unified-top-card__primary-description-container"]//div//span[3]//span')
            time_posted = " ".join([element.text.strip() for element in time_posted_elements if element.text.strip()])
        except:
            time_posted = None

        try:
            hiring_manager = driver.find_element(By.XPATH, '//div[contains(@class, "job-details-people-who-can-help__section")]//strong').text.strip()
            name_parts = hiring_manager.split()
            if len(name_parts) > 1:
                hiring_manager_first_name = name_parts[0]
                hiring_manager_last_name = " ".join(name_parts[1:])
            else:
                hiring_manager_first_name = hiring_manager
                hiring_manager_last_name = None 
        except:
            hiring_manager_first_name, hiring_manager_last_name = None, None

        try:
            hiring_manager_profile = driver.find_element(By.XPATH, '//div[contains(@class, "job-details-people-who-can-help__section")]//a').get_attribute("href")
        except:
            hiring_manager_profile = None

        try:
            job_description = driver.find_element(By.XPATH, '//div[contains(@class, "jobs-description__content")]').get_attribute('innerText').strip()
        except:
            job_description = None

        time.sleep(sleep_time) 
        driver.quit()

        yield {
            "job_title": job_title,
            "company_name": company_name,
            "location": location,
            "time_posted": time_posted,
            "hiring_manager_first_name": hiring_manager_first_name,
            "hiring_manager_last_name": hiring_manager_last_name,
            "hiring_manager_profile": hiring_manager_profile,
            "job_url": response.url,
            "job_description": job_description,
        }

        time.sleep(sleep_time) 


    def human_scroll(self, driver):
        for _ in range(random.randint(2, 5)): 
            driver.execute_script("window.scrollBy(0, 500);") 
            time.sleep(random.uniform(2, 5)) 

    def human_mouse_movements(self, driver):
        action = ActionChains(driver)
        
        window_size = driver.get_window_size()
        max_x = window_size["width"] - 100 
        max_y = window_size["height"] - 100

        for _ in range(random.randint(3, 7)):
            x_offset = random.randint(50, max_x - 50)
            y_offset = random.randint(50, max_y - 50)
            
            try:
                action.move_by_offset(x_offset, y_offset).perform()
            except Exception as e:
                print(f"Mouse movement error: {e}")

            time.sleep(random.uniform(0.5, 1.5))
    
    def scroll_to_load_jobs(self, driver, max_scrolls=5):
        """Scroll down to load more job listings"""
        try:
            jobs_block = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.scaffold-layout__list '))
            )

            n = 0  

            for _ in range(max_scrolls):
                jobs_list = jobs_block.find_elements(By.CSS_SELECTOR, '.job-card-container__link')

                if len(jobs_list) == 0:
                    print("No job listings found, stopping scroll")
                    break

                for job in jobs_list[n:]:  
                    driver.execute_script("arguments[0].scrollIntoView();", job)
                    time.sleep(random.uniform(1.5, 3))  

                    n += 1  
                    print(f"Scrolled to job {n}")

                updated_jobs_list = jobs_block.find_elements(By.CSS_SELECTOR, '.job-card-container__link')
                if len(updated_jobs_list) == len(jobs_list):
                    print("No new jobs loaded, stopping scroll")
                    break  

        except Exception as e:
            print(f"Error scrolling job list: {e}")