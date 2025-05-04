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
from config import get_db
from passlib.context import CryptContext

# Security configuration
SECRET_KEY = "your-secret-key-here"  # In production, use a secure secret key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

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
        #insert data
        _user = User(
            username = request.username,
            email = request.email,
            password = request.password,
            first_name = request.first_name,
            last_name = request.last_name,)
        userRepository.insert(db, _user)
        return ResponseSchema(code="200", status="success", message="User created successfully", data=_user)
    except Exception as error:
        print(error.args)
        return ResponseSchema(code="500", status="error", message="Internal server error", data=error.args).model_dump(exclude_none=True)
        
#login

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.post("/login", response_model=TokenResponse)
async def login(request: Login, db: Session = Depends(get_db)):
    try:
        #get user by username
        _user = userRepository.get_user_by_username(db, User, request.username)
        if not _user:
            return TokenResponse(
                code="404",
                status="error",
                message="User not found",
                access_token="",
                token_type="bearer"
            )
        
        #verify password
        if not pwd_context.verify(request.password, _user.password):
            return TokenResponse(
                code="401",
                status="error",
                message="Invalid credentials",
                access_token="",
                token_type="bearer"
            )
        
        #generate token
        token = JWTRepo.generate_token(data={"sub": _user.username})
        
        return TokenResponse(
            code="200",
            status="success",
            message="Login successful",
            access_token=token,
            token_type="bearer"
        )
    except Exception as error:
        print(error.args)
        return TokenResponse(
            code="500",
            status="error",
            message="Internal server error",
            access_token="",
            token_type="bearer"
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
