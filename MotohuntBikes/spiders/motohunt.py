import scrapy
from datetime import date
from pprint import pprint
from bs4 import BeautifulSoup

from MotohuntBikes.items import MotohuntbikesItem

class MotohuntSpider(scrapy.Spider):
    '''
    Usage ==> scrapy crawl motohunt
    '''

    name = "motohunt"
    allowed_domains = ["motohunt.com"]
    start_urls = ["https://motohunt.com/motorcycles-for-sale/Dealer?hasprice=on&hasvin=on&start=1"]
    
    # Custom attrs
    durl = "https://motohunt.com"
    site_name = "Motohunt"
    selling_type='Motor Bikes'
    car_unique_id = date.today() # - timedelta(days=1)


    def parse(self, response):
        # Get links to motor page by make
        # print('Home Page')
        make_paths = response.css('#content > div:nth-child(4) > div > div:nth-child(2) > div > a::attr(href)').getall()
        make_links = [self.durl + path for path in make_paths]

        for make_page in make_links:
            yield response.follow(make_page, callback=self.get_make_page)

    def get_make_page(self, response):
        # Get links to motor page by model
        # print("Make Page:", response.url)
        model_paths = response.css('#content > div:nth-child(4) > div > div > div > a::attr(href)').getall()
        model_links = [self.durl + path for path in model_paths]

        for model_page in model_links:
            yield response.follow(model_page, callback=self.get_model_page)

    def get_model_page(self, response):
        # Go through all pages to scrape motors
        # print("Model Page:", response.url)
        models_page_url = response.url

        results_text = response.css('#results-text::text').get()

        try:
            page_offet, total_records = results_text.strip().split('of')
            
            start, end = page_offet.strip().split('-')
            start = int(start.strip())
            end   = int(end.strip())
            total_records = int(total_records.strip().replace(',',''))

            # print('Start:', start, 'End:', end, "Total Records:",total_records)

            for i in range(start, total_records, end): # Remember to correct this
                next_page = models_page_url + f'&start={i}'
                yield response.follow(next_page, callback=self.get_paginated_motor_page)

        except Exception as e:
            # print('No results pagination:', results_text, 'Error Message:', e)
            motors = response.css("#srp-results-container > div > div > div.card-body.nolinkcolor > a::attr(href)").getall()
            motor_links = [self.durl + path for path in motors]

            for model_page in motor_links:
                yield response.follow(model_page, callback=self.scrape_motorbike)

    def get_paginated_motor_page(self, response):
        # print("Scrape Page:", response.url)

        motors = response.css("#srp-results-container > div > div > div.card-body.nolinkcolor > a::attr(href)").getall()
        motor_links = [self.durl + path for path in motors]
        # pprint(motors)

        for model_page in motor_links:
            yield response.follow(model_page, callback=self.scrape_motorbike)

    def scrape_motorbike(self, response):
        item = MotohuntbikesItem()

        soup = BeautifulSoup(response.body, 'lxml')

        # Get VIN
        vin_label = soup.find('b', text='VIN:')
        vin_parent = vin_label.parent
        vin = vin_parent.find_next('div').text.strip()
        item['vin'] = vin
        if not item['vin']:
            return

        # Get MAKE
        try:
            make_label = soup.find('div', text='Make')
            make = make_label.find_next('div').text.strip()
            item['make'] = make
            if not item['make']:
                return
            # print('MAKE:', make)
        except Exception:
            return

        # Get MODEL
        try:
            model_label = soup.find('div', text='Model')
            model = model_label.find_next('div').text.strip()
            item['model'] = model
            if not item['model']:
                return
            # print('MODEL:', model, response.url)
        except Exception:
            return
        
        # Get TRIM
        try:
            trim_label = soup.find('div', text='Trim')
            trim = trim_label.find_next('div').text.strip()
            item['trim'] = trim
            if not item['trim']:
                return
            # print('TRIM:', trim, response.url)
        except Exception:
            item['trim'] = None


        # Get YEAR
        year_label = soup.find('div', text='Model Year')
        year = year_label.find_next('div').text.strip()
        item['year'] = year
        if not item['year']:
            return
        # print('YEAR:', year, response.url)

        # Get PRICE
        try:
            price_label = soup.find('b', text='Price:')
            price_parent = price_label.parent
            price = float(price_parent.find_next('div').text.strip().replace(',','').replace('$',''))
            item['price'] = price
            # print('PRICE:', price, response.url)
        except Exception:
            item['price'] = None

        # Get CONDITION
        try:
            condition_label = soup.find('b', text='Condition:')
            condition_parent = condition_label.parent
            condition = condition_parent.find_next('div').text.strip()
            item['condition'] = condition
            # print('CONDITION:', condition, response.url)
        except Exception:
            item['condition'] = None

        # Get DEALER
        try:
            dealer_label = soup.find('b', text='Dealer:')
            dealer_parent = dealer_label.parent
            dealer = dealer_parent.find_next('div').text.strip()
            item['dealer'] = dealer
            # print('DEALER:', dealer, response.url)
        except Exception:
            item['dealer'] = None

        item['car_url']             = response.url
        item['dealer_link']         = response.css('#viewondealerwebsitelink::attr(href)').get()
        item['dealer_number']       = response.css('#content > div.row > div > div.row.bottom-margin > div.col-xs-12.col-sm-12.col-md-5.col-lg-5.col-xl-5 > div:nth-child(1) > div > a::text').get()
        if item['dealer_number']:
            item['dealer_number'] = str(item['dealer_number']).strip()

        # Get DESCRIPTION
        try:
            description_label = soup.find('h4', text='Description')
            description_parent = description_label.parent.parent
            description = description_parent.find_next_sibling().text.strip()
            item['description'] = description
        except Exception:
            item['description'] = None

        # Get MILEAGE
        try:
            mileage_label = soup.find('b', text='Mileage:')
            mileage_parent = mileage_label.parent
            mileage = mileage_parent.find_next('div').text.strip()
            item['mileage'] = int(mileage.replace('miles','').replace(',',''))
        except Exception:
            item['mileage'] = None

        # Get COLOR
        try:
            color_label = soup.find('b', text='Color:')
            color_parent = color_label.parent
            color = color_parent.find_next('div').text.strip()
            item['color'] = color if str(color).lower() != 'insufficient color' else None
            # print('COLOR:', color, response.url)
        except Exception:
            item['color'] = None

        # Get LOCATION
        try:
            location_label = soup.find('b', text='Location:')
            location_parent = location_label.parent
            location = location_parent.find_next('div').text.strip()
            item['location'] = str(location).replace('see map','').strip()
            # print('LOCATION:', item['location'], response.url)
        except Exception:
            item['location'] = None

        # Get ENGINE
        try:
            engine_label = soup.find('b', text='Engine:')
            engine_parent = engine_label.parent
            engine = engine_parent.find_next('div').text.strip()
            item['engine'] = engine
            # print('ENGINE:', item['engine'], response.url)
        except Exception:
            item['engine'] = None

        # Get FUEL TYPE
        try:
            fuel_type_label = soup.find('div', text='Fuel Type - Primary')
            fuel_type = fuel_type_label.find_next('div').text.strip()
            item['fuel_type'] = fuel_type
            # print('FUEL TYPE:', fuel_type, response.url)
        except Exception:
            item['fuel_type'] = None

        # Get BODY CLASS
        try:
            body_type_label = soup.find('div', text='Body Class')
            body_type = body_type_label.find_next('div').text.strip()
            item['body_type'] = body_type
            # print('BODY TYPE:', body_type, response.url)
        except Exception:
            item['body_type'] = None

        # Get IMAGES
        try:
            # get images from gallery
            image_gallery_div = soup.find('div', {'id':'imagegallery'})
            images_elems      = image_gallery_div.find_all('img')
            image_links       = [link['data-src'] for link in images_elems]
            
            # if no gallery, get single image
            if not image_links:
                si_div      = soup.find('div', {'id':'single-image'})
                si_elems    = si_div.find_all('img')
                image_links = [link['data-src'] for link in si_elems]

            item['image_links'] = image_links
            # print('Image Links:', image_links, response.url)
        except Exception:
            item['image_links'] = None

        yield item

