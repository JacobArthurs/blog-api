import uuid
from pathlib import Path
from fastapi import APIRouter, Depends, UploadFile, HTTPException, status

from ..schemas import UploadResponse
from app.utils.auth import verify_admin

router = APIRouter(
    prefix="/uploads",
    tags=["uploads"]
)

UPLOAD_DIR = Path("/app/uploads/photos")
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

@router.post("/photos", response_model=UploadResponse, status_code=201)
async def upload_photo(file: UploadFile, _ = Depends(verify_admin)):
    """Upload a single photo"""

    # Validate file type
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # Validate file size
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE / (1024 * 1024)}MB"
        )

    # Save file with unique name
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = UPLOAD_DIR / unique_filename

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    with open(file_path, "wb") as f:
        f.write(content)

    return UploadResponse(
        fileName=unique_filename,
        url=f"/uploads/photos/{unique_filename}"
    )


@router.delete("/photos/{filename}", status_code=204)
async def delete_photo(filename: str, _ = Depends(verify_admin)):
    """Delete a photo by filename"""

    file_path = UPLOAD_DIR / filename

    # Path traversal protection
    try:
        file_path = file_path.resolve()
        if not str(file_path).startswith(str(UPLOAD_DIR.resolve())):
            raise HTTPException(
                status_code=400,
                detail="Invalid filename"
            )
    except (ValueError, OSError):
        raise HTTPException(
            status_code=400,
            detail="Invalid filename"
        )

    # Existence checks
    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Photo not found"
        )

    if not file_path.is_file():
        raise HTTPException(
            status_code=400,
            detail="Invalid file"
        )

    # Delete file
    try:
        file_path.unlink()
    except OSError as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete file: {str(e)}")

    return None