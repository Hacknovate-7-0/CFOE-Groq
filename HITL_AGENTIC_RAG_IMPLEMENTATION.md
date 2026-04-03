# CfoE Critical Updates - HITL & Agentic RAG Implementation

## Overview
This document describes the three critical changes implemented to align CfoE with the stated approach:
1. **MonitorAgent with LLM Reasoning** (Agentic RAG)
2. **HITL Workflow Pause** (Actual workflow interruption)
3. **Web Dashboard Approval Interface** (Human review UI)

---

## 1. MonitorAgent - Agentic RAG Implementation

### What Changed
- **Before**: DeterministicAgent with simple search result concatenation
- **After**: LLMAgent with intelligent analysis of external search results

### Key Features
- Uses Groq LLM to analyze Tavily search results
- Provides risk assessment with severity levels (0.0-0.3 scale)
- Identifies patterns, recurring issues, and source credibility
- Grounds decisions in real-time external data
- Outputs structured risk reports with specific findings

### Technical Implementation
```python
# agents/monitor_agent.py
- Changed from DeterministicAgent to LLMAgent
- Added custom MonitorAgentWithSearch class
- Integrated Tavily search with LLM reasoning
- Extracts external_risk_score from LLM output
- Stores results in context.state['external_risk_score']
```

### Impact on Risk Scoring
The external_risk_score (0.0-0.3) is now integrated into the final ESG risk calculation:
```python
# agents/calculation_agent.py
adjusted_risk_score = min(1.0, base_risk_score + external_risk_score)
```

This means adverse media findings can push a supplier from Moderate to Critical risk.

---

## 2. HITL Workflow Pause Implementation

### What Changed
- **Before**: `human_approval_required` was just a flag, workflow continued automatically
- **After**: Workflow actually pauses, audit saved to pending queue, requires human action

### Key Features
- Audits with risk_score >= 0.70 are routed to pending approval queue
- Workflow stops until human approves or rejects
- Approval/rejection tracked with approver name, notes, and timestamp
- Approved audits move to history, rejected audits marked as rejected

### Technical Implementation

#### Backend (webapp.py)
```python
# New data structure
PENDING_PATH = DATA_DIR / "pending_approvals.json"

# Workflow routing
if result.get("human_approval_required", False):
    pending = load_pending()
    pending.insert(0, result)
    save_pending(pending)
else:
    history = load_history()
    history.insert(0, result)
    save_history(history)
```

#### New API Endpoints
- `GET /api/approvals` - List pending approvals
- `POST /api/approvals/{audit_id}/approve` - Approve audit
- `POST /api/approvals/{audit_id}/reject` - Reject audit
- `DELETE /api/approvals` - Clear pending queue

#### Approval Data Model
```python
class ApprovalRequest(BaseModel):
    audit_id: str
    decision: str  # "approve" or "reject"
    approver_name: str
    approval_notes: str
```

### Workflow States
1. **pending_approval**: Audit awaiting human review
2. **completed**: Audit approved and finalized
3. **rejected**: Audit rejected by human reviewer

---

## 3. Web Dashboard Approval Interface

### What Changed
- **Before**: No UI for pending approvals, all audits auto-completed
- **After**: Dedicated approval panel with review and decision interface

### Key Features
- **Pending Approvals Panel**: Shows all critical audits awaiting review
- **Approval Dialog**: Detailed view with approve/reject actions
- **Approver Identity**: Requires name and optional notes
- **Audit Trail**: Tracks who approved/rejected and when
- **Visual Indicators**: Red borders, warning badges for critical audits

### UI Components

#### Pending Approvals Panel (index.html)
```html
<section class="panel approval-panel" id="approval-panel">
  <div class="approval-head">
    <h2>🚨 Pending Approvals (HITL)</h2>
    <p>Critical risk audits require human review before completion</p>
  </div>
  <div id="approval-list" class="approval-list"></div>
</section>
```

#### Approval Dialog
- Displays full audit details
- Input fields for approver name and notes
- Three action buttons: Approve, Reject, Cancel
- Executive report preview

#### JavaScript Functions (app.js)
```javascript
// Core functions
fetchPendingApprovals()      // Load pending audits from API
renderPendingApprovals()      // Display approval cards
openApprovalDialog(item)      // Show approval dialog
handleApproval(decision)      // Submit approval/rejection
```

### Visual Design
- **Red theme** for critical/pending items
- **Approval cards** with supplier details and risk metrics
- **Review button** to open approval dialog
- **Status badges** showing pending/approved/rejected state

