"""
Knowledge Base - Task 4.0

Single Responsibility: "Read/write patterns from KB file"

Manages the knowledge base (KNOWLEDGE_BASE.md) for:
- Finding patterns that match error categories
- Saving new patterns discovered during runtime validation

Design Notes:
- Parses structured "Runtime Validation Patterns" section
- Returns Optional[Pattern] - None means "no known fix" (caller decides what to do)
- Does NOT suggest fixes (that's FixSuggester)
- Does NOT apply fixes (that's AI orchestration)

PRD Reference: enhanced-runtime-validation
"""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class Pattern:
    """
    A pattern from the knowledge base.

    Attributes:
        error_category: Error category this pattern addresses
            (e.g., LOCATOR_NOT_FOUND, NOT_VISIBLE, NOT_INTERACTABLE)
        context_match: Context conditions for this pattern to apply
            (e.g., {"element_type": "button", "symptom": "intercepts pointer"})
        fix: Description of the fix to apply
        confidence: How confident we are in this fix (0.0-1.0)
        source: Where this pattern came from (e.g., "kb_file", "user_provided")
    """
    error_category: str
    context_match: Dict[str, Any]
    fix: str
    confidence: float = 0.8
    source: str = "kb_file"

    def matches_context(self, context: Dict[str, Any]) -> bool:
        """
        Check if this pattern matches the given context.

        Matching rules:
        - Empty context_match matches everything
        - Each key in context_match must exist in context
        - Values must match (case-insensitive for strings)
        """
        if not self.context_match:
            return True

        for key, expected in self.context_match.items():
            actual = context.get(key)
            if actual is None:
                return False

            # Case-insensitive string comparison
            if isinstance(expected, str) and isinstance(actual, str):
                if expected.lower() not in actual.lower():
                    return False
            elif actual != expected:
                return False

        return True


