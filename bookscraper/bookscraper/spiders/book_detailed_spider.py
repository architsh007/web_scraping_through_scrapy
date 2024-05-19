import scrapy
from bookscraper.items import BookItem

class BookDetailedSpiderSpider(scrapy.Spider):
    name = "book_detailed_spider"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]


    def parse(self, response):
        books = response.css('article.product_pod')

        for book in books:
            relative_url = str(book.css('a[title]').attrib['href'])
            
            if 'catalogue/' in relative_url:
                book_url = 'https://books.toscrape.com/' + relative_url
            else:
                book_url = 'https://books.toscrape.com/catalogue/' + relative_url
            
            yield scrapy.Request(book_url, callback=self.parse_book)

        next_page = str(response.css('li.next a::attr(href)').get())

        if next_page is not None:
            if 'catalogue/' in next_page:
                next_page_url = "https://books.toscrape.com/" + next_page
            else:
                next_page_url = "https://books.toscrape.com/catalogue/" + next_page
            
            yield response.follow(next_page_url, callback=self.parse)

    def parse_book(self, response):
        book_item = BookItem()
        book_item['book_url'] = response.url
        book_item['book_name'] =  response.css('li.active ::text').get()
        book_item['book_category'] = response.xpath("//ul[@class='breadcrumb']/li[@class='active']/preceding-sibling::li[1]/a/text()").get()
        book_item['rating'] = response.css('a::text')[-1].get()
        book_item['upc'] = response.css('table tr td::text')[0].get()
        book_item['product_type'] = response.css('table tr td::text')[1].get()
        book_item['price_excl_tax'] = response.css('table tr td::text')[2].get()
        book_item['price_incl_tax'] = response.css('table tr td::text')[3].get()
        book_item['tax'] = response.css('table tr td::text')[4].get()
        book_item['availability'] = response.css('table tr td::text')[5].get()
        book_item['number_of_reviews'] = response.css('table tr td::text')[6].get()
        book_item['description'] = response.xpath("//div[@class='sub-header']/following-sibling::p/text()").get()
    
        yield book_item