from abc import abstractmethod


class EpisodesScraper:
    """
    Returns scraping result as async iterators
    """
    @abstractmethod
    async def episodes(self, search_string: str) -> dict:
        """
        :param url: torrent site to scrape
        :param search_string: string to search
        :return: episode's dicts
        """
        pass
