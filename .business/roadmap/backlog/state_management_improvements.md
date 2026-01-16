# State Management Improvements

**Status:** Idea
**Created:** 2026-01-15
**Target Version:** v1.2 (Optimization), v2.0 (Advanced Features)
**Effort:** v1.2: 5-6 hours, v2.0: 10-12 hours
**Impact:** Medium (performance), High (multi-session workflows)

---

## Context

Workflow state management enables pause/resume capability. Currently implemented via JSON state files in `tests/_state/{workflow_id}/` with workflow ID tracking. Step 11 meta-gate (qg_workflow_complete) validates workflow integrity using state.

While functional, it lacks:
- Performance optimization (caching)
- Multi-session workflows (pause/resume across days)
- State visualization (debugging)
- State versioning (migration)

---

## Problem

**Current State:**
- ✅ JSON state files per workflow
- ✅ Workflow ID tracking
- ✅ Step 11 meta-gate reads state for cross-step validation
- ❌ No caching (re-reads JSON on every gate call)
- ❌ No multi-session support (can't pause/resume across days)
- ❌ No state visualization (hard to debug complex workflows)
- ❌ No state versioning (breaking changes require manual migration)

**What Works:**
```json
{
  "workflow_id": "parabank10_20260114",
  "step_1_data": {...},
  "step_2_data": {...},
  "step_11_result": {...},
  "created_at": "2026-01-14T23:13:11.156117Z",
  "updated_at": "2026-01-14T23:45:30.789012Z"
}
```

**What's Missing:**
- In-memory cache (avoid re-reading JSON 11 times)
- Session token for pause/resume (across days)
- State visualization (CLI tool to inspect state)
- State versioning (schema changes, migrations)

---

## Proposed Improvements

### v1.2: Performance Optimization

**Features:**
- In-memory state cache (load once, update in memory)
- Lazy loading (only load state when needed)
- Write-through cache (write to JSON on updates)
- Cache invalidation (clear on workflow completion)

**Implementation:**
```python
# mcp_server/tools/state/cache.py
class WorkflowStateCache:
    _cache: Dict[str, dict] = {}

    def get(self, workflow_id: str) -> dict:
        """Get state from cache, load from disk if missing."""
        if workflow_id not in self._cache:
            self._cache[workflow_id] = self._load_from_disk(workflow_id)
        return self._cache[workflow_id]

    def update(self, workflow_id: str, step_data: dict):
        """Update state in cache and write to disk."""
        self._cache[workflow_id].update(step_data)
        self._write_to_disk(workflow_id, self._cache[workflow_id])

    def invalidate(self, workflow_id: str):
        """Clear cache for completed workflow."""
        if workflow_id in self._cache:
            del self._cache[workflow_id]
```

**Benefits:**
- ✅ 10x faster state reads (in-memory vs disk)
- ✅ Reduces I/O load (single load per workflow)
- ✅ Backward compatible (still uses JSON files)

**Effort:** 5-6 hours

---

### v2.0: Advanced Multi-Session Workflows

**Features:**
- **Session tokens:** Pause/resume across days (store session ID)
- **State visualization:** CLI tool to inspect workflow state
- **State versioning:** Schema version + migration support
- **State snapshots:** Save checkpoints for rollback
- **State replay:** Re-run workflow from any step

**Implementation:**

**1. Session Tokens:**
```python
# mcp_server/tools/state/session.py
class WorkflowSession:
    def create_session(self, workflow_id: str) -> str:
        """Create session token for pause/resume."""
        session_token = generate_token()  # UUID
        self._save_session(workflow_id, session_token)
        return session_token

    def resume_session(self, session_token: str) -> str:
        """Resume workflow using session token."""
        workflow_id = self._load_session(session_token)
        return workflow_id
```

**2. State Visualization:**
```bash
# CLI tool to inspect state
$ python -m mcp_server.tools.state.visualize parabank10_20260114

Workflow State: parabank10_20260114
Created: 2026-01-14 23:13:11
Status: In Progress (Step 7/11)

✅ Step 1: Pre-flight (PASS)
✅ Step 2: User Input (PASS)
✅ Step 3: AI Processing (PASS)
✅ Step 4: Test Scenarios (PASS)
✅ Step 5: Element Discovery (PASS)
✅ Step 6: POM Generation (PASS)
🔄 Step 7: Task Generation (IN PROGRESS)
⏸️  Step 8: Role Generation (PENDING)
⏸️  Step 9: Test Generation (PENDING)
⏸️  Step 10: Save & Run (PENDING)
⏸️  Step 11: Execution (PENDING)

Next Step: Complete Step 7
Resume Token: abc123-def456-ghi789
```

**3. State Versioning:**
```python
# mcp_server/tools/state/version.py
class StateVersionManager:
    CURRENT_VERSION = "2.0"

    def migrate(self, state: dict) -> dict:
        """Migrate state from old version to current."""
        if state.get("version", "1.0") == "1.0":
            state = self._migrate_1_0_to_2_0(state)
        return state

    def _migrate_1_0_to_2_0(self, state: dict) -> dict:
        """Add session token, rename fields."""
        state["version"] = "2.0"
        state["session_token"] = generate_token()
        return state
```

**4. State Snapshots:**
```python
# mcp_server/tools/state/snapshots.py
class StateSnapshotManager:
    def save_snapshot(self, workflow_id: str, step: int):
        """Save checkpoint for rollback."""
        state = self.cache.get(workflow_id)
        snapshot_path = f"tests/_state/{workflow_id}/snapshots/step_{step}.json"
        save_json(snapshot_path, state)

    def rollback_to_snapshot(self, workflow_id: str, step: int):
        """Rollback to previous checkpoint."""
        snapshot_path = f"tests/_state/{workflow_id}/snapshots/step_{step}.json"
        state = load_json(snapshot_path)
        self.cache.update(workflow_id, state)
```

**Effort:** 10-12 hours

---

## Value

**Benefits:**

**v1.2 (Performance Optimization):**
- ✅ 10x faster state reads (in-memory cache)
- ✅ Reduced I/O load (fewer disk reads)
- ✅ Backward compatible (no breaking changes)

**v2.0 (Advanced Features):**
- ✅ Multi-session workflows (pause/resume across days)
- ✅ State visualization (debugging, transparency)
- ✅ State versioning (schema evolution, migrations)
- ✅ State snapshots (rollback, replay)
- ✅ Session tokens (shareable workflows)

**Platform Impact:**
- **QA Vertical:** Faster workflow execution, pause/resume long tests
- **Consumer Vertical:** Multi-day task execution (research, writing)
- **Agent Management:** Long-running agent workflows (days/weeks)
- **Enterprise:** Compliance workflows with checkpoints

---

## Use Cases

**Multi-Session Workflow Example:**
```
Day 1:
- User starts workflow: "Generate tests for checkout flow"
- AI completes Steps 1-7 (POM + Task generation)
- User pauses: "I'll review tomorrow"
- System saves session token: abc123-def456-ghi789

Day 2:
- User resumes: "Resume session abc123-def456-ghi789"
- AI loads state, continues from Step 8 (Role generation)
- User approves Role → Step 9 (Test generation)
- Workflow completes
```

**State Rollback Example:**
```
- Workflow at Step 9 (Test generation)
- AI generates incorrect test code
- User: "Rollback to Step 6, I want to change the POM"
- System: Loads Step 6 snapshot
- User: Edits POM manually
- User: "Resume from Step 7"
- AI regenerates Task/Role/Test using updated POM
```

---

## Implementation Plan

**v1.2 (Performance Optimization):**
1. Create `WorkflowStateCache` class
2. Replace direct JSON reads with cache.get()
3. Add write-through logic (update cache + disk)
4. Add cache invalidation on workflow completion
5. Test with 11-step workflow (measure performance gain)

**v2.0 (Advanced Features):**
1. Implement session token system
2. Build CLI state visualization tool
3. Add state versioning + migrations
4. Implement snapshot save/rollback
5. Add replay capability (re-run from any step)
6. Update workflow state schema to v2.0

---

## Configuration

**Environment Variables:**
```bash
# State management
STATE_CACHE_ENABLED=true                      # Enable in-memory cache
STATE_SNAPSHOTS_ENABLED=true                  # Save snapshots per step
STATE_PATH=tests/_state/                      # Base path for state files
STATE_VERSION=2.0                             # Current schema version

# Session tokens (v2.0)
SESSION_TOKEN_EXPIRY_DAYS=30                  # Session expires after 30 days
SESSION_TOKEN_LENGTH=32                       # Token length (UUID)
```

---

## Next Steps

1. Move to `.business/roadmap/backlog/` when ready to implement
2. Create PRD for v1.2 (performance optimization)
3. Implement v1.2 for MVP+1 release
4. Follow with v2.0 after multi-session validation
