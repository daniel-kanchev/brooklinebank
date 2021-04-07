import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from brooklinebank.items import Article


class brooklinebankSpider(scrapy.Spider):
    name = 'brooklinebank'
    start_urls = ['https://brooklinebank.com/aboutus/brookline-bank-in-the-news/']

    def parse(self, response):
        links = response.xpath('//div[@id="subpage-content"]/ul/li/a/@href').getall()
        yield from response.follow_all(links, self.parse_article)

        next_page = response.xpath('//a[@class="next page-numbers"]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('(//strong)[3]/text()').get() or response.xpath('//h2/span/text()').get()
        if title and title.strip():
            title = title.strip()
        else:
            return

        content = response.xpath('//div[@id="subpage-content"]//text()').getall() or response.xpath('//div[@id="irwWrapper"]//text()').getall()
        content = [text for text in content if text.strip() and '{' not in text]
        content = " ".join(content[1:]).strip()

        item.add_value('title', title)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
