from fastapi import APIRouter

router = APIRouter(prefix="", tags=[""])

@router.get("/")
def root():
    return {"message": "API DEV is running"}