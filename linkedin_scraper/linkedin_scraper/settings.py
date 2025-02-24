import datetime
import random

# Scrapy settings for linkedin_scraper project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = "linkedin_scraper"

SPIDER_MODULES = ["linkedin_scraper.spiders"]
NEWSPIDER_MODULE = "linkedin_scraper.spiders"


# Log settings
LOG_ENABLED = True  # Enable logging
LOG_LEVEL = 'INFO'  # Set log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_FILE = "scrapy_logs.txt"  # Save logs to a file



# SCRAPEOPS_API_KEY = '818447e1-3904-4f8f-b026-9a9d2396ee71'
# SCRAPEOPS_PROXY_ENABLED = True


# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = None

# Obey robots.txt rules
ROBOTSTXT_OBEY = False


# current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
# FEEDS = {
#     f"linkedin_scraper/data/linkedin_posts_{current_time}.json": {"format": "json"},
#     f"linkedin_scraper/data/linkedin_posts_{current_time}.csv": {"format": "csv"},
# }


# Enable rotating proxies

# ROTATING_PROXY_LIST = [
#     "http://user:pass@residential-proxy1.com:8000",
#     "http://user:pass@residential-proxy2.com:8000",
#     "http://user:pass@residential-proxy3.com:8000"
# ]

# Reduce bot detection

RANDOMIZE_DOWNLOAD_DELAY = True

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 10

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#    "Accept-Language": "en",
#}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    "linkedin_scraper.middlewares.LinkedinScraperSpiderMiddleware": 543,
#}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    "linkedin_scraper.middlewares.LinkedinScraperDownloaderMiddleware": 543,
#}

DOWNLOADER_MIDDLEWARES = {
    'linkedin_scraper.middlewares.CustomRetryMiddleware': 550,  # Make sure the path matches your project name
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,  # Disable default retry middleware
}

RETRY_ENABLED = True  # Enable retry mechanism
RETRY_TIMES = 5  # Number of retries before failing
RETRY_HTTP_CODES = [429, 500, 502, 503, 504, 522, 524, 408, 403] 


# DOWNLOADER_MIDDLEWARES = {

#     ## ScrapeOps Monitor
#     'scrapeops_scrapy.middleware.retry.RetryMiddleware': 550,
#     'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
    
#     ## Proxy Middleware
#     'scrapeops_scrapy_proxy_sdk.scrapeops_scrapy_proxy_sdk.ScrapeOpsScrapyProxySdk': 725,
# }

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    "scrapy.extensions.telnet.TelnetConsole": None,
#}
# EXTENSIONS = {
#    'scrapeops_scrapy.extension.ScrapeOpsMonitor': 500, 
# }


# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
# ITEM_PIPELINES = {
#    "linkedin_scraper.pipelines.LinkedinScraperPipeline": 300,
# }

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = "httpcache"
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

# Set settings whose default value is deprecated to a future-proof value
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"
