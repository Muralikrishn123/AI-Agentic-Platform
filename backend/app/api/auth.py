from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
import bcrypt

from app.database.models import UserModel
from config.settings import settings

router = APIRouter()
security = HTTPBearer()


# ---------------------------------------------------------------------------
# Password helpers — use bcrypt directly to avoid passlib Python 3.14 issues
# ---------------------------------------------------------------------------

def _encode_password(password: str) -> bytes:
    """Encode password to bytes, truncated to 72 bytes (bcrypt limit)."""
    return password.encode("utf-8")[:72]


def hash_password(password: str) -> str:
    """Hash a password with bcrypt."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(_encode_password(password), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a bcrypt hash."""
    try:
        return bcrypt.checkpw(
            _encode_password(plain_password),
            hashed_password.encode("utf-8")
        )
    except Exception:
        return False


# ---------------------------------------------------------------------------
# JWT helpers
# ---------------------------------------------------------------------------

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Dependency to get current authenticated user."""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid authentication token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication token")

    user = await UserModel.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    return user


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------

class SignupRequest(BaseModel):
    name: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.post("/signup", response_model=TokenResponse)
async def signup(request: SignupRequest):
    """Register a new user."""

    # Check if user exists
    existing_user = await UserModel.get_user_by_email(request.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash password with bcrypt directly
    hashed_password = hash_password(request.password)

    # Create user
    user_data = {
        "name": request.name,
        "email": request.email,
        "password": hashed_password,
        "role": "user"
    }

    user = await UserModel.create_user(user_data)

    # Create access token
    access_token = create_access_token(data={"sub": user["_id"]})

    # Remove password from response
    user.pop("password", None)

    return TokenResponse(
        access_token=access_token,
        user=user
    )


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """Login user."""

    # Get user
    user = await UserModel.get_user_by_email(request.email)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Verify password using bcrypt directly
    if not verify_password(request.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Create access token
    access_token = create_access_token(data={"sub": user["_id"]})

    # Remove password from response
    user.pop("password", None)

    return TokenResponse(
        access_token=access_token,
        user=user
    )


@router.get("/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    """Get current user info."""
    current_user.pop("password", None)
    return current_user
