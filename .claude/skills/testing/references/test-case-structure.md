<!-- LICENSE: Proprietary - Isagawa Corp -->
<!-- You may USE this skill with Claude Code. -->
<!-- You may NOT redistribute, modify, or create derivative works. -->
<!-- See LICENSE.md for full terms. -->

# Test Case Structure

How to write individual test cases. Applies to all test files.

## AAA Pattern (Mandatory)

Every test follows **Arrange-Act-Assert**:

```python
def test_example(self):
    """
    Test description.

    AAA Pattern:
    1. Arrange - Setup test data and dependencies
    2. Act - Execute the code under test
    3. Assert - Verify the expected outcome
    """
    # Arrange
    input_data = create_test_data()
    expected = "expected result"

    # Act
    result = function_under_test(input_data)

    # Assert
    assert result == expected, "Descriptive error message"
```

**Rules:**
| Rule | Description |
|------|-------------|
| Comments required | `# Arrange`, `# Act`, `# Assert` on separate lines |
| Single Act | Only ONE action per test |
| Descriptive assertion | Include message explaining what failed |
| Docstring explains AAA | Document what each section does |

## Test Class Structure

```python
class TestComponentName:
    """
    Test suite for [Component].

    Tests organized by: [data structure / functionality / layer]
    """

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup shared test dependencies."""
        self.component = Component()
        # Other shared setup

    # ==================== TEST METHODS ====================

    def test_specific_behavior(self):
        """P0: Description of what this tests."""
        # Arrange
        ...
        # Act
        ...
        # Assert
        ...
```

## Pytest Markers

Apply markers for test filtering:

```python
@pytest.mark.unit           # Fast, isolated test
@pytest.mark.integration    # Tests multiple components
@pytest.mark.slow           # Takes > 1 second
@pytest.mark.smoke          # Critical path test

# Component markers (domain-specific)
@pytest.mark.loader         # Loader component
@pytest.mark.chunker        # Chunker component
@pytest.mark.embedder       # Embedder component
```

**Usage:**
```bash
pytest -m "unit"                    # Only unit tests
pytest -m "not slow"                # Skip slow tests
pytest -m "loader or chunker"       # Specific components
pytest -m "smoke"                   # Critical paths only
```

## Fixtures

### When to Use Fixtures

| Scenario | Fixture Type |
|----------|--------------|
| Shared setup within class | `@pytest.fixture(autouse=True)` on `setup()` |
| Expensive initialization | Session-scoped in `conftest.py` |
| Temp files | Built-in `tmp_path` fixture |
| Parametrized data | `@pytest.fixture(params=[...])` |

### Class-Level Setup (autouse)

```python
class TestMyComponent:
    @pytest.fixture(autouse=True)
    def setup(self):
        """Runs before each test in this class."""
        self.component = MyComponent()
        self.test_data = {"key": "value"}
```

### Session-Scoped (Expensive Resources)

In `conftest.py`:
```python
@pytest.fixture(scope="session")
def embedder():
    """Shared embedder - model loads once for all tests."""
    return Embedder()
```

### Temp Files

```python
def test_load_file(self, tmp_path):
    # Arrange
    test_file = tmp_path / "test.md"
    test_file.write_text("# Test content")

    # Act
    result = load_file(test_file)

    # Assert
    assert result.text == "# Test content"
```

## Docstrings

### Test Method Docstring

```python
def test_synonyms_have_high_similarity(self):
    """
    P0: Verify synonyms produce similar embeddings.

    AAA Pattern:
    1. Arrange - Define synonym pairs
    2. Act - Embed both and compute similarity
    3. Assert - Similarity > 0.5
    """
```

**Components:**
| Component | Purpose |
|-----------|---------|
| `P0:` / `P1:` / `P2:` | Priority indicator |
| First line | What the test verifies |
| AAA section | Documents test structure |

### Test Class Docstring

```python
class TestSemanticCorrectness:
    """
    Tests for semantic meaning preservation.

    Verifies that:
    - Same text = similarity ~1.0
    - Synonyms = high similarity
    - Unrelated = low similarity
    """
```

## Assertion Messages

Always include descriptive messages:

```python
# Bad
assert result == expected

# Good
assert result == expected, f"Expected {expected}, got {result}"

# Better (context)
assert page.is_loaded(), "Product page should load after clicking category"
```

## Priority Indicators

| Priority | Meaning | When to Use |
|----------|---------|-------------|
| P0 | Must pass | Core functionality |
| P1 | Should pass | Important but not critical |
| P2 | Nice to have | Edge cases, polish |

## Anti-Patterns

| Wrong | Right |
|-------|-------|
| No AAA comments | Always include `# Arrange`, `# Act`, `# Assert` |
| Multiple actions in Act | One action per test |
| No assertion message | Include descriptive message |
| Setup in each test | Use `@pytest.fixture(autouse=True)` |
| Missing markers | Add component + type markers |
| Generic docstring | Document AAA and purpose |

## Example: Complete Test

```python
import pytest
from rag.ingestion import Embedder, cosine_similarity


class TestSemanticCorrectness:
    """
    Tests for semantic meaning preservation in embeddings.

    Pyramid Layer: SEMANTIC CORRECTNESS
    Verifies embeddings capture meaning, not just string matching.
    """

    @pytest.fixture(autouse=True)
    def setup(self, embedder):
        """Setup with shared embedder instance."""
        self.embedder = embedder

    # ==================== TEST METHODS ====================

    @pytest.mark.embedder
    @pytest.mark.unit
    def test_synonyms_have_high_similarity(self):
        """
        P0: Synonyms should produce similar embeddings.

        AAA Pattern:
        1. Arrange - Define synonym pair (login, sign in)
        2. Act - Embed both and compute similarity
        3. Assert - Similarity > 0.5
        """
        # Arrange
        text1, text2 = "login", "sign in"

        # Act
        vec1 = self.embedder.embed_text(text1)
        vec2 = self.embedder.embed_text(text2)
        similarity = cosine_similarity(vec1, vec2)

        # Assert
        assert similarity > 0.5, f"Synonyms should be similar, got {similarity:.3f}"
```
