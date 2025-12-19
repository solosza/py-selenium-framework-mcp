"""
Convert Marketing Brief to PDF-ready HTML
Run: python convert_to_pdf.py
Then open the HTML file in browser and Print > Save as PDF
"""

import markdown
from pathlib import Path

# Read the markdown file
md_path = Path(__file__).parent / "marketing-brief-isagawa.md"
html_path = Path(__file__).parent / "marketing-brief-isagawa.html"

with open(md_path, 'r', encoding='utf-8') as f:
    md_content = f.read()

# Convert to HTML with tables extension
html_body = markdown.markdown(
    md_content,
    extensions=['tables', 'fenced_code', 'toc']
)

# Professional HTML template optimized for PDF printing
html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Isagawa Marketing Brief</title>
    <style>
        @media print {{
            body {{ font-size: 11pt; }}
            h1 {{ page-break-before: avoid; }}
            h2 {{ page-break-before: always; page-break-after: avoid; }}
            h2:first-of-type {{ page-break-before: avoid; }}
            table {{ page-break-inside: avoid; }}
            pre {{ page-break-inside: avoid; }}
        }}

        * {{
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            line-height: 1.6;
            max-width: 900px;
            margin: 0 auto;
            padding: 40px 20px;
            color: #1a1a1a;
            background: #fff;
        }}

        h1 {{
            font-size: 2.5em;
            font-weight: 700;
            border-bottom: 3px solid #2563eb;
            padding-bottom: 15px;
            margin-bottom: 10px;
            color: #111;
        }}

        h2 {{
            font-size: 1.6em;
            font-weight: 600;
            color: #2563eb;
            margin-top: 50px;
            margin-bottom: 20px;
            padding-bottom: 8px;
            border-bottom: 1px solid #e5e7eb;
        }}

        h3 {{
            font-size: 1.2em;
            font-weight: 600;
            color: #374151;
            margin-top: 30px;
            margin-bottom: 15px;
        }}

        p {{
            margin: 15px 0;
        }}

        strong {{
            color: #111;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            font-size: 0.9em;
        }}

        th {{
            background: #2563eb;
            color: white;
            font-weight: 600;
            text-align: left;
            padding: 12px 15px;
        }}

        td {{
            padding: 10px 15px;
            border-bottom: 1px solid #e5e7eb;
            vertical-align: top;
        }}

        tr:nth-child(even) {{
            background: #f9fafb;
        }}

        tr:hover {{
            background: #f3f4f6;
        }}

        code {{
            background: #f3f4f6;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'SF Mono', Monaco, 'Courier New', monospace;
            font-size: 0.9em;
        }}

        pre {{
            background: #1e293b;
            color: #e2e8f0;
            padding: 20px;
            border-radius: 8px;
            overflow-x: auto;
            font-family: 'SF Mono', Monaco, 'Courier New', monospace;
            font-size: 0.85em;
            line-height: 1.5;
            margin: 20px 0;
        }}

        pre code {{
            background: none;
            padding: 0;
            color: inherit;
        }}

        blockquote {{
            border-left: 4px solid #2563eb;
            margin: 20px 0;
            padding: 15px 20px;
            background: #eff6ff;
            color: #1e40af;
            font-style: italic;
        }}

        blockquote p {{
            margin: 0;
        }}

        ul, ol {{
            margin: 15px 0;
            padding-left: 25px;
        }}

        li {{
            margin: 8px 0;
        }}

        hr {{
            border: none;
            border-top: 2px solid #e5e7eb;
            margin: 40px 0;
        }}

        /* Cover page styling */
        h1 + p {{
            font-size: 1.1em;
            color: #4b5563;
        }}

        /* Visual diagram boxes */
        pre {{
            white-space: pre;
            word-wrap: normal;
        }}

        /* Print-specific */
        @page {{
            margin: 1in;
            size: letter;
        }}
    </style>
</head>
<body>
{html_body}

<footer style="margin-top: 60px; padding-top: 20px; border-top: 1px solid #e5e7eb; color: #6b7280; font-size: 0.9em;">
    <p><strong>Isagawa Corp</strong> — Execution Engines for Complex Domains</p>
    <p>Confidential — For Internal Use Only</p>
</footer>
</body>
</html>
"""

# Write the HTML file
with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html_template)

print(f"✓ Created: {html_path}")
print(f"")
print(f"To create PDF:")
print(f"1. Open the HTML file in Chrome/Edge")
print(f"2. Press Ctrl+P (or Cmd+P on Mac)")
print(f"3. Select 'Save as PDF'")
print(f"4. Click Save")
print(f"")
print(f"Or use online converter: https://www.markdowntopdf.com/")
