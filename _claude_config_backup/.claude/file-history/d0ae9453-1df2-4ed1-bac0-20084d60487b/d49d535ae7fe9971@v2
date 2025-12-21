"""
Document: The common data structure passed through all RAG layers.

Framework analogy:
    WebInterface is passed through Pages → Tasks → Roles
    Document is passed through Loader → Chunker → Embedder → VectorStore

Every layer knows how to work with Document.
"""

from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass
class Document:
    """
    Represents a piece of text with its metadata.

    Attributes:
        text: The actual content (markdown, code, etc.)
        metadata: Source info for citations and filtering

    Why dataclass?
        - Clean, readable (like your Page Object pattern)
        - Immutable-ish (discourages mutation)
        - Same pattern LangChain/LlamaIndex use (easy migration later)

    Why metadata as dict?
        - Flexible: markdown has 'title', Python has 'module_name'
        - Extensible: add fields without changing the class
    """
    text: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __len__(self) -> int:
        """Return character count of text."""
        return len(self.text)

    def __repr__(self) -> str:
        """Short representation for debugging."""
        source = self.metadata.get("source", "unknown")
        preview = self.text[:50].replace("\n", " ")
        return f"Document(source='{source}', len={len(self)}, preview='{preview}...')"
