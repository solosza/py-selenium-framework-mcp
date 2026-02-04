"""
Lesson 3: Chunk Boundaries & File Types

Experiments showing how fixed-size chunking cuts text and
how this affects different content types.
"""

import sys
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from rag.ingestion.document import Document
from rag.ingestion.chunker import chunk_document


def experiment_1_sentence_splitting():
    """
    Experiment 1: Watch how sentences get split

    Key Question: Does fixed-size respect sentence boundaries?
    """
    print("\n" + "=" * 60)
    print("EXPERIMENT 1: Sentence Splitting")
    print("=" * 60)

    # Text with clear sentences
    text = (
        "The quick brown fox jumps over the lazy dog. "
        "This is the second sentence in the paragraph. "
        "The third sentence adds more context to the document. "
        "Finally, the fourth sentence concludes the thought."
    )

    print(f"\nOriginal text ({len(text)} chars):")
    print(f'"{text}"')

    # Small chunk size to force splits
    doc = Document(text=text, metadata={"source": "test"})
    chunks = chunk_document(doc, chunk_size=60, overlap=10)

    print(f"\nChunked with size=60, overlap=10:")
    print("-" * 40)

    for i, chunk in enumerate(chunks):
        # Check if chunk ends mid-sentence
        ends_cleanly = chunk.text.rstrip().endswith(('.', '!', '?'))
        status = "OK" if ends_cleanly else "SPLIT!"

        print(f"\nChunk {i}: [{status}]")
        print(f'  "{chunk.text}"')
        print(f"  Start: {chunk.metadata['start_char']}, End: {chunk.metadata['end_char']}")

    # Count clean vs split boundaries
    clean = sum(1 for c in chunks if c.text.rstrip().endswith(('.', '!', '?')))
    split = len(chunks) - clean

    print(f"\n>> Result: {clean} clean endings, {split} mid-sentence cuts")
    print(">> Fixed-size chunking does NOT respect sentences")


def experiment_2_code_vs_prose():
    """
    Experiment 2: Compare chunking code vs prose

    Key Question: Does file type matter for chunking?
    """
    print("\n" + "=" * 60)
    print("EXPERIMENT 2: Code vs Prose")
    print("=" * 60)

    # Python code with logical structure
    code_text = '''def login(self, email: str, password: str):
    """Login a user with credentials."""
    self.enter_email(email)
    self.enter_password(password)
    self.click_submit()

def logout(self):
    """Logout the current user."""
    self.click_logout_button()
    self.wait_for_login_page()
'''

    # Equivalent prose description
    prose_text = '''The login function accepts an email and password parameter.
It enters the email into the email field. Then it enters the password
into the password field. Finally it clicks the submit button.

The logout function ends the user session. It clicks the logout button
and waits for the login page to appear.'''

    print("\n--- CODE ---")
    print(code_text)
    print("\n--- PROSE ---")
    print(prose_text)

    # Chunk both with same settings
    code_doc = Document(text=code_text, metadata={"source": "code.py"})
    prose_doc = Document(text=prose_text, metadata={"source": "docs.md"})

    code_chunks = chunk_document(code_doc, chunk_size=150, overlap=20)
    prose_chunks = chunk_document(prose_doc, chunk_size=150, overlap=20)

    print(f"\nChunk size=150, overlap=20")
    print("-" * 40)

    print(f"\nCODE chunks ({len(code_chunks)}):")
    for i, chunk in enumerate(code_chunks):
        # Check if cut mid-function
        has_def = "def " in chunk.text
        has_complete_def = chunk.text.count("def ") == chunk.text.count('"""')
        print(f"  Chunk {i}: {len(chunk)} chars")
        print(f'    "{chunk.text[:50]}..."')
        if has_def and not has_complete_def:
            print("    WARNING: May have incomplete function!")

    print(f"\nPROSE chunks ({len(prose_chunks)}):")
    for i, chunk in enumerate(prose_chunks):
        print(f"  Chunk {i}: {len(chunk)} chars")
        print(f'    "{chunk.text[:50]}..."')

    print("\n>> Observation: Same chunk_size produces similar # chunks")
    print(">> But CODE cuts may split functions, PROSE cuts may split sentences")
    print(">> Content-aware chunking would preserve these structures")


