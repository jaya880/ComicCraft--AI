import os
import time
from pathlib import Path

from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from PIL import Image, ImageDraw, ImageFont

load_dotenv()

# --------------------------------------------------
# PATH CONFIGURATION
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

PANELS_DIR = BASE_DIR / "static" / "panels"
PANELS_DIR.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------
# HUGGING FACE CONFIGURATION
# --------------------------------------------------

HF_API_KEY = os.getenv("HF_API_KEY")

MODEL = os.getenv(
    "HF_IMAGE_MODEL",
    "black-forest-labs/FLUX.1-schnell"
)

MAX_RETRIES = 3


# --------------------------------------------------
# FONT HELPER
# --------------------------------------------------

def get_font(size, bold=False):
    """
    Load a system font for professional fallback artwork.
    """

    if bold:
        font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
        ]
    else:
        font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/dejavu/DejaVuSans.ttf",
        ]

    for path in font_paths:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)

    return ImageFont.load_default()


# --------------------------------------------------
# LOCAL FALLBACK IMAGE
# --------------------------------------------------

def create_placeholder(prompt, panel_number):
    """
    Create a professional local comic-style fallback image.

    This is used when:
    - Hugging Face credits are exhausted
    - API request fails
    - API key is missing
    - Image generation fails after retries
    """

    width = 1024
    height = 768

    output = PANELS_DIR / f"panel_{panel_number}.png"

    # --------------------------------------------------
    # DARK CINEMATIC BACKGROUND
    # --------------------------------------------------

    image = Image.new(
        "RGB",
        (width, height),
        (14, 20, 38)
    )

    draw = ImageDraw.Draw(image)

    # Cinematic gradient
    for y in range(height):
        ratio = y / height

        r = int(14 + ratio * 22)
        g = int(20 + ratio * 24)
        b = int(38 + ratio * 45)

        draw.line(
            [(0, y), (width, y)],
            fill=(r, g, b)
        )

    # --------------------------------------------------
    # COMIC FRAME
    # --------------------------------------------------

    margin = 28

    draw.rounded_rectangle(
        (
            margin,
            margin,
            width - margin,
            height - margin
        ),
        radius=28,
        outline=(220, 225, 240),
        width=6
    )

    # --------------------------------------------------
    # FONTS
    # --------------------------------------------------

    small_font = get_font(22)
    title_font = get_font(52, bold=True)
    subtitle_font = get_font(28)
    footer_font = get_font(20)

    # --------------------------------------------------
    # HEADER
    # --------------------------------------------------

    header_text = f"COMICCRAFT  •  PANEL {panel_number}"

    draw.text(
        (65, 60),
        header_text,
        fill=(215, 220, 235),
        font=small_font
    )

    # --------------------------------------------------
    # DECORATIVE COMIC LINES
    # --------------------------------------------------

    for i in range(8):

        y = 115 + i * 9

        draw.line(
            [(65, y), (300, y)],
            fill=(75, 95, 135),
            width=2
        )

    # --------------------------------------------------
    # MAIN TITLE
    # --------------------------------------------------

    title = "THE FINAL CHAPTER"

    bbox = draw.textbbox(
        (0, 0),
        title,
        font=title_font
    )

    title_width = bbox[2] - bbox[0]
    title_height = bbox[3] - bbox[1]

    title_x = (width - title_width) / 2
    title_y = 245

    # Shadow
    draw.text(
        (
            title_x + 4,
            title_y + 4
        ),
        title,
        fill=(5, 8, 18),
        font=title_font
    )

    # Main title
    draw.text(
        (
            title_x,
            title_y
        ),
        title,
        fill=(245, 248, 255),
        font=title_font
    )

    # --------------------------------------------------
    # CENTER COMIC EFFECT
    # --------------------------------------------------

    center_x = width // 2
    center_y = 390

    # Explosion / dramatic rays
    for angle in range(0, 360, 30):

        import math

        rad = math.radians(angle)

        x1 = center_x + int(math.cos(rad) * 75)
        y1 = center_y + int(math.sin(rad) * 75)

        x2 = center_x + int(math.cos(rad) * 170)
        y2 = center_y + int(math.sin(rad) * 170)

        draw.line(
            [(x1, y1), (x2, y2)],
            fill=(100, 125, 175),
            width=3
        )

    # Central glowing-style circle
    draw.ellipse(
        (
            center_x - 58,
            center_y - 58,
            center_x + 58,
            center_y + 58
        ),
        outline=(225, 230, 245),
        width=5
    )

    draw.ellipse(
        (
            center_x - 20,
            center_y - 20,
            center_x + 20,
            center_y + 20
        ),
        fill=(225, 230, 245)
    )

    # --------------------------------------------------
    # DESCRIPTION
    # --------------------------------------------------

    message = (
        "AI illustration temporarily unavailable.\n"
        "This panel uses ComicCraft local fallback artwork."
    )

    lines = message.split("\n")

    y = 525

    for line in lines:

        bbox = draw.textbbox(
            (0, 0),
            line,
            font=subtitle_font
        )

        text_width = bbox[2] - bbox[0]

        draw.text(
            (
                (width - text_width) / 2,
                y
            ),
            line,
            fill=(190, 200, 220),
            font=subtitle_font
        )

        y += 42

    # --------------------------------------------------
    # FOOTER
    # --------------------------------------------------

    footer = "YOUR IDEA  •  YOUR COMIC"

    bbox = draw.textbbox(
        (0, 0),
        footer,
        font=footer_font
    )

    footer_width = bbox[2] - bbox[0]

    draw.text(
        (
            (width - footer_width) / 2,
            700
        ),
        footer,
        fill=(155, 170, 200),
        font=footer_font
    )

    # --------------------------------------------------
    # SAVE
    # --------------------------------------------------

    image.save(
        output,
        format="PNG"
    )

    print(
        f"Local fallback created for panel {panel_number}."
    )

    return f"/static/panels/{output.name}"


