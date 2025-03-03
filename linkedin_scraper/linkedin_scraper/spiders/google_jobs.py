import scrapy
import undetected_chromedriver as uc
from scrapy.http import HtmlResponse
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import urllib.parse
import time
import random
import os

class GoogleJobsSpider(scrapy.Spider):
    name = "google_jobs"
    allowed_domains = ["google.com"]

    def __init__(self, *args, **kwargs):
        super(GoogleJobsSpider, self).__init__(*args, **kwargs)
        self.scraped_jobs = set()
        self.keywords = os.getenv("SCRAPER_KEYWORDS", "Python Developer").split(",")
        self.SCROLLS = int(os.getenv("SCRAPER_SCROLLS", 3))

    def google_jobs_url(self):
        base_url = "https://www.google.com/search?"
        formatted_keywords = ", ".join([f'"{keyword}"' for keyword in self.keywords])
        encoded_keywords = urllib.parse.quote(formatted_keywords)
        params = {"q": encoded_keywords}
        return base_url + "&".join([f"{k}={v}" for k, v in params.items()])

    start_urls = []

    custom_settings = {
        'FEEDS': {
            'data/%(name)s_%(time)s.csv': {'format': 'csv'},
        },
    }

    def start_requests(self):
        url = self.google_jobs_url()
        self.start_urls.append(url)

        options = uc.ChromeOptions()
        # options.binary_location = "/usr/bin/google-chrome"
        driver = uc.Chrome(options=options)
        driver.get(url)

        time.sleep(random.uniform(3, 5))

        page_html = driver.page_source
        response = HtmlResponse(url=driver.current_url, body=page_html, encoding='utf-8')

        yield from self.parse(response)

        driver.quit()

    def parse(self, response):
        
        sleep_time = random.uniform(3, 5)
        
        options = uc.ChromeOptions()
        # options.binary_location = "/usr/bin/google-chrome"
        driver = uc.Chrome(options=options)

        driver.maximize_window()

        driver.get(response.url)
        time.sleep(sleep_time) 

        try:
            location_not_now = driver.find_element(By.XPATH, '//div[@class="mpQYc"]//div[@class="sjVJQd"]')
            location_not_now.click()
        except:
            self.logger.info("No location not now button")

        time.sleep(sleep_time)

        try:
            load_more_button = driver.find_element(By.XPATH, '//div[@class="crJ18e"]//div[contains(text(), "Jobs")]')
            load_more_button.click()
        except:
            self.logger.info("No load more button")

        time.sleep(sleep_time)

        self.scroll_to_load_jobs(driver, max_scrolls=self.SCROLLS)  

        wait = WebDriverWait(driver, 10)
        try:
            wait.until(EC.presence_of_element_located((By.XPATH, '//a[@class="MQUd2b"]')))
        except:
            self.logger.info("Timeout: No jobs found within 15 seconds.")

        job_items = driver.find_elements(By.XPATH, '//a[@class="MQUd2b"]')

        for i in range(len(job_items)):
            try:
                job_items = driver.find_elements(By.XPATH, '//a[@class="MQUd2b"]')
                job_item = job_items[i]

                driver.execute_script("arguments[0].click();", job_item)  

                time.sleep(random.uniform(2, 4)) 

                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, '//div[@class="AQyBn"]'))
                )

                job_details = driver.find_element(By.XPATH, '//div[@class="BIB1wf EIehLd fHE6De Emjfjd"]')
                job_title = job_details.find_element(By.XPATH, './/div[@class="JmvMcb"]//h1').text.strip()
                company_name = job_details.find_element(By.XPATH, './/div[@class="UxTHrf"]').text.strip()

                apply_buttons = job_details.find_elements(By.XPATH, './/a[contains(@title, "Apply ")]')
                apply_link = apply_buttons[0].get_attribute("href") if apply_buttons else None

                job_description = job_details.find_element(By.XPATH, '//div[@class="NgUYpe"]').get_attribute('innerText').strip()

                google_job_link = driver.current_url

                yield {
                    "job_title": job_title,
                    "company_name": company_name,
                    "apply_link": apply_link,
                    "google_job_link": google_job_link,
                    "job_description": job_description,
                }

            except Exception as e:
                self.logger.error(f"Error extracting job details: {e}")

        driver.quit()

    def scroll_to_load_jobs(self, driver, max_scrolls=5):
        for _ in range(max_scrolls):
            driver.execute_script("window.scrollBy(0, 1000);")
            time.sleep(random.uniform(1.5, 3))
            try:
                driver.find_element(By.XPATH, '//div[@class="ZNyqGc"]')
            except:
                break
            print(f"Scrolled {_ + 1} times")
