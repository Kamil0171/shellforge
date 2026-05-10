from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates


router = APIRouter(prefix="/about", tags=["about"])

templates = Jinja2Templates(directory="app/templates")


@router.get("/")
def about_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="about.html",
        context={},
    )