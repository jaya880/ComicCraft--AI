import os, json, re
import google.generativeai as genai
from dotenv import load_dotenv
load_dotenv()
KEY=os.getenv("GEMINI_API_KEY"); MODEL=os.getenv("GEMINI_PRO_MODEL","gemini-1.5-pro")
if KEY: genai.configure(api_key=KEY)

def generate_story(outline, character, tone):
    if not KEY: return fallback(outline,character)
    try:
        model=genai.GenerativeModel(MODEL)
        src="\n".join(f"Panel {p['panel']}: {p['title']} — {p['scene_description']}" for p in outline)
        r=model.generate_content(f'''Create narration/dialogue for these 5 comic panels. Character={character}, tone={tone}.
{src}
Return JSON array only with panel,caption,narration,dialogue.''')
        text=re.sub(r"^```(?:json)?\s*|\s*```$","",r.text.strip())
        m=re.search(r"\[[\s\S]*\]",text)
        return json.loads(m.group(0) if m else text)[:5]
    except Exception: return fallback(outline,character)

def fallback(outline,character):
    return [{"panel":p["panel"],"caption":p["scene_description"],
             "narration":f"{character} moves forward with courage.",
             "dialogue":f"{character}: Let's see what happens next!"} for p in outline]
