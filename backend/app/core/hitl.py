"""
Human-in-the-Loop (HITL) Agent
Pauses the workflow and creates a pending approval record.
The workflow resumes only after the human approves or rejects.
"""
from app.core.interfaces import Agent, AgentContext, AgentResponse
from app.database.models import HITLModel
from datetime import datetime


class HITLApprovalAgent(Agent):
    """
    Step 7: Human-in-the-Loop approval before final recommendations are sent.

    Flow:
      1. Extracts the prospect list / shortlist from workflow data
      2. Creates a 'pending_approval' record in MongoDB
      3. Returns success=True with status='awaiting_approval'
      4. WorkflowEngine marks workflow as 'pending_approval'
      5. Human reviews on /approvals page and clicks Approve or Reject
      6. On approval: workflow status updated to 'completed'
      7. On rejection: workflow status updated to 'rejected' with feedback
    """

    def __init__(self):
        super().__init__("HITLApprovalAgent")

    async def execute(self, context: AgentContext) -> AgentResponse:
        """Create HITL approval record and pause workflow."""

        # Extract the payload to review
        plugin_data = context.data
        prospect_list = plugin_data.get("prospect_list", []) or plugin_data.get("qualified_companies", []) or plugin_data.get("prospects", [])
        shortlist = plugin_data.get("shortlist", [])   # HR plugin output
        pipeline_summary = plugin_data.get("pipeline_summary", {})

        # Determine what type of review this is
        review_type = "b2b_prospects" if (prospect_list or plugin_data.get("qualified_companies") or plugin_data.get("prospects")) else "hr_candidates"
        review_items = prospect_list if prospect_list else shortlist

        approval_record = {
            "workflow_id": context.workflow_id,
            "user_request": context.user_request,
            "review_type": review_type,
            "review_items": review_items[:10],  # cap at 10 for display
            "pipeline_summary": pipeline_summary,
            "status": "pending",
            "created_at": datetime.utcnow().isoformat(),
            "approved_at": None,
            "rejected_at": None,
            "reviewer_notes": None,
        }

        # Persist the approval record
        try:
            await HITLModel.create_approval(approval_record)
        except Exception as e:
            # Non-fatal — approval UI can still work with workflow_id lookup
            print(f"⚠️  HITL: Failed to save approval record: {e}")

        return AgentResponse(
            success=True,
            data={
                "hitl_status": "awaiting_approval",
                "review_type": review_type,
                "items_pending_review": len(review_items),
                "approval_message": (
                    f"✋ {len(review_items)} {'prospects' if review_type == 'b2b_prospects' else 'candidates'} "
                    f"ready for your review. Please approve or reject on the Approvals page."
                ),
                "workflow_id": context.workflow_id,
            },
            confidence=1.0,
            next_step="awaiting_human_approval",
        )
