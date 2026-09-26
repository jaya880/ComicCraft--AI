def build_comic_layout(outline,stories,images):
    out=[]
    for i,p in enumerate(outline):
        s=stories[i] if i<len(stories) else {}
        out.append({"panel":p.get("panel",i+1),"title":p.get("title","Panel"),
        "scene_description":p.get("scene_description",""),"image_prompt":p.get("image_prompt",""),
        "image":images[i] if i<len(images) else "","caption":s.get("caption",""),
        "narration":s.get("narration",""),"dialogue":s.get("dialogue","")})
    return out
