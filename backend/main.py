from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.database import Base, engine

# Import models so SQLAlchemy creates tables
from app.models.user import User
from app.models.chat_message import ChatMessage

# Import Qdrant service
from app.services.qdrant_service import create_collection

# Import routers
from app.api.home import router as home_router
from app.api.upload import router as upload_router
from app.api.search import router as search_router
from app.api.chat import router as chat_router
from app.api.memory import router as memory_router
from app.api.documents import router as documents_router
from app.api.auth import router as auth_router


# --------------------------------------------------
# Create SQLAlchemy database tables
# --------------------------------------------------

Base.metadata.create_all(bind=engine)


# --------------------------------------------------
# Create FastAPI application
# --------------------------------------------------

app = FastAPI(
    title="AI Memory Search Engine",
    version="1.0.0"
)


# --------------------------------------------------
# Startup Event
# --------------------------------------------------

@app.on_event("startup")
def startup_event():
    """
    Initialize external services when the application starts.
    """

    try:
        # Create Qdrant collection if it does not exist
        create_collection()

        print("=" * 50)
        print("Application startup completed successfully.")
        print("Qdrant collection is ready.")
        print("=" * 50)

    except Exception as error:

        print("=" * 50)
        print(f"Application startup error: {error}")
        print("=" * 50)

        # Re-raise so deployment logs clearly show
        # that an external service failed.
        raise


# --------------------------------------------------
# CORS Configuration
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        # Local development frontend
        "http://localhost:5173",

        # Add your deployed frontend URL here
        # Example:
        # "https://your-frontend.onrender.com",
    ],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


# --------------------------------------------------
# Register API Routers
# --------------------------------------------------

app.include_router(
    home_router
)

app.include_router(
    upload_router
)

app.include_router(
    search_router
)

app.include_router(
    chat_router
)

app.include_router(
    memory_router
)

app.include_router(
    documents_router
)

app.include_router(
    auth_router,
    prefix="/auth",
    tags=["Authentication"]
)


# --------------------------------------------------
# Root Endpoint
# --------------------------------------------------

@app.get("/")
def root():
    return {
        "message": "AI Memory Search Engine API is running",
        "status": "healthy",
        "version": "1.0.0"
    }