from datetime import date, time
from pathlib import Path
from typing import Iterable, Type

import pytest
from peewee import SqliteDatabase

from deepfield.data.dbmodels import Game, Play, Player, Team, Venue
from deepfield.data.dependencies import IgnoreDependencies
from deepfield.data.enums import FieldType, OnBase, TimeOfDay
from deepfield.data.pages import GamePage, Page, SchedulePage

test_db = SqliteDatabase(":memory:")
MODELS = [Game, Play, Player, Team, Venue]

def get_res_path(name: str) -> Path:
    base_path = Path(__file__).parent
    return (base_path / ("resources/" + name)).resolve()

def setup_module(module):
    test_db.bind(MODELS, bind_refs=False, bind_backrefs=False)
    test_db.connect()

def teardown_module(module):
    test_db.close()

class TestPage:
            
    base_url = "https://www.baseball-reference.com"
    page: Page
    page_type: Type[Page]
    
    @classmethod
    def setup_method(cls):
        test_db.create_tables(MODELS)
        file_path = (get_res_path(cls.name)).resolve()
        with open(file_path, "r", encoding="utf-8") as page_file:
            html = page_file.read()
            cls.page = cls.page_type(html, IgnoreDependencies())
    
    @classmethod
    def teardown_method(cls):
        test_db.drop_tables(MODELS)
    
    @classmethod
    def expand_urls(cls, suffixes: Iterable[str]) -> Iterable[str]:
        return [cls.base_url + s for s in suffixes]

    @classmethod
    def test_urls(cls, on_list_suffixes: Iterable[str], not_on_list_suffixes: Iterable[str]):
        page_urls = cls.page.get_referenced_page_urls()
        for url in cls.expand_urls(on_list_suffixes):
            assert url in page_urls
        for url in cls.expand_urls(not_on_list_suffixes):
            assert url not in page_urls

class TestSchedulePage(TestPage):
    
    name = "2016schedule.html"
    page_type = SchedulePage
    
    def test_urls(self):
        on_list = [
            "/boxes/KCA/KCA201604030.shtml",
            "/boxes/ANA/ANA201604040.shtml",
            "/boxes/TBA/TBA201604040.shtml",
        ]
        not_on_list = [
            "/leagues/MLB/2016-standard-batting.shtml",
            "/leagues/MLB/2016-schedule.shtml",
            "/boxes/BOS/BOS201708270.shtml"
        ]
        super().test_urls(on_list, not_on_list)

class TestGamePage(TestPage):
    
    name = "WAS201710120.shtml"
    page_type = GamePage

    def test_urls(self):
        on_list = [
            "/players/j/jayjo02.shtml",
            "/players/t/turnetr01.shtml",
            "/players/h/hendrky01.shtml",
            "/players/g/gonzagi01.shtml",
            "/players/d/daviswa01.shtml"
        ]
        not_on_list = [
            "/boxes/CHN/CHN201710090.shtml",
        ]
        super().test_urls(on_list, not_on_list)

    def test_queries(self):
        """TODO now that plays are being added, they need to be tested for
        correctness; player pages also need to be inserted before the page runs
        its queries because the plays reference player IDs. Use mock player
        records or just do a full insert of all dependencies here? Proper unit
        testing practices would probably encourage just hardcoding mock player
        records...
        """
        self.page._run_queries()
        venue = Venue.get(Venue.name == "Nationals Park")
        home = Team.get(Team.name == "Washington Nationals" and Team.abbreviation == "WSN")
        away = Team.get(Team.name == "Chicago Cubs" and Team.abbreviation == "CHC")
        Game.get(
                Game.name_id == "WAS201710120"
                and Game.local_start_time == time(20, 8)
                and Game.time_of_day == TimeOfDay.NIGHT.value
                and Game.field_type == FieldType.GRASS.value
                and Game.date == date(2017, 10, 12)
                and Game.venue_id == venue.id
                and Game.home_team_id == home.id
                and Game.away_team_id == away.id
            )