---

## Integration Flow

### Complete Audit Workflow

```
1. User submits audit
   ↓
2. MonitorAgent (LLM) analyzes external risks → external_risk_score
   ↓
3. CalculationAgent integrates external_risk_score → adjusted_risk_score
   ↓
4. PolicyAgent checks threshold (>= 0.70)
   ↓
   ├─ If Critical → Save to pending_approvals.json (WORKFLOW PAUSES)
   │                 ↓
   │              Human reviews in dashboard
   │                 ↓
   │              Approve or Reject
   │                 ↓
   │              Move to audit_history.json
   │
   └─ If Low/Moderate → Save directly to audit_history.json
```

### Data Flow

```
External Search Results
    ↓
MonitorAgent (LLM Analysis)
    ↓
external_risk_score (0.0-0.3)
    ↓
CalculationAgent
    ↓
adjusted_risk_score = base_score + external_risk_score
    ↓
PolicyAgent
    ↓
human_approval_required = (adjusted_risk_score >= 0.70)
    ↓
    ├─ True → pending_approvals.json
    └─ False → audit_history.json
```

---

## File Changes Summary

### Modified Files
1. **agents/monitor_agent.py** - Converted to LLMAgent with Agentic RAG
2. **agents/calculation_agent.py** - Integrated external_risk_score
3. **orchestrators/root_coordinator.py** - Exposed context for external access
4. **webapp.py** - Added HITL workflow pause and approval endpoints
5. **web/index.html** - Added approval panel and dialog
6. **web/static/app.js** - Added approval UI logic
7. **web/static/styles.css** - Added approval styling

### New Files
1. **data/pending_approvals.json** - Pending approval queue storage

---

## Testing the Implementation

### Test Case 1: Low Risk (Auto-Approved)
```
Supplier: GreenTech Solutions
Emissions: 500 tons
Violations: 0
Expected: Goes directly to history, no approval needed
```

### Test Case 2: Critical Risk (HITL Required)
```
Supplier: PolluteCo Industries
Emissions: 8000 tons
Violations: 5
Expected: Appears in Pending Approvals panel, requires human review
```

### Test Case 3: External Risk Escalation
```
Supplier: BorderlineSupplier
Emissions: 3000 tons (base_score = 0.60)
Violations: 2
External findings: Recent EPA fine (external_risk_score = 0.15)
Adjusted score: 0.75 (Critical)
Expected: Escalated to HITL due to external risks
```

---

## Benefits of Implementation

### 1. True Agentic RAG
- LLM actively reasons about external search results
- Intelligent risk assessment vs. simple aggregation
- Pattern recognition and credibility evaluation

### 2. Compliance-Ready HITL
- Actual workflow pause for critical decisions
- Audit trail with approver identity
- Regulatory compliance for high-risk suppliers

### 3. Production-Ready UI
- Clear separation of pending vs. completed audits
- Intuitive approval workflow
- Visual indicators for critical items

### 4. Integrated Risk Assessment
- External risks influence final scoring
- Holistic evaluation (internal + external data)
- More accurate risk classification

---

## Configuration

### Required Environment Variables
```env
GROQ_API_KEY=your_groq_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here  # Optional but recommended
```

### API Endpoints
- `POST /api/audit` - Submit new audit
- `GET /api/audits` - List completed audits
- `GET /api/approvals` - List pending approvals
- `POST /api/approvals/{audit_id}/approve` - Approve audit
- `POST /api/approvals/{audit_id}/reject` - Reject audit

---

## Future Enhancements

### Potential Improvements
1. **Email Notifications**: Alert approvers when critical audits arrive
2. **Role-Based Access**: Different permissions for analysts vs. approvers
3. **Approval Deadlines**: SLA tracking for pending approvals
4. **Batch Approvals**: Approve multiple audits at once
5. **Approval History**: Dedicated view of all approval decisions
6. **External Risk Weighting**: Configurable weight for external_risk_score

---

## Conclusion

These three critical changes transform CfoE from a demonstration system into a production-ready ESG compliance platform:

1. ✅ **MonitorAgent uses LLM reasoning** for intelligent external risk analysis
2. ✅ **HITL workflow actually pauses** for critical audits
3. ✅ **Web dashboard provides approval interface** for human reviewers

The system now fully implements the stated CfoE approach with Agentic RAG, HITL enforcement, and sequential multi-agent orchestration.
