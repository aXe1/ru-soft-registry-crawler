poetry run scrapy parse https://reestr.digital.gov.ru/reestr/61304/
poetry run scrapy crawl --logfile=scrapy.log -o items.json -t json ru_soft_registry

poetry run scrapy parse -s HTTPCACHE_ENABLED=false https://reestr.digital.gov.ru/reestr/61304/
poetry run scrapy crawl -s HTTPCACHE_ENABLED=false --logfile=scrapy.log -o items.json -t json ru_soft_registry
