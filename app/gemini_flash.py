import os, json, re
import google.generativeai as genai
from dotenv import load_dotenv
load_dotenv()
KEY=os.getenv("GEMINI_API_KEY"); MODEL=os.getenv("GEMINI_FLASH_MODEL","gemini-1.5-flash")
if KEY: genai.configure(api_key=KEY)

def _json(text):
    text=re.sub(r"^```(?:json)?\s*|\s*```$","",text.strip())
    m=re.search(r"\[[\s\S]*\]",text)
    return json.loads(m.group(0) if m else text)

def generate_outline(prompt, character, setting, tone, art_style):
    if not KEY: return fallback(prompt,character,setting,tone,art_style)
    try:
        model=genai.GenerativeModel(MODEL)
        r=model.generate_content(f'''Create exactly 5 comic panels as JSON only.
Story: {prompt}; Character: {character}; Setting: {setting}; Tone: {tone}; Art style: {art_style}.
Each object: panel,title,scene_description,image_prompt. No markdown.''')
        return _json(r.text)[:5]
    except Exception:
        return fallback(prompt,character,setting,tone,art_style)

def fallback(prompt,character,setting,tone,style):
    beats=[("The Beginning",f"{character} discovers the mystery."),
           ("The Clue",f"{character} finds a surprising clue."),
           ("The Challenge",f"{character} faces a difficult obstacle."),
           ("The Turning Point",f"{character} finds a clever way forward."),
           ("The Ending",f"{character} reaches a satisfying conclusion.")]
    return [{"panel":i+1,"title":t,"scene_description":d,
             "image_prompt":f"{style} comic illustration, {setting}, {character}, {tone}, {prompt}, panel {i+1}"}
            for i,(t,d) in enumerate(beats)]
