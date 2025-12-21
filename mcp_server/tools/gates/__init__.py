"""Quality Gates module for QA Execution Engine."""

from .base_gate import BaseGate
from .test_structure_validator import TestStructureValidator

__all__ = ["BaseGate", "TestStructureValidator"]
