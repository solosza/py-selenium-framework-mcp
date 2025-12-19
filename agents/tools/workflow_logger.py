"""
Visual Workflow Logger

Provides real-time visual feedback during QA validation workflow.
Shows step-by-step progress, agent handoffs, and failure points.

Design Decisions:
- DD-VA-24: Visual workflow logging required for validation runs
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime


# =============================================================================
# Constants
# =============================================================================

class StepStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


class AgentType(str, Enum):
    SUPERVISOR = "SUPERVISOR"
    SQA_AGENT = "SQA_AGENT"
    AI_ORCHESTRATOR = "AI_ORCHESTRATOR"
    REVIEWER = "REVIEWER"


# Status icons for visual display (ASCII-compatible for Windows)
STATUS_ICONS = {
    StepStatus.PENDING: "[..]",
    StepStatus.RUNNING: "[>>]",
    StepStatus.SUCCESS: "[OK]",
    StepStatus.FAILED: "[XX]",
    StepStatus.SKIPPED: "[--]",
}


def _truncate(text: str, max_len: int) -> str:
    """Truncate text with ellipsis if too long."""
    if len(text) <= max_len:
        return text
    return text[:max_len-3] + "..."


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class ToolMetadata:
    """Metadata passed between MCP tools (DD-03: metadata context)."""
    tool_name: str
    input_data: Dict[str, Any] = field(default_factory=dict)
    output_data: Dict[str, Any] = field(default_factory=dict)
    passed_to: Optional[str] = None  # Which tool receives this output


@dataclass
class SubStep:
    """A sub-step within a main workflow step."""
    name: str
    status: StepStatus = StepStatus.PENDING
    message: Optional[str] = None
    timestamp: Optional[str] = None
    # Enhanced: MCP tool details for AI Orchestrator steps
    tool_metadata: Optional[ToolMetadata] = None


@dataclass
class WorkflowStep:
    """A main step in the workflow."""
    step_number: int
    total_steps: int
    from_agent: AgentType
    to_agent: AgentType
    action: str
    status: StepStatus = StepStatus.PENDING

    # Timing
    started_at: Optional[str] = None
    completed_at: Optional[str] = None

    # Input/Output
    input_summary: Optional[str] = None
    output_summary: Optional[str] = None

    # Sub-steps (e.g., MCP tool calls within AI Orchestrator)
    sub_steps: List[SubStep] = field(default_factory=list)

    # Failure info
    error_message: Optional[str] = None
    error_location: Optional[str] = None


@dataclass
class WorkflowLog:
    """Complete workflow log for a validation run."""
    run_id: str
    scenario_id: str
    scenario_name: str
    started_at: str
    completed_at: Optional[str] = None

    steps: List[WorkflowStep] = field(default_factory=list)

    overall_status: StepStatus = StepStatus.PENDING
    failure_step: Optional[int] = None
    failure_reason: Optional[str] = None


# =============================================================================
# Visual Logger Class
# =============================================================================

class VisualWorkflowLogger:
    """
    Logs and displays workflow progress visually.

    Usage:
        logger = VisualWorkflowLogger("QA-EASY-001", "Create new account")

        with logger.step(1, 5, AgentType.SUPERVISOR, AgentType.SQA_AGENT, "Get scenario"):
            # Do work
            logger.set_input("level='QA-EASY-001'")
            logger.set_output("persona='new user', url='...'")

        logger.print_summary()
    """

    def __init__(self, scenario_id: str, scenario_name: str):
        self.log = WorkflowLog(
            run_id=f"RUN-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            scenario_id=scenario_id,
            scenario_name=scenario_name,
            started_at=datetime.now().isoformat()
        )
        self._current_step: Optional[WorkflowStep] = None
        self._live_output = True  # Print as we go

    # =========================================================================
    # Step Management
    # =========================================================================

    def start_step(
        self,
        step_number: int,
        total_steps: int,
        from_agent: AgentType,
        to_agent: AgentType,
        action: str
    ) -> WorkflowStep:
        """Start a new workflow step."""
        step = WorkflowStep(
            step_number=step_number,
            total_steps=total_steps,
            from_agent=from_agent,
            to_agent=to_agent,
            action=action,
            status=StepStatus.RUNNING,
            started_at=datetime.now().isoformat()
        )
        self._current_step = step
        self.log.steps.append(step)

        if self._live_output:
            self._print_step_start(step)

        return step

    def complete_step(self, success: bool = True, error: Optional[str] = None):
        """Complete the current step."""
        if not self._current_step:
            return

        self._current_step.completed_at = datetime.now().isoformat()

        if success:
            self._current_step.status = StepStatus.SUCCESS
        else:
            self._current_step.status = StepStatus.FAILED
            self._current_step.error_message = error
            self.log.failure_step = self._current_step.step_number
            self.log.failure_reason = error
            self.log.overall_status = StepStatus.FAILED

        if self._live_output:
            self._print_step_complete(self._current_step)

        self._current_step = None

    def skip_step(
        self,
        step_number: int,
        total_steps: int,
        from_agent: AgentType,
        to_agent: AgentType,
        action: str,
        reason: str
    ):
        """Mark a step as skipped."""
        step = WorkflowStep(
            step_number=step_number,
            total_steps=total_steps,
            from_agent=from_agent,
            to_agent=to_agent,
            action=action,
            status=StepStatus.SKIPPED,
            error_message=reason
        )
        self.log.steps.append(step)

        if self._live_output:
            self._print_step_skipped(step)

    # =========================================================================
    # Sub-Step Management (for MCP tools within AI Orchestrator)
    # =========================================================================

    def add_sub_step(self, name: str, status: StepStatus = StepStatus.RUNNING, message: Optional[str] = None):
        """Add a sub-step to the current step."""
        if not self._current_step:
            return

        sub_step = SubStep(
            name=name,
            status=status,
            message=message,
            timestamp=datetime.now().isoformat()
        )
        self._current_step.sub_steps.append(sub_step)

        if self._live_output:
            self._print_sub_step(sub_step)

    def add_mcp_tool_step(
        self,
        step_num: int,
        tool_name: str,
        status: StepStatus = StepStatus.RUNNING,
        input_data: Optional[Dict[str, Any]] = None,
        output_data: Optional[Dict[str, Any]] = None,
        passed_to: Optional[str] = None
    ):
        """
        Add an MCP tool invocation sub-step with metadata tracking.

        This shows the 9-step MCP workflow within AI Orchestrator:
        - Which tool is being called
        - What input it receives
        - What output it produces
        - Where the output goes next (metadata passing)
        """
        if not self._current_step:
            return

        tool_metadata = ToolMetadata(
            tool_name=tool_name,
            input_data=input_data or {},
            output_data=output_data or {},
            passed_to=passed_to
        )

        sub_step = SubStep(
            name=f"Step {step_num}: {tool_name}",
            status=status,
            message=None,
            timestamp=datetime.now().isoformat(),
            tool_metadata=tool_metadata
        )
        self._current_step.sub_steps.append(sub_step)

        if self._live_output:
            self._print_mcp_tool_step(sub_step)

    def update_sub_step(self, name: str, status: StepStatus, message: Optional[str] = None):
        """Update an existing sub-step."""
        if not self._current_step:
            return

        for sub_step in self._current_step.sub_steps:
            if sub_step.name == name:
                sub_step.status = status
                sub_step.message = message or sub_step.message
                sub_step.timestamp = datetime.now().isoformat()

                if self._live_output:
                    self._print_sub_step_update(sub_step)
                break

    # =========================================================================
    # Input/Output Tracking
    # =========================================================================

    def set_input(self, summary: str):
        """Set input summary for current step."""
        if self._current_step:
            self._current_step.input_summary = summary
            if self._live_output:
                print(f"      Input:  {summary}")

    def set_output(self, summary: str):
        """Set output summary for current step."""
        if self._current_step:
            self._current_step.output_summary = summary
            if self._live_output:
                print(f"      Output: {summary}")

    # =========================================================================
    # Finalization
    # =========================================================================

    def complete_workflow(self, success: bool = True):
        """Mark the entire workflow as complete."""
        self.log.completed_at = datetime.now().isoformat()

        if success and self.log.overall_status != StepStatus.FAILED:
            self.log.overall_status = StepStatus.SUCCESS
        elif not success:
            self.log.overall_status = StepStatus.FAILED

    # =========================================================================
    # Visual Output
    # =========================================================================

    def _print_header(self):
        """Print workflow header."""
        print()
        print("=" * 78)
        print(f" QA VALIDATION WORKFLOW".center(78))
        print(f" {self.log.scenario_id}: {self.log.scenario_name}".center(78))
        print(f" Run: {self.log.run_id}".center(78))
        print("=" * 78)
        print()

    def _print_step_start(self, step: WorkflowStep):
        """Print step start."""
        icon = STATUS_ICONS[step.status]
        print(f"+{'-' * 76}+")
        print(f"| [{step.step_number}/{step.total_steps}] {step.from_agent.value} -> {step.to_agent.value}".ljust(68) + f"{icon} RUNNING |")
        print(f"+{'-' * 76}+")
        print(f"| Action: {step.action}".ljust(77) + "|")

    def _print_step_complete(self, step: WorkflowStep):
        """Print step completion."""
        icon = STATUS_ICONS[step.status]
        status_text = step.status.value

        if step.error_message:
            print(f"|".ljust(77) + "|")
            print(f"| ==> ERROR: {step.error_message[:60]}".ljust(77) + "|")

        print(f"+{'-' * 68} {icon} {status_text} +")
        print()

    def _print_step_skipped(self, step: WorkflowStep):
        """Print skipped step."""
        icon = STATUS_ICONS[step.status]
        print(f"+{'-' * 76}+")
        print(f"| [{step.step_number}/{step.total_steps}] {step.from_agent.value} -> {step.to_agent.value}".ljust(68) + f"{icon} SKIPPED |")
        print(f"+{'-' * 76}+")
        print(f"| Action: {step.action}".ljust(77) + "|")
        print(f"| Reason: {step.error_message or 'Previous step failed'}".ljust(77) + "|")
        print(f"+{'-' * 76}+")
        print()

    def _print_sub_step(self, sub_step: SubStep):
        """Print sub-step."""
        icon = STATUS_ICONS[sub_step.status]
        msg = f": {sub_step.message}" if sub_step.message else ""
        print(f"|      {icon} {sub_step.name}{msg}".ljust(77) + "|")

    def _print_sub_step_update(self, sub_step: SubStep):
        """Print sub-step update."""
        icon = STATUS_ICONS[sub_step.status]
        msg = f": {sub_step.message}" if sub_step.message else ""
        print(f"|      {icon} {sub_step.name}{msg}".ljust(77) + "|")

    def _print_mcp_tool_step(self, sub_step: SubStep):
        """Print detailed MCP tool step with metadata."""
        icon = STATUS_ICONS[sub_step.status]
        meta = sub_step.tool_metadata

        # Tool name line
        print(f"|      {icon} {sub_step.name}".ljust(77) + "|")

        if meta:
            # Input data (truncated for display)
            if meta.input_data:
                input_str = ", ".join(f"{k}={_truncate(str(v), 25)}" for k, v in meta.input_data.items())
                print(f"|         Input:  {input_str[:58]}".ljust(77) + "|")

            # Output data (truncated for display)
            if meta.output_data:
                output_str = ", ".join(f"{k}={_truncate(str(v), 25)}" for k, v in meta.output_data.items())
                print(f"|         Output: {output_str[:58]}".ljust(77) + "|")

            # Metadata passing arrow
            if meta.passed_to:
                print(f"|         --> passes to: {meta.passed_to}".ljust(77) + "|")

    def print_summary(self):
        """Print final summary."""
        print()
        print("=" * 78)

        icon = STATUS_ICONS[self.log.overall_status]
        status = self.log.overall_status.value

        if self.log.failure_step:
            print(f" RESULT: {icon} {status} at Step {self.log.failure_step}/{len(self.log.steps)}".center(78))
            print(f" Root Cause: {self.log.failure_reason or 'Unknown'}".center(78))
        else:
            passed = sum(1 for s in self.log.steps if s.status == StepStatus.SUCCESS)
            total = len(self.log.steps)
            print(f" RESULT: {icon} {status} ({passed}/{total} steps)".center(78))

        print("=" * 78)
        print()

    def print_full_log(self):
        """Print the complete workflow log."""
        self._print_header()

        for step in self.log.steps:
            icon = STATUS_ICONS[step.status]
            status = step.status.value

            print(f"+{'-' * 76}+")
            print(f"| [{step.step_number}/{step.total_steps}] {step.from_agent.value} -> {step.to_agent.value}".ljust(68) + f"{icon} {status:>7} |")
            print(f"+{'-' * 76}+")
            print(f"| Action: {step.action}".ljust(77) + "|")

            if step.input_summary:
                print(f"| Input:  {step.input_summary[:65]}".ljust(77) + "|")

            if step.output_summary:
                print(f"| Output: {step.output_summary[:65]}".ljust(77) + "|")

            for sub_step in step.sub_steps:
                sub_icon = STATUS_ICONS[sub_step.status]
                msg = f": {sub_step.message[:50]}" if sub_step.message else ""
                print(f"|      {sub_icon} {sub_step.name}{msg}".ljust(77) + "|")

            if step.error_message:
                print(f"|".ljust(77) + "|")
                print(f"| ==> ERROR: {step.error_message[:60]}".ljust(77) + "|")
                if step.error_location:
                    print(f"|     Location: {step.error_location[:58]}".ljust(77) + "|")

            print(f"+{'-' * 76}+")
            print()

        self.print_summary()

    # =========================================================================
    # Context Manager Support
    # =========================================================================

    class StepContext:
        """Context manager for a workflow step."""
        def __init__(self, logger: 'VisualWorkflowLogger', step: WorkflowStep):
            self.logger = logger
            self.step = step

        def __enter__(self):
            return self.logger

        def __exit__(self, exc_type, exc_val, exc_tb):
            if exc_type:
                self.logger.complete_step(success=False, error=str(exc_val))
                return False  # Re-raise exception
            else:
                self.logger.complete_step(success=True)
                return True

    def step(
        self,
        step_number: int,
        total_steps: int,
        from_agent: AgentType,
        to_agent: AgentType,
        action: str
    ) -> StepContext:
        """Create a step context manager."""
        step = self.start_step(step_number, total_steps, from_agent, to_agent, action)
        return self.StepContext(self, step)


# =============================================================================
# Convenience Functions
# =============================================================================

def create_validation_logger(scenario_id: str, scenario_name: str) -> VisualWorkflowLogger:
    """Create a new workflow logger for a validation run."""
    logger = VisualWorkflowLogger(scenario_id, scenario_name)
    logger._print_header()
    return logger


# =============================================================================
# Standalone Test
# =============================================================================

if __name__ == "__main__":
    # Demo the visual logger with detailed MCP tool tracking
    print("\n" + "=" * 78)
    print(" VISUAL WORKFLOW LOGGER DEMO".center(78))
    print(" With Detailed MCP Tool & Metadata Tracking".center(78))
    print("=" * 78 + "\n")

    # Create logger
    logger = create_validation_logger("QA-EASY-001", "Create new account with valid data")

    # Step 1: Supervisor → SQA Agent
    with logger.step(1, 4, AgentType.SUPERVISOR, AgentType.SQA_AGENT, "Get test scenario"):
        logger.set_input("level='QA-EASY-001'")
        logger.set_output("persona='new user', url='...authentication', next_action=skill")

    # Step 2: SQA Agent → AI Orchestrator (with detailed MCP tool logging)
    logger.start_step(2, 4, AgentType.SQA_AGENT, AgentType.AI_ORCHESTRATOR, "Execute 9-step MCP workflow")
    logger.set_input("next_action.skill='/skill execute-from-step1'")

    # Detailed MCP tool steps with metadata passing
    logger.add_mcp_tool_step(
        step_num=1,
        tool_name="User Input",
        status=StepStatus.SUCCESS,
        input_data={"persona": "new user", "url": "authentication"},
        output_data={"requirement": "create account"},
        passed_to="Step 2"
    )

    logger.add_mcp_tool_step(
        step_num=2,
        tool_name="AI Processing",
        status=StepStatus.SUCCESS,
        input_data={"requirement": "from Step 1"},
        output_data={"role": "NewUser", "bdd": "Given/When/Then", "expected_states": ["is_account_created"]},
        passed_to="Tool 1"
    )

    logger.add_mcp_tool_step(
        step_num=3,
        tool_name="Tool 1: generate_tests_from_user_story",
        status=StepStatus.SUCCESS,
        input_data={"user_story": "As a new user...", "workflow": "auth"},
        output_data={"scenarios": "[{given, when, then}]"},
        passed_to="Tool 6"
    )

    logger.add_mcp_tool_step(
        step_num=4,
        tool_name="Tool 2: discover_page_elements",
        status=StepStatus.RUNNING,
        input_data={"url": "authentication page", "page_name": "RegistrationPage"},
        output_data={},
        passed_to="Tool 3"
    )

    # Simulate failure at Tool 2
    logger.update_sub_step("Step 4: Tool 2: discover_page_elements", StepStatus.FAILED, "Element not found: #email")
    logger.complete_step(success=False, error="Tool 2 failed: Element not found on page")

    # Skip remaining steps
    logger.skip_step(3, 4, AgentType.AI_ORCHESTRATOR, AgentType.REVIEWER, "Validate artifacts", "MCP workflow failed at Step 4")
    logger.skip_step(4, 4, AgentType.REVIEWER, AgentType.SUPERVISOR, "Generate report", "Previous step failed")

    # Complete workflow
    logger.complete_workflow(success=False)

    # Print summary
    logger.print_summary()

    print("\n[SUCCESS] Visual logger with MCP tool tracking working!")
