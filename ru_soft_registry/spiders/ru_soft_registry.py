# -*- coding: utf-8 -*-
from scrapy import Item, Field, Spider
from scrapy.selector import Selector
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst, MapCompose, Identity
import dateparser
import re
from w3lib.html import remove_tags_with_content


class Software(Item):
    _id = Field()
    name = Field()
    exclusive_rights = Field()
    alt_names = Field()
    _class = Field()
    url = Field()
    num = Field()
    registration_date = Field()
    org_id = Field()
    decision_date = Field()
    decision = Field()
    order_url = Field()
    security_certificate_url = Field()


class SoftwareLoader(ItemLoader):
    def datetime_to_date(dt):
        return dt.date()

    def filter_empty(x):
        return None if x == '' else x

    def absolute_path(path, loader_context):
        return loader_context['response'].urljoin(path)

    default_input_processor = MapCompose(str.strip)
    default_output_processor = TakeFirst()

    num_in = MapCompose(str.strip, int)
    registration_date_in = MapCompose(str.strip, dateparser.parse,
                                      datetime_to_date)
    decision_date_in = MapCompose(str.strip, dateparser.parse,
                                  datetime_to_date)
    _class_out = Identity()  # Avoid default TakeFirst()
    alt_names_in = MapCompose(str.strip, filter_empty)
    alt_names_out = Identity()  # Avoid default TakeFirst()
    security_certificate_url_in = MapCompose(absolute_path)


class Organization(Item):
    _id = Field()
    _type = Field()
    name = Field()
    inn = Field()


class OrganizationLoader(ItemLoader):
    default_input_processor = MapCompose(str.strip)
    default_output_processor = TakeFirst()


class RuSoftRegistrySpider(Spider):
    # custom_settings = {
    #     'DOWNLOAD_DELAY': 2,
    # }
    name = 'ru_soft_registry'
    allowed_domains = ['reestr.digital.gov.ru']
    start_urls = ['https://reestr.digital.gov.ru/reestr/']

    # start_urls = ['https://reestr.digital.gov.ru/reestr/?PAGEN_1=262']

    def parse_details_page_right_pane_kv(self, selector):
        for item in selector.css('div > div'):
            key = item.css('span ::text').re_first('(.+):\Z').strip()
            value = Selector(
                text=remove_tags_with_content(item.get(), which_ones=['span']),
                type='html').css('html > body > div')
            yield (key, value)

    def parse_details_page(self, response):
        meaningful_area = response.css('.main_area > .flow_area')

        org_loader = OrganizationLoader(
            item=Organization(),
            selector=meaningful_area.css('.clear > div[style*="left"] > div'),
            response=response)
        org_loader.add_css('_type', 'h5 ::text')
        org_loader.add_css(
            'name',
            'div.clear:nth-of-type(1) > div:not([style*="width"]) a ::text')
        org_loader.add_css(
            '_id',
            'div.clear:nth-of-type(1) > div:not([style*="width"]) a::attr(href)',
            re='filter_owner=(\d+)')
        org_loader.add_css(
            'inn',
            'div.clear:nth-of-type(2) > div:not([style*="width"]) ::text')
        org = org_loader.load_item()
        yield org

        item = response.meta['item'] if 'item' in response.meta else Software()
        soft_loader = SoftwareLoader(
            item=item, selector=meaningful_area, response=response)

        soft_loader.add_value('_id', response.url, re='/reestr/(\d+)')
        soft_loader.add_value('org_id', org['_id'])
        soft_loader.add_css('name', '#pagetitle ::text')
        soft_loader.add_css('exclusive_rights',
                            'div[style*="left"] > p ::text')

        right_panel = meaningful_area.css('.clear > div[style*="right"]')
        keys = [
            'Альтернативные наименования',
            'Класс ПО',
            'Сайт производителя',
            'Дата регистрации',
            'Рег. номер ПО',
            'Дата решения уполномоченного органа',
            'Решение уполномоченного органа',
            'Ссылка на приказ Минкомсвязи',
            'Сертификат безопасности',
        ]
        for key, value in self.parse_details_page_right_pane_kv(right_panel):
            if key == 'Альтернативные наименования':
                soft_loader.add_value('alt_names',
                                      value.css('::text').getall())
            elif key == 'Класс ПО':
                soft_loader.add_value('_class',
                                      value.css('font::attr(title)').getall())
            elif key == 'Сайт производителя':
                soft_loader.add_value('url', value.css('a::attr(href)').get())
            elif key == 'Дата регистрации':
                soft_loader.add_value('registration_date',
                                      value.css('::text').get())
            elif key == 'Рег. номер ПО':
                soft_loader.add_value('num', value.css('::text').get())
            elif key == 'Дата решения уполномоченного органа':
                soft_loader.add_value('decision_date',
                                      value.css('::text').get())
            elif key == 'Решение уполномоченного органа':
                soft_loader.add_value('decision', value.css('::text').get())
            elif key == 'Ссылка на приказ Минкомсвязи':
                soft_loader.add_value('order_url',
                                      value.css('a::attr(href)').get())
            elif key == 'Сертификат безопасности':
                soft_loader.add_value('security_certificate_url',
                                      value.css('a::attr(href)').get())
            elif not key in keys:
                self.logger.warning(
                    'Unknown key in right pane of details page: %s', key)

        yield soft_loader.load_item()

    def parse_page(self, response):
        table_body = response.css('.result_area>.line:not(.head)')
        for row in table_body:
            # soft_loader = SoftwareLoader(item=Software(), selector=row, response=response)
            # soft_loader.add_css('num', '.num ::text')
            # soft_loader.add_css('name', '.name * ::text')
            # soft_loader.add_css('_class', '.class * ::text')
            # soft_loader.add_css('registration_date', '.date::text')
            # soft_loader.add_css('url', '.status > a::attr(href)')
            # soft_loader.add_css('_id', '.name a::attr(href)', re='/reestr/(\d+)')

            details_page_url = row.css('.name a::attr(href)').get()
            yield response.follow(
                details_page_url, callback=self.parse_details_page)
            # meta={'item': soft_loader.load_item()})

    def parse(self, response):
        if re.search(r'/reestr/\d+', response.url):
            yield from self.parse_details_page(response)
            return

        yield from self.parse_page(response)

        last_page_num = int(
            response.css(
                '.page_nav_area>.nav_item.dots+a.nav_item::text').get())
        pagination = '?PAGEN_1={}'
        for next_page in range(2, last_page_num + 1):
            yield response.follow(
                pagination.format(next_page), callback=self.parse_page)
