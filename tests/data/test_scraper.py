import pytest

from deepfield.data.bbref_pages import (BBRefLink, GamePage, PlayerPage,
                                        SchedulePage)
from deepfield.data.scraper import BBRefPageFactory, HtmlCache
import tests.data.test_utils

RES_URLS = [
    "https://www.baseball-reference.com/boxes/WAS/WAS201710120.shtml",
    "https://www.baseball-reference.com/leagues/MLB/2016-schedule.shtml",
    "https://www.baseball-reference.com/players/v/vendipa01.shtml"
]

class TestBBRefPageFactory:
    
    def test_page_types(self):
        for url, page_type in zip(RES_URLS, [GamePage, SchedulePage, PlayerPage]):
            assert type(BBRefPageFactory().create_page_from_url(url)) == page_type

class TestCache:
    
    def test_find_html_in_cache(self):
        cache = HtmlCache.get()
        for url in RES_URLS:
            assert cache.find_html(BBRefLink(url)) is not None
            
    def test_find_html_not_in_cache(self):
        pass