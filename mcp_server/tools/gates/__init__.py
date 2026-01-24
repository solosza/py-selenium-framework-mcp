"""Quality Gates module for QA Management Engine.

ACTIVE GATES (4-Step Pair Programming Workflow v3.1):
- QGUserInput (Step 1) - User input validation
- QGPreflight (Step 2) - Pre-flight configuration validation
- QGAIProcessing (Step 3) - AI processing validation
- QGDiscoveredElements (Step 4) - Discovered elements validation
- QGDiscoveryComplete (Step 4) - Discovery completion checkpoint

ARCHIVED GATES (moved to _archived/autonomous_workflow_v1/gates/):
- 2026-01-22: QGPageObject, QGTask, QGRole, QGTestRunner, QGSaveRun, QGExecution, QGWorkflowComplete
- 2026-01-23: QGTestScenarios (redundant Tool 1)
"""

from .base_gate import BaseGate
from .test_structure_validator import TestStructureValidator
from .qg_preflight import QGPreflight
from .qg_user_input import QGUserInput
from .qg_ai_processing import QGAIProcessing
from .qg_discovered_elements import QGDiscoveredElements
from .qg_discovery_complete import QGDiscoveryComplete

__all__ = [
    "BaseGate",
    "TestStructureValidator",
    "QGPreflight",
    "QGUserInput",
    "QGAIProcessing",
    "QGDiscoveredElements",
    "QGDiscoveryComplete",
]
