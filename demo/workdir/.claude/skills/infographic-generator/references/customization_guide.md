# Infographic Generator Reference

## Color Schemes

The infographic generator uses a carefully selected color palette that can be customized:

### Default Colors

- **Background**: `(255, 255, 255)` - White
- **Primary (Header)**: `(191, 97, 64)` - Claude's signature color
- **Secondary**: `(74, 85, 104)` - Dark gray-blue
- **Text**: `(26, 32, 44)` - Near black
- **Accent**: `(237, 242, 247)` - Light gray-blue

### Customizing Colors

To customize colors, modify the color definitions in `generate_infographic.py`:

```python
# Colors
bg_color = (255, 255, 255)
primary_color = (191, 97, 64)
secondary_color = (74, 85, 104)
text_color = (26, 32, 44)
accent_color = (237, 242, 247)
```

## Layout Specifications

### Image Dimensions
- **Width**: 1200px
- **Height**: 800px
- **Aspect Ratio**: 3:2 (ideal for social media and presentations)

### Text Areas

#### Request Section
- **Maximum characters displayed**: 200
- **Maximum lines**: 3
- **Font size**: 24pt
- **Position**: Upper third of infographic

#### Response Section
- **Maximum characters displayed**: 300
- **Maximum lines**: 5
- **Font size**: 24pt
- **Position**: Middle section of infographic

### Margins and Spacing
- **Side margins**: 60px
- **Section spacing**: 30-40px
- **Line height**: 35px

## Font Configuration

### Default Fonts

The script uses DejaVu Sans fonts (available on most Linux systems):

- **Title**: DejaVuSans-Bold, 48pt
- **Headers**: DejaVuSans-Bold, 32pt
- **Body**: DejaVuSans, 24pt
- **Footer**: DejaVuSans, 18pt

### Using Custom Fonts

To use custom fonts, place TrueType (.ttf) or OpenType (.otf) fonts in the `assets/` directory and update the font loading code:

```python
title_font = ImageFont.truetype("assets/your-font.ttf", 48)
```

## Template Backgrounds

### Using Custom Templates

Place your custom background image in `assets/` and reference it when calling the script:

```bash
python scripts/generate_infographic.py "Request text" "Response text" output.png assets/custom_template.png
```

### Template Requirements

- **Format**: PNG or JPEG
- **Recommended size**: 1200x800px
- **Design**: Keep backgrounds subtle to maintain text readability
- **Opacity**: Use semi-transparent elements for visual interest

## API Usage

### Python Function

```python
from scripts.generate_infographic import create_infographic

create_infographic(
    request_text="User's question or request",
    response_text="Claude's response summary",
    output_path="output/infographic.png",
    template_path="assets/template_background.png"  # Optional
)
```

### Command Line

```bash
python scripts/generate_infographic.py \
    "What is machine learning?" \
    "Machine learning is a subset of AI that enables systems to learn..." \
    output/ml_summary.png \
    assets/template_background.png
```

## Output Quality

- **Format**: PNG
- **Quality**: 95 (high quality, minimal compression)
- **Color space**: RGB
- **Typical file size**: 200-500KB

## Best Practices

### Text Length

- Keep request text under 200 characters for best display
- Keep response text under 300 characters
- Longer text will be truncated with "..."

### Content Selection

For best results, extract the key points from conversations:
- **Request**: The core question or task
- **Response**: The main takeaway or conclusion

### Visual Balance

- Use the template for brand consistency
- Ensure sufficient contrast between text and background
- Test readability at different sizes

## Troubleshooting

### Common Issues

**Fonts not loading**: The script falls back to default PIL fonts if custom fonts aren't found.

**Dependencies missing**: The script auto-installs Pillow if needed using pip.

**Template not found**: The script creates a plain white background if template is missing.

### Error Messages

- `"Usage: python generate_infographic.py..."` - Incorrect command line arguments
- `"Installing Pillow..."` - Automatic dependency installation in progress
