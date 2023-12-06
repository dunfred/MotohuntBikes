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
        print('Home Page')
        make_paths = response.css('#content > div:nth-child(4) > div > div:nth-child(2) > div > a::attr(href)').getall()
        make_links = [self.durl + path for path in make_paths]
        # pprint(make_links)

        for make_page in make_links:
            yield response.follow(make_page, callback=self.get_make_page)

    def get_make_page(self, response):
        # Get links to motor page by model
        print("Make Page:", response.url)
        model_paths = response.css('#content > div:nth-child(4) > div > div > div > a::attr(href)').getall()
        model_links = [self.durl + path for path in model_paths]
        # pprint(model_links)

        for model_page in model_links:
            yield response.follow(model_page, callback=self.get_model_page)

    def get_model_page(self, response):
        # Go through all pages to scrape motors
        print("Model Page:", response.url)
        models_page_url = response.url

        results_text = response.css('#results-text::text').get()

        try:
            page_offet, total_records = results_text.strip().split('of')
            
            start, end = page_offet.strip().split('-')
            start = int(start.strip())
            end   = int(end.strip())
            total_records = int(total_records.strip().replace(',',''))

            print('Start:', start, 'End:', end, "Total Records:",total_records)

            for i in range(start, total_records, end)[:1]: # Remember to correct this
                next_page = models_page_url + f'&start={i}'
                yield response.follow(next_page, callback=self.get_paginated_motor_page)

        except Exception as e:
            print('No results pagination:', results_text, 'Error Message:', e)
            motors = response.css("#srp-results-container > div > div > div.card-body.nolinkcolor > a::attr(href)").getall()
            motor_links = [self.durl + path for path in motors]
            # pprint(motors)

            for model_page in motor_links:
                yield response.follow(model_page, callback=self.scrape_motorbike)


    def get_paginated_motor_page(self, response):
        print("Scrape Page:", response.url)

        motors = response.css("#srp-results-container > div > div > div.card-body.nolinkcolor > a::attr(href)").getall()
        motor_links = [self.durl + path for path in motors]
        # pprint(motors)

        for model_page in motor_links:
            yield response.follow(model_page, callback=self.scrape_motorbike)

    def scrape_motorbike(self, response):
        print("Scrape Bike Page:", response.url)
        item = MotohuntbikesItem()

        # all_rows = response.css('#content > div.row > div > div.row.bottom-margin > div.col-xs-12.col-sm-12.col-md-7.col-lg-7.col-xl-7.bottom-margin > div').getall()
        # for row in all_rows:
        soup = BeautifulSoup(response.body, 'lxml')

        # Get VIN
        vin_label = soup.find('b', text='VIN:')
        vin_parent = vin_label.parent
        vin = vin_parent.find_next('div').text.strip()
        item['vin'] = vin
        if not item['vin']:
            return
        print('VIN:', vin)

        # Get MAKE
        make_label = soup.find('div', text='Make')
        make = make_label.find_next('div').text.strip()
        item['make'] = make
        if not item['make']:
            return
        print('MAKE:', make)

        # Get MODEL
        try:
            model_label = soup.find('div', text='Model')
            print('MODEL LABEL:', model_label, response.url)
            model = model_label.find_next('div').text.strip()
            item['model'] = model
            if not item['model']:
                return
            print('MODEL:', model, response.url)
        except Exception:
            return

        # Get YEAR
        year_label = soup.find('div', text='Model Year')
        year = year_label.find_next('div').text.strip()
        item['year'] = year
        if not item['year']:
            return
        print('YEAR:', year, response.url)

        # Get PRICE
        try:
            price_label = soup.find('b', text='Price:')
            price_parent = price_label.parent
            price = float(price_parent.find_next('div').text.strip().replace(',','').replace('$',''))
            item['price'] = price
            print('PRICE:', price, response.url)
        except Exception:
            pass

        # Get CONDITION
        try:
            condition_label = soup.find('b', text='Condition:')
            print('CONDITION LABEL:', condition_label, response.url)
            condition_parent = condition_label.parent
            condition = condition_parent.find_next('div').text.strip()
            item['condition'] = condition
            print('CONDITION:', condition, response.url)
        except Exception:
            pass

        # item['vin']                 = response.css('#content > div.row > div > div.row.bottom-margin > div.col-xs-12.col-sm-12.col-md-7.col-lg-7.col-xl-7.bottom-margin > div:nth-child(12) > div.col-6.col-md-5.col-lg-4::text').get()
        # item['make']                = response.css('#content > div.row > div > div.row.bottom-margin > div.col-xs-12.col-sm-12.col-md-7.col-lg-7.col-xl-7.bottom-margin > div.row.d-none.d-md-block.d-lg-block.d-xl-block > div > div:nth-child(2) > div > div:nth-child(12) > div.col-6.col-sm-7::text').get()
        # item['model']               = response.css('#content > div.row > div > div.row.bottom-margin > div.col-xs-12.col-sm-12.col-md-7.col-lg-7.col-xl-7.bottom-margin > div.row.d-none.d-md-block.d-lg-block.d-xl-block > div > div:nth-child(2) > div > div:nth-child(14) > div.col-6.col-sm-7::text').get()
        # item['year']                = response.css('#content > div.row > div > div.row.bottom-margin > div.col-xs-12.col-sm-12.col-md-7.col-lg-7.col-xl-7.bottom-margin > div.row.d-none.d-md-block.d-lg-block.d-xl-block > div > div:nth-child(2) > div > div:nth-child(15) > div.col-6.col-sm-7::text').get()
        # item['price']               = response.css('#content > div.row > div > div.row.bottom-margin > div.col-xs-12.col-sm-12.col-md-7.col-lg-7.col-xl-7.bottom-margin > div:nth-child(7) > div.col-9.col-lg-10::text').get()
        # item['condition']           = response.css('#content > div.row > div > div.row.bottom-margin > div.col-xs-12.col-sm-12.col-md-7.col-lg-7.col-xl-7.bottom-margin > div:nth-child(5) > div.col-9.col-lg-10::text').get()
        
        # item['dealer']              = response.css('#content > div.row > div > div.row.bottom-margin > div.col-xs-12.col-sm-12.col-md-7.col-lg-7.col-xl-7.bottom-margin > div:nth-child(6) > div.col-9.col-lg-10::text').get()
        # item['car_url']             = response.url
        # item['dealer_link']         = response.css('#viewondealerwebsitelink::attr(href)').get()
        # item['dealer_number']       = response.css('#content > div.row > div > div.row.bottom-margin > div.col-xs-12.col-sm-12.col-md-5.col-lg-5.col-xl-5 > div:nth-child(1) > div > a::text').get()
        # item['dealer_description']  = response.css('#content > div.row > div > div.row.bottom-margin > div.col-xs-12.col-sm-12.col-md-5.col-lg-5.col-xl-5 > div:nth-child(5) > div > p::text').get()
        # item['mileage']             = response.css('#content > div.row > div > div.row.bottom-margin > div.col-xs-12.col-sm-12.col-md-7.col-lg-7.col-xl-7.bottom-margin > div:nth-child(8) > div.col-9.col-lg-10::text').get()
        # item['color']               = response.css('#content > div.row > div > div.row.bottom-margin > div.col-xs-12.col-sm-12.col-md-7.col-lg-7.col-xl-7.bottom-margin > div:nth-child(9) > div.col-9.col-lg-10::text').get()
        # item['location']            = response.css('#content > div.row > div > div.row.bottom-margin > div.col-xs-12.col-sm-12.col-md-7.col-lg-7.col-xl-7.bottom-margin > div:nth-child(4) > div.col-9.col-lg-10::text').get()
        # item['engine']              = response.css('#content > div.row > div > div.row.bottom-margin > div.col-xs-12.col-sm-12.col-md-7.col-lg-7.col-xl-7.bottom-margin > div:nth-child(26) > div.col-8.col-lg-9.spec-right::text').get()
        # item['fuel_type']           = response.css('#content > div.row > div > div.row.bottom-margin > div.col-xs-12.col-sm-12.col-md-7.col-lg-7.col-xl-7.bottom-margin > div.row.d-none.d-md-block.d-lg-block.d-xl-block > div > div:nth-child(2) > div > div:nth-child(7) > div.col-6.col-sm-7::text').get()
        # item['body_type']           = response.css('#content > div.row > div > div.row.bottom-margin > div.col-xs-12.col-sm-12.col-md-7.col-lg-7.col-xl-7.bottom-margin > div.row.d-none.d-md-block.d-lg-block.d-xl-block > div > div:nth-child(2) > div > div:nth-child(9) > div.col-6.col-sm-7::text').get()
        # item['image_links']         = response.css('#imagegallery > div.carousel-inner > div.carousel-item > img').xpath('@src').getall()
        # print('Images:', response.css('#imagegallery > div.carousel-inner > div.carousel-item > img').xpath('@src').getall())
        
        
        
        # Clean
        # item['vin']                 = str(item['vin']).strip() if item['vin'] else item['vin'] 
        # item['make']                = str(item['make']).strip() if item['make'] else item['make'] 
        # item['model']               = str(item['model']).strip() if item['model'] else item['model'] 
        # item['year']                = str(item['year']).strip() if item['year'] else item['year'] 
        # item['price']               = str(item['price']).strip() if item['price'] else item['price'] 
        # item['condition']           = str(item['condition']).strip() if item['condition'] else item['condition'] 
        # item['dealer']              = str(item['dealer']).strip() if item['dealer'] else item['dealer'] 
        # item['dealer_link']         = str(item['dealer_link']).strip() if item['dealer_link'] else item['dealer_link'] 
        # item['dealer_number']       = str(item['dealer_number']).strip() if item['dealer_number'] else item['dealer_number'] 
        # item['dealer_description']  = str(item['dealer_description']).strip() if item['dealer_description'] else item['dealer_description'] 
        # item['mileage']             = str(item['mileage']).strip() if item['mileage'] else item['mileage'] 
        # item['color']               = str(item['color']).strip() if item['color'] else item['color'] 
        # item['location']            = str(item['location']).strip() if item['location'] else item['location'] 
        # item['engine']              = str(item['engine']).strip() if item['engine'] else item['engine'] 
        # item['fuel_type']           = str(item['fuel_type']).strip() if item['fuel_type'] else item['fuel_type'] 
        # item['body_type']           = str(item['body_type']).strip() if item['body_type'] else item['body_type'] 
        # item['image_links']         = str(item['image_links']).strip() if item['image_links'] else item['image_links'] 
        # item['car_url']             = str(item['car_url']).strip() if item['car_url'] else item['car_url'] 
        yield item

# scrapy crawl motohunt -O motohunt.json