# --------------------------------------------------
# AI PROMPT BUILDER
# --------------------------------------------------

def build_prompt(prompt):
    """
    Create a professional cinematic comic prompt.
    """

    return (
        f"{prompt}. "
        "Professional cinematic comic book illustration, "
        "highly detailed environment, "
        "expressive characters, "
        "consistent character design, "
        "dynamic composition, "
        "dramatic cinematic lighting, "
        "vibrant colors, "
        "professional graphic novel artwork, "
        "high quality digital illustration. "
        "No text, no letters, no words, "
        "no captions, no speech bubbles, "
        "no watermark, no logo."
    )


# --------------------------------------------------
# AI IMAGE GENERATION
# --------------------------------------------------

def generate_image(prompt, panel_number):
    """
    Generate one comic panel using Hugging Face.

    If generation fails, automatically switches
    to the local professional fallback.
    """

    # --------------------------------------------------
    # CHECK API KEY
    # --------------------------------------------------

    if not HF_API_KEY:

        print(
            "HF_API_KEY is missing."
        )

        return create_placeholder(
            prompt,
            panel_number
        )

    # --------------------------------------------------
    # HUGGING FACE CLIENT
    # --------------------------------------------------

    client = InferenceClient(
        api_key=HF_API_KEY,
        provider="auto"
    )

    final_prompt = build_prompt(prompt)

    # --------------------------------------------------
    # RETRY LOOP
    # --------------------------------------------------

    for attempt in range(
        1,
        MAX_RETRIES + 1
    ):

        try:

            print(
                f"Generating panel {panel_number} "
                f"({attempt}/{MAX_RETRIES})..."
            )

            image = client.text_to_image(
                prompt=final_prompt,
                model=MODEL
            )

            # --------------------------------------------------
            # SAVE AI IMAGE
            # --------------------------------------------------

            output = PANELS_DIR / (
                f"panel_{panel_number}.png"
            )

            image.convert("RGB").save(
                output,
                format="PNG"
            )

            print(
                f"Panel {panel_number} "
                f"generated successfully."
            )

            return (
                f"/static/panels/"
                f"{output.name}"
            )

        except Exception as error:

            print(
                f"Panel {panel_number} failed "
                f"(attempt {attempt}/{MAX_RETRIES}): "
                f"{error}"
            )

            # Wait before retry
            if attempt < MAX_RETRIES:

                time.sleep(3)

    # --------------------------------------------------
    # AI FAILED
    # --------------------------------------------------

    print(
        f"Panel {panel_number} failed after "
        f"{MAX_RETRIES} attempts."
    )

    print(
        "Switching to local fallback artwork..."
    )

    return create_placeholder(
        prompt,
        panel_number
    )