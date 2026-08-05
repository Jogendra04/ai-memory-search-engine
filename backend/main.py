from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.database import Base, engine

# Import models so SQLAlchemy creates tables
from app.models.user import User

# Import routers
from app.api.home import router as home_router
from app.api.upload import router as upload_router
from app.api.search import router as search_router
from app.api.chat import router as chat_router
from app.api.memory import router as memory_router
from app.api.documents import router as documents_router
from app.api.auth import router as auth_router


# Create database tables
Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="AI Memory Search Engine",
    version="1.0.0"
)


# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Register API routes
app.include_router(home_router)
app.include_router(upload_router)
app.include_router(search_router)
app.include_router(chat_router)
app.include_router(memory_router)
app.include_router(documents_router)

app.include_router(
    auth_router,
    prefix="/auth",
    tags=["Authentication"]
)