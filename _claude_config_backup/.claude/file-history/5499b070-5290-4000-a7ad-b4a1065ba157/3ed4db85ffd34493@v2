"""
Convert Marketing Brief Markdown to Word Document
Run: python convert_to_docx.py
"""

import re
from pathlib import Path
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

def set_cell_shading(cell, color):
    """Set cell background color"""
    shading = OxmlElement('w:shd')
    shading.set(qn('w:fill'), color)
    cell._tc.get_or_add_tcPr().append(shading)

def add_table_from_lines(doc, lines):
    """Parse markdown table and add to document"""
    # Parse header
    header_line = lines[0].strip()
    headers = [h.strip() for h in header_line.split('|') if h.strip()]

    # Parse data rows (skip separator line)
    data_rows = []
    for line in lines[2:]:
        if line.strip():
            cells = [c.strip() for c in line.split('|') if c.strip()]
            if cells:
                data_rows.append(cells)

    if not headers or not data_rows:
        return

    # Create table
    table = doc.add_table(rows=1 + len(data_rows), cols=len(headers))
    table.style = 'Table Grid'

    # Header row
    header_cells = table.rows[0].cells
    for i, header in enumerate(headers):
        if i < len(header_cells):
            header_cells[i].text = header.replace('**', '')
            set_cell_shading(header_cells[i], '2563EB')
            for paragraph in header_cells[i].paragraphs:
                for run in paragraph.runs:
                    run.font.color.rgb = RGBColor(255, 255, 255)
                    run.font.bold = True

    # Data rows
    for row_idx, row_data in enumerate(data_rows):
        row_cells = table.rows[row_idx + 1].cells
        for col_idx, cell_data in enumerate(row_data):
            if col_idx < len(row_cells):
                # Clean markdown formatting
                clean_text = cell_data.replace('**', '').replace('*', '')
                row_cells[col_idx].text = clean_text
                # Alternate row colors
                if row_idx % 2 == 1:
                    set_cell_shading(row_cells[col_idx], 'F9FAFB')

    doc.add_paragraph()

def convert_md_to_docx(md_path, docx_path):
    """Convert markdown file to Word document"""

    # Read markdown
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Create document
    doc = Document()

    # Set up styles
    style = doc.styles['Normal']
    style.font.name = 'Calibri'
    style.font.size = Pt(11)

    # Process content
    lines = content.split('\n')
    i = 0
    in_code_block = False
    code_lines = []

    while i < len(lines):
        line = lines[i]

        # Handle code blocks
        if line.strip().startswith('```'):
            if in_code_block:
                # End of code block - add as formatted text
                code_text = '\n'.join(code_lines)
                p = doc.add_paragraph()
                p.paragraph_format.left_indent = Inches(0.25)
                run = p.add_run(code_text)
                run.font.name = 'Consolas'
                run.font.size = Pt(9)
                code_lines = []
                in_code_block = False
            else:
                in_code_block = True
            i += 1
            continue

        if in_code_block:
            code_lines.append(line)
            i += 1
            continue

        # Handle tables
        if line.strip().startswith('|') and i + 1 < len(lines) and lines[i + 1].strip().startswith('|'):
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                table_lines.append(lines[i])
                i += 1
            add_table_from_lines(doc, table_lines)
            continue

        # Handle headers
        if line.startswith('# '):
            p = doc.add_heading(line[2:].strip(), level=0)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        elif line.startswith('## '):
            doc.add_heading(line[3:].strip(), level=1)
        elif line.startswith('### '):
            doc.add_heading(line[4:].strip(), level=2)
        elif line.startswith('**') and line.endswith('**'):
            # Bold paragraph
            p = doc.add_paragraph()
            run = p.add_run(line.replace('**', ''))
            run.bold = True
        elif line.startswith('- '):
            # Bullet point
            p = doc.add_paragraph(line[2:].replace('**', ''), style='List Bullet')
        elif line.startswith('> '):
            # Blockquote
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Inches(0.5)
            run = p.add_run(line[2:].replace('**', ''))
            run.italic = True
        elif line.startswith('---'):
            # Horizontal rule - add page break
            doc.add_page_break()
        elif line.strip() == '':
            # Empty line
            pass
        else:
            # Regular paragraph
            clean_line = line.replace('**', '').replace('*', '')
            if clean_line.strip():
                doc.add_paragraph(clean_line)

        i += 1

    # Save document
    doc.save(docx_path)
    print(f"[OK] Created: {docx_path}")

if __name__ == '__main__':
    md_path = Path(__file__).parent / "marketing-brief-isagawa.md"
    docx_path = Path(__file__).parent / "Isagawa-Marketing-Brief.docx"
    convert_md_to_docx(md_path, docx_path)
