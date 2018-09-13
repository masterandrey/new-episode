import scrapy
from scrapy.loader.processors import Join, MapCompose, TakeFirst


def size_processor(tds):
    MULT = {
        ' МБ': 10 ** 6,
        ' ГБ': 10**9,
    }
    size_str = tds[1]
    for mult in MULT:
        if size_str.endswith(mult):
            return int(float(size_str[:-len(mult)]) * MULT[mult])
    return int(size_str)


class Movie(scrapy.Item):
    title = scrapy.Field(output_processor=TakeFirst())
    seeds_num = scrapy.Field(input_processor=MapCompose(int), output_processor=TakeFirst())
    size = scrapy.Field(input_processor=size_processor, output_processor=TakeFirst())
    details_link = scrapy.Field(output_processor=TakeFirst())
    seasons = scrapy.Field()
    last_season = scrapy.Field()
    name = scrapy.Field()
    original_name = scrapy.Field()
    last_episode = scrapy.Field()
    subtitles = scrapy.Field()
    has_english_subtitles = scrapy.Field()
    torrent_link = scrapy.Field()
    id = scrapy.Field()
