#!/usr/bin/env python3
"""
Generate a simple application icon for the CCX Plugin Installer.

Creates assets/icon.ico — a simple box-with-arrow icon.
Requires: pip install Pillow
"""

from pathlib import Path

try:
    from PIL import Image, ImageDraw
except ImportError:
    print("Pillow is required. Run: pip install Pillow")
    raise


ASSETS_DIR = Path(__file__).parent / "assets"
ICON_PATH = ASSETS_DIR / "icon.ico"
SIZES = [256, 128, 64, 48, 32, 16]


def generate_icon() -> None:
    """Generate a simple CCX installer icon and save as .ico."""
    ASSETS_DIR.mkdir(exist_ok=True)

    size = 256
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Background rounded rectangle
    margin = 20
    # Main color: blue accent (#1f6aa5)
    bg_color = (31, 106, 165, 255)

    # Draw a box with rounded corners (approximated)
    draw.rounded_rectangle(
        [margin, margin + 60, size - margin, size - margin],
        radius=20,
        fill=bg_color,
    )

    # Draw a "package" shape on top
    pkg_color = (255, 255, 255, 255)
    pkg_left = size // 2 - 40
    pkg_top = margin + 15
    pkg_right = size // 2 + 40
    pkg_bottom = margin + 70

    draw.rectangle([pkg_left, pkg_top, pkg_right, pkg_bottom], fill=pkg_color)
    draw.polygon(
        [
            (pkg_left, pkg_top),
            (size // 2, pkg_top - 30),
            (pkg_right, pkg_top),
        ],
        fill=pkg_color,
    )

    # Arrow going down into the box
    arrow_color = (220, 220, 220, 255)
    arrow_x = size // 2
    arrow_top = margin + 85
    arrow_bottom = size - margin - 30

    draw.line(
        [(arrow_x, arrow_top), (arrow_x, arrow_bottom)],
        fill=arrow_color,
        width=4,
    )
    # Arrow head
    draw.polygon(
        [
            (arrow_x, arrow_bottom + 5),
            (arrow_x - 10, arrow_bottom - 10),
            (arrow_x + 10, arrow_bottom - 10),
        ],
        fill=arrow_color,
    )

    # Save as .ico with multiple sizes
    img.save(str(ICON_PATH), format="ICO", sizes=[(s, s) for s in SIZES])
    print(f"✓ Icon saved to {ICON_PATH}")


if __name__ == "__main__":
    generate_icon()
