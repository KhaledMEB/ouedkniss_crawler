import scrapy


class VehiculesSpider(scrapy.Spider):
    name = 'vehicules'
    allowed_domains = ['ouedkniss.com']
    start_urls = ['https://ouedkniss.com/automobiles/']

    def parse(self, response):
        # get urls of each article
        urls = response.css('div.annonce > ul > li.annonce_titre > a::attr(href)').extract()
        for url in urls:
            if url:
                url = response.urljoin(url)
                yield scrapy.Request(url=url, callback=self.parse_details)

        # follow pagination link
        # the class in ouedkniss website are missleading (next is previous?)
        next_page_urls = response.xpath('//div[@id="divPages"]').css('a.page_arrow::attr(href)').extract()
        next_page_url = next_page_urls[len(next_page_urls)-1]
        if next_page_url:
            # next page exemple: '//www.ouedkniss.com/automobiles/2'
            next_page_url = 'https:'+next_page_url
            yield scrapy.Request(url=next_page_url, callback=self.parse)


    def parse_details(self, response):
        annonce = response.xpath('//div[@id="annonce"]')
        description = annonce.xpath('//div[@id="Description"]')

        yield{
            'numero': annonce.xpath('//div[@id="Description"]/p/a/span/text()').get(),
            'nom': annonce.xpath('//h1/text()').get(),

            # a quick way to get all the below commented filled
            **(dict(zip(description.xpath('//p/label/text()').getall(), description.xpath('//p/span/text()').getall()))),
            # 'date_publication':  description.xpath('//p/span/text()').getall()[1],
            # 'type': description.xpath('//p[@id="Catégorie"]/span/text()').get(),
            # 'energie': description.xpath('//p[@id="Energie"]/span/text()').get(),
            # 'moteur': description.xpath('//p[@id="Moteur"]/span/text()').get(),
            # 'transmission': description.xpath('//p[@id="Transmission"]/span/text()').get(),
            # 'kilometrage': description.xpath('//p[@id="Kilométrage"]/span/text()').get(),
            # 'couleur': description.xpath('//p[@id="Couleur"]/span/text()').get(),
            # 'papiers': description.xpath('//p[@id="Papiers"]/span/text()').get(),
            # 'options': description.xpath('//p[@id="Options"]/span/text()').getall(),

            'adresse': annonce.xpath('//div[@id="Annonceur"]').css('p.Adresse::text').extract_first(),
            'prix':  annonce.xpath('//div[@id="espace_prix"]/p[@id="Prix"]/span/text()').get(),
            'description': description.xpath('//div[@id="GetDescription"]/text()').get(),
            'url': response.url,
        }