@dataclass
class KnowledgeBase:
    """
    Manages the knowledge base for runtime validation patterns.

    Single Responsibility: Read/write patterns from KB file.

    Usage:
        kb = KnowledgeBase("docs/KNOWLEDGE_BASE.md")
        pattern = kb.find_pattern("NOT_INTERACTABLE", {"symptom": "pointer events"})
        if pattern:
            print(f"Try: {pattern.fix}")
        else:
            print("No known fix")
    """
    kb_path: str
    _patterns: List[Pattern] = field(default_factory=list, repr=False)
    _loaded: bool = field(default=False, repr=False)

    def __post_init__(self):
        """Load patterns on initialization."""
        self._load_patterns()

    def find_pattern(
        self,
        error_category: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[Pattern]:
        """
        Find a pattern matching the error category and context.

        Args:
            error_category: Error category to match (e.g., "NOT_INTERACTABLE")
            context: Additional context for matching (optional)
                If None or empty, returns best match by category only.
                If provided, filters to patterns matching context.

        Returns:
            Pattern if found, None otherwise (caller decides what to do)
        """
        best_match: Optional[Pattern] = None
        best_confidence = 0.0

        for pattern in self._patterns:
            # Must match error category
            if pattern.error_category.upper() != error_category.upper():
                continue

            # If context provided, must match context
            # If no context provided, match any pattern of this category
            if context and not pattern.matches_context(context):
                continue

            # Track highest confidence match
            if pattern.confidence > best_confidence:
                best_match = pattern
                best_confidence = pattern.confidence

        return best_match

    def find_all_patterns(
        self,
        error_category: str,
        context: Optional[Dict[str, Any]] = None
    ) -> List[Pattern]:
        """
        Find all patterns matching the error category and context.

        Args:
            error_category: Error category to match
            context: Additional context for matching
                If None or empty, returns all patterns for category.
                If provided, filters to patterns matching context.

        Returns:
            List of matching patterns, sorted by confidence (highest first)
        """
        matches = []

        for pattern in self._patterns:
            if pattern.error_category.upper() != error_category.upper():
                continue
            # If context provided, must match
            if context and not pattern.matches_context(context):
                continue
            matches.append(pattern)

        # Sort by confidence descending
        matches.sort(key=lambda p: p.confidence, reverse=True)
        return matches

    def save_pattern(self, pattern: Pattern) -> None:
        """
        Save a new pattern to the knowledge base.

        Args:
            pattern: Pattern to save

        Side effects:
            - Adds pattern to in-memory list
            - Appends pattern to KB file in structured format
        """
        # Add to in-memory list
        self._patterns.append(pattern)

        # Append to file
        self._append_pattern_to_file(pattern)

    def get_all_patterns(self) -> List[Pattern]:
        """Return all patterns in the knowledge base."""
        return list(self._patterns)

    def get_patterns_by_category(self, error_category: str) -> List[Pattern]:
        """Return all patterns for a specific error category."""
        return [
            p for p in self._patterns
            if p.error_category.upper() == error_category.upper()
        ]

    def reload(self) -> None:
        """Reload patterns from the KB file."""
        self._patterns = []
        self._loaded = False
        self._load_patterns()

    # =========================================================================
    # PRIVATE METHODS
    # =========================================================================

    def _load_patterns(self) -> None:
        """Load patterns from the KB file."""
        if self._loaded:
            return

        kb_path = Path(self.kb_path)
        if not kb_path.exists():
            self._loaded = True
            return

        content = kb_path.read_text(encoding="utf-8")

        # Parse structured patterns section
        self._parse_structured_patterns(content)

        # Parse legacy patterns (best effort)
        self._parse_legacy_patterns(content)

        self._loaded = True

    def _parse_structured_patterns(self, content: str) -> None:
        """
        Parse structured patterns from "Runtime Validation Patterns" section.

        Expected format:
        ```
        ## Runtime Validation Patterns

        ### PATTERN: [error_category] - [brief description]

        **Context:** key1=value1, key2=value2
        **Fix:** Description of the fix
        **Confidence:** 0.9
        ```
        """
        # Find Runtime Validation Patterns section
        section_pattern = r"## Runtime Validation Patterns\s*\n(.*?)(?=\n## |\Z)"
        match = re.search(section_pattern, content, re.DOTALL)
        if not match:
            return

        section_content = match.group(1)

        # Find individual patterns - more flexible regex that handles blank lines
        # Split by pattern headers first
        pattern_blocks = re.split(r"### PATTERN:\s*", section_content)

        for block in pattern_blocks[1:]:  # Skip first empty split
            if not block.strip():
                continue

            # Parse error category and description from first line
            first_line_match = re.match(r"(\w+)\s*-\s*([^\n]+)", block)
            if not first_line_match:
                continue

            error_category = first_line_match.group(1).strip()

            # Parse Context
            context_match_obj = re.search(r"\*\*Context:\*\*\s*([^\n]*)", block)
            context_str = context_match_obj.group(1).strip() if context_match_obj else ""

            # Parse Fix
            fix_match = re.search(r"\*\*Fix:\*\*\s*([^\n]+)", block)
            fix = fix_match.group(1).strip() if fix_match else ""

            # Parse Confidence
            confidence_match = re.search(r"\*\*Confidence:\*\*\s*([\d.]+)", block)
            confidence_str = confidence_match.group(1).strip() if confidence_match else "0.8"

            if not fix:
                continue  # Skip patterns without fix

            # Parse context
            context_match = self._parse_context_string(context_str)

            # Parse confidence
            try:
                confidence = float(confidence_str)
            except ValueError:
                confidence = 0.8

            pattern = Pattern(
                error_category=error_category,
                context_match=context_match,
                fix=fix,
                confidence=confidence,
                source="kb_file"
            )
            self._patterns.append(pattern)

    def _parse_legacy_patterns(self, content: str) -> None:
        """
        Parse legacy patterns from "Specific Patterns" section.

        Extracts patterns like "Pointer Events Interception" and maps
        them to error categories.
        """
        # Map known legacy patterns to error categories
        legacy_mappings = [
            {
                "search": r"### Pointer Events Interception",
                "error_category": "NOT_INTERACTABLE",
                "context_match": {"symptom": "intercepts pointer events"},
                "fix": "Use JavaScript click (click_js) to bypass CSS pointer events interception",
                "confidence": 0.9
            },
            {
                "search": r"timing issue.*element not ready",
                "error_category": "LOCATOR_NOT_FOUND",
                "context_match": {"symptom": "timing"},
                "fix": "Add explicit wait for element visibility before interaction",
                "confidence": 0.7
            }
        ]

        for mapping in legacy_mappings:
            if re.search(mapping["search"], content, re.IGNORECASE):
                # Check if we already have this pattern
                existing = self.find_pattern(
                    mapping["error_category"],
                    mapping["context_match"]
                )
                if existing is None:
                    pattern = Pattern(
                        error_category=mapping["error_category"],
                        context_match=mapping["context_match"],
                        fix=mapping["fix"],
                        confidence=mapping["confidence"],
                        source="legacy_kb"
                    )
                    self._patterns.append(pattern)

    def _parse_context_string(self, context_str: str) -> Dict[str, Any]:
        """
        Parse context string like "key1=value1, key2=value2" into dict.
        """
        if not context_str or context_str.lower() in ("none", "any", ""):
            return {}

        context = {}
        pairs = context_str.split(",")
        for pair in pairs:
            if "=" in pair:
                key, value = pair.split("=", 1)
                context[key.strip()] = value.strip()

        return context

    def _append_pattern_to_file(self, pattern: Pattern) -> None:
        """
        Append a pattern to the KB file in structured format.
        """
        kb_path = Path(self.kb_path)

        # Read existing content
        if kb_path.exists():
            content = kb_path.read_text(encoding="utf-8")
        else:
            content = "# Knowledge Base\n\n"

        # Check if Runtime Validation Patterns section exists
        if "## Runtime Validation Patterns" not in content:
            # Add section before "Adding New Patterns" or at end
            insert_marker = "## Adding New Patterns"
            if insert_marker in content:
                content = content.replace(
                    insert_marker,
                    "## Runtime Validation Patterns\n\n" + insert_marker
                )
            else:
                content = content.rstrip() + "\n\n## Runtime Validation Patterns\n\n"

        # Format the pattern
        context_str = ", ".join(
            f"{k}={v}" for k, v in pattern.context_match.items()
        ) if pattern.context_match else "any"

        pattern_text = f"""
### PATTERN: {pattern.error_category} - Auto-generated

**Context:** {context_str}
**Fix:** {pattern.fix}
**Confidence:** {pattern.confidence}

---
"""

        # Insert pattern into Runtime Validation Patterns section
        section_end_pattern = r"(## Runtime Validation Patterns\s*\n)"
        if re.search(section_end_pattern, content):
            # Find where to insert (after section header)
            match = re.search(section_end_pattern, content)
            if match:
                insert_pos = match.end()
                content = content[:insert_pos] + pattern_text + content[insert_pos:]
        else:
            # Append at end
            content = content.rstrip() + "\n" + pattern_text

        # Write back
        kb_path.write_text(content, encoding="utf-8")


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def load_knowledge_base(kb_path: Optional[str] = None) -> KnowledgeBase:
    """
    Load the knowledge base from the default or specified path.

    Args:
        kb_path: Path to KB file (default: docs/KNOWLEDGE_BASE.md)

    Returns:
        KnowledgeBase instance
    """
    if kb_path is None:
        # Default path relative to project root
        kb_path = "docs/KNOWLEDGE_BASE.md"

    return KnowledgeBase(kb_path=kb_path)


def find_pattern_for_error(
    error_category: str,
    context: Optional[Dict[str, Any]] = None,
    kb_path: Optional[str] = None
) -> Optional[Pattern]:
    """
    Convenience function to find a pattern for an error.

    Args:
        error_category: Error category to match
        context: Additional context for matching
        kb_path: Path to KB file (optional)

    Returns:
        Pattern if found, None otherwise
    """
    kb = load_knowledge_base(kb_path)
    return kb.find_pattern(error_category, context)
