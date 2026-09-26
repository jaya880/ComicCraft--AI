from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from .gemini_flash import generate_outline
from .gemini_pro import generate_story
from .image_generator import generate_image
from .layout_builder import build_comic_layout
from .exporters import save_pdf


BASE = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE / "templates"))
router = APIRouter()


def create_comic(prompt, character, setting, tone, style):
    outline = generate_outline(prompt, character, setting, tone, style)
    story = generate_story(outline, character, tone)

    images = [
        generate_image(
            p.get("image_prompt", ""),
            int(p.get("panel", i + 1))
        )
        for i, p in enumerate(outline)
    ]

    layout = build_comic_layout(outline, story, images)

    return layout, save_pdf(layout)


class PromptRequest(BaseModel):
    prompt: str
    character_name: str = "Alex"
    setting: str = "forest"
    tone: str = "funny"
    art_style: str = "comic book"


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"request": request}
    )


@router.post("/generate", response_class=HTMLResponse)
async def generate(
    request: Request,
    prompt: str = Form(...),
    character_name: str = Form(...),
    setting: str = Form(...),
    tone: str = Form(...),
    art_style: str = Form(...)
):
    try:
        layout, pdf = create_comic(
            prompt,
            character_name,
            setting,
            tone,
            art_style
        )

        return templates.TemplateResponse(
            request=request,
            name="comic_preview.html",
            context={
                "request": request,
                "layout": layout,
                "pdf_path": pdf
            }
        )

    except Exception as e:
        raise HTTPException(500, str(e))


@router.post("/generate-comic/json")
async def generate_json(x: PromptRequest):
    try:
        layout, pdf = create_comic(
            x.prompt,
            x.character_name,
            x.setting,
            x.tone,
            x.art_style
        )

        return JSONResponse({
            "layout": layout,
            "pdf_path": pdf
        })

    except Exception as e:
        raise HTTPException(500, str(e))


@router.get("/export-success", response_class=HTMLResponse)
async def export_success(
    request: Request,
    pdf_path: Optional[str] = None
):
    return templates.TemplateResponse(
        request=request,
        name="export_success.html",
        context={
            "request": request,
            "pdf_path": pdf_path or ""
        }
    )


@router.get("/test-image")
async def test_image(
    prompt: str = "friendly fox in an enchanted forest, comic book art"
):
    return {
        "image": generate_image(prompt, 999)
    }