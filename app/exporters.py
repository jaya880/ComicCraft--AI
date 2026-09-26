from pathlib import Path
from datetime import datetime
from fpdf import FPDF
BASE=Path(__file__).resolve().parent.parent; OUT=BASE/"static"/"exports"; OUT.mkdir(parents=True,exist_ok=True)

def save_pdf(layout):
    p=OUT/f"comic_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"; pdf=FPDF()
    for i,x in enumerate(layout):
        pdf.add_page(); pdf.set_font("Helvetica","B",18); pdf.cell(0,12,f"Panel {x['panel']}: {x['title']}",ln=True)
        img=x.get("image","")
        if img.startswith("/static/"):
            ip=BASE/img.lstrip("/")
            if ip.exists(): pdf.image(str(ip),x=15,y=35,w=180); pdf.ln(125)
        pdf.set_font("Helvetica","I",11); pdf.multi_cell(0,7,x.get("scene_description","")); pdf.ln(2)
        pdf.set_font("Helvetica","",11); pdf.multi_cell(0,7,x.get("caption","")); pdf.multi_cell(0,7,x.get("narration",""))
        pdf.set_font("Helvetica","B",11); pdf.multi_cell(0,7,x.get("dialogue",""))
    pdf.output(str(p)); return f"/static/exports/{p.name}"
