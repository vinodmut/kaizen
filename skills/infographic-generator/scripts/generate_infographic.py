#!/usr/bin/env python3
"""
Infographic Generator Script
Generates visual summaries of user requests and Claude responses.
"""

import sys
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import textwrap

def ensure_dependencies():
    """Install required packages if not available."""
    try:
        import PIL
    except ImportError:
        print("Installing Pillow...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--break-system-packages", "Pillow"])
        import PIL

def wrap_text(text, font, max_width, draw):
    """Wrap text to fit within max_width."""
    lines = []
    words = text.split()
    current_line = []
    
    for word in words:
        test_line = ' '.join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=font)
        width = bbox[2] - bbox[0]
        
        if width <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]
    
    if current_line:
        lines.append(' '.join(current_line))
    
    return lines

def create_infographic(request_text, response_text, output_path, template_path=None, tips=None):
    """
    Create an infographic summarizing a request and response.

    Args:
        request_text (str): The user's request
        response_text (str): Claude's response summary
        output_path (str): Where to save the infographic
        template_path (str): Optional path to background template image
        tips (list): Optional list of tip dicts with content, rationale, category, trigger
    """
    ensure_dependencies()

    # Image dimensions - increase height if tips provided
    width = 1200
    height = 1000 if tips else 800

    # Colors
    bg_color = (255, 255, 255)
    primary_color = (191, 97, 64)  # Claude's color
    secondary_color = (74, 85, 104)
    text_color = (26, 32, 44)
    accent_color = (237, 242, 247)
    tip_color = (56, 161, 105)  # Green for tips

    # Category badge colors
    category_colors = {
        "strategy": (59, 130, 246),   # Blue
        "recovery": (239, 68, 68),    # Red
        "optimization": (16, 185, 129)  # Green
    }

    # Create base image
    if template_path and Path(template_path).exists():
        img = Image.open(template_path).resize((width, height))
    else:
        img = Image.new('RGB', (width, height), bg_color)

    draw = ImageDraw.Draw(img)

    # Load fonts (fallback to default if custom fonts unavailable)
    try:
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
        header_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
        body_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
        small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
        badge_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
    except:
        title_font = ImageFont.load_default()
        header_font = ImageFont.load_default()
        body_font = ImageFont.load_default()
        small_font = ImageFont.load_default()
        badge_font = ImageFont.load_default()

    # Draw header bar
    draw.rectangle([(0, 0), (width, 100)], fill=primary_color)
    draw.text((width // 2, 50), "Conversation Summary", font=title_font,
              fill=(255, 255, 255), anchor="mm")

    # Content margins
    margin = 60
    content_width = width - (2 * margin)
    y_position = 140

    # Draw request section
    draw.text((margin, y_position), "Request:", font=header_font, fill=primary_color)
    y_position += 50

    # Wrap and draw request text
    request_lines = wrap_text(request_text[:200], body_font, content_width, draw)
    for line in request_lines[:3]:  # Limit to 3 lines
        draw.text((margin, y_position), line, font=body_font, fill=text_color)
        y_position += 35

    if len(request_text) > 200:
        draw.text((margin, y_position), "...", font=body_font, fill=text_color)
        y_position += 35

    y_position += 30

    # Draw separator line
    draw.line([(margin, y_position), (width - margin, y_position)],
              fill=accent_color, width=3)
    y_position += 40

    # Draw response section
    draw.text((margin, y_position), "Response:", font=header_font, fill=secondary_color)
    y_position += 50

    # Wrap and draw response text
    response_lines = wrap_text(response_text[:300], body_font, content_width, draw)
    for line in response_lines[:5]:  # Limit to 5 lines
        draw.text((margin, y_position), line, font=body_font, fill=text_color)
        y_position += 35

    if len(response_text) > 300:
        draw.text((margin, y_position), "...", font=body_font, fill=text_color)
        y_position += 35

    # Draw tips section if tips provided
    if tips:
        y_position += 30

        # Draw separator line
        draw.line([(margin, y_position), (width - margin, y_position)],
                  fill=accent_color, width=3)
        y_position += 40

        # Tips header
        draw.text((margin, y_position), "Tips:", font=header_font, fill=tip_color)
        y_position += 50

        # Display up to 3 tips
        for i, tip in enumerate(tips[:3]):
            tip_content = tip.get("content", "")
            tip_category = tip.get("category", "strategy")

            # Draw category badge
            badge_color = category_colors.get(tip_category, category_colors["strategy"])
            badge_text = tip_category.upper()
            badge_bbox = draw.textbbox((0, 0), badge_text, font=badge_font)
            badge_width = badge_bbox[2] - badge_bbox[0] + 16
            badge_height = badge_bbox[3] - badge_bbox[1] + 8

            # Draw rounded rectangle for badge
            badge_x = margin
            badge_y = y_position
            draw.rounded_rectangle(
                [(badge_x, badge_y), (badge_x + badge_width, badge_y + badge_height)],
                radius=4,
                fill=badge_color
            )
            draw.text((badge_x + 8, badge_y + 4), badge_text, font=badge_font, fill=(255, 255, 255))

            # Draw tip content next to badge
            tip_x = badge_x + badge_width + 12
            tip_lines = wrap_text(tip_content[:150], small_font, content_width - badge_width - 20, draw)
            for line in tip_lines[:2]:  # Limit each tip to 2 lines
                draw.text((tip_x, y_position), line, font=small_font, fill=text_color)
                y_position += 25

            y_position += 10  # Space between tips

        # Save tips to JSON file
        output_path_obj = Path(output_path)
        tips_json_path = output_path_obj.parent / f"{output_path_obj.stem}_tips.json"
        with open(tips_json_path, 'w') as f:
            json.dump({"tips": tips}, f, indent=2)
        print(f"✓ Tips saved to: {tips_json_path}")

    # Draw footer
    footer_text = "Generated by Claude"
    draw.text((width // 2, height - 30), footer_text, font=small_font,
              fill=secondary_color, anchor="mm")

    # Save the image
    img.save(output_path, quality=95)
    print(f"✓ Infographic saved to: {output_path}")
    return output_path

def main():
    """CLI interface for the infographic generator."""
    if len(sys.argv) < 4:
        print("Usage: python generate_infographic.py <request> <response> <output_path> [template_path] [tips_json]")
        print("\nArguments:")
        print("  request       - User's request summary (string)")
        print("  response      - Claude's response summary (string)")
        print("  output_path   - Path to save the infographic PNG")
        print("  template_path - Optional background template image")
        print("  tips_json     - Optional JSON string with tips array")
        sys.exit(1)

    request = sys.argv[1]
    response = sys.argv[2]
    output = sys.argv[3]
    template = sys.argv[4] if len(sys.argv) > 4 else None
    tips = None

    if len(sys.argv) > 5:
        try:
            tips_data = json.loads(sys.argv[5])
            tips = tips_data.get("tips", [])
        except json.JSONDecodeError as e:
            print(f"Warning: Could not parse tips JSON: {e}")
            tips = None

    create_infographic(request, response, output, template, tips)

if __name__ == "__main__":
    main()
