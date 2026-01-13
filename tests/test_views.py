from unittest.mock import Mock

from main import app
from tests.fixtures import mock_tmdb_session

import pytest

@pytest.mark.parametrize('list_type', ['popular','top_rated'])
def test_homepage(mock_tmdb_session, list_type):
    mock_tmdb_session["response"].json.return_value = {"results": []}

    with app.test_client() as client:
        response = client.get(f"/?list_type={list_type}")
        assert response.status_code == 200
        mock_tmdb_session["session"].get.assert_called_once_with(
            f"https://api.themoviedb.org/3/movie/{list_type}?page=1", params=None
        )

