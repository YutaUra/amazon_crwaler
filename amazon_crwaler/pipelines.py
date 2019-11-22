import psycopg2


class AmazonPipeline(object):

    def open_spider(self, spider):
        self.conn = psycopg2.connect(
            'host=database-1.caizbo93ln5z.us-east-2.rds.amazonaws.com '
            'port=5432 '
            'dbname=amazon '
            'user=postgres '
            'password=thym3594'
        )

    def close_spider(self, spider):
        self.conn.close()

    def process_item(self, item, spider):
        try:
            cur = self.conn.cursor()
            cur.execute(
                'insert into product('
                'time,'
                'title,'
                'url,'
                'review_num,'
                'description,'
                'shop_name,'
                'shop_url,'
                'shop_address,'
                'categories'
                ') values ('
                '%s,%s,%s,%s,%s,%s,%s,%s,%s'
                ')',
                (item['time'],
                 item['title'],
                 item['url'],
                 item['review_num'],
                 item['description'],
                 item['shop_name'],
                 item['shop_url'],
                 item['shop_address'],
                 item['categories'],
                 )
            )
        except Exception:
            self.conn = psycopg2.connect(
                'host=database-1.caizbo93ln5z.us-east-2.rds.amazonaws.com '
                'port=5432 '
                'dbname=amazon '
                'user=postgres '
                'password=thym3594'
            )
            return self.process_item(item, spider)
        self.conn.commit()
        return item