# scrapy crawl motohunt -O motohunt.json


# item['vin']                 = response.css('#content > div.row > div > div.row.bottom-margin > div.col-xs-12.col-sm-12.col-md-7.col-lg-7.col-xl-7.bottom-margin > div:nth-child(12) > div.col-6.col-md-5.col-lg-4::text').get()
# item['make']                = response.css('#content > div.row > div > div.row.bottom-margin > div.col-xs-12.col-sm-12.col-md-7.col-lg-7.col-xl-7.bottom-margin > div.row.d-none.d-md-block.d-lg-block.d-xl-block > div > div:nth-child(2) > div > div:nth-child(12) > div.col-6.col-sm-7::text').get()
# item['model']               = response.css('#content > div.row > div > div.row.bottom-margin > div.col-xs-12.col-sm-12.col-md-7.col-lg-7.col-xl-7.bottom-margin > div.row.d-none.d-md-block.d-lg-block.d-xl-block > div > div:nth-child(2) > div > div:nth-child(14) > div.col-6.col-sm-7::text').get()
# item['year']                = response.css('#content > div.row > div > div.row.bottom-margin > div.col-xs-12.col-sm-12.col-md-7.col-lg-7.col-xl-7.bottom-margin > div.row.d-none.d-md-block.d-lg-block.d-xl-block > div > div:nth-child(2) > div > div:nth-child(15) > div.col-6.col-sm-7::text').get()
# item['price']               = response.css('#content > div.row > div > div.row.bottom-margin > div.col-xs-12.col-sm-12.col-md-7.col-lg-7.col-xl-7.bottom-margin > div:nth-child(7) > div.col-9.col-lg-10::text').get()
# item['condition']           = response.css('#content > div.row > div > div.row.bottom-margin > div.col-xs-12.col-sm-12.col-md-7.col-lg-7.col-xl-7.bottom-margin > div:nth-child(5) > div.col-9.col-lg-10::text').get()
# item['dealer']              = response.css('#content > div.row > div > div.row.bottom-margin > div.col-xs-12.col-sm-12.col-md-7.col-lg-7.col-xl-7.bottom-margin > div:nth-child(6) > div.col-9.col-lg-10::text').get()
# item['dealer_link']         = response.css('#viewondealerwebsitelink::attr(href)').get()
# item['dealer_number']       = response.css('#content > div.row > div > div.row.bottom-margin > div.col-xs-12.col-sm-12.col-md-5.col-lg-5.col-xl-5 > div:nth-child(1) > div > a::text').get()
# item['description']  = response.css('#content > div.row > div > div.row.bottom-margin > div.col-xs-12.col-sm-12.col-md-5.col-lg-5.col-xl-5 > div:nth-child(5) > div > p::text').get()
# item['mileage']             = response.css('#content > div.row > div > div.row.bottom-margin > div.col-xs-12.col-sm-12.col-md-7.col-lg-7.col-xl-7.bottom-margin > div:nth-child(8) > div.col-9.col-lg-10::text').get()
# item['color']               = response.css('#content > div.row > div > div.row.bottom-margin > div.col-xs-12.col-sm-12.col-md-7.col-lg-7.col-xl-7.bottom-margin > div:nth-child(9) > div.col-9.col-lg-10::text').get()
# item['location']            = response.css('#content > div.row > div > div.row.bottom-margin > div.col-xs-12.col-sm-12.col-md-7.col-lg-7.col-xl-7.bottom-margin > div:nth-child(4) > div.col-9.col-lg-10::text').get()
# item['engine']              = response.css('#content > div.row > div > div.row.bottom-margin > div.col-xs-12.col-sm-12.col-md-7.col-lg-7.col-xl-7.bottom-margin > div:nth-child(26) > div.col-8.col-lg-9.spec-right::text').get()
# item['fuel_type']           = response.css('#content > div.row > div > div.row.bottom-margin > div.col-xs-12.col-sm-12.col-md-7.col-lg-7.col-xl-7.bottom-margin > div.row.d-none.d-md-block.d-lg-block.d-xl-block > div > div:nth-child(2) > div > div:nth-child(7) > div.col-6.col-sm-7::text').get()
# item['body_type']           = response.css('#content > div.row > div > div.row.bottom-margin > div.col-xs-12.col-sm-12.col-md-7.col-lg-7.col-xl-7.bottom-margin > div.row.d-none.d-md-block.d-lg-block.d-xl-block > div > div:nth-child(2) > div > div:nth-child(9) > div.col-6.col-sm-7::text').get()
# item['image_links']         = response.css('#imagegallery > div.carousel-inner > div.carousel-item > img').xpath('@src').getall()
# print('Images:', response.css('#imagegallery > div.carousel-inner > div.carousel-item > img').xpath('@src').getall())
