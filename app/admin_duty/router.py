from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/admin-duty", tags=["admin-duty"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
def admin_duty(request: Request):
    return templates.TemplateResponse(
        request=request, name="admin_duty/index.html", context={}
    )
