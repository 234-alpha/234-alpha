from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timedelta
import hashlib
import jwt
from passlib.context import CryptContext


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()
SECRET_KEY = "your-secret-key-change-in-production"  # Change this in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI(title="CreatorHub API", description="Creator Economy Platform API")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Authentication Models
class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: str
    user_type: str = Field(..., description="creator or buyer")

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(UserBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True
    profile_completed: bool = False

class Token(BaseModel):
    access_token: str
    token_type: str

# Creator Profile Models
class CreatorProfile(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    bio: str
    skills: List[str] = []
    experience_level: str = Field(..., description="beginner, intermediate, expert")
    portfolio_items: List[str] = []  # URLs or file paths
    rating: float = 0.0
    total_reviews: int = 0
    total_earnings: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class CreatorProfileCreate(BaseModel):
    bio: str
    skills: List[str]
    experience_level: str

class CreatorProfileUpdate(BaseModel):
    bio: Optional[str] = None
    skills: Optional[List[str]] = None
    experience_level: Optional[str] = None
    portfolio_items: Optional[List[str]] = None

# Service Listing Models
class ServiceListing(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    creator_id: str
    title: str
    description: str
    category: str
    tags: List[str] = []
    base_price: float
    delivery_time_days: int
    revisions_included: int
    images: List[str] = []  # Base64 encoded images
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ServiceListingCreate(BaseModel):
    title: str
    description: str
    category: str
    tags: List[str] = []
    base_price: float
    delivery_time_days: int
    revisions_included: int = 1
    images: List[str] = []

class ServiceListingUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    base_price: Optional[float] = None
    delivery_time_days: Optional[int] = None
    revisions_included: Optional[int] = None
    images: Optional[List[str]] = None
    is_active: Optional[bool] = None

# Order Models
class Order(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    service_id: str
    buyer_id: str
    creator_id: str
    status: str = Field(default="pending", description="pending, in_progress, completed, cancelled")
    price: float
    requirements: str
    delivery_date: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class OrderCreate(BaseModel):
    service_id: str
    requirements: str

# Utility functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    
    user = await db.users.find_one({"email": email})
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return User(**user)

# Authentication Routes
@api_router.post("/auth/register", response_model=Token)
async def register(user_data: UserCreate):
    # Check if user already exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    existing_username = await db.users.find_one({"username": user_data.username})
    if existing_username:
        raise HTTPException(status_code=400, detail="Username already taken")
    
    # Create new user
    user_dict = user_data.dict()
    user_dict["password"] = get_password_hash(user_data.password)
    user_obj = User(**user_dict)
    
    await db.users.insert_one(user_obj.dict())
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_obj.email}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@api_router.post("/auth/login", response_model=Token)
async def login(user_credentials: UserLogin):
    user = await db.users.find_one({"email": user_credentials.email})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Convert MongoDB document to dict if it's not already
    if not isinstance(user, dict):
        user = dict(user)
        
    if not verify_password(user_credentials.password, user.get("password", "")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"]}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@api_router.get("/auth/me", response_model=User)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user

# Creator Profile Routes
@api_router.post("/creators/profile", response_model=CreatorProfile)
async def create_creator_profile(
    profile_data: CreatorProfileCreate,
    current_user: User = Depends(get_current_user)
):
    if current_user.user_type != "creator":
        raise HTTPException(status_code=403, detail="Only creators can create profiles")
    
    # Check if profile already exists
    existing_profile = await db.creator_profiles.find_one({"user_id": current_user.id})
    if existing_profile:
        raise HTTPException(status_code=400, detail="Creator profile already exists")
    
    profile_dict = profile_data.dict()
    profile_dict["user_id"] = current_user.id
    profile_obj = CreatorProfile(**profile_dict)
    
    await db.creator_profiles.insert_one(profile_obj.dict())
    
    # Update user profile_completed status
    await db.users.update_one(
        {"id": current_user.id},
        {"$set": {"profile_completed": True}}
    )
    
    return profile_obj

@api_router.get("/creators/profile", response_model=CreatorProfile)
async def get_creator_profile(current_user: User = Depends(get_current_user)):
    profile = await db.creator_profiles.find_one({"user_id": current_user.id})
    if not profile:
        raise HTTPException(status_code=404, detail="Creator profile not found")
    return CreatorProfile(**profile)

@api_router.put("/creators/profile", response_model=CreatorProfile)
async def update_creator_profile(
    profile_data: CreatorProfileUpdate,
    current_user: User = Depends(get_current_user)
):
    profile = await db.creator_profiles.find_one({"user_id": current_user.id})
    if not profile:
        raise HTTPException(status_code=404, detail="Creator profile not found")
    
    update_data = {k: v for k, v in profile_data.dict().items() if v is not None}
    update_data["updated_at"] = datetime.utcnow()
    
    await db.creator_profiles.update_one(
        {"user_id": current_user.id},
        {"$set": update_data}
    )
    
    updated_profile = await db.creator_profiles.find_one({"user_id": current_user.id})
    return CreatorProfile(**updated_profile)

# Service Listing Routes
@api_router.post("/services", response_model=ServiceListing)
async def create_service_listing(
    service_data: ServiceListingCreate,
    current_user: User = Depends(get_current_user)
):
    if current_user.user_type != "creator":
        raise HTTPException(status_code=403, detail="Only creators can create services")
    
    service_dict = service_data.dict()
    service_dict["creator_id"] = current_user.id
    service_obj = ServiceListing(**service_dict)
    
    await db.service_listings.insert_one(service_obj.dict())
    return service_obj

@api_router.get("/services", response_model=List[ServiceListing])
async def get_service_listings(
    category: Optional[str] = None,
    search: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    limit: int = 20,
    skip: int = 0
):
    filters = {"is_active": True}
    
    if category:
        filters["category"] = category
    if min_price is not None:
        filters["base_price"] = {"$gte": min_price}
    if max_price is not None:
        if "base_price" in filters:
            filters["base_price"]["$lte"] = max_price
        else:
            filters["base_price"] = {"$lte": max_price}
    if search:
        filters["$text"] = {"$search": search}
    
    services = await db.service_listings.find(filters).skip(skip).limit(limit).to_list(limit)
    return [ServiceListing(**service) for service in services]

@api_router.get("/services/{service_id}", response_model=ServiceListing)
async def get_service_listing(service_id: str):
    service = await db.service_listings.find_one({"id": service_id})
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return ServiceListing(**service)

@api_router.get("/creators/{creator_id}/services", response_model=List[ServiceListing])
async def get_creator_services(creator_id: str):
    services = await db.service_listings.find({"creator_id": creator_id, "is_active": True}).to_list(100)
    return [ServiceListing(**service) for service in services]

# Add your routes to the router instead of directly to app
@api_router.get("/")
async def root():
    return {"message": "CreatorHub API - Where Creators Thrive!"}

@api_router.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
