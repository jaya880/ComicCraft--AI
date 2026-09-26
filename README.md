# ComicCraft — AI Comic Story Creator using Gemini Models

Polished implementation based on the supplied Skill Wallet ComicCraft project brief.

Features: Gemini story outline/dialogue, Hugging Face image generation, 5-panel preview,
FastAPI + Jinja2 frontend, PDF export, JSON API, Swagger docs, GitHub-ready secrets handling,
and Render deployment configuration.

## Run
python -m venv comiccraft-env
# Windows: comiccraft-env\\Scripts\\activate
# macOS/Linux: source comiccraft-env/bin/activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload

Open http://127.0.0.1:8000 and /docs.
Never commit .env or API keys.
After testing, push the real repo to GitHub, deploy the real app publicly, then add the real
GitHub and Demo URLs in Skill Wallet. Skill Wallet task/progress requirements still apply.
