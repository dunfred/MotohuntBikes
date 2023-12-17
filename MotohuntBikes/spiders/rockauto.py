import re
import json
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

    # custom_settings = {
    #     "DOWNLOAD_DELAY": 0,
    #     "DOWNLOAD_TIMEOUT": 10,
    #     "RANDOMIZE_DOWNLOAD_DELAY": True,
    #     "REACTOR_THREADPOOL_MAXSIZE": 10,
    #     "CONCURRENT_REQUESTS": 3,
    #     "CONCURRENT_REQUESTS_PER_DOMAIN": 3,
    #     "CONCURRENT_REQUESTS_PER_IP": 3,
    #     "AUTOTHROTTLE_ENABLED": True,
    #     "AUTOTHROTTLE_START_DELAY": 1,
    #     "AUTOTHROTTLE_MAX_DELAY": 0.25,
    #     "AUTOTHROTTLE_TARGET_CONCURRENCY": 10,
    #     "AUTOTHROTTLE_DEBUG": True,
    #     "RETRY_ENABLED": True,
    #     "RETRY_TIMES": 3,
    #     "RETRY_HTTP_CODES": [500, 502, 503, 504, 400, 401, 403, 404, 405, 406, 407, 408, 409, 410, 429],
    #     "LOG_ENABLED": True,
    #     "LOG_LEVEL": "DEBUG",
    #     'ZYTE_SMARTPROXY_ENABLED': True,
    #     'ZYTE_SMARTPROXY_APIKEY': '2cf4c91d781f4dd9b4e5ecc4b6c2b24f',
    #     'ZYTE_SMARTPROXY_URL': 'http://2cf4c91d781f4dd9b4e5ecc4b6c2b24f:@proxy.crawlera.com:8011/',

    #     'DOWNLOADER_MIDDLEWARES': {
    #         'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    #         # 'scrapy_user_agents.middlewares.RandomUserAgentMiddleware': 400,
    #         'scrapy_zyte_smartproxy.ZyteSmartProxyMiddleware': 610,

    #     },
    # }

    def parse(self, response):        
        make_elems = response.xpath('//*[starts-with(@id, "navhref")]') #.getall()
        print('TOTAL MAKES:', len(make_elems))
        
        for make in make_elems[:3]:
            href_attribute = make.attrib.get('href')
            text_content = make.css('::text').extract_first().strip()

            yield response.follow(
                self.durl + href_attribute,
                callback=self.get_makes,
                meta={'make': text_content}
            )

    def get_makes(self, response):
        soup = BeautifulSoup(response.body, 'lxml')

        selected_make_elem = soup.find('a', {'href':str(response.url).replace('https://www.rockauto.com', '')})

        years_under_make_elem = selected_make_elem.parent.parent.parent.parent.parent.next_sibling

        year_anchor_elems = years_under_make_elem.find_all('a', {'id': re.compile("^navhref\[\d+\]$")})
        
        updated_meta = response.meta.copy()
        for year in year_anchor_elems:
            href_attribute = year.get('href')
            text_content = year.text.strip()

            updated_meta['year'] = text_content
            yield response.follow(
                self.durl + href_attribute,
                callback=self.get_years,
                meta = updated_meta
            )
    
    def get_years(self, response):
        soup = BeautifulSoup(response.body, 'lxml')

        selected_year_elem = soup.find('a', {'href':str(response.url).replace('https://www.rockauto.com', '')})

        models_under_year_elem = selected_year_elem.parent.parent.parent.parent.parent.next_sibling

        model_anchor_elems = models_under_year_elem.find_all('a', {'id': re.compile("^navhref\[\d+\]$")})
        
        updated_meta = response.meta.copy()
        for model in model_anchor_elems:
            href_attribute = model.get('href')
            text_content = model.text.strip()

            updated_meta['model'] = text_content
            yield response.follow(
                self.durl + href_attribute,
                callback=self.get_engine,
                meta = updated_meta
            )


    def get_engine(self, response):
        soup = BeautifulSoup(response.body, 'lxml')

        model_year_elem = soup.find('a', {'href':str(response.url).replace('https://www.rockauto.com', '')})

        engines_under_model_elem = model_year_elem.parent.parent.parent.parent.parent.next_sibling

        engine_anchor_elems = engines_under_model_elem.find_all('a', {'id': re.compile("^navhref\[\d+\]$")})
        
        updated_meta = response.meta.copy()
        for engine in engine_anchor_elems:
            print('Engine:', engine)
            href_attribute = engine.get('href')
            text_content = engine.text.strip()

            updated_meta['engine'] = text_content
            yield response.follow(
                self.durl + href_attribute,
                callback=self.get_part_type,
                meta = updated_meta
            )

    def get_part_type(self, response):
        soup = BeautifulSoup(response.body, 'lxml')

        engine_year_elem = soup.find('a', {'href':str(response.url).replace('https://www.rockauto.com', '')})

        part_types_under_engine_elem = engine_year_elem.parent.parent.parent.parent.parent.next_sibling

        part_type_anchor_elems = part_types_under_engine_elem.find_all('a', {'id': re.compile("^navhref\[\d+\]$")})
        
        updated_meta = response.meta.copy()
        for part_type in part_type_anchor_elems:
            href_attribute = part_type.get('href')
            text_content = part_type.text.strip()

            updated_meta['part_type'] = text_content
            yield response.follow(
                self.durl + href_attribute,
                callback=self.get_part_sub_type,
                meta = updated_meta
            )

    def get_part_sub_type(self, response):
        soup = BeautifulSoup(response.body, 'lxml')

        part_type_year_elem = soup.find('a', {'href':str(response.url).replace('https://www.rockauto.com', '')})

        part_sub_types_under_part_type_elem = part_type_year_elem.parent.parent.parent.parent.parent.next_sibling

        part_sub_type_anchor_elems = part_sub_types_under_part_type_elem.find_all('a', {'id': re.compile("^navhref\[\d+\]$")})
        
        updated_meta = response.meta.copy()
        for part_sub_type in part_sub_type_anchor_elems:
            href_attribute = part_sub_type.get('href')
            text_content = part_sub_type.text.strip()

            updated_meta['part_sub_type'] = text_content
            yield response.follow(
                self.durl + href_attribute,
                callback=self.get_part_sub_types_listings,
                meta = updated_meta
            )

    def get_part_sub_types_listings(self, response):
        soup = BeautifulSoup(response.body, 'lxml')

        # listingcontainer[424]
        listings = soup.find_all('tbody', {'id': re.compile("^listingcontainer\[\d+\]$")})

        for listing in listings:
            item = RockAutoItem()

            price_elm = listing.find('span', {'id': re.compile("^dprice\[\d+\]\[v\]$")})
            # print('Price Elm:', price_elm)

            part_images_elm = listing.find('input', {'id': re.compile("^jsninlineimg\[\d+\]$")})
            # Get the value attribute from the input element
            json_string = part_images_elm.get('value', [])
            # Load the JSON string into a Python object
            data = json.loads(json_string)
            # Extract all the full image URLs
            full_image_urls = [slot['ImageData']['Full'] for slot in data['Slots']]
            # print('Part Images:', full_image_urls)

             
            part_manufacturer_elm = listing.find('span', {'class': "listing-final-manufacturer"})
            # print('Part Manufacturer Elm:', part_manufacturer_elm)

            part_number_elm = listing.find('span', {'id': re.compile("^vew_partnumber\[\d+\]$")})
            # print('Part Number Elm:', part_number_elm)

            part_link = part_number_elm.find_next_sibling('a')
            # print('Part Link Elm:', part_link)

            part_elm = part_link.parent.find_next_sibling('div').span
            # print('Part Elm:', part_elm)

            item['make']    = response.meta.get('make')
            item['year']    = response.meta.get('year')
            item['model']   = response.meta.get('model')
            item['engine']  = response.meta.get('engine')
            item['part_type']     = response.meta.get('part_type')
            item['part_sub_type'] = response.meta.get('part_sub_type')
            
            item['part_name']         = str(part_elm.text).strip()
            item['price']             = float(str(price_elm.text).replace('$','').replace(',','').strip())
            item['part_manufacturer'] = str(part_manufacturer_elm.text).strip()
            item['part_number']       = str(part_number_elm.text).strip()
            item['part_url']          = part_link.get('href')
            item['part_images']       = full_image_urls
            yield item
        
