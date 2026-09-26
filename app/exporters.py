from pathlib import Path
import re

from fpdf import FPDF


# ============================================================
# PATH
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
EXPORT_DIR = BASE_DIR / "static" / "exports"
EXPORT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# TEXT HELPERS
# ============================================================

def safe_text(value):
    """
    Convert text into safe PDF-compatible text.
    """

    if value is None:
        return ""

    text = str(value)

    replacements = {
        "–": "-",
        "—": "-",
        "“": '"',
        "”": '"',
        "‘": "'",
        "’": "'",
        "…": "...",
        "•": "-",
        "→": "->",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return text.encode(
        "latin-1",
        "replace"
    ).decode("latin-1")


def clean_dialogue(text):
    """
    Clean dialogue text before placing it in the PDF.
    """

    text = safe_text(text)

    # Remove unnecessary labels
    text = re.sub(
        r"^(dialogue|dialog|character)\s*:\s*",
        "",
        text,
        flags=re.IGNORECASE
    )

    return text.strip()


# ============================================================
# PDF CLASS
# ============================================================

class ComicPDF(FPDF):

    def footer(self):

        # Keep footer away from story/dialogue content
        self.set_y(-15)

        self.set_font(
            "Helvetica",
            "",
            8
        )

        self.set_text_color(
            120,
            125,
            140
        )

        self.cell(
            0,
            5,
            f"ComicCraft - AI Comic Story Creator    Page {self.page_no()}",
            align="C"
        )


# ============================================================
# COVER PAGE
# ============================================================

def add_cover(pdf):
    """
    Professional ComicCraft cover page.
    """

    pdf.add_page()

    page_w = pdf.w
    page_h = pdf.h

    # Background
    pdf.set_fill_color(
        17,
        23,
        43
    )

    pdf.rect(
        0,
        0,
        page_w,
        page_h,
        style="F"
    )

    # Top branding
    pdf.set_text_color(
        255,
        255,
        255
    )

    pdf.set_font(
        "Helvetica",
        "B",
        28
    )

    pdf.set_xy(
        25,
        30
    )

    pdf.cell(
        160,
        12,
        "COMICCRAFT",
        align="C"
    )

    # Subtitle
    pdf.set_font(
        "Helvetica",
        "",
        13
    )

    pdf.set_text_color(
        190,
        200,
        225
    )

    pdf.set_xy(
        25,
        48
    )

    pdf.cell(
        160,
        8,
        "AI COMIC STORY CREATOR",
        align="C"
    )

    # Main title
    pdf.set_text_color(
        255,
        255,
        255
    )

    pdf.set_font(
        "Helvetica",
        "B",
        34
    )

    pdf.set_xy(
        25,
        92
    )

    pdf.multi_cell(
        160,
        14,
        "YOUR IDEA.\nYOUR STORY.\nYOUR COMIC.",
        align="C"
    )

    # Divider
    pdf.set_draw_color(
        100,
        120,
        180
    )

    pdf.set_line_width(
        0.8
    )

    pdf.line(
        55,
        155,
        155,
        155
    )

    # Features
    pdf.set_font(
        "Helvetica",
        "",
        12
    )

    pdf.set_text_color(
        205,
        212,
        230
    )

    features = (
        "AI Story Generation\n"
        "Panel-by-Panel Narration\n"
        "AI Comic Illustrations\n"
        "Professional Comic Layout\n"
        "PDF Export"
    )

    pdf.set_xy(
        35,
        175
    )

    pdf.multi_cell(
        140,
        9,
        features,
        align="C"
    )

    # Bottom
    pdf.set_font(
        "Helvetica",
        "B",
        11
    )

    pdf.set_text_color(
        150,
        165,
        195
    )

    pdf.set_xy(
        25,
        255
    )

    pdf.cell(
        160,
        8,
        "GENERATED WITH GEMINI + AI IMAGE GENERATION",
        align="C"
    )


# ============================================================
# PANEL HEADER
# ============================================================

def add_panel_header(
    pdf,
    panel_number,
    title
):
    """
    Add clean header to every comic panel page.
    """

    page_w = pdf.w

    # Header background
    pdf.set_fill_color(
        17,
        23,
        43
    )

    pdf.rect(
        0,
        0,
        page_w,
        25,
        style="F"
    )

    # Logo
    pdf.set_text_color(
        255,
        255,
        255
    )

    pdf.set_font(
        "Helvetica",
        "B",
        11
    )

    pdf.set_xy(
        15,
        8
    )

    pdf.cell(
        60,
        7,
        "COMICCRAFT"
    )

    # Panel number
    pdf.set_font(
        "Helvetica",
        "B",
        9
    )

    pdf.set_xy(
        150,
        8
    )

    pdf.cell(
        45,
        7,
        f"PANEL {panel_number}",
        align="R"
    )

    # Title
    pdf.set_text_color(
        25,
        30,
        45
    )

    pdf.set_font(
        "Helvetica",
        "B",
        18
    )

    pdf.set_xy(
        15,
        34
    )

    pdf.multi_cell(
        180,
        8,
        safe_text(title),
        align="L"
    )


# ============================================================
# IMAGE PATH
# ============================================================

def resolve_image_path(image_path):
    """
    Convert generated image URL/path into local filesystem path.
    """

    if not image_path:
        return None

    image_path = str(image_path)

    # Already an absolute path
    path = Path(image_path)

    if path.is_absolute() and path.exists():
        return path

    # /static/panels/panel_1.png
    clean = image_path.lstrip("/")

    candidate = BASE_DIR / clean

    if candidate.exists():
        return candidate

    # Direct panels filename
    candidate = BASE_DIR / "static" / "panels" / Path(clean).name

    if candidate.exists():
        return candidate

    return None


# ============================================================
# PANEL PAGE
# ============================================================

def add_panel(
    pdf,
    panel,
    panel_number
):
    """
    Add one complete comic panel page.

    Layout:
    Header
    Title
    Image
    Scene/Narration card
    Dialogue card
    Footer
    """

    pdf.add_page()

    title = panel.get(
        "title",
        f"Panel {panel_number}"
    )

    add_panel_header(
        pdf,
        panel_number,
        title
    )

    # --------------------------------------------------------
    # IMAGE
    # --------------------------------------------------------

    image_path = (
        panel.get("image")
        or panel.get("image_path")
        or panel.get("image_url")
    )

    image_file = resolve_image_path(
        image_path
    )

    image_x = 15
    image_y = 52
    image_w = 180
    image_h = 92

    # Image border
    pdf.set_draw_color(
        190,
        195,
        205
    )

    pdf.set_line_width(
        0.6
    )

    pdf.rect(
        image_x - 1,
        image_y - 1,
        image_w + 2,
        image_h + 2
    )

    if image_file:

        try:

            pdf.image(
                str(image_file),
                x=image_x,
                y=image_y,
                w=image_w,
                h=image_h
            )

        except Exception:

            pdf.set_fill_color(
                240,
                242,
                247
            )

            pdf.rect(
                image_x,
                image_y,
                image_w,
                image_h,
                style="F"
            )

            pdf.set_text_color(
                100,
                105,
                115
            )

            pdf.set_font(
                "Helvetica",
                "",
                10
            )

            pdf.set_xy(
                image_x,
                image_y + 42
            )

            pdf.cell(
                image_w,
                8,
                "Illustration unavailable",
                align="C"
            )

    else:

        pdf.set_fill_color(
            240,
            242,
            247
        )

        pdf.rect(
            image_x,
            image_y,
            image_w,
            image_h,
            style="F"
        )

        pdf.set_text_color(
            100,
            105,
            115
        )

        pdf.set_font(
            "Helvetica",
            "",
            10
        )

        pdf.set_xy(
            image_x,
            image_y + 42
        )

        pdf.cell(
            image_w,
            8,
            "Illustration unavailable",
            align="C"
        )

    # --------------------------------------------------------
    # STORY CARD
    # --------------------------------------------------------

    card_x = 15
    card_y = 152
    card_w = 180
    card_h = 62

    pdf.set_fill_color(
        246,
        247,
        251
    )

    pdf.set_draw_color(
        225,
        227,
        235
    )

    pdf.rect(
        card_x,
        card_y,
        card_w,
        card_h,
        style="DF"
    )

    # Scene
    scene = safe_text(
        panel.get(
            "scene",
            ""
        )
    )

    caption = safe_text(
        panel.get(
            "caption",
            ""
        )
    )

    narration = safe_text(
        panel.get(
            "narration",
            ""
        )
    )

    # Scene
    pdf.set_xy(
        card_x + 7,
        card_y + 7
    )

    pdf.set_text_color(
        45,
        50,
        65
    )

    pdf.set_font(
        "Helvetica",
        "B",
        9
    )

    pdf.cell(
        20,
        5,
        "SCENE"
    )

    pdf.set_font(
        "Helvetica",
        "",
        9
    )

    pdf.multi_cell(
        150,
        5,
        scene
    )

    # Caption
    pdf.set_xy(
        card_x + 7,
        card_y + 24
    )

    pdf.set_font(
        "Helvetica",
        "B",
        9
    )

    pdf.cell(
        23,
        5,
        "CAPTION"
    )

    pdf.set_font(
        "Helvetica",
        "",
        9
    )

    pdf.multi_cell(
        147,
        5,
        caption
    )

    # Narration
    pdf.set_xy(
        card_x + 7,
        card_y + 41
    )

    pdf.set_font(
        "Helvetica",
        "B",
        9
    )

    pdf.cell(
        27,
        5,
        "NARRATION"
    )

    pdf.set_font(
        "Helvetica",
        "",
        9
    )

    pdf.multi_cell(
        143,
        5,
        narration
    )

    # --------------------------------------------------------
    # DIALOGUE CARD
    # --------------------------------------------------------

    dialogue = clean_dialogue(
        panel.get(
            "dialogue",
            ""
        )
    )

    dialogue_y = 220
    dialogue_h = 42

    pdf.set_fill_color(
        235,
        230,
        255
    )

    pdf.set_draw_color(
        125,
        90,
        220
    )

    pdf.set_line_width(
        0.8
    )

    pdf.rect(
        15,
        dialogue_y,
        180,
        dialogue_h,
        style="DF"
    )

    # Dialogue label
    pdf.set_text_color(
        80,
        55,
        150
    )

    pdf.set_font(
        "Helvetica",
        "B",
        9
    )

    pdf.set_xy(
        22,
        dialogue_y + 7
    )

    pdf.cell(
        30,
        6,
        "DIALOGUE"
    )

    # Dialogue text
    pdf.set_text_color(
        35,
        35,
        45
    )

    pdf.set_font(
        "Helvetica",
        "",
        10
    )

    pdf.set_xy(
        22,
        dialogue_y + 17
    )

    pdf.multi_cell(
        165,
        6,
        dialogue
    )


# ============================================================
# END PAGE
# ============================================================

def add_end_page(pdf):
    """
    Final ComicCraft ending page.
    """

    pdf.add_page()

    page_w = pdf.w
    page_h = pdf.h

    pdf.set_fill_color(
        17,
        23,
        43
    )

    pdf.rect(
        0,
        0,
        page_w,
        page_h,
        style="F"
    )

    pdf.set_text_color(
        255,
        255,
        255
    )

    pdf.set_font(
        "Helvetica",
        "B",
        32
    )

    pdf.set_xy(
        25,
        105
    )

    pdf.cell(
        160,
        14,
        "THE END",
        align="C"
    )

    pdf.set_font(
        "Helvetica",
        "",
        13
    )

    pdf.set_text_color(
        190,
        200,
        225
    )

    pdf.set_xy(
        25,
        135
    )

    pdf.multi_cell(
        160,
        8,
        "Thank you for creating your story with ComicCraft.",
        align="C"
    )

    pdf.set_font(
        "Helvetica",
        "B",
        12
    )

    pdf.set_text_color(
        150,
        165,
        195
    )

    pdf.set_xy(
        25,
        220
    )

    pdf.cell(
        160,
        8,
        "COMICCRAFT",
        align="C"
    )

    pdf.set_font(
        "Helvetica",
        "",
        10
    )

    pdf.set_xy(
        25,
        232
    )

    pdf.cell(
        160,
        7,
        "AI COMIC STORY CREATOR",
        align="C"
    )


# ============================================================
# MAIN PDF EXPORT FUNCTION
# ============================================================

def save_pdf(layout):
    """
    Generate the complete ComicCraft PDF.

    Returns:
        /static/exports/<filename>.pdf
    """

    pdf = ComicPDF(
        orientation="P",
        unit="mm",
        format="A4"
    )

    # Margins
    pdf.set_margins(
        left=15,
        top=15,
        right=15
    )

    pdf.set_auto_page_break(
        auto=False
    )

    # --------------------------------------------------------
    # COVER
    # --------------------------------------------------------

    add_cover(pdf)

    # --------------------------------------------------------
    # PANELS
    # --------------------------------------------------------

    panels = layout

    # Support dictionary layout
    if isinstance(layout, dict):

        panels = (
            layout.get("panels")
            or layout.get("layout")
            or []
        )

    if not isinstance(panels, list):
        panels = []

    for index, panel in enumerate(
        panels[:5],
        start=1
    ):

        if not isinstance(panel, dict):
            panel = {}

        add_panel(
            pdf,
            panel,
            index
        )

    # --------------------------------------------------------
    # END PAGE
    # --------------------------------------------------------

    add_end_page(pdf)

    # --------------------------------------------------------
    # SAVE
    # --------------------------------------------------------

    filename = (
        f"comic_{__import__('time').strftime('%Y%m%d_%H%M%S')}.pdf"
    )

    output = EXPORT_DIR / filename

    pdf.output(
        str(output)
    )

    print(
        f"Comic PDF created successfully: {output}"
    )

    return f"/static/exports/{filename}"