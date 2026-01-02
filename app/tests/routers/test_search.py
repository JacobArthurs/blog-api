from fastapi.testclient import TestClient
from app.main import app
from app.tests.utils import create_mock_post, create_mock_tag

client = TestClient(app)

def test_autocomplete_search_posts_and_tags(mock_db):
    # Arrange
    mock_post1 = create_mock_post(1, "Python Tutorial", "python-tutorial", "Learn Python programming")
    mock_post2 = create_mock_post(2, "Advanced Python", "advanced-python", "Deep dive into Python")
    mock_tag1 = create_mock_tag(1, "Python", "python")
    mock_tag2 = create_mock_tag(2, "Programming", "programming")

    mock_db.query.return_value.filter.return_value.limit.return_value.all.side_effect = [
        [mock_post1, mock_post2],
        [mock_tag1, mock_tag2]
    ]

    # Act
    response = client.get("/search/autocomplete?q=python")
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert "posts" in data
    assert "tags" in data
    assert len(data["posts"]) == 2
    assert len(data["tags"]) == 2
    assert data["posts"][0]["title"] == "Python Tutorial"
    assert data["posts"][1]["title"] == "Advanced Python"
    assert data["tags"][0]["name"] == "Python"

def test_autocomplete_search_no_results(mock_db):
    # Arrange
    mock_db.query.return_value.filter.return_value.limit.return_value.all.side_effect = [
        [],
        []
    ]

    # Act
    response = client.get("/search/autocomplete?q=nonexistent")
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert data["posts"] == []
    assert data["tags"] == []

def test_autocomplete_search_posts_only(mock_db):
    # Arrange
    mock_post = create_mock_post(1, "JavaScript Basics", "javascript-basics", "Learn JS")

    mock_db.query.return_value.filter.return_value.limit.return_value.all.side_effect = [
        [mock_post],
        []
    ]

    # Act
    response = client.get("/search/autocomplete?q=javascript")
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert len(data["posts"]) == 1
    assert len(data["tags"]) == 0
    assert data["posts"][0]["title"] == "JavaScript Basics"

def test_autocomplete_search_tags_only(mock_db):
    # Arrange
    mock_tag = create_mock_tag(1, "React", "react")

    mock_db.query.return_value.filter.return_value.limit.return_value.all.side_effect = [
        [],
        [mock_tag]
    ]

    # Act
    response = client.get("/search/autocomplete?q=react")
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert len(data["posts"]) == 0
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
    mock_posts = [create_mock_post(i, f"Post {i}", f"post-{i}", f"Content {i}") for i in range(1, 16)]
    mock_tags = [create_mock_tag(i, f"Tag {i}", f"tag-{i}") for i in range(1, 16)]

    mock_db.query.return_value.filter.return_value.limit.return_value.all.side_effect = [
        mock_posts[:10], 
        mock_tags[:5]
    ]

    # Act
    response = client.get("/search/autocomplete?q=test")
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert len(data["posts"]) == 10
    assert len(data["tags"]) == 5
