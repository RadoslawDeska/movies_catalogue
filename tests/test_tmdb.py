from requests.exceptions import HTTPError

import tmdb_client

__doc__ = """
# Testing Workflow with `mock_tmdb_session`

1. A test function (e.g., `test_get_movies_list`) requests the `mock_tmdb_session` fixture.
2. The `mock_tmdb_session` fixture runs:
   - It creates a `mock_response` and a `mock_session` (both are `Mock` objects).
   - It sets `mock_session.get.return_value = mock_response`.
   - It monkeypatches `tmdb_client.get_session` to always return `mock_session`.
3. The test calls `tmdb_client.get_movies_list("popular")`.
4. `get_movies_list` calls `get_json(...)`.
5. `get_json` calls the patched `get_session()`.
6. `get_session()` returns the mocked session.
7. `get_json` calls `mock_session.get(...)`.
8. `mock_session.get()` returns `mock_response`.
9. `mock_response.json()` returns the fake data configured by the test.
10. `get_json` returns that fake data.
11. The test asserts that the result matches the fake data.
"""


# ============ Define reusable fixture to mock session and response ============
from tests.fixtures import mock_tmdb_session

# ========================== Use the fixture in tests ==========================
import pytest  # the order of imports matters

def test_get_movies_list(mock_tmdb_session):
    # 1. Setup: Configure what the API should "return"
    mock_tmdb_session["response"].json.return_value = {
        "results": ["Movie 1", "Movie 2"],
        "total_pages": 1,
    }
    # 2. Execute: Call the function
    movies_list = tmdb_client.get_movies_list(list_type="popular")
    # 3. Assert: Verify the result
    assert movies_list == {"results": ["Movie 1", "Movie 2"], "total_pages": 1}
    # 4. Verify that the session.get method was called exactly once, using the specified URL and with params=None."
    mock_tmdb_session["session"].get.assert_called_once_with(
        "https://api.themoviedb.org/3/movie/popular?page=1",
        params=None,  # the actual params to be checked are in URL for this function
    )


def test_get_movie_details(mock_tmdb_session):
    tmdb_client.get_movie_details.cache_clear()  # the tested function uses cache, so clear it to always test new call
    mock_tmdb_session["response"].json.return_value = {
        "title": "Movie Title",
        "runtime": 1,
    }
    movie_details = tmdb_client.get_movie_details(movie_id=1)
    assert movie_details == {"title": "Movie Title", "runtime": 1}
    mock_tmdb_session["session"].get.assert_called_once_with(
        "https://api.themoviedb.org/3/movie/1", params=None
    )

def test_get_movie_details_invalid_id_api_error(mock_tmdb_session):
    """Test that calling get_movie_details with an invalid ID results in an
    HTTPError from the API due to invalid input.
    """
    tmdb_client.get_movie_details.cache_clear()

    # 1. Setup: Configure the mock response to simulate an API error
    #    We need to mock the HTTP status code that would cause raise_for_status to trigger (404 error).
    mock_tmdb_session["response"].status_code = 404
    mock_tmdb_session["response"].json.return_value = {
        "success": False,
        "status_code": 6,
        "status_message": "Invalid id: The pre-requisite id is invalid or not found."
    }
    # Critically, configure raise_for_status to raise an exception.
    # The actual HTTPError constructor needs a response object, but when mocking side_effect,
    # we just provide an instance of the exception.
    mock_tmdb_session["response"].raise_for_status.side_effect = HTTPError(
        "404 Client Error: Not Found for url: https://api.themoviedb.org/3/movie/abc"
    )

    # 2. Execute & Assert: Call the function and assert that it raises the expected exception
    with pytest.raises(HTTPError):
        tmdb_client.get_movie_details(movie_id="abc") # Passing the string "abc"

    # 3. Verify: Check the API call was attempted with the incorrect ID in the URL
    mock_tmdb_session["session"].get.assert_called_once_with(
        "https://api.themoviedb.org/3/movie/abc", # The URL will include "abc"
        params=None
    )

def test_get_movie_images(mock_tmdb_session):
    mock_tmdb_session["response"].json.return_value = {
        "id": 1,
        "backdrops": [],
    }
    result = tmdb_client.get_movie_images(movie_id=1)
    assert result == []  # assert the extracted backdrops is empty list
    mock_tmdb_session["session"].get.assert_called_once_with(
        "https://api.themoviedb.org/3/movie/1/images", params=None
    )


def test_get_single_movie_cast(mock_tmdb_session):
    mock_tmdb_session["response"].json.return_value = {
        "id": 1,
        "cast": [],
    }
    result = tmdb_client.get_single_movie_cast(movie_id=1)
    assert result == []  # assert the extracted cast is empty list
    mock_tmdb_session["session"].get.assert_called_once_with(
        "https://api.themoviedb.org/3/movie/1/credits", params=None
    )


def test_get_poster_url_uses_default_size():
    # Przygotowanie danych
    poster_api_path = "some-poster-path"
    expected_default_size = "w342"
    # Wywołanie kodu, który testujemy
    poster_url = tmdb_client.get_poster_url(poster_path=poster_api_path)
    # Porównanie wyników
    assert expected_default_size in poster_url


def test_search(mock_tmdb_session):
    mock_tmdb_session["response"].json.return_value = {
        "results": ["Movie 1", "Movie 2"]
    }
    result = tmdb_client.search(search_query="1")
    assert result == {"results": ["Movie 1", "Movie 2"]}
    mock_tmdb_session["session"].get.assert_called_once_with(
        "https://api.themoviedb.org/3/search/movie", params={"query": "1"}
    )


if __name__ == "__main__":
    print(__doc__)
