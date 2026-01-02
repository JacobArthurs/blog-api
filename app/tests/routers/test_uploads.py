from unittest.mock import mock_open, MagicMock
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_upload_photo_success(mocker, mock_auth):
    # Arrange
    mock_file_content = b"fake image content"
    mock_uuid = "test-uuid-1234"
    mocker.patch("app.routers.uploads.uuid.uuid4", return_value=MagicMock(__str__=lambda x: mock_uuid))
    mock_open_file = mocker.patch("builtins.open", mock_open())

    # Act
    response = client.post(
        "/uploads/photos",
        files={"file": ("test.jpg", mock_file_content, "image/jpeg")}
    )
    data = response.json()

    # Assert
    assert response.status_code == 201
    assert data["fileName"] == f"{mock_uuid}.jpg"
    assert data["url"] == f"/uploads/photos/{mock_uuid}.jpg"
    mock_open_file.assert_called_once()

def test_upload_photo_webp(mocker, mock_auth):
    # Arrange
    mock_file_content = b"fake webp content"
    mock_uuid = "test-uuid-5678"
    mocker.patch("app.routers.uploads.uuid.uuid4", return_value=MagicMock(__str__=lambda x: mock_uuid))
    mocker.patch("builtins.open", mock_open())

    # Act
    response = client.post(
        "/uploads/photos",
        files={"file": ("test.webp", mock_file_content, "image/webp")}
    )
    data = response.json()

    # Assert
    assert response.status_code == 201
    assert data["fileName"] == f"{mock_uuid}.webp"

def test_upload_photo_invalid_extension(mock_auth):
    # Arrange
    mock_file_content = b"fake pdf content"

    # Act
    response = client.post(
        "/uploads/photos",
        files={"file": ("document.pdf", mock_file_content, "application/pdf")}
    )

    # Assert
    assert response.status_code == 400
    assert "File type not allowed" in response.json()["detail"]

def test_upload_photo_file_too_large(mock_auth):
    # Arrange
    # Create content larger than 10MB
    large_content = b"x" * (11 * 1024 * 1024)

    # Act
    response = client.post(
        "/uploads/photos",
        files={"file": ("large.jpg", large_content, "image/jpeg")}
    )

    # Assert
    assert response.status_code == 400
    assert "File too large" in response.json()["detail"]

def test_upload_photo_unauthorized(mock_db):
    # Act
    response = client.post(
        "/uploads/photos",
        files={"file": ("test.jpg", b"content", "image/jpeg")}
    )

    # Assert
    assert response.status_code == 401

def test_upload_photo_png(mocker, mock_auth):
    # Arrange
    mock_file_content = b"fake png content"
    mock_uuid = "test-uuid-png"
    mocker.patch("app.routers.uploads.uuid.uuid4", return_value=MagicMock(__str__=lambda x: mock_uuid))
    mocker.patch("builtins.open", mock_open())

    # Act
    response = client.post(
        "/uploads/photos",
        files={"file": ("test.png", mock_file_content, "image/png")}
    )
    data = response.json()

    # Assert
    assert response.status_code == 201
    assert data["fileName"] == f"{mock_uuid}.png"

def test_upload_photo_gif(mocker, mock_auth):
    # Arrange
    mock_file_content = b"fake gif content"
    mock_uuid = "test-uuid-gif"
    mocker.patch("app.routers.uploads.uuid.uuid4", return_value=MagicMock(__str__=lambda x: mock_uuid))
    mocker.patch("builtins.open", mock_open())

    # Act
    response = client.post(
        "/uploads/photos",
        files={"file": ("test.gif", mock_file_content, "image/gif")}
    )
    data = response.json()

    # Assert
    assert response.status_code == 201
    assert data["fileName"] == f"{mock_uuid}.gif"

