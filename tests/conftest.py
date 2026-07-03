import pytest

import store
from app import app


@pytest.fixture
def client():
    store.reset_store(seed=True)
    app.config["TESTING"] = True
    with app.test_client() as test_client:
        yield test_client
