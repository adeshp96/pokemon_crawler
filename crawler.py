#!/usr/bin/env python

import sqlite3

import requests


class PokemonCrawler:
    POKE_API_ROOT = "https://pokeapi.co/api/v2/pokemon"

    def __init__(self):
        self.reset_database()

    def reset_database(self) -> None:
        with sqlite3.connect("pokemon.db") as connection:
            cursor = connection.cursor()
            cursor.executescript(
                """
                    CREATE TABLE IF NOT EXISTS Pokemon (
                        pokemon_id INT primary key,
                        name VARCHAR(255),
                        description VARCHAR(255)
                    );
                    CREATE TABLE IF NOT EXISTS Ability (
                        pokemon_id INT,
                        ability_id INT,
                        name VARCHAR(255),
                        is_hidden BOOLEAN,
                        slot INT,
                        CONSTRAINT PK_Ability PRIMARY KEY (pokemon_id, ability_id),
                        FOREIGN KEY(pokemon_id) REFERENCES Pokemon(pokemon_id) ON DELETE CASCADE
                    );
                    CREATE TABLE IF NOT EXISTS Form (
                        pokemon_id INT,
                        form_id INT,
                        name VARCHAR(255),
                        CONSTRAINT PK_Form PRIMARY KEY (pokemon_id, form_id),
                        FOREIGN KEY(pokemon_id) REFERENCES Pokemon(pokemon_id) ON DELETE CASCADE
                    );
                    CREATE TABLE IF NOT EXISTS Stat (
                        pokemon_id INT,
                        stat_id INT,
                        name VARCHAR(255),
                        base_stat INT,
                        effort INT,
                        CONSTRAINT PK_Stat PRIMARY KEY (pokemon_id, stat_id),
                        FOREIGN KEY(pokemon_id) REFERENCES Pokemon(pokemon_id) ON DELETE CASCADE
                    );
                    CREATE TABLE IF NOT EXISTS Species (
                        pokemon_id INT,
                        species_id INT,
                        name VARCHAR(255),
                        CONSTRAINT PK_Species PRIMARY KEY (pokemon_id, species_id),
                        FOREIGN KEY(pokemon_id) REFERENCES Pokemon(pokemon_id) ON DELETE CASCADE
                    );
                """
            )

    def _process_pokemon(self, pokemon_entry):
        with sqlite3.connect("pokemon.db") as connection:
            # To enable foreign key constraints and cascade delete
            connection.execute("PRAGMA foreign_keys = ON")

            pokemon_name = pokemon_entry["name"]

            # Need to use same id as PokeAPI to pick up any updates
            pokemon_id = pokemon_entry["url"].split("/")[-2]

            # Delete older entries to update the entries properly and use cascade deletes
            connection.execute(f"DELETE FROM Pokemon WHERE pokemon_id={pokemon_id}")
            connection.execute(f"INSERT INTO Pokemon VALUES ('{pokemon_id}', '{pokemon_name}', '{pokemon_name}')")

            print(f"Processing id:{pokemon_id} name:{pokemon_name}")
            # Get detailed info for this pokemon
            pokemon_detail = requests.get(pokemon_entry["url"])
            if pokemon_detail.ok:
                pokemon_detail_json = pokemon_detail.json()
            else:
                raise RuntimeError("Cannot fetch pokemon detail")

            # Update abilities
            for idx, ability in enumerate(sorted(pokemon_detail_json["abilities"], key=lambda x: x["ability"]["name"])):
                connection.execute(
                    f"INSERT INTO Ability VALUES ('{pokemon_id}', '{idx + 1}', '{ability['ability']['name']}', {ability['is_hidden']}, '{ability['slot']}')"
                )
            # Update forms
            for idx, form in enumerate(sorted(pokemon_detail_json["forms"], key=lambda x: x["name"])):
                connection.execute(f"INSERT INTO Form VALUES ('{pokemon_id}', '{idx + 1}', '{form['name']}')")
            # Update stats
            for idx, stat in enumerate(sorted(pokemon_detail_json["stats"], key=lambda x: x["stat"]["name"])):
                connection.execute(
                    f"INSERT INTO Stat VALUES ('{pokemon_id}', '{idx + 1}', '{stat['stat']['name']}', '{stat['base_stat']}', '{stat['effort']}')"
                )
            # Update species
            species = pokemon_detail_json["species"]
            connection.execute(f"INSERT INTO Species VALUES ('{pokemon_id}', '0', '{species['name']}')")

    def run(self) -> None:
        next_url_poke_api = self.POKE_API_ROOT
        while next_url_poke_api:
            response = requests.get(next_url_poke_api)
            if response.ok:
                response_json = response.json()
                next_url_poke_api = response_json["next"]
                for pokemon_entry in response_json["results"]:
                    self._process_pokemon(pokemon_entry)
            else:
                raise RuntimeError("Cannot fetch pokemons")


if __name__ == "__main__":
    crawler = PokemonCrawler()
    crawler.run()
