from unittest.mock import Mock

import pytest

@pytest.fixture
def mock_tmdb_session(monkeypatch):
    """Creates a mock session and patches get_session"""
    mock_response = Mock()
    mock_response.raise_for_status = Mock()

    mock_session = Mock()
    mock_session.get.return_value = mock_response

    monkeypatch.setattr(
        "tmdb_client.get_session", lambda: mock_session
    )  # substitute with anonymous function returning `mock_session`

    # Return both so tests can configure response and verify calls
    return {"session": mock_session, "response": mock_response}

