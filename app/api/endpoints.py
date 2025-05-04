from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from typing import Optional
import numpy as np
import cv2
import base64
import tempfile
from app.services.yolo_segmentation import segment_rooms
from jose import JWTError, jwt
from passlib.context import CryptContext
from repository.users import userRepository, JWTRepo
from models.users import ResponseSchema, TokenResponse, Login, Register
from sqlalchemy.orm import Session
from config import get_db, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from passlib.context import CryptContext

# Security configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

router = APIRouter()

from tables.users import User

router = APIRouter(
    tags=["Authentication"]
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

#register
@router.post("/signup")
async def signup(request: Register, db: Session = Depends(get_db)):
    try:
        # Hash the password before storing
        hashed_password = pwd_context.hash(request.password)
        
        # Create user data dictionary
        user_data = {
            "username": request.username,
            "email": request.email,
            "password": hashed_password,
            "first_name": request.first_name,
            "last_name": request.last_name,
        }
        
        # Use repository to create user
        _user = userRepository.create_user(db, User, user_data)
        
        return ResponseSchema(
            code="200",
            status="success",
            message="User created successfully",
            data=_user
        ).dict(exclude_none=True)
    except HTTPException as e:
        return ResponseSchema(
            code=str(e.status_code),
            status="error",
            message=e.detail,
            data=None
        ).dict(exclude_none=True)
    except Exception as error:
        print(f"Signup error: {str(error)}")
        return ResponseSchema(
            code="500",
            status="error",
            message="Internal server error",
            data=str(error)
        ).dict(exclude_none=True)
        
#login

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.post("/login", response_model=TokenResponse)
async def login(request: Login, db: Session = Depends(get_db)):
    try:
        print(f"Login attempt for username: {request.username}")
        
        # Get user by username
        _user = userRepository.get_user_by_username(db, User, request.username)
        if not _user:
            print(f"User not found: {request.username}")
            return TokenResponse(
                code="404",
                status="error",
                message="User not found",
                access_token="",
                token_type="bearer"
            )
        
        # Verify password
        if not pwd_context.verify(request.password, _user.password):
            print(f"Invalid password for user: {request.username}")
            return TokenResponse(
                code="401",
                status="error",
                message="Invalid credentials",
                access_token="",
                token_type="bearer"
            )
        
        # Generate token
        token = JWTRepo.generate_token(data={"sub": _user.username})
        print(f"Token generated for user: {request.username}")
        print(f"{token}")
        
        return TokenResponse(
            code="200",
            status="success",
            message="Login successful",
            access_token=token,
            token_type="bearer"
        )
    except Exception as error:
        print(f"Login error: {str(error)}")
        return TokenResponse(
            code="500",
            status="error",
            message="Internal server error",
            access_token="",
            token_type="bearer"
        )

@router.get("/verify-token")
async def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        print("Verifying token...")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            print("Token verification failed: No username in payload")
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        print(f"Token verified for user: {username}")
        return {"username": username, "valid": True}
    except JWTError as e:
        print(f"Token verification failed: {str(e)}")
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.post("/segment-rooms/")
def segment_rooms_api(file: UploadFile = File(...)):
    # Save uploaded file to a temporary location
    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
        tmp.write(file.file.read())
        tmp_path = tmp.name

    # Run segmentation
    overlay, room_polygons = segment_rooms(tmp_path)

    # Encode overlay image as base64
    _, buffer = cv2.imencode('.png', overlay)
    overlay_base64 = base64.b64encode(buffer).decode('utf-8')

    # Convert polygons to JSON-serializable format
    polygons_json = [contour.squeeze().tolist() for contour in room_polygons if contour.shape[0] > 2]

    return JSONResponse({
        "overlay_image_base64": overlay_base64,
        "room_polygons": polygons_json
    })
