import pytest
from datetime import datetime, timezone, timedelta
from fastapi import HTTPException
from jose import jwt
from app.utils.auth import authenticate_admin, create_access_token, verify_admin, SECRET_KEY, ALGORITHM, ISSUER, AUDIENCE, ACCESS_TOKEN_EXPIRE_MINUTES, ADMIN_USERNAME

def test_authenticate_admin_valid_credentials(mocker):
    # Arrange
    mock_verify = mocker.patch("app.utils.auth.pwd_context.verify", return_value=True)

    # Act
    result = authenticate_admin("test_admin", "correct_password")

    # Assert
    assert result is True
    mock_verify.assert_called_once_with("correct_password", mocker.ANY)

def test_authenticate_admin_wrong_username(mocker):
    # Act
    result = authenticate_admin("wrong_user", "correct_password")

    # Assert
    assert result is False

def test_authenticate_admin_wrong_password(mocker):
    # Arrange
    mock_verify = mocker.patch("app.utils.auth.pwd_context.verify", return_value=False)

    # Act
    result = authenticate_admin("test_admin", "wrong_password")

    # Assert
    assert result is False
    mock_verify.assert_called_once_with("wrong_password", mocker.ANY)

def test_authenticate_admin_empty_credentials():
    assert authenticate_admin("", "password") is False
    assert authenticate_admin("username", "") is False

def test_create_access_token():
    # Arrange
    username = "test_admin"
    before_creation = datetime.now(timezone.utc) - timedelta(seconds=1)

    # Act
    token = create_access_token(username)
    after_creation = datetime.now(timezone.utc) + timedelta(seconds=1)

    # Assert
    assert token is not None
    assert isinstance(token, str)

    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], issuer=ISSUER, audience=AUDIENCE)

    assert payload["sub"] == username
    assert payload["iss"] == ISSUER
    assert payload["aud"] == AUDIENCE
    assert "jti" in payload
    assert "exp" in payload
    assert "iat" in payload
    assert "nbf" in payload

    iat = datetime.fromtimestamp(payload["iat"], tz=timezone.utc)
    assert iat >= before_creation
    assert iat <= after_creation

def test_create_access_token_expiration():
    # Arrange
    username = "test_admin"

    # Act
    token = create_access_token(username)

    # Assert
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], issuer=ISSUER, audience=AUDIENCE)

    iat = datetime.fromtimestamp(payload["iat"], tz=timezone.utc)
    exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)

    expected_exp = iat + timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
    assert abs((exp - expected_exp).total_seconds()) < 1

@pytest.mark.asyncio
async def test_verify_admin_valid_token():
    """Test verify_admin with a valid token"""
    # Arrange
    token = create_access_token(ADMIN_USERNAME)

    # Act
    result = await verify_admin(token)

    # Assert
    assert result == ADMIN_USERNAME

@pytest.mark.asyncio
async def test_verify_admin_invalid_signature():
    """Test that tampered tokens are rejected"""
    # Arrange
    token = create_access_token(ADMIN_USERNAME)
    tampered_token = token[:-5] + "AAAAA"

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await verify_admin(tampered_token)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid authentication"

@pytest.mark.asyncio
async def test_verify_admin_expired_token():
    """Test that expired tokens are rejected"""
    # Arrange
    now = datetime.now(timezone.utc)
    expired_time = now - timedelta(hours=1)

    data = {
        "sub": ADMIN_USERNAME,
        "exp": expired_time,
        "iat": expired_time - timedelta(minutes=30),
        "nbf": expired_time - timedelta(minutes=30),
        "iss": ISSUER,
        "aud": AUDIENCE,
        "jti": "test-jti"
    }
    expired_token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await verify_admin(expired_token)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid authentication"

@pytest.mark.asyncio
async def test_verify_admin_wrong_issuer():
    """Test that tokens with wrong issuer are rejected"""
    # Arrange
    now = datetime.now(timezone.utc)

    data = {
        "sub": ADMIN_USERNAME,
        "exp": now + timedelta(minutes=30),
        "iat": now,
        "nbf": now,
        "iss": "wrong-issuer",
        "aud": AUDIENCE,
        "jti": "test-jti"
    }
    token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await verify_admin(token)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid authentication"

@pytest.mark.asyncio
async def test_verify_admin_wrong_audience():
    """Test that tokens with wrong audience are rejected"""
    # Arrange
    now = datetime.now(timezone.utc)

    data = {
        "sub": ADMIN_USERNAME,
        "exp": now + timedelta(minutes=30),
        "iat": now,
        "nbf": now,
        "iss": ISSUER,
        "aud": "wrong-audience",
        "jti": "test-jti"
    }
    token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await verify_admin(token)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid authentication"

@pytest.mark.asyncio
async def test_verify_admin_malformed_token():
    """Test that malformed tokens are rejected"""
    # Arrange
    malformed_token = "this.is.not.a.valid.jwt"

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await verify_admin(malformed_token)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid authentication"

@pytest.mark.asyncio
async def test_verify_admin_wrong_username():
    """Test that tokens with wrong username are rejected"""
    # Arrange
    now = datetime.now(timezone.utc)

    data = {
        "sub": "wrong_user",
        "exp": now + timedelta(minutes=30),
        "iat": now,
        "nbf": now,
        "iss": ISSUER,
        "aud": AUDIENCE,
        "jti": "test-jti"
    }
    token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await verify_admin(token)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid authentication"
