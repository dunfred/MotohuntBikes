import scrapy
from datetime import date
from pprint import pprint
from bs4 import BeautifulSoup

from MotohuntBikes.items import RockAutoItem

class RockAutoSpider(scrapy.Spider):
    '''
    Usage ==> scrapy crawl rockauto
    '''

    name = "rockauto"
    durl = "https://www.rockauto.com"
    allowed_domains = ["rockauto.com"]
    start_urls = ["https://www.rockauto.com/en/catalog/"]
    
    # Custom attrs
    site_name = "RockAuto"

    def parse(self, response):        
        make_elems = response.xpath('//*[starts-with(@id, "navhref")]') #.getall()
        print('TOTAL MAKES:', len(make_elems))
        
        for make in make_elems:
            href_attribute = make.attrib.get('href')
            text_content = make.css('::text').extract_first().strip()

            yield response.follow(
                self.durl + href_attribute,
                callback=self.get_makes,
                meta={'make': text_content}
            )

    def get_makes(self, response):
        year_range = range(1986,2025)[::-1]

        updated_meta = response.meta.copy()

        for year in year_range:
            updated_meta['year'] = year
            yield response.follow(
                response.url + f',{year}',
                callback=self.get_years,
                meta = updated_meta
            )
    
    def get_years(self, response):
        print(response.url)
        print("Make:", response.meta.get('make', None), response.meta.get('year', None))

        # make_elems = response.xpath('//*[starts-with(@id, "navhref")]') #.getall()
        # print('TOTAL MAKES:', len(make_elems))
        
        # for make in make_elems:
        #     href_attribute = make.attrib.get('href')
        #     text_content = make.css('::text').extract_first().strip()

        #     yield response.follow(
        #         self.durl + href_attribute,
        #         callback=self.get_make_page,
        #         meta={'make': text_content}
        #     )
