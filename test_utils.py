import crawler


class MockResponse:
    def __init__(self, data, ok):
        self.data = data
        self.ok = ok

    def json(self):
        return self.data


def mocked_requests_get(url: str) -> MockResponse:
    if url == crawler.PokemonCrawler.POKE_API_ROOT:
        return MockResponse(
            {"next": None, "results": [{"name": "bulbasaur", "url": "https://pokeapi.co/api/v2/pokemon/1/"}]}, True
        )
    elif url == "https://pokeapi.co/api/v2/pokemon/1/":
        return MockResponse(bulbasaur_response, True)
    else:
        return MockResponse(None, False)


bulbasaur_response = {
    "abilities": [
        {
            "ability": {"name": "overgrow", "url": "https://pokeapi.co/api/v2/ability/65/"},
            "is_hidden": False,
            "slot": 1,
        },
        {
            "ability": {"name": "chlorophyll", "url": "https://pokeapi.co/api/v2/ability/34/"},
            "is_hidden": True,
            "slot": 3,
        },
    ],
    "forms": [{"name": "bulbasaur", "url": "https://pokeapi.co/api/v2/pokemon-form/1/"}],
    "id": 1,
    "name": "bulbasaur",
    "species": {"name": "bulbasaur", "url": "https://pokeapi.co/api/v2/pokemon-species/1/"},
    "stats": [
        {"base_stat": 49, "effort": 0, "stat": {"name": "attack", "url": "https://pokeapi.co/api/v2/stat/2/"}},
        {"base_stat": 49, "effort": 0, "stat": {"name": "defense", "url": "https://pokeapi.co/api/v2/stat/3/"}},
        {"base_stat": 45, "effort": 0, "stat": {"name": "hp", "url": "https://pokeapi.co/api/v2/stat/1/"}},
        {"base_stat": 65, "effort": 1, "stat": {"name": "special-attack", "url": "https://pokeapi.co/api/v2/stat/4/"}},
        {"base_stat": 65, "effort": 0, "stat": {"name": "special-defense", "url": "https://pokeapi.co/api/v2/stat/5/"}},
        {"base_stat": 45, "effort": 0, "stat": {"name": "speed", "url": "https://pokeapi.co/api/v2/stat/6/"}},
    ],
}