def test_upload_photo_case_insensitive_extension(mocker, mock_auth):
    # Arrange
    mock_file_content = b"fake image content"
    mock_uuid = "test-uuid-upper"
    mocker.patch("app.routers.uploads.uuid.uuid4", return_value=MagicMock(__str__=lambda x: mock_uuid))
    mocker.patch("builtins.open", mock_open())

    # Act - uppercase extension
    response = client.post(
        "/uploads/photos",
        files={"file": ("test.JPG", mock_file_content, "image/jpeg")}
    )
    data = response.json()

    # Assert - should be normalized to lowercase
    assert response.status_code == 201
    assert data["fileName"] == f"{mock_uuid}.jpg"


# Test DELETE /uploads/photos/{filename}

def test_delete_photo_success(mocker, mock_auth):
    # Arrange
    filename = "test-uuid-1234.jpg"
    mock_path = mocker.MagicMock()
    mock_path.exists.return_value = True
    mock_path.is_file.return_value = True
    mock_path.resolve.return_value = mock_path
    mock_path.__str__ = lambda x: f"/app/uploads/photos/{filename}"

    mock_upload_dir = mocker.MagicMock()
    mock_upload_dir.resolve.return_value = mocker.MagicMock(__str__=lambda x: "/app/uploads/photos")
    mock_upload_dir.__truediv__ = lambda x, y: mock_path

    mocker.patch("app.routers.uploads.UPLOAD_DIR", mock_upload_dir)

    # Act
    response = client.delete(f"/uploads/photos/{filename}")

    # Assert
    assert response.status_code == 204
    mock_path.unlink.assert_called_once()

def test_delete_photo_not_found(mocker, mock_auth):
    # Arrange
    filename = "nonexistent.jpg"
    mock_path = mocker.MagicMock()
    mock_path.exists.return_value = False
    mock_path.resolve.return_value = mock_path
    mock_path.__str__ = lambda x: f"/app/uploads/photos/{filename}"

    mock_upload_dir = mocker.MagicMock()
    mock_upload_dir.resolve.return_value = mocker.MagicMock(__str__=lambda x: "/app/uploads/photos")
    mock_upload_dir.__truediv__ = lambda x, y: mock_path

    mocker.patch("app.routers.uploads.UPLOAD_DIR", mock_upload_dir)

    # Act
    response = client.delete(f"/uploads/photos/{filename}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Photo not found"

def test_delete_photo_is_directory(mocker, mock_auth):
    # Arrange
    filename = "somedir"
    mock_path = mocker.MagicMock()
    mock_path.exists.return_value = True
    mock_path.is_file.return_value = False  # It's a directory
    mock_path.resolve.return_value = mock_path
    mock_path.__str__ = lambda x: f"/app/uploads/photos/{filename}"

    mock_upload_dir = mocker.MagicMock()
    mock_upload_dir.resolve.return_value = mocker.MagicMock(__str__=lambda x: "/app/uploads/photos")
    mock_upload_dir.__truediv__ = lambda x, y: mock_path

    mocker.patch("app.routers.uploads.UPLOAD_DIR", mock_upload_dir)

    # Act
    response = client.delete(f"/uploads/photos/{filename}")

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid file"

def test_delete_photo_unauthorized(mock_db):
    # Act
    response = client.delete("/uploads/photos/test.jpg")

    # Assert
    assert response.status_code == 401

def test_delete_photo_os_error(mocker, mock_auth):
    # Arrange
    filename = "test-uuid-1234.jpg"
    mock_path = mocker.MagicMock()
    mock_path.exists.return_value = True
    mock_path.is_file.return_value = True
    mock_path.resolve.return_value = mock_path
    mock_path.__str__ = lambda x: f"/app/uploads/photos/{filename}"
    mock_path.unlink.side_effect = OSError("Permission denied")

    mock_upload_dir = mocker.MagicMock()
    mock_upload_dir.resolve.return_value = mocker.MagicMock(__str__=lambda x: "/app/uploads/photos")
    mock_upload_dir.__truediv__ = lambda x, y: mock_path

    mocker.patch("app.routers.uploads.UPLOAD_DIR", mock_upload_dir)

    # Act
    response = client.delete(f"/uploads/photos/{filename}")

    # Assert
    assert response.status_code == 500
    assert "Failed to delete file" in response.json()["detail"]
