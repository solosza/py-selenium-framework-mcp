"""
Experiment with document loader.

Run this script to:
1. Load your real documents
2. See what metadata is extracted
3. Modify and observe changes

Usage:
    cd training-assistant
    python experiment_loader.py

Experiments to try:
- Change SOURCES to load different files
- Add a new file type to SUPPORTED_EXTENSIONS in loader.py
- Modify metadata extraction for .py files
- Try loading a file with encoding issues
"""

import sys
from pathlib import Path

# Add rag to path
sys.path.insert(0, str(Path(__file__).parent))

from rag.ingestion import load_file, load_documents, get_loader_stats


# ============================================================
# EXPERIMENT 1: Load a single file
# ============================================================
print("=" * 60)
print("EXPERIMENT 1: Load a single file")
print("=" * 60)

single_file = Path("D:/my_ai_projects/py_sel_framework_mcp/FRAMEWORK.md")
if single_file.exists():
    doc = load_file(single_file)
    print(f"\nFile: {doc.metadata['filename']}")
    print(f"Size: {len(doc)} characters")
    print(f"Type: {doc.metadata.get('file_type', 'unknown')}")
    print(f"Title: {doc.metadata.get('title', 'N/A')}")
    print(f"\nFirst 200 chars:")
    print(doc.text[:200])
else:
    print(f"File not found: {single_file}")


# ============================================================
# EXPERIMENT 2: Load from multiple sources
# ============================================================
print("\n" + "=" * 60)
print("EXPERIMENT 2: Load from multiple sources")
print("=" * 60)

SOURCES = [
    # Current project docs
    "D:/my_ai_projects/py_sel_framework_mcp/FRAMEWORK.md",
    "D:/my_ai_projects/py_sel_framework_mcp/CLAUDE.md",
    "D:/my_ai_projects/py_sel_framework_mcp/docs/",

    # Nakupuna production framework (Python files)
    "C:/Users/solos/OneDrive/Documents/nakupuna/v2_04112025/v2/",
]

docs = load_documents(SOURCES)
stats = get_loader_stats(docs)

print(f"\nTotal documents: {stats['total_docs']}")
print(f"Total characters: {stats['total_chars']:,}")
print(f"Estimated tokens: {stats['estimated_tokens']:,}")
print(f"\nBy file type:")
for file_type, count in stats['by_file_type'].items():
    print(f"  {file_type}: {count}")


# ============================================================
# EXPERIMENT 3: Inspect specific documents
# ============================================================
print("\n" + "=" * 60)
print("EXPERIMENT 3: Inspect specific documents")
print("=" * 60)

# Show first 5 documents
print("\nFirst 5 documents loaded:")
for i, doc in enumerate(docs[:5]):
    print(f"\n{i+1}. {doc.metadata['filename']}")
    print(f"   Type: {doc.metadata.get('file_type', 'unknown')}")
    print(f"   Size: {len(doc)} chars")

# Show documents by type
print("\n\nSample Python files:")
py_docs = [d for d in docs if d.metadata.get('file_type') == 'python']
for doc in py_docs[:3]:
    print(f"  - {doc.metadata['module_name']}.py ({len(doc)} chars)")

print("\nSample Markdown files:")
md_docs = [d for d in docs if d.metadata.get('file_type') == 'markdown']
for doc in md_docs[:3]:
    title = doc.metadata.get('title', 'No title')
    print(f"  - {doc.metadata['filename']}: {title}")


# ============================================================
# EXPERIMENT 4: Try your own modifications
# ============================================================
print("\n" + "=" * 60)
print("EXPERIMENT 4: Try your own modifications")
print("=" * 60)

print("""
Things to try:

1. Add a source path and re-run:
   SOURCES.append("path/to/your/docs")

2. Modify loader.py to extract more metadata:
   - For .py files: extract class names, function names
   - For .md files: extract all headings

3. Add support for a new file type:
   - Add ".json" to SUPPORTED_EXTENSIONS
   - Add metadata extraction in load_file()

4. Test edge cases:
   - Empty file
   - Very large file
   - File with non-UTF8 encoding

Modify this script and run again!
""")
