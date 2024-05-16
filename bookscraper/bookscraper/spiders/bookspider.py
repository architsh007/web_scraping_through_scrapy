import scrapy


class BookspiderSpider(scrapy.Spider):
    name = "bookspider"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response):
        books = response.css('article.product_pod')
        for book in books:
            yield{
                'name' : book.css('a::attr(title)').get(),
                'price' : book.css('div p.price_color::text').get(),
                'url' : "https://books.toscrape.com/" + str(book.css('a[title]').attrib['href'])
            }

        next_page = str(response.css('li.next a::attr(href)').get())

        if next_page is not None:
            if 'catalogue/' in next_page:
                next_page_url = "https://books.toscrape.com/" + next_page
            else:
                next_page_url = "https://books.toscrape.com/catalogue/" + next_page
            
            yield response.follow(next_page_url, callback=self.parse)