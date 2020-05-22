from os import environ
from pathlib import Path

from deepfield.scraping.bbref_pages import BBRefLink, GamePage
from deepfield.scraping.dbmodels import Player, create_tables, db, drop_tables
from deepfield.enums import Handedness
from deepfield.scraping.pages import HtmlCache

db.init(":memory:")
environ["TESTING"] = "TRUE"

resources = HtmlCache.get()

def clean_db():
    drop_tables()
    create_tables()

def insert_mock_players(page: GamePage) -> None:
    ptables = page._player_tables
    with db.atomic():
        for table in ptables:
            for name, name_id in table.get_name_name_ids():
                _insert_mock_player(name, name_id)

def _insert_mock_player(name: str, name_id: str) -> None:
    fields = {
        "name": name,
        "name_id": name_id,
        "bats": Handedness.RIGHT.value,
        "throws": Handedness.RIGHT.value,
    }
    if Player.get_or_none(Player.name_id == name_id) is None:
        Player.create(**fields)