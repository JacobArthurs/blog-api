import pytest
from fastapi import HTTPException
from app.utils.slugify import slugify, validate_unique_slug

def test_slugify_basic():
    assert slugify("Hello World") == "hello-world"

def test_slugify_lowercase():
    assert slugify("UPPERCASE TEXT") == "uppercase-text"
    assert slugify("MiXeD CaSe") == "mixed-case"

def test_slugify_special_characters():
    assert slugify("Hello! World?") == "hello-world"
    assert slugify("test@example#.com") == "testexamplecom"
    assert slugify("price: $99.99") == "price-9999"

def test_slugify_multiple_spaces():
    assert slugify("multiple   spaces") == "multiple-spaces"
    assert slugify("too     many     spaces") == "too-many-spaces"

def test_slugify_underscores():
    assert slugify("hello_world") == "hello-world"
    assert slugify("test_under_score") == "test-under-score"

def test_slugify_consecutive_hyphens():
    assert slugify("hello---world") == "hello-world"
    assert slugify("test--slug") == "test-slug"

def test_slugify_leading_trailing_hyphens():
    assert slugify("-hello-world-") == "hello-world"
    assert slugify("---test---") == "test"

def test_slugify_mixed_special_and_spaces():
    assert slugify("The Quick! Brown@ Fox#") == "the-quick-brown-fox"
    assert slugify("C++ Programming 101") == "c-programming-101"

def test_slugify_numbers():
    assert slugify("Python 3.11") == "python-311"
    assert slugify("2024 Goals") == "2024-goals"

def test_slugify_empty_string():
    assert slugify("") == ""

def test_slugify_only_special_characters():
    assert slugify("!!!@@@###") == ""
    assert slugify("---") == ""

def test_slugify_already_valid_slug():
    assert slugify("already-valid-slug") == "already-valid-slug"
    assert slugify("test-123") == "test-123"

def test_validate_unique_slug_success(mocker):
    # Arrange
    mock_db = mocker.MagicMock()
    mock_model = mocker.MagicMock()
    mock_model.__name__ = "Post"
    mock_db.query.return_value.filter.return_value.first.return_value = None

    # Act & Assert
    validate_unique_slug("unique-slug", mock_model, mock_db)

def test_validate_unique_slug_duplicate(mocker):
    # Arrange
    mock_db = mocker.MagicMock()
    mock_model = mocker.MagicMock()
    mock_model.__name__ = "Post"
    mock_existing = mocker.MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = mock_existing

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        validate_unique_slug("duplicate-slug", mock_model, mock_db)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Post with this slug already exists"

def test_validate_unique_slug_different_models(mocker):
    # Arrange
    mock_db = mocker.MagicMock()
    mock_tag_model = mocker.MagicMock()
    mock_tag_model.__name__ = "Tag"
    mock_existing = mocker.MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = mock_existing

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        validate_unique_slug("duplicate", mock_tag_model, mock_db)

    assert exc_info.value.detail == "Tag with this slug already exists"

def test_validate_unique_slug_query_called_correctly(mocker):
    # Arrange
    mock_db = mocker.MagicMock()
    mock_model = mocker.MagicMock()
    mock_model.__name__ = "Post"
    mock_db.query.return_value.filter.return_value.first.return_value = None

    # Act
    validate_unique_slug("test-slug", mock_model, mock_db)

    # Assert
    mock_db.query.assert_called_once_with(mock_model)
    mock_db.query.return_value.filter.return_value.first.assert_called_once()
