# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class BookscraperPipeline:

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        ## Strip all whitespaces from strings
        field_names = adapter.field_names()
        for field_name in field_names:
            if field_name != 'description':
                value = adapter.get(field_name)
                adapter[field_name] = value.strip()

        ## Category & Product Type --> switch to lowercase
        lowercase_keys = ['book_category', 'product_type']
        for lowercase_key in lowercase_keys:
            value = adapter.get(lowercase_key)
            adapter[lowercase_key] = value.lower()

        ## Price --> convert to float
        price_keys = ['price_excl_tax', 'price_incl_tax', 'tax']
        for price_key in price_keys:
            value = adapter.get(price_key)
            value = value.replace('£', '')
            adapter[price_key] = float(value)

        ## Availability --> extract number of books in stock
        availability_string = adapter.get('availability')
        split_string_array = availability_string.split('(')
        if len(split_string_array) < 2:
            adapter['availability'] = 0
        else:
            availability_array = split_string_array[1].split(' ')
            adapter['availability'] = int(availability_array[0])

        ## Reviews --> convert string to number
        num_reviews_string = adapter.get('number_of_reviews')
        adapter['number_of_reviews'] = int(num_reviews_string)
        
        ## Stars --> convert text to number
        stars_string = adapter.get('rating')
        split_stars_array = stars_string.split(' ')
        stars_text_value = split_stars_array[1].lower()
        if stars_text_value == "zero":
            adapter['rating'] = 0
        elif stars_text_value == "one":
            adapter['rating'] = 1
        elif stars_text_value == "two":
            adapter['rating'] = 2
        elif stars_text_value == "three":
            adapter['rating'] = 3
        elif stars_text_value == "four":
            adapter['rating'] = 4
        elif stars_text_value == "five":
            adapter['rating'] = 5
        
        return item


import sqlite3

class SaveToSQLitePipeline:

    def __init__(self):
        self.conn = sqlite3.connect('books.db')

        self.cur = self.conn.cursor()

        self.cur.execute("""
                    CREATE TABLE IF NOT EXISTS books(
                        id INTEGER PRIMARY KEY AUTOINCREMENT, 
                        book_url TEXT,
                        book_name TEXT,
                        upc TEXT,
                        product_type TEXT,
                        price_excl_tax REAL,
                        price_incl_tax REAL,
                        tax REAL,
                        availability INTEGER,
                        number_of_reviews INTEGER,
                        rating INTEGER,
                        book_category TEXT,
                        description TEXT
                    )
                        """)
        
    def process_item(self, item, spider):
        self.cur.execute("""INSERT INTO books (
            book_url, 
            book_name, 
            upc, 
            product_type, 
            price_excl_tax,
            price_incl_tax,
            tax,
            availability,
            number_of_reviews,
            rating,
            book_category,
            description
            ) VALUES (
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?
                )""", (
            item["book_url"],
            item["book_name"],
            item["upc"],
            item["product_type"],
            item["price_excl_tax"],
            item["price_incl_tax"],
            item["tax"],
            item["availability"],
            item["number_of_reviews"],
            item["rating"],
            item["book_category"],
            str(item["description"])
        ))

        self.conn.commit()

    def close_spider(self, spider):
        self.cur.close()
        self.conn.close()