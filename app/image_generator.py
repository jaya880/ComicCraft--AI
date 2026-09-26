import os
from pathlib import Path
from io import BytesIO
import requests
from PIL import Image, ImageDraw
from dotenv import load_dotenv
load_dotenv()
BASE=Path(__file__).resolve().parent.parent
OUT=BASE/"static"/"panels"; OUT.mkdir(parents=True,exist_ok=True)
KEY=os.getenv("HF_API_KEY"); MODEL=os.getenv("HF_IMAGE_MODEL","runwayml/stable-diffusion-v1-5")

def placeholder(prompt,n):
    p=OUT/f"panel_{n}.png"; im=Image.new("RGB",(1024,768),(235,240,250))
    d=ImageDraw.Draw(im); d.rounded_rectangle((25,25,999,743),25,outline=(55,70,100),width=6)
    d.text((60,65),f"COMICCRAFT • PANEL {n}",fill=(20,30,50))
    d.text((60,150),prompt[:220],fill=(55,60,70))
    d.text((60,690),"Demo placeholder — add HF_API_KEY for AI illustration generation.",fill=(80,80,90))
    im.save(p); return f"/static/panels/{p.name}"

def generate_image(prompt,n):
    if not KEY: return placeholder(prompt,n)
    try:
        r=requests.post(f"https://api-inference.huggingface.co/models/{MODEL}",
                        headers={"Authorization":f"Bearer {KEY}"},json={"inputs":prompt},timeout=180)
        if "image" not in r.headers.get("content-type",""): return placeholder(prompt,n)
        p=OUT/f"panel_{n}.png"; Image.open(BytesIO(r.content)).convert("RGB").save(p)
        return f"/static/panels/{p.name}"
    except Exception: return placeholder(prompt,n)
