from pathlib import Path

TEMPLATES_DIR = Path("templates")

SECTION_REGISTRY = {
    "card_metadata": {
        "prefix": "card_metadata_",
        "template": "card_metadata.md.j2",
    }
}
