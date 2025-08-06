#!/usr/bin/env python3
"""
FastAPI router for ClaimDecisionAgent.
This router implements the DecisionSupportTool which evaluates investigation reports and claim details
to make an informed claim decision.
"""

from fastapi import APIRouter, Body
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
import logging

# Import shared Pydantic models from models module
from models import (
    ClaimDecisionInput,
    ToolResponse,
)

# Initialize logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Define router with prefix as the agent id in lowercase
router = APIRouter(
    prefix="/claim_decision_agent",
    tags=["ClaimDecisionAgent"],
)

# Define the DecisionSupportTool response model, subclassing ToolResponse.
class DecisionSupportToolResponse(ToolResponse):
    claimId: str = Field(..., description="Unique identifier for the claim")
    decision: str = Field(..., description="Decision outcome for the claim: Approved, Rejected, Additional Info Required, or Escalate")
    rationale: str = Field(..., description="Explanation and justification for the decision")
    requiredFollowUp: str = Field(..., description="Instructions for follow-up actions, e.g., trigger payment, notify claimant, or request additional info")
    questionsForUser: str = Field(..., description="Any questions or clarifications required from the user")

@router.post("/decision_support_tool", description="Assesses investigation reports and other claim details to make an informed claim decision.")
def DecisionSupportTool(
    request: ClaimDecisionInput = Body(..., description="Input data for claim decision making")
) -> DecisionSupportToolResponse:
    try:
        logger.info(f"DecisionSupportTool called with request: {request}")
        # Extract investigation data for decision making
        evidence = request.investigationData.evidenceSummary.lower().strip() if request.investigationData and request.investigationData.evidenceSummary else ""
        notes = request.investigationData.notes.lower().strip() if request.investigationData and request.investigationData.notes else ""
        
        # Basic decision logic:
        if (not evidence) or ("blurry" in evidence) or ("sparse" in evidence):
            decision = "Additional Info Required"
            rationale = "The evidence provided is insufficient or unclear to reach a conclusive decision."
            required_followup = "Request additional documentation and clearer evidence from the claimant."
            questions_for_user = "Please submit detailed photos, reports, or any additional documentation that can clarify the claim."
        elif ("inconclusive" in evidence) or ("fraud" in notes) or ("suspicious" in notes):
            decision = "Escalate"
            rationale = "The investigation findings indicate potential issues that require further human expert review."
            required_followup = "Escalate to a human claims examiner for a detailed evaluation."
            questions_for_user = ""
        else:
            decision = "Approved"
            rationale = "Investigation findings are clear and all necessary documentation are verified."
            required_followup = "Trigger payment and notify the claimant of the approval."
            questions_for_user = ""
        
        result = DecisionSupportToolResponse(
            error=False,
            details="Decision processed successfully",
            claimId=request.claimId,
            decision=decision,
            rationale=rationale,
            requiredFollowUp=required_followup,
            questionsForUser=questions_for_user,
        )
        logger.info(f"DecisionSupportTool output: {result}")
        return result
    except Exception as e:
        logger.error("Error in DecisionSupportTool: " + str(e))
        return DecisionSupportToolResponse(
            error=True,
            details=f"An error occurred: {str(e)}",
            claimId=request.claimId if request and hasattr(request, "claimId") else "",
            decision="",
            rationale="",
            requiredFollowUp="",
            questionsForUser="",
        )