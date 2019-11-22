#　使い方
```tarminal
pip install -r requirements.txt

cd amazon_crwaler

scrapy crawl AmazonProduct
```

# クローリングファイル
`amazon_crawler/spiders/AmazonProduct.py`

最初のカテゴリー一覧から始まり、順々にカテゴリーを絞り、商品の単一ページまでさかのぼってクロールする

URLの簡略化を適宜行っている。

> 例:\
> `https://www.amazon.co.jp/%E3%82%BF%E3%83%AF%E3%83%BC-%E6%98%9F4%E3%81%A4%E4%BB%A5%E4%B8%8A-%E3%83%87%E3%82%B9%E3%82%AF%E3%83%88%E3%83%83%E3%83%97/s?bbn=2151949051&rh=n%3A2127209051%2Cn%3A%212127210051%2Cn%3A2151949051%2Cn%3A6111448051%2Cp_72%3A2150400051&s=review-rank&dc&qid=1573566740&rnid=2151949051&ref=sr_nr_n_1`\
>
> `https://www.amazon.co.jp/s?rh=n%3A2127209051%2Cn%3A%212127210051%2Cn%3A2151949051%2Cn%3A6111448051%2Cp_72%3A2150400051&s=review-rank`\
>
> 理由：URLのフォーマットを統一することで、別URLでも同一内容のページをクロール（重複）することを防ぐ

# データの保存
デフォルトではAWSのデータベースにデータを格納するようにしている。
それに加えて手元のcsvもデータが欲しければ
```terminal
scrapy crawl AmazonProduct -o 〇〇.csv
```
とするとよい

データの保存に関しては、
`amazon_crawler/pipelines.py`
がAWSへの登録処理を行っている。

# バン対策等
1. アクセスする際のUserAgentをランダムに切り替える
1. ipアドレスを適宜偽装する
これらの処理は
`amazon_crwaler/middlewares.py`
で行っている。

1. に関してはモジュールでの動作をそのまま使っており、
2. に関してはTor, polipoを使っている。これは設定がややこしいので、最悪なくてもよい。

# 各種セッティング
`amazon_crwaler/settings.py`
で設定を行う。

### 重要な項目だけ説明する。

`DOWNLOAD_DELAY`はリクエストの間隔(秒）を設定する\
動作での経験上3以上かつ、ip等を偽装すればバンされにくい。

