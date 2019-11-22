import subprocess

from stem import Signal
from stem.control import Controller
import requests
from scrapy import signals
from time import sleep
import logging
from fake_useragent import UserAgent

logger = logging.getLogger(__name__)


def retrieve_ip():
    session = requests.session()
    session.proxies = {'http': 'socks5://127.0.0.1:9050',
                       'https': 'socks5://127.0.0.1:9050'}
    return session


def set_new_ip(get_ip=False):
    with Controller.from_port(port=9051) as controller:
        controller.authenticate(password='thym3594')
        slp = controller.get_newnym_wait()
        logging.info(f'sleep to change ip {slp} sec')
        sleep(controller.get_newnym_wait())
        controller.signal(Signal.NEWNYM)
    if get_ip:
        t = retrieve_ip().get('http://httpbin.org/ip').text
        return t.split('"')[3].split(',')[0]


class MyRandomUserAgentMiddleware(object):
    counter = 0

    def __init__(self, crawler):
        super().__init__()

        fallback = crawler.settings.get('FAKEUSERAGENT_FALLBACK', None)
        self.ua = UserAgent(fallback=fallback)
        self.per_proxy = crawler.settings.get('RANDOM_UA_PER_PROXY', False)
        self.ua_type = crawler.settings.get('RANDOM_UA_TYPE', 'random')
        self.proxy2ua = {}

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def process_request(self, request, spider):
        def get_ua():
            return getattr(self.ua, self.ua_type)

        ua = get_ua()
        request.headers.setdefault('User-Agent', ua)


class ProxyMiddleware:
    counter = 0

    def process_request(self, request, spider):
        if ProxyMiddleware.counter % 30 == 0:
            subprocess.run('python ../change_ip.py')
            t = retrieve_ip().get('http://httpbin.org/ip').text.split('"')[3].split(',')[0]
            logging.info(f'Change IP to {t}')
            ProxyMiddleware.counter = 1
        else:
            ProxyMiddleware.counter += 1
        request.meta['proxy'] = 'http://127.0.0.1:8123'


class AmazonCrwalerSpiderMiddleware(object):

    @classmethod
    def from_crawler(cls, crawler):
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        return None

    def process_spider_output(self, response, result, spider):
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        pass

    def process_start_requests(self, start_requests, spider):
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class AmazonCrwalerDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
