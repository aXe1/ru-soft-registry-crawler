# ru-soft-registry-crawler

Scrapy web crawler for [Unifed Registry of Russian software and databases](https://reestr.digital.gov.ru/reestr/)

## About

In Russian Federation government organizations are enforced to use so-called "Russian Software".
It could be true Russian software (produced by Russian company), or open source software for which some Russian company provides support, or even software produced by company, 51% of which is owned by Russian company.

Government publishes "Unified Registry of Russian software and databases" on the [official site](https://reestr.digital.gov.ru/reestr/).
There you could paginate over that big table, do some simple filter, sort and search, and see detailed card. But you cannot download it in any way, despite the government open data pursuit.
And AFAIK is not included in central government archives of open data, such as [Russian Open Data Portal](https://data.gov.ru/), or [Open Data Portal owned by Ministry of Digital Development, Communications and Mass Media of the Russian Federation](https://digital.gov.ru/opendata/).
So I wrote Scrapy crawler for that.

The registry is based on popular in Russia [Bitrix framework](https://www.1c-bitrix.ru/products/cms/). It contains some pagination bugs, and other quirks.

## Status

It can:

- Parse whole registry and a single page from command line
- Produce normalized output for both organizations and software items
- Is aware of site bugs (pagination problems)

But at this point it does **NOT**:

- Seperate organization and software items. _(BTW, you could do it easily: only software items contain `org_id` field)_
- Store data anywhere with relations
- Written paranoid enough to detect anomalies, and warn user about them. Only info about unknown fields in right pane of details page will be logged. And it will not stop crawling if exception occured - examine logs.
- Detects broken links

## Requirements

1. [Python 3](https://www.python.org/)
2. [Poetry](https://poetry.eustace.io/)

## How to use

1. Install [requirements](#Requirements)
2. Install project dependencies:

   ```sh
   poetry install
   ```

3. Run crawler for whole registry:

   ```sh
   poetry run scrapy crawl --output=items.json --output-format=json ru_soft_registry
   ```

**Note that currently it produces JSON array with mixed organizations and software objects.**

You could also:

- Adjust output format, and logging. Read `poetry run scrapy crawl --help` for details.
- Enable permanent HTTP cache by setting [HTTPCACHE_ENABLED](https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-enabled) to `true`. It will store cache in `./scrapy/httpcache`:
  ```sh
  poetry run scrapy crawl --set=HTTPCACHE_ENABLED=true --output=items.json --output-format=json ru_soft_registry
  ```
- Parse just one software page:
  ```sh
  poetry run scrapy parse https://reestr.digital.gov.ru/reestr/61304/
  ```
