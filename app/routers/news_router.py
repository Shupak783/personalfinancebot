from fastapi import APIRouter

from app.news import get_news

router = APIRouter(prefix="/news", tags=["news"])


@router.get("")
def news():
    return get_news()
