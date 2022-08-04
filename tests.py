import sqlite3
from unittest import mock
from unittest.mock import patch

import pytest

import crawler
import pokemon_server
import test_utils


class Test:
    def setup(self):
        with sqlite3.connect("pokemon.db") as connection:
            cursor = connection.cursor()
            cursor.executescript(
                """
                DROP table IF EXISTS Pokemon;
                DROP table IF EXISTS Ability;
                DROP table IF EXISTS Form;
                DROP table IF EXISTS Stat;
                DROP table IF EXISTS Species;
            """
            )
        self.crawler = crawler.PokemonCrawler()

    @mock.patch("crawler.requests.get", side_effect=test_utils.mocked_requests_get)
    def test_db_entry(self, mock_get, client, bulbasaur_entry):
        # Test if crawler sets DB entries appropriately
        self.crawler.run()
        response = client.get("/pokemon/bulbasaur/")
        assert response.json == bulbasaur_entry

    @mock.patch("crawler.requests.get", side_effect=test_utils.mocked_requests_get)
    def test_pokemon_modified(self, mock_get, client, bulbasaur_entry):
        # Test if modifications at PokeAPI are updated properly
        self.crawler.run()
        response = client.get("/pokemon/bulbasaur/")
        assert response.json == bulbasaur_entry
        test_utils.bulbasaur_response["forms"][0]["name"] = "new-bulbasaur"  # type: ignore
        self.crawler.run()
        response = client.get("/pokemon/bulbasaur/")
        bulbasaur_entry_updated = dict(bulbasaur_entry)
        bulbasaur_entry_updated["forms"][0]["name"] = "new-bulbasaur"
        assert response.json == bulbasaur_entry_updated

    def test_our_api(self, client, bulbasaur_entry):
        # Test we expose the retrieved data correctly
        with sqlite3.connect("pokemon.db") as connection:
            connection.row_factory = sqlite3.Row
            connection.executescript(
                """
                    INSERT INTO Pokemon VALUES ('1', 'bulbasaur', 'bulbasaur');
                    INSERT INTO Ability VALUES ('1', '1', 'chlorophyll', True, '3');
                    INSERT INTO Ability VALUES ('1', '2', 'overgrow', False, '1');
                    INSERT INTO Form VALUES ('1', '1', 'bulbasaur');
                    INSERT INTO Stat VALUES ('1', '1', 'attack', '49', '0');
                    INSERT INTO Stat VALUES ('1', '2', 'defense', '49', '0');
                    INSERT INTO Stat VALUES ('1', '3', 'hp', '45', '0');
                    INSERT INTO Stat VALUES ('1', '4', 'special-attack', '65', '1');
                    INSERT INTO Stat VALUES ('1', '5', 'special-defense', '65', '0');
                    INSERT INTO Stat VALUES ('1', '6', 'speed', '45', '0');
                    INSERT INTO Species VALUES ('1', '1', 'bulbasaur');
                """
            )
        response = client.get("/pokemon/bulbasaur/")
        assert response.json == bulbasaur_entry

    @mock.patch("crawler.requests.get", side_effect=test_utils.mocked_requests_get)
    def test_failures(self, mock_get, client):
        # Test failures are gracefully handled
        self.crawler.POKE_API_ROOT = "non existent"
        with pytest.raises(RuntimeError):
            self.crawler.run()
        response = client.get("/pokemon/bulbasaur/")
        assert response.status_code == 404

    @pytest.mark.skip(reason="integration test which runs entire crawler so run only before release")
    @pytest.mark.integrationtest
    def test_end_to_end(self, client, bulbasaur_entry):
        self.crawler.run()
        response = client.get("/pokemon/bulbasaur")
        assert response.json == bulbasaur_entry


@pytest.fixture()
def client():
    return pokemon_server.app.test_client()


@pytest.fixture()
def bulbasaur_entry():
    return {
        "abilities": [
            {"is_hidden": 1, "name": "chlorophyll", "slot": 3},
            {"is_hidden": 0, "name": "overgrow", "slot": 1},
        ],
        "forms": [{"name": "bulbasaur"}],
        "name": "bulbasaur",
        "pokemon_id": 1,
        "species": {"name": "bulbasaur"},
        "stats": [
            {"base_stat": 49, "effort": 0, "name": "attack"},
            {"base_stat": 49, "effort": 0, "name": "defense"},
            {"base_stat": 45, "effort": 0, "name": "hp"},
            {"base_stat": 65, "effort": 1, "name": "special-attack"},
            {"base_stat": 65, "effort": 0, "name": "special-defense"},
            {"base_stat": 45, "effort": 0, "name": "speed"},
        ],
    }
