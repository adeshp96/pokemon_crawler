import sqlite3
from typing import List, Optional

from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route("/pokemon/", methods=["GET"], defaults={"pokemon_identifier": None})
@app.route("/pokemon/<string:pokemon_identifier>/", methods=["GET"])
def pokemon_endpoint(pokemon_identifier):
    print(f"Received request to fetch {pokemon_identifier}")
    with sqlite3.connect("pokemon.db") as connection:
        connection.row_factory = sqlite3.Row

        query = f"SELECT * FROM Pokemon"
        if pokemon_identifier:
            query += f" WHERE name='{pokemon_identifier}' or pokemon_id='{pokemon_identifier}'"

        # Query the database, getting all the pokemons as per the query
        try:
            db_rows = connection.execute(query).fetchall()
        except sqlite3.OperationalError:
            # Table missing
            return jsonify({"message": "Pokemon(s) not found"}), 404

        # Construct responses from each db row
        results = []
        for db_row in db_rows:
            results.append(construct_pokemon_response(db_row))

        if results:
            if pokemon_identifier:
                # Client asked for only one pokemon
                return jsonify(results[0]), 200
            else:
                return jsonify(results), 200
        else:
            return jsonify({"message": "Pokemon(s) not found"}), 404
    return jsonify({"message": "Internal server error"}), 500


def construct_pokemon_response(db_row: sqlite3.Row) -> Optional[dict]:
    # Extract relevant data from db rows
    if db_row:
        pokemon_id = db_row["pokemon_id"]
        return {
            "name": db_row["name"],
            "pokemon_id": pokemon_id,
            "abilities": get_abilities(pokemon_id),
            "forms": get_forms(pokemon_id),
            "stats": get_stats(pokemon_id),
            "species": get_species(pokemon_id),
        }
    return None


def get_attributes_from_db(pokemon_id: str, table_name: str, fields: List[str]) -> List[dict]:
    result = []
    with sqlite3.connect("pokemon.db") as connection:
        connection.row_factory = sqlite3.Row
        for row in connection.execute(f"SELECT * FROM {table_name} WHERE pokemon_id='{pokemon_id}'"):
            entry = {key: row[key] for key in fields}
            result.append(entry)
    return result


def get_abilities(pokemon_id: str) -> List[dict]:
    return get_attributes_from_db(pokemon_id, "Ability", ["name", "is_hidden", "slot"])


def get_forms(pokemon_id: str) -> List[dict]:
    return get_attributes_from_db(pokemon_id, "Form", ["name"])


def get_stats(pokemon_id: str) -> List[dict]:
    return get_attributes_from_db(pokemon_id, "Stat", ["name", "base_stat", "effort"])


def get_species(pokemon_id: str) -> dict:
    return get_attributes_from_db(pokemon_id, "Species", ["name"])[0]
