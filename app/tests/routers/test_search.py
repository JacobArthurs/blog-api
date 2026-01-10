from fastapi.testclient import TestClient
from app.main import app
from app.tests.utils import create_mock_post, create_mock_tag

client = TestClient(app)

def test_autocomplete_search_posts_and_tags(mock_db):
    # Arrange
    from unittest.mock import MagicMock
    
    mock_post1 = create_mock_post(1, "Python Tutorial", "python-tutorial", "Learn Python programming")
    mock_post2 = create_mock_post(2, "Advanced Python", "advanced-python", "Deep dive into Python")
    mock_tag1 = create_mock_tag(1, "Python", "python")

    posts_query = MagicMock()
    posts_query.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [mock_post1, mock_post2]
    posts_query.filter.return_value.order_by.return_value.count.return_value = 2
    
    tags_query = MagicMock()
    tags_query.filter.return_value.order_by.return_value.limit.return_value.all.return_value = [mock_tag1]
    
    query_counter = [0]
    def query_side_effect(*args, **kwargs):
        query_counter[0] += 1
        return posts_query if query_counter[0] == 1 else tags_query
    
    mock_db.query.side_effect = query_side_effect

    # Act
    response = client.get("/search/autocomplete?q=python")
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert "posts" in data
    assert "tags" in data
    assert len(data["posts"]["items"]) == 2
    assert len(data["tags"]) == 1

def test_autocomplete_search_no_results(mock_db):
    # Arrange
    from unittest.mock import MagicMock
    
    posts_mock = MagicMock()
    posts_mock.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = []
    posts_mock.filter.return_value.order_by.return_value.count.return_value = 0
    
    tags_mock = MagicMock()
    tags_mock.filter.return_value.order_by.return_value.limit.return_value.all.return_value = []
    
    mock_db.query.side_effect = [posts_mock, tags_mock]

    # Act
    response = client.get("/search/autocomplete?q=nonexistent")
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert data["posts"]["items"] == []
    assert data["tags"] == []

def test_autocomplete_search_posts_only(mock_db):
    # Arrange
    from unittest.mock import MagicMock
    
    mock_post = create_mock_post(1, "JavaScript Basics", "javascript-basics", "Learn JS")

    posts_query = MagicMock()
    posts_query.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [mock_post]
    posts_query.filter.return_value.order_by.return_value.count.return_value = 1
    
    tags_query = MagicMock()
    tags_query.filter.return_value.order_by.return_value.limit.return_value.all.return_value = []
    
    query_counter = [0]
    def query_side_effect(*args, **kwargs):
        query_counter[0] += 1
        return posts_query if query_counter[0] == 1 else tags_query
    
    mock_db.query.side_effect = query_side_effect

    # Act
    response = client.get("/search/autocomplete?q=javascript")
    data = response.json()

    # Assert
    assert response.status_code == 200
    print(data)
    assert len(data["posts"]["items"]) == 1
    assert len(data["tags"]) == 0
    assert data["posts"]["items"][0]["title"] == "JavaScript Basics"

def test_autocomplete_search_tags_only(mock_db):
    # Arrange
    mock_tag = create_mock_tag(1, "React", "react")

    from unittest.mock import MagicMock
    
    posts_mock = MagicMock()
    posts_mock.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = []
    posts_mock.filter.return_value.order_by.return_value.count.return_value = 0
    
    tags_mock = MagicMock()
    tags_mock.filter.return_value.order_by.return_value.limit.return_value.all.return_value = [mock_tag]
    
    mock_db.query.side_effect = [posts_mock, tags_mock]

    # Act
    response = client.get("/search/autocomplete?q=react")
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert len(data["posts"]["items"]) == 0
    assert len(data["tags"]) == 1
    assert data["tags"][0]["name"] == "React"

def test_autocomplete_search_missing_query(mock_db):
    # Act
    response = client.get("/search/autocomplete")

    # Assert
    assert response.status_code == 422


def test_autocomplete_search_empty_query(mock_db):
    # Act
    response = client.get("/search/autocomplete?q=")

    # Assert
    assert response.status_code == 422

def test_autocomplete_search_limit_enforced(mock_db):
    # Arrange
    from unittest.mock import MagicMock
    
    mock_posts = [create_mock_post(i, f"Post {i}", f"post-{i}", f"Content {i}") for i in range(1, 16)]
    mock_tags = [create_mock_tag(i, f"Tag {i}", f"tag-{i}") for i in range(1, 16)]

    posts_query = MagicMock()
    posts_query.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = mock_posts[:10]
    posts_query.filter.return_value.order_by.return_value.count.return_value = 15
    
    tags_query = MagicMock()
    tags_query.filter.return_value.order_by.return_value.limit.return_value.all.return_value = mock_tags[:5]
    
    query_counter = [0]
    def query_side_effect(*args, **kwargs):
        query_counter[0] += 1
        return posts_query if query_counter[0] == 1 else tags_query
    
    mock_db.query.side_effect = query_side_effect

    # Act
    response = client.get("/search/autocomplete?q=test")
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert len(data["posts"]["items"]) == 10
    assert len(data["tags"]) == 5
