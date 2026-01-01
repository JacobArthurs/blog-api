import os
import pytest

# Set all required environment variables for testing
os.environ["DATABASE_URL"] = "postgresql://user:test@localhost/test_db"
os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only"
os.environ["ALGORITHM"] = "HS256"
os.environ["ADMIN_USERNAME"] = "test_admin"
os.environ["ADMIN_PASSWORD_HASH"] = "$2b$12$test_hash"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"
os.environ["ISSUER"] = "test-issuer"
os.environ["AUDIENCE"] = "test-audience"

from app.utils.auth import verify_admin
from app.db.database import get_db
from app.main import app

@pytest.fixture(autouse=True)
def mock_db(mocker):
    """Automatically mock the database for all tests"""
    mock_db_session = mocker.MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db_session
    
    yield mock_db_session
    
    app.dependency_overrides.clear()

@pytest.fixture(autouse=True)
def mock_utils(mocker):
    """Automatically mock utils for all tests"""
    mocker.patch("app.routers.posts.slugify", return_value="auto-slug")
    mocker.patch("app.routers.posts.validate_unique_slug", return_value=None)
    mocker.patch("app.routers.tags.slugify", return_value="auto-slug")
    mocker.patch("app.routers.tags.validate_unique_slug", return_value=None)
    yield

@pytest.fixture()
def mock_auth():
    """Selectively bypass authentication for all tests"""
    app.dependency_overrides[verify_admin] = lambda: None
    yield