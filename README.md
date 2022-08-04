# Pokemon Crawler

`PokemonCrawler` is a crawler to catch pokemons from the `PokeAPI` and store it in an SQLite database. The pokemons are then exposed via a REST API built on Flask.

## Design
* `crawler.py` contains the crawler class `PokemonCrawler`. `PokemonCrawler::run()` fetches the pokemons using pagination of PokeAPI.
* Data is stored in SQLite in Python.
* Retrieved data is exposed via REST API at endpoint `http://127.0.0.1:5000/pokemon/<identifier>` to get a particular Pokemon or `http://127.0.0.1:5000/pokemon/` to get all Pokemons. Identifier could be Pokemon's name or id.
* Type hints are added to all interface methods. Boundary conditions are being checked for robustness. Code has been processed through code formatter (`black`), `isort` and type checked using `mypy`.

## Run

```bash
$ ./crawler.py # Start catching Pokemon
Processing id:1 name:bulbasaur
Processing id:2 name:ivysaur
Processing id:3 name:venusaur
...
$ FLASK_APP=pokemon_server.py FLASK_ENV=development flask run --port 5000 # Start the REST server
```
Note that you can start the REST server while crawler is still running.
```bash
$ curl --location --request GET 'http://127.0.0.1:5000/pokemon/bulbasaur'
{
  "abilities": [
    {
      "is_hidden": 1, 
      "name": "chlorophyll", 
      "slot": 3
    }, 
    {
      "is_hidden": 0, 
      "name": "overgrow", 
      "slot": 1
    }
  ], 
  "forms": [
    {
      "name": "bulbasaur"
    }
  ], 
  "name": "bulbasaur", 
  "pokemon_id": 1, 
  "species": {
    "name": "bulbasaur"
  }, 
  "stats": [
    {
      "base_stat": 49, 
      "effort": 0, 
      "name": "attack"
    }, 
    {
      "base_stat": 49, 
      "effort": 0, 
      "name": "defense"
    }, 
    ...
  ]
}

```

## Database
* `SQLite` is used to manage data. Pokemons are stored in table called `Pokemon` and the other properties (Abilities, Forms, Stats and Species) are stored in a different table each and uses foreign key to `Pokemon` table's id.
* Cascade delete is used to delete Pokemon's entries from all tables on deletion of entry from `Pokemon` table.
* Database Schema is as described below:
```sql
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
```
## Testing
Exhaustive testing to cover various potential scenarios as described below. 
```bash
$ pytest -v tests.py
...
tests.py::Test::test_db_entry # Test if crawler sets database entries appropriately
tests.py::Test::test_pokemon_updated_at_pokeapi # Test if modifications at PokeAPI are updated properly
tests.py::Test::test_our_api_working # Test we expose the retrieved data correctly
tests.py::Test::test_failures # Test failures are gracefully handled
```

## Scaling
* Exposed data won't scale with the flask development server being used. For production, we need to use a WSGI server.
* To crawl data at scale, we can use multiple processes or even multiple nodes writing to same database.
* To scale up the database, we can add indexing or use a distributed database like DynamoDB or Cassandra. Another alternative would be sharding the database.