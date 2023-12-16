import re
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
        
        for make in make_elems[:3]:
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
        print("Opened Engine Section:",response.url)
        pprint(response.meta)

        soup = BeautifulSoup(response.body, 'lxml')

        engine_year_elem = soup.find('a', {'href':str(response.url).replace('https://www.rockauto.com', '')})

        part_types_under_engine_elem = engine_year_elem.parent.parent.parent.parent.parent.next_sibling

        part_type_anchor_elems = part_types_under_engine_elem.find_all('a', {'id': re.compile("^navhref\[\d+\]$")})
        
        updated_meta = response.meta.copy()
        for part_type in part_type_anchor_elems:
            print('Part Type:', part_type)
            href_attribute = part_type.get('href')
            text_content = part_type.text.strip()

            updated_meta['part_type'] = text_content
            yield response.follow(
                self.durl + href_attribute,
                callback=self.get_part_sub_type,
                meta = updated_meta
            )

    def get_part_sub_type(self, response):
        print("Opened Part Type Section:",response.url)
        pprint(response.meta)

        soup = BeautifulSoup(response.body, 'lxml')

        part_type_year_elem = soup.find('a', {'href':str(response.url).replace('https://www.rockauto.com', '')})

        part_sub_types_under_part_type_elem = part_type_year_elem.parent.parent.parent.parent.parent.next_sibling

        part_sub_type_anchor_elems = part_sub_types_under_part_type_elem.find_all('a', {'id': re.compile("^navhref\[\d+\]$")})
        
        updated_meta = response.meta.copy()
        for part_sub_type in part_sub_type_anchor_elems:
            print('Part Sub Type:', part_sub_type)
            href_attribute = part_sub_type.get('href')
            text_content = part_sub_type.text.strip()

            updated_meta['part_sub_type'] = text_content
            yield response.follow(
                self.durl + href_attribute,
                callback=self.get_car_parts,
                meta = updated_meta
            )

    def get_car_parts(self, response):
        print("Opened Part Sub Type Section:",response.url)
        pprint(response.meta)
        soup = BeautifulSoup(response.body, 'lxml')

        # listingcontainer[424]
        parts_elems = soup.find_all('tbody', {'id': re.compile("^listingcontainer\[\d+\]$")})
        print('parts_elems:', parts_elems)
        yield {'done':'Yes'}
        
