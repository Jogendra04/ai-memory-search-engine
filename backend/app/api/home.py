from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def home():
    return {
        "message": "Backend is running!"
    }


@router.get("/hello")
def hello():
    return {
        "message": "Hello from FastAPI!"
    }