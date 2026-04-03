# Quick Start Guide - HITL Approval Workflow

## For End Users

### Running an Audit

1. **Start the application**
   ```bash
   uvicorn webapp:app --reload
   ```

2. **Open dashboard**
   - Navigate to `http://127.0.0.1:8000`

3. **Submit supplier data**
   - Fill in supplier name, emissions, violations
   - Click "Run Audit"

### Understanding Results

#### Auto-Approved Audits (Low/Moderate Risk)
- Appear immediately in "Latest Result"
- Show green "Completed" badge
- Added directly to "Audit History"

#### Critical Audits (HITL Required)
- Show red "Pending Approval" badge
- Appear in "🚨 Pending Approvals (HITL)" panel
- **Workflow is paused** until human reviews

### Approving/Rejecting Audits

1. **Locate pending audit**
   - Check the "Pending Approvals" panel (appears when critical audits exist)

2. **Click "Review & Decide"**
   - Opens approval dialog with full audit details

3. **Enter your information**
   - Your Name (required)
   - Approval Notes (optional but recommended)

4. **Make decision**
   - Click "Approve" to accept the supplier
   - Click "Reject" to decline the supplier
   - Click "Cancel" to return without deciding

5. **Confirmation**
   - Approved/rejected audit moves to history
   - Approval details (name, notes, timestamp) are recorded
   - Pending panel updates automatically

---

## For Developers

### Key Files Modified

```
agents/
  ├── monitor_agent.py          # Now uses LLM for Agentic RAG
  └── calculation_agent.py      # Integrates external_risk_score

orchestrators/
  └── root_coordinator.py       # Exposes context for external access

data/
  ├── audit_history.json        # Completed/approved audits
  └── pending_approvals.json    # Audits awaiting HITL review

web/
  ├── index.html                # Added approval panel & dialog
  └── static/
      ├── app.js                # Added approval logic
      └── styles.css            # Added approval styling

webapp.py                       # Added HITL endpoints & workflow pause
```

### API Endpoints

#### Approval Management
```javascript
// List pending approvals
GET /api/approvals
Response: { items: [...], count: N }

// Approve audit
POST /api/approvals/{audit_id}/approve
Body: {
  audit_id: "AUD-xxx",
  decision: "approve",
  approver_name: "John Doe",
  approval_notes: "Reviewed and approved"
}

// Reject audit
POST /api/approvals/{audit_id}/reject
Body: {
  audit_id: "AUD-xxx",
  decision: "reject",
  approver_name: "Jane Smith",
  approval_notes: "Risk too high"
}

// Clear pending queue
DELETE /api/approvals
```

### Testing Scenarios

#### Scenario 1: Low Risk (No HITL)
```python
# Test data
supplier_name = "EcoFriendly Corp"
emissions = 800
violations = 0

# Expected behavior
# - base_risk_score = 0.1 + 0.0 = 0.10
# - external_risk_score = ~0.0 (no adverse findings)
# - adjusted_risk_score = 0.10
# - Classification: Low Risk
# - human_approval_required = False
# - Goes directly to audit_history.json
```

#### Scenario 2: Critical Risk (HITL Required)
```python
# Test data
supplier_name = "HighEmissions Inc"
emissions = 9000
violations = 6

# Expected behavior
# - base_risk_score = 0.5 + 0.5 = 1.00
# - external_risk_score = ~0.0-0.3 (depends on search)
# - adjusted_risk_score = 1.00+
# - Classification: Critical Risk
# - human_approval_required = True
# - Saved to pending_approvals.json
# - Appears in Pending Approvals panel
```

#### Scenario 3: External Risk Escalation
```python
# Test data
supplier_name = "BorderlineCorp"
emissions = 3500
violations = 3

# Expected behavior
# - base_risk_score = 0.35 + 0.30 = 0.65
# - external_risk_score = 0.15 (recent EPA fine found)
# - adjusted_risk_score = 0.80
# - Classification: Critical Risk (escalated by external data)
# - human_approval_required = True
# - Demonstrates Agentic RAG impact
```

### Debugging

#### Check Pending Queue
```bash
cat data/pending_approvals.json
```

#### Check Audit History
```bash
cat data/audit_history.json
```

#### Monitor Logs
```bash
# Watch console output for:
# - MonitorAgent LLM analysis
# - external_risk_score extraction
# - HITL workflow pause messages
```

### Customization

#### Adjust HITL Threshold
```python
# agents/policy_agent.py
# Change threshold from 0.7 to desired value
if risk_score >= 0.7:  # Modify this line
    return {
        "decision": "ESCALATE_TO_HUMAN_REVIEW",
        "human_approval_required": True,
        ...
    }
```

#### Modify External Risk Weight
```python
# agents/calculation_agent.py
# Currently: external_risk_score range is 0.0-0.3
# To increase impact, multiply by factor:
external_risk_score = context.state.get('external_risk_score', 0.0) * 1.5
```

---

## Troubleshooting

### Issue: Pending Approvals Panel Not Showing
**Solution**: No critical audits exist. Submit audit with high emissions/violations.

### Issue: MonitorAgent Not Using LLM
**Solution**: Check GROQ_API_KEY in .env file. Verify Groq client initialization.

### Issue: External Risk Score Always 0.0
**Solution**: 
1. Check TAVILY_API_KEY in .env
2. Verify internet connection
3. Check MonitorAgent LLM output for score extraction

### Issue: Approval Not Moving to History
**Solution**: Check browser console for API errors. Verify approver name is filled.

---

## Best Practices

### For Approvers
1. Always provide meaningful approval notes
2. Review full executive report before deciding
3. Check external risk findings carefully
4. Document reasoning for rejections

### For Developers
1. Monitor pending queue size regularly
2. Set up alerts for long-pending approvals
3. Backup pending_approvals.json before clearing
4. Test HITL workflow with various risk levels
5. Validate external_risk_score extraction

---

## Next Steps

After implementing these changes:

1. ✅ Test with low, moderate, and critical risk suppliers
2. ✅ Verify HITL workflow pause works correctly
3. ✅ Confirm external risks influence scoring
4. ✅ Test approval and rejection flows
5. ✅ Review audit trail in history

For production deployment:
- Add authentication for approvers
- Implement email notifications
- Set up approval SLA monitoring
- Add role-based access control
- Configure external risk weight per industry
