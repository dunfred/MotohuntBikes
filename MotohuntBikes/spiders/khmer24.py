import scrapy
from datetime import date
from pprint import pprint
from bs4 import BeautifulSoup

from MotohuntBikes.items import RockAutoItem

class RockAutoSpider(scrapy.Spider):
    '''
    Usage ==> scrapy crawl khmer24
    '''

    name = "khmer24"
    durl = "https://www.khmer24.com"
    allowed_domains = ["khmer24.com"]
    start_urls = ["https://www.khmer24.com/en/motorcycles"]
    
    # Custom attrs
    site_name = "Khmer24"

    def parse(self, response):        
        brands = response.css("body > div.home-page > section.border-bottom.search-box > div > div.pb-3.pt-2 > div > div > form > div > select:nth-child(2) > option::text").getall()
        print('Brands:', brands)
        yield {'k':24}

    def get_makes(self, response):
        yield {}



