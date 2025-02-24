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

class LinkedInPostSpider(scrapy.Spider):
    name = "linkedin_post"
    allowed_domains = ["linkedin.com"]
    


    
    keywords = ["python developer", "jobs", "remote"]

    SCROLLS = 2

    SESSION_ID = 'AQEDAVfxB5UFTrdQAAABlR5UOzwAAAGVQmC_PFYAf7CMEwRIp0SZD_EYgPT5w_GcspTCtgoHGUKwvaz4dyXVYm75ojI9WZORnfC4_RBOcT4k5hE-iPouB12jPIuzT9ZZc8AloYTacnU1sKTuIxJetAhw'





    def build_linkedin_content_url(keywords):
        base_url = "https://www.linkedin.com/search/results/content/?"
        
        formatted_keywords = ", ".join([f'"{keyword}"' for keyword in keywords])
        
        encoded_keywords = urllib.parse.quote(formatted_keywords)
        
        params = {
            "keywords": encoded_keywords,  
            "origin": "GLOBAL_SEARCH_HEADER",
        }
        
        return base_url + "&".join([f"{k}={v}" for k, v in params.items()])
    
    start_urls = [build_linkedin_content_url(keywords)]

    custom_settings = {
        'FEEDS': {
            'data/%(name)s_%(time)s.json': {'format': 'json'},
            'data/%(name)s_%(time)s.csv': {'format': 'csv'},
        },
    }

    COOKIES = {
        'li_at': SESSION_ID,  # Replace with your valid LinkedIn session cookie
    }

    def __init__(self, *args, **kwargs):
        super(LinkedInPostSpider, self).__init__(*args, **kwargs)
        self.scraped_urls = set()

    def start_requests(self):
        """ Start requests with LinkedIn session cookies. """
        for url in self.start_urls:
            yield scrapy.Request(
                url=url,
                cookies=self.COOKIES,
                callback=self.parse
            )

    def parse(self, response):
        """ Load LinkedIn posts with Selenium, scroll to load more posts, and extract data. """
        
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

        self.scroll_to_load_posts(driver, max_scrolls=self.SCROLLS)

        wait = WebDriverWait(driver, 10)
        try:
            wait.until(EC.presence_of_element_located((By.XPATH, '//div[@class="search-marvel-srp"]')))
        except:
            self.logger.info("Timeout: No posts found within 15 seconds.")

        search_page_html = driver.page_source

        new_response = HtmlResponse(url=response.url, body=search_page_html, encoding='utf-8')

        posts = new_response.xpath('//li[@class="artdeco-card mb2"]')

        for post in posts:
            name = post.xpath('.//span[contains(@class, "update-components-actor__title")]//span[@aria-hidden="true"]/text()').get()
            tagline = post.xpath('.//span[contains(@class, "update-components-actor__description")]//span[@aria-hidden="true"]/text()').get()
            profile_url = post.xpath('.//a[contains(@class, "update-components-actor__meta-link")]/@href').get()
            description = post.xpath('string(.//div[@class="update-components-text relative update-components-update-v2__commentary "])').get()

            try:
                job_link = post.xpath('.//div[@class="update-components-entity__content-wrapper"]//a/@href').get()
            except:
                self.logger.info('Job link not available')

            if name:
                name = name.strip()
                name_parts = name.split()
                if len(name_parts) > 1:
                    first_name = name_parts[0]
                    last_name = " ".join(name_parts[1:])
                else:
                    first_name = name
                    last_name = None
            if tagline:
                tagline = tagline.strip()
            if description:
                description = description.strip()

            yield {
                "first_name": first_name,
                "last_name": last_name,
                "tagline": tagline,
                "profile_url": profile_url,
                "job_link": job_link,
                "job_description": description
            }

        driver.quit()


    def scroll_to_load_posts(self, driver, max_scrolls=5):
        for _ in range(max_scrolls):
            driver.execute_script("window.scrollBy(0, 1000);")
            time.sleep(random.uniform(2, 5)) 

            try:
                load_more_button = driver.find_element(By.XPATH, '//button[contains(@class, "scaffold-finite-scroll__load-button")]')
                if load_more_button.is_displayed():
                    load_more_button.click()
                    time.sleep(random.uniform(2, 4)) 
                    print("Clicked 'Load more' button")
            except:
                pass

            print(f"Scrolled {_ + 1} times")