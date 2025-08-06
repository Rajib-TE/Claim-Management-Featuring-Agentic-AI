#!/usr/bin/env python3
"""
FastAPI router for ClaimClosureAgent.

This router implements the ClaimClosureTool which updates the claim record status
to "Closed" and archives supporting documents upon successful closure of a claim.
"""

from fastapi import APIRouter, Body, Query
from pydantic import Field
from typing import Optional, List
from datetime import datetime
import logging

from models import (
    ClaimClosureInput,
    ClaimRepository,
    ClosureRepository,
    ToolResponse,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

router = APIRouter(prefix="/claim_closure_agent", tags=["ClaimClosureAgent"])

# ------------------------------
# Response Models
# ------------------------------

class ClaimClosureSuccessResponse(ToolResponse):
    result: str = Field(..., description="Indicates a successful closure operation, should be 'success'")
    claimId: str = Field(..., description="Unique identifier for the closed claim")
    status: str = Field(..., description="Final status of the claim, always 'Closed'")
    timestamp: str = Field(..., description="Timestamp of when the claim was closed in ISO format")
    archivedDocuments: List[str] = Field(..., description="List of documents archived during closure")
    closureNotes: Optional[str] = Field(None, description="Optional notes provided during closure")

class ClaimClosureAlertResponse(ToolResponse):
    result: str = Field(..., description="Indicates an alert situation, should be 'alert'")
    claimId: str = Field(..., description="Unique identifier for the claim")
    issue: str = Field(..., description="Description of the discrepancy or issue encountered")
    actionRequired: str = Field(..., description="Recommended action to resolve the issue")

# ------------------------------
# Repository Instances
# ------------------------------
# Using the shared ClaimRepository (seeded) and a dedicated ClosureRepository
claim_repo = ClaimRepository()
closure_repo = ClosureRepository()

# ------------------------------
# ClaimClosureTool Endpoint
# ------------------------------

@router.post(
    "/ClaimClosureTool",
    description="Updates the claim record status to closed and archives supporting documents."
)
def ClaimClosureTool(
    request: ClaimClosureInput = Body(..., description="Input parameters for claim closure")
) -> ClaimClosureSuccessResponse | ClaimClosureAlertResponse:
    """
    Processes the final closure of a claim. If required closure notes are provided
    and the claim exists in the system, the claim is marked as closed and supporting
    documents are archived. If required details are missing, an alert is issued.
    """
    try:
        logger.info(f"Received ClaimClosureTool request: {request}")

        # Check if the claim exists in the repository
        claim = claim_repo.find_by_claimId(request.claimId)
        if not claim:
            msg = f"Claim record with claimId {request.claimId} not found."
            logger.error(msg)
            return ClaimClosureAlertResponse(
                error=False,
                details=msg,
                result="alert",
                claimId=request.claimId,
                issue="Claim record not found",
                actionRequired="Please verify the claim ID and try again."
            )

        # Validate that closureNotes is provided (non-empty)
        if not request.closureNotes or not request.closureNotes.strip():
            msg = "Closure notes not provided or empty."
            logger.error(msg)
            return ClaimClosureAlertResponse(
                error=False,
                details=msg,
                result="alert",
                claimId=request.claimId,
                issue="No closureNotes provided and the notification step is not recorded as completed.",
                actionRequired="Please provide closure notes and confirm claimant notification."
            )

        # Simulate archiving supporting documents (fixed list for demonstration)
        archived_documents = [
            "claim-form.pdf",
            "investigator-report.pdf",
            "payment-confirmation.pdf"
        ]

        # Simulate claim closure by adding the record to the ClosureRepository
        closure_repo.add_closure(request)

        # Generate current timestamp in ISO8601 format (UTC assumed)
        closure_timestamp = datetime.utcnow().isoformat() + "Z"

        result_message = f"Claim {request.claimId} closed successfully."
        logger.info(result_message)

        return ClaimClosureSuccessResponse(
            error=False,
            details=result_message,
            result="success",
            claimId=request.claimId,
            status="Closed",
            timestamp=closure_timestamp,
            archivedDocuments=archived_documents,
            closureNotes=request.closureNotes.strip()
        )
    except Exception as e:
        logger.error("Error in ClaimClosureTool: " + str(e))
        # Return a generic ToolResponse error instance (must be a subclass, so using ClaimClosureAlertResponse)
        return ClaimClosureAlertResponse(
            error=True,
            details=str(e),
            result="alert",
            claimId=request.claimId if request and request.claimId else "Unknown",
            issue="Internal processing error",
            actionRequired="Please contact system administrator."
        )