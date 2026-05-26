import json
import os

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from jinja2 import Environment, FileSystemLoader

from app.data import get_education, get_hobbies, get_locations, get_work_experiences
from app.database import get_pool

router = APIRouter()

templates_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
env = Environment(loader=FileSystemLoader(templates_dir), autoescape=True)
env.filters["json_encode"] = lambda v: json.dumps(v)

NAV_ITEMS = [
    {"href": "/#about", "caption": "about"},
    {"href": "/#experience", "caption": "experience"},
    {"href": "/#travels", "caption": "travels"},
    {"href": "/#guestbook", "caption": "guestbook"},
    {"href": "/blog", "caption": "blog"},
    {"href": "/book", "caption": "book"},
]

SKILLS = [
    "Python", "Ruby", "Rust", "Go", "TypeScript", "JavaScript",
    "Docker", "Kubernetes", "Terraform", "NixOS",
    "PostgreSQL", "MySQL", "Redis", "Kafka",
    "FastAPI", "Rails", "React",
    "Prometheus", "Grafana",
    "Linux", "Git",
]


def render(template_name: str, **context) -> HTMLResponse:
    template = env.get_template(template_name)
    html = template.render(navigation=NAV_ITEMS, **context)
    return HTMLResponse(html)


@router.get("/", response_class=HTMLResponse)
async def index():
    pool = await get_pool()
    work_items = await get_work_experiences(pool)
    location_items = await get_locations(pool)
    url = os.environ.get("URL", "http://localhost:5000")
    return render(
        "index.html",
        title="Abrar Habib",
        url=url,
        request_path="/",
        work=work_items,
        locations=location_items,
        skills=SKILLS,
    )


# ── Blog ──

@router.get("/blog", response_class=HTMLResponse)
async def blog():
    return render("blog.html", title="Abrar Habib — Blog", request_path="/blog", posts=[])


@router.get("/book", response_class=HTMLResponse)
async def book():
    return render(
        "book.html",
        title="Abrar Habib — Book time",
        request_path="/book",
        turnstile_site_key=os.environ.get("TURNSTILE_SITE_KEY", ""),
    )


# ── Redirects for old routes ──

@router.get("/aboutme")
async def aboutme():
    return RedirectResponse("/#about", status_code=301)


@router.get("/work")
async def work():
    return RedirectResponse("/#experience", status_code=301)


@router.get("/education")
async def education():
    return RedirectResponse("/#education", status_code=301)


@router.get("/hobbies")
async def hobbies():
    return RedirectResponse("/#hobbies", status_code=301)


@router.get("/travels")
async def travels():
    return RedirectResponse("/#travels", status_code=301)


@router.get("/timeline")
async def timeline():
    return RedirectResponse("/#guestbook", status_code=301)
