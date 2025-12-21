"""
Document Loader: Reads files from disk into Document objects.

Framework analogy:
    LoginPage.enter_email() - atomic action on one element
    AuthTasks.log_in() - combines multiple page actions

    load_file() - atomic, loads one file
    load_documents() - combines multiple load_file() calls

Separation of concerns:
    Loader ONLY reads files. It doesn't chunk, embed, or store.
    Just like Pages ONLY interact with UI. They don't orchestrate workflows.
"""

from pathlib import Path
from typing import List, Union
from ..core.document import Document


# File extensions we know how to load
SUPPORTED_EXTENSIONS = {".md", ".py", ".txt", ".rst"}


def load_file(file_path: Union[str, Path]) -> Document:
    """
    Load a single file into a Document.

    Args:
        file_path: Path to the file

    Returns:
        Document with text and metadata

    Framework analogy:
        Like a Page Object method - atomic, does one thing.
        enter_email(text) -> types into one field
        load_file(path) -> reads one file
    """
    path = Path(file_path)

    # Read the file
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        # Fallback for files with different encoding
        text = path.read_text(encoding="latin-1")

    # Build metadata (you'll use this for citations later)
    metadata = {
        "source": str(path.absolute()),
        "filename": path.name,
        "extension": path.suffix,
        "size_bytes": path.stat().st_size,
    }

    # Add file-type specific metadata
    if path.suffix == ".py":
        metadata["file_type"] = "python"
        metadata["module_name"] = path.stem
    elif path.suffix == ".md":
        metadata["file_type"] = "markdown"
        # Extract title from first heading if present
        first_line = text.split("\n")[0].strip()
        if first_line.startswith("# "):
            metadata["title"] = first_line[2:]

    return Document(text=text, metadata=metadata)


def load_documents(sources: List[Union[str, Path]]) -> List[Document]:
    """
    Load documents from multiple files or directories.

    Args:
        sources: List of file paths or directory paths
                 Directories are walked recursively

    Returns:
        List of Documents

    Framework analogy:
        Like a Task method - orchestrates multiple atomic actions.
        log_in() calls enter_email(), enter_password(), click_submit()
        load_documents() calls load_file() for each file found
    """
    documents = []
    seen_paths = set()  # Avoid duplicates

    for source in sources:
        path = Path(source)

        if path.is_file():
            # Single file
            if path.suffix in SUPPORTED_EXTENSIONS:
                if str(path.absolute()) not in seen_paths:
                    documents.append(load_file(path))
                    seen_paths.add(str(path.absolute()))

        elif path.is_dir():
            # Directory - walk recursively
            for ext in SUPPORTED_EXTENSIONS:
                for file_path in path.rglob(f"*{ext}"):
                    # Skip __pycache__, .git, etc.
                    if "__pycache__" in str(file_path):
                        continue
                    if ".git" in str(file_path):
                        continue

                    if str(file_path.absolute()) not in seen_paths:
                        documents.append(load_file(file_path))
                        seen_paths.add(str(file_path.absolute()))

    return documents


def get_loader_stats(documents: List[Document]) -> dict:
    """
    Get statistics about loaded documents.

    Useful for verifying the loader worked as expected.
    """
    if not documents:
        return {"total_docs": 0}

    total_chars = sum(len(doc) for doc in documents)
    by_type = {}
    for doc in documents:
        file_type = doc.metadata.get("file_type", "unknown")
        by_type[file_type] = by_type.get(file_type, 0) + 1

    return {
        "total_docs": len(documents),
        "total_chars": total_chars,
        "estimated_tokens": total_chars // 4,  # Rough estimate
        "by_file_type": by_type,
    }
