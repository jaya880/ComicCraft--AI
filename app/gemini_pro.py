import json
import os

from dotenv import load_dotenv

load_dotenv()

# --------------------------------------------------
# GEMINI CONFIGURATION
# --------------------------------------------------

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

MODEL = os.getenv(
    "GEMINI_PRO_MODEL",
    "gemini-1.5-pro"
)


# --------------------------------------------------
# FALLBACK STORY
# --------------------------------------------------

def fallback_story(outline, character, tone):
    """
    Create a clean 5-panel story if Gemini is unavailable.
    """

    panels = []

    fallback_dialogues = [
        f"{character}: Something strange is happening...",
        f"{character}: This clue must lead somewhere.",
        f"{character}: I have to solve this puzzle!",
        f"{character}: I finally understand the secret!",
        f"{character}: We did it! The city is safe!"
    ]

    fallback_narrations = [
        f"{character} discovers something mysterious and decides to investigate.",
        f"{character} follows an important clue and discovers a hidden secret.",
        f"{character} reaches an ancient puzzle and faces the biggest challenge.",
        f"{character} understands the puzzle and finds the solution.",
        f"{character} solves the mystery and saves the floating city before sunset."
    ]

    for i in range(5):

        panel_data = (
            outline[i]
            if i < len(outline)
            else {}
        )

        panels.append({
            "panel": i + 1,
            "title": [
                "The Discovery",
                "The Clue",
                "The Ancient Secret",
                "The Solution",
                "The Ending"
            ][i],
            "scene": panel_data.get(
                "scene",
                f"{character} continues the adventure."
            ),
            "caption": panel_data.get(
                "caption",
                fallback_narrations[i]
            ),
            "narration": fallback_narrations[i],
            "dialogue": fallback_dialogues[i],
            "image_prompt": panel_data.get(
                "image_prompt",
                ""
            )
        })

    return panels


# --------------------------------------------------
# GEMINI STORY GENERATION
# --------------------------------------------------

def generate_story(outline, character, tone):
    """
    Generate unique narration and dialogue
    for every comic panel.
    """

    # ----------------------------------------------
    # API KEY CHECK
    # ----------------------------------------------

    if not GEMINI_API_KEY:
        print("GEMINI_API_KEY is missing.")
        return fallback_story(
            outline,
            character,
            tone
        )

    try:

        import google.generativeai as genai

        genai.configure(
            api_key=GEMINI_API_KEY
        )

        model = genai.GenerativeModel(
            MODEL
        )

        # ------------------------------------------
        # BUILD PANEL INFORMATION
        # ------------------------------------------

        outline_text = ""

        for i, panel in enumerate(outline):

            outline_text += f"""
PANEL {i + 1}
Title: {panel.get("title", "")}
Scene: {panel.get("scene", "")}
Image Prompt: {panel.get("image_prompt", "")}
"""

        # ------------------------------------------
        # PROFESSIONAL STORY PROMPT
        # ------------------------------------------

        prompt = f"""
You are a professional comic-book writer.

Create a 5-panel comic story using the supplied
panel outline.

Character:
{character}

Tone:
{tone}

IMPORTANT REQUIREMENTS:

1. Every panel MUST have unique narration.
2. Every panel MUST have unique dialogue.
3. Do NOT repeat the same sentence between panels.
4. The story must progress naturally from Panel 1
   to Panel 5.
5. Keep the same main character throughout.
6. Panel 1 must introduce the mystery.
7. Panel 2 must develop the clue.
8. Panel 3 must present the main challenge.
9. Panel 4 must show the solution or turning point.
10. Panel 5 must provide a satisfying ending.
11. Dialogue should sound natural and short.
12. Narration should describe what is happening.
13. Do NOT add speech bubbles or text instructions
    to image prompts.
14. Return ONLY valid JSON.
15. Do not add markdown or ```json.

PANEL OUTLINE:
{outline_text}

Return exactly this JSON structure:

{{
  "panels": [
    {{
      "panel": 1,
      "title": "The Discovery",
      "scene": "...",
      "caption": "...",
      "narration": "...",
      "dialogue": "..."
    }},
    {{
      "panel": 2,
      "title": "The Clue",
      "scene": "...",
      "caption": "...",
      "narration": "...",
      "dialogue": "..."
    }},
    {{
      "panel": 3,
      "title": "The Challenge",
      "scene": "...",
      "caption": "...",
      "narration": "...",
      "dialogue": "..."
    }},
    {{
      "panel": 4,
      "title": "The Turning Point",
      "scene": "...",
      "caption": "...",
      "narration": "...",
      "dialogue": "..."
    }},
    {{
      "panel": 5,
      "title": "The Ending",
      "scene": "...",
      "caption": "...",
      "narration": "...",
      "dialogue": "..."
    }}
  ]
}}
"""

        # ------------------------------------------
        # GENERATE
        # ------------------------------------------

        response = model.generate_content(
            prompt
        )

        raw_text = response.text.strip()

        # Remove accidental markdown fences
        if raw_text.startswith("```"):
            raw_text = raw_text.replace(
                "```json",
                ""
            ).replace(
                "```",
                ""
            ).strip()

        # ------------------------------------------
        # PARSE JSON
        # ------------------------------------------

        data = json.loads(raw_text)

        panels = data.get(
            "panels",
            []
        )

        if len(panels) != 5:
            print(
                "Gemini returned an invalid number "
                "of panels."
            )

            return fallback_story(
                outline,
                character,
                tone
            )

        # ------------------------------------------
        # MERGE IMAGE PROMPTS FROM OUTLINE
        # ------------------------------------------

        for i, panel in enumerate(panels):

            if i < len(outline):

                panel["image_prompt"] = outline[i].get(
                    "image_prompt",
                    ""
                )

            panel["panel"] = i + 1

        print(
            "Gemini generated 5 unique comic panels."
        )

        return panels

    # ----------------------------------------------
    # ERROR HANDLING
    # ----------------------------------------------

    except Exception as error:

        print(
            f"Gemini story generation failed: {error}"
        )

        print(
            "Using professional fallback story."
        )

        return fallback_story(
            outline,
            character,
            tone
        )