def experiment_3_boundary_inspection():
    """
    Experiment 3: Look at exactly what gets cut

    Key Question: What characters appear at boundaries?
    """
    print("\n" + "=" * 60)
    print("EXPERIMENT 3: Boundary Inspection")
    print("=" * 60)

    # Mix of content with clear structure
    text = """# Header One

This is the first paragraph with some content that explains things.

## Header Two

This is the second paragraph. It continues the explanation.

```python
def example():
    return "code block"
```

Final paragraph here."""

    doc = Document(text=text, metadata={"source": "mixed.md"})
    chunks = chunk_document(doc, chunk_size=80, overlap=15)

    print(f"\nOriginal ({len(text)} chars):")
    print(text)
    print(f"\nChunked with size=80, overlap=15:")
    print("-" * 40)

    for i, chunk in enumerate(chunks):
        start = chunk.metadata['start_char']
        end = chunk.metadata['end_char']

        # Show boundary characters
        first_5 = repr(chunk.text[:5])
        last_5 = repr(chunk.text[-5:])

        print(f"\nChunk {i}:")
        print(f"  Starts with: {first_5}")
        print(f"  Ends with: {last_5}")

        # Detect what was cut
        if '\\n' in last_5:
            print("  >> Ends at line break (good)")
        elif ' ' in last_5:
            print("  >> Ends mid-word or sentence (BAD)")
        else:
            print("  >> Ends at unknown boundary")

    print("\n>> Fixed-size doesn't detect headers, code blocks, or paragraphs")
    print(">> Semantic chunking would preserve these structures")


def experiment_4_overlap_rescue():
    """
    Experiment 4: Does overlap help with bad cuts?

    Key Question: Can overlap compensate for hard boundaries?
    """
    print("\n" + "=" * 60)
    print("EXPERIMENT 4: Overlap as Rescue")
    print("=" * 60)

    # A sentence that will get split
    text = "The framework uses a 4-layer architecture: Tests, Roles, Tasks, and Pages."

    print(f"\nOriginal ({len(text)} chars):")
    print(f'"{text}"')

    doc = Document(text=text, metadata={"source": "test"})

    # Without overlap
    chunks_no_overlap = chunk_document(doc, chunk_size=40, overlap=0)
    # With overlap
    chunks_with_overlap = chunk_document(doc, chunk_size=40, overlap=15)

    print("\n--- NO OVERLAP (size=40, overlap=0) ---")
    for i, c in enumerate(chunks_no_overlap):
        print(f"  Chunk {i}: \"{c.text}\"")

    print("\n--- WITH OVERLAP (size=40, overlap=15) ---")
    for i, c in enumerate(chunks_with_overlap):
        print(f"  Chunk {i}: \"{c.text}\"")

    # Check if key term is preserved
    key_term = "4-layer architecture"

    no_overlap_has_term = any(key_term in c.text for c in chunks_no_overlap)
    with_overlap_has_term = any(key_term in c.text for c in chunks_with_overlap)

    print(f"\nKey term '{key_term}' preserved?")
    print(f"  No overlap: {no_overlap_has_term}")
    print(f"  With overlap: {with_overlap_has_term}")

    print("\n>> Overlap helps recover context at boundaries")
    print(">> But it's a patch, not a solution - still cuts mid-sentence")


def main():
    """Run all boundary experiments."""
    print("\n" + "=" * 60)
    print("LESSON 3: CHUNK BOUNDARIES & FILE TYPES")
    print("=" * 60)

    experiment_1_sentence_splitting()
    experiment_2_code_vs_prose()
    experiment_3_boundary_inspection()
    experiment_4_overlap_rescue()

    print("\n" + "=" * 60)
    print("KEY TAKEAWAYS")
    print("=" * 60)
    print("""
1. Fixed-size uses HARD boundaries (character position)
   - Cuts sentences, words, code blocks indiscriminately

2. File type affects what gets broken
   - Prose: sentences, paragraphs
   - Code: functions, classes, imports

3. Overlap PARTIALLY rescues bad cuts
   - Provides context at boundaries
   - Does NOT prevent the cut itself

4. When to use fixed-size despite limitations:
   - Learning/prototyping (simple to understand)
   - Homogeneous content (similar throughout)
   - When semantic chunking is overkill

5. When to upgrade to semantic/recursive:
   - Code repositories (preserve functions)
   - Technical docs (preserve sections)
   - When retrieval quality suffers
""")


if __name__ == "__main__":
    main()
