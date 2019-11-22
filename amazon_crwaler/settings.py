BOT_NAME = 'amazon_crwaler'

SPIDER_MODULES = ['amazon_crwaler.spiders']
NEWSPIDER_MODULE = 'amazon_crwaler.spiders'

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

DEPTH_PRIORITY = -1

LOG_LEVEL = 'INFO'

DOWNLOAD_DELAY = 2

# Override the default request headers:
DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en',
}

# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    # 'amazon_crwaler.middlewares.ProxyMiddleware': 100,
    # 'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,

    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'amazon_crwaler.middlewares.MyRandomUserAgentMiddleware': 400,
}
RANDOM_UA_PER_PROXY = True

ITEM_PIPELINES = {
    'amazon_crwaler.pipelines.AmazonPipeline': 300,
}

# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = 'httpcache'
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
