import psycopg2
import scrapy

from scrapy import Request
from pytz import timezone
from datetime import datetime as dt

from scrapy.http import Response
import logging
import os

from amazon_crwaler.items import AmazonItem
from scrapy.utils.response import open_in_browser


def log(text):
    logging.debug(text)


def split_query(url: str):
    domain, _, query_part = url.partition('?')
    query = {}
    for q in query_part.split('&'):
        key, _, val = q.partition('=')
        query[key] = val
    return domain, query


def parse_query(base: str, query: dict) -> str:
    return base + '?' + '&'.join([f'{key}={val}' for key, val in query.items()])


def remove_query(url: str, *use_key):
    base, query = split_query(url)
    new_query = {key: val for key, val in query.items() if key in use_key}
    return parse_query(base, new_query)


def update_query(url: str, **query):
    base, q = split_query(url)
    q.update(**query)
    return parse_query(base, q)


def get_query_val(url: str, key: str, default=''):
    query = split_query(url)[1]
    return query.get(key, str(default))


amazon_url = 'https://www.amazon.co.jp'
max_page = 4


class AmazonproductSpider(scrapy.Spider):
    name = 'AmazonProduct'
    allowed_domains = ['www.amazon.co.jp']

    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)
        self.conn = psycopg2.connect(
            'host=database-1.caizbo93ln5z.us-east-2.rds.amazonaws.com '
            'port=5432 '
            'dbname=amazon '
            'user=postgres '
            'password=thym3594'
        )

    def debug(self, response):
        if response.status == 200:
            return
        logging.error(f'url: {response.url}')
        logging.info(f'ua : {response.request.headers.get("User-Agent", b"").decode()}')

    def create_connect(self):
        self.conn = psycopg2.connect(
            'host=database-1.caizbo93ln5z.us-east-2.rds.amazonaws.com '
            'port=5432 '
            'dbname=amazon '
            'user=postgres '
            'password=thym3594'
        )

    start_urls = [
        'https://www.amazon.co.jp/gp/site-directory?ref_=nav_em_T1_0_2_2_21__fullstore',
        # 1つの商品
        # 'https://www.amazon.co.jp/Windows10-%E4%B8%AD%E5%8F%A4%E3%83%87%E3%82%B9%E3%82%AF%E3%83%88%E3%83%83%E3%83%97%E3%83%91%E3%82%BD%E3%82%B3%E3%83%B3-NEC-DVD%E3%82%B9%E3%83%BC%E3%83%91%E3%83%BC%E3%83%9E%E3%83%AB%E3%83%81-Win10Pro/dp/B0199JYAXA/ref=sr_1_2?brr=1&qid=1573582471&rd=1&refinements=p_72%3A2150400051&rnid=2150399051&s=computers&sr=1-2',
        # 商品一覧
        # 'https://www.amazon.co.jp/%E3%83%91%E3%82%BD%E3%82%B3%E3%83%B3%E3%83%BB%E5%91%A8%E8%BE%BA%E6%A9%9F%E5%99%A8-%E6%98%9F4%E3%81%A4%E4%BB%A5%E4%B8%8A/s?rh=n%3A2127209051%2Cn%3A%212127210051%2Cn%3A2151949051%2Cn%3A6111448051%2Cp_72%3A2150400051&s=review-rank',
        # 複数のカテゴリ
        # 'https://www.amazon.co.jp/s?rh=n%3A2127209051%2Cn%3A%212127210051%2Cn%3A2151949051%2Cp_72%3A2150400051&s=review-rank',
        # カテゴリのトップ
        # 'https://www.amazon.co.jp/PC%E5%91%A8%E8%BE%BA%E6%A9%9F%E5%99%A8-%E3%83%91%E3%82%BD%E3%82%B3%E3%83%B3%E5%91%A8%E8%BE%BA%E6%A9%9F%E5%99%A8-%E9%80%9A%E8%B2%A9/b/?ie=UTF8&node=2127209051&ref_=topnav_storetab_computers',
    ]

    def errors(self, name, url=None):
        def error_back(failure):
            while True:
                try:
                    cur = self.conn.cursor()
                    cur.execute(f'insert into {name}(url) values (%s)', (url if url else failure.request.url,))
                    cur.connection.commit()
                except Exception:
                    self.create_connect()
                else:
                    break

        return error_back

    def start_requests(self):
        # files = ['single_parse', 'single_category', 'multi_category', 'star_4', 'parse']
        # delete_conn = psycopg2.connect(
        #     'host=database-1.caizbo93ln5z.us-east-2.rds.amazonaws.com '
        #     'port=5432 '
        #     'dbname=amazon '
        #     'user=postgres '
        #     'password=thym3594'
        # )
        # for file in files:
        #     fetch = self.conn.cursor()
        #     fetch.execute(f'select url from {file}')
        #     cur = delete_conn.cursor()
        #     callback = getattr(self, file)
        #     for url in fetch:
        #         cur.execute(f'delete from {file} where url=%s', (url[0],))
        #         delete_conn.commit()
        #         yield Request(url[0], callback, errback=self.errors(file), dont_filter=True)
        for url in self.start_urls:
            yield Request(url, self.start, errback=self.errors('start'))

    def start(self, response: Response):
        links = response.css('#shopAllLinks tr > td:nth-child(1n+2) a::attr(href)').getall()
        for link in links:
            node = get_query_val(link, 'node')
            if node:
                url = f'{amazon_url}/s?node={node}'
                yield Request(url, self.parse, errback=self.errors('parse'))

    def parse(self, response: Response):
        log('parse')
        if response.css('#leftNav a > i.a-star-medium-4'):
            log('go star')
            yield Request(response.url, self.star_4, dont_filter=True, errback=self.errors('star_4'))
        else:
            links = response.css('div.left_nav.browseBox a::attr(href)').getall()
            for link in links:
                node = get_query_val(link, 'node')
                if node:
                    url = f'{amazon_url}/s?node={node}'
                    yield Request(url, self.parse, errback=self.errors('parse'))
                else:
                    rh = get_query_val(link, 'rh')
                    if rh:
                        url = f'{amazon_url}/s?rh={rh}'
                        yield Request(url, self.parse, errback=self.errors('parse'))

    def star_4(self, response: Response):
        log('star')
        link = response.xpath('//div[@id="leftNav"]//a[i[contains(@class,"a-star-medium-4")]]/@href').get()
        if not link:
            yield Request(response.url, self.star_4, dont_filter=True, errback=self.errors('star_4'))
        else:
            rh = get_query_val(link, 'rh')
            if rh:
                url = f'{amazon_url}/s?rh={rh}'
                yield Request(update_query(url, s='review-rank'), self.multi_category,
                              errback=self.errors('multi_category'))
        # yield Request(update_query(remove_query(url, 'rh'), s='review-rank'), self.multi_category,
        #               dont_filter=True)

    def multi_category(self, response: Response):
        log('multi')
        indent_2 = response.xpath('//*[@id="departments"]/ul/li[contains(@class, "s-navigation-indent-2")]//a/@href')
        if indent_2:
            for li in indent_2:
                rh = get_query_val(li.get(), 'rh')
                if rh:
                    url = f'{amazon_url}/s?rh={rh}'
                    yield Request(url, self.multi_category, errback=self.errors('multi_category'))
        else:
            yield Request(response.url, self.single_category, dont_filter=True, errback=self.errors('single_category'))

    def single_category(self, response: Response):
        log('single')
        if get_query_val(response.url, 's', '') != 'review-rank':
            yield Request(update_query(response.url, s='review-rank'), self.single_category, dont_filter=True,
                          errback=self.errors('single_category'))
        else:
            links = response.css(
                'div.s-result-list.s-search-results.sg-row > div[data-asin] h2 > a::attr(href)').getall()
            for link in links:
                dirs = link.split('/')
                dp = dirs[dirs.index('dp') + 1]
                url = f'{amazon_url}/dp/{dp}'
                yield Request(url, self.single_parse, errback=self.errors('single_parse'))
            page = int(get_query_val(response.url, 'page', 1))
            if page < max_page:
                next_link = response.css('ul.a-pagination > li.a-last > a::attr(href)').get()
                if next_link:
                    yield Request(remove_query(amazon_url + next_link, 's', 'rh', 'page'), self.single_category,
                                  errback=self.errors('single_category'))
                    # yield Request(remove_query(amazon_url + next_link, 's', 'rh', 'page'), self.single_category,
                    #               dont_filter=True)

    def single_parse(self, response: Response):
        self.debug(response)
        if not response.xpath('//h1[@id="title"]/*/text()').get('').strip():
            return Request(response.url, self.single_parse, dont_filter=True, errback=self.errors('single_parse'))
        log('product')
        now = dt.now(timezone('Asia/Tokyo'))
        product = AmazonItem()

        product['time'] = now.strftime('%Y-%m-%dT%H-%M-%S')
        product['title'] = response.xpath('//h1[@id="title"]/*/text()').get('').strip()
        product['url'] = response.url
        review = response.css('span#acrCustomerReviewText::text').get('')
        product['review_num'] = review[0:-4] if review else 0
        product['description'] = '\n'.join(
            [x.strip() for x in response.css('#feature-bullets > ul > li *::text').getall() if
             x.strip() not in ('', 'モデル番号を入力してください', 'これが適合するか確認：')])
        seller = response.css('a#sellerProfileTriggerId')
        if seller:
            shop_name = seller.css('*::text').get('')
            seller_id = get_query_val(seller.attrib['href'], 'seller')
            shop_url = f'{amazon_url}/sp?seller={seller_id}' if seller_id else ''
        elif response.xpath('//*[@id="merchant-info"]/a'):
            shop_name = 'Amazon.co.jp'
            shop_url = 'https://www.amazon.co.jp/gp/help/customer/display.html?nodeId=202008070'
        else:
            shop_name = '-'
            shop_url = ''
        product['shop_name'] = shop_name
        product['shop_url'] = shop_url
        product['categories'] = ' > '.join([
            el.get().strip() for el in
            response.css('#wayfinding-breadcrumbs_feature_div > ul > li > span > a::text')
        ])
        if shop_url == 'https://www.amazon.co.jp/gp/help/customer/display.html?nodeId=202008070':
            product['shop_address'] = '〒153-0064 東京都目黒区下目黒1-8-1 日本'
            yield product
        elif shop_url:
            yield Request(shop_url, self.shop_parse, meta={'product': product},
                          dont_filter=True, errback=self.errors('single_parse', response.url))
        else:
            product['shop_address'] = '---'
            yield product

    def shop_parse(self, response: Response):
        product = response.meta['product']
        address = response.css(
            'ul.a-unordered-list.a-nostyle.a-vertical ul.a-unordered-list.a-nostyle.a-vertical *::text').getall()
        if address:
            address = '\n'.join(address)
        else:
            address = ''
        product['shop_address'] = address
        yield product
