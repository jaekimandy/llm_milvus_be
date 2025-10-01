from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from encryption.crypto import encryption_service
from auth.security import get_current_active_user
from auth.models import User
from io import BytesIO

router = APIRouter(prefix="/encryption", tags=["Encryption"])


class EncryptRequest(BaseModel):
    plaintext: str


class EncryptResponse(BaseModel):
    ciphertext: str


class DecryptRequest(BaseModel):
    ciphertext: str


class DecryptResponse(BaseModel):
    plaintext: str


@router.post("/encrypt", response_model=EncryptResponse)
async def encrypt_data(
    request: EncryptRequest,
    current_user: User = Depends(get_current_active_user)
):
    """Encrypt plaintext data"""
    try:
        ciphertext = encryption_service.encrypt_string(request.plaintext)
        return {"ciphertext": ciphertext}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Encryption failed: {str(e)}")


@router.post("/decrypt", response_model=DecryptResponse)
async def decrypt_data(
    request: DecryptRequest,
    current_user: User = Depends(get_current_active_user)
):
    """Decrypt encrypted data"""
    try:
        plaintext = encryption_service.decrypt_string(request.ciphertext)
        return {"plaintext": plaintext}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Decryption failed: {str(e)}")


@router.post("/encrypt-file")
async def encrypt_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user)
):
    """Encrypt a file"""
    try:
        file_data = await file.read()
        encrypted_data = encryption_service.encrypt_file(file_data)

        return StreamingResponse(
            BytesIO(encrypted_data),
            media_type="application/octet-stream",
            headers={
                "Content-Disposition": f"attachment; filename=encrypted_{file.filename}"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File encryption failed: {str(e)}")


@router.post("/decrypt-file")
async def decrypt_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user)
):
    """Decrypt a file"""
    try:
        encrypted_data = await file.read()
        decrypted_data = encryption_service.decrypt_file(encrypted_data)

        # Remove 'encrypted_' prefix from filename if present
        original_filename = file.filename.replace("encrypted_", "")

        return StreamingResponse(
            BytesIO(decrypted_data),
            media_type="application/octet-stream",
            headers={
                "Content-Disposition": f"attachment; filename={original_filename}"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File decryption failed: {str(e)}")
