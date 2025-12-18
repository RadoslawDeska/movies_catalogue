import requests
import random
from flask import current_app
from functools import lru_cache

def get_session():
    session = requests.Session()
    token = current_app.config.get("TMDB_TOKEN")
    session.headers.update({"Authorization": f"Bearer {token}"})
    return session


def get_json(url, params=None):
    session = get_session()
    response = session.get(url, params=params)
    response.raise_for_status()
    return response.json()


def print_response(response):
    import json

    # surowy słownik
    if isinstance(response, requests.Response):
        data = response.json()
    else:
        data = response
    # pretty-print
    print(json.dumps(data, indent=4, sort_keys=True))


def get_movies(how_many, list_type="popular"):
    data = []
    current_page = 1
    total_pages = None

    # Build the results list if asked for more than one page of results
    while how_many > len(data):
        response = get_movies_list(list_type, page=current_page)

        # Validate response structure
        if not isinstance(response, dict) or "results" not in response:
            break
        if total_pages is None:
            total_pages = response.get("total_pages", 1)

        # Extend the data list by new page data
        results = response.get("results")
        if results:
            data.extend(results)

        current_page += 1
        if current_page > total_pages:
            break

    # randomize the order
    random.shuffle(data)

    return data[:how_many]


def get_movies_list(list_type, page: int = 1):
    try:
        page = int(page)
    except (ValueError, TypeError):
        raise ValueError("page must be an integer")
    if page < 1:
        page = 1

    return get_json(f"https://api.themoviedb.org/3/movie/{list_type}?page={page}")


def get_poster_url(poster_path, size="w342"):
    base_url = "https://image.tmdb.org/t/p/"
    if poster_path:
        return f"{base_url}{size}{poster_path}"
    return ""

## PER ID ##
@lru_cache(maxsize=128)
def get_movie_details(movie_id: int):
    return get_json(f"https://api.themoviedb.org/3/movie/{movie_id}")


def get_movie_images(movie_id: int):
    return get_json(f"https://api.themoviedb.org/3/movie/{movie_id}/images").get(
        "backdrops", []
    )


def get_single_movie_cast(movie_id: int):
    return get_json(f"https://api.themoviedb.org/3/movie/{movie_id}/credits").get(
        "cast", []
    )


def search(search_query):
    return get_json(
        "https://api.themoviedb.org/3/search/movie", params={"query": search_query}
    )
