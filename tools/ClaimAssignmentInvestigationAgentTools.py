#!/usr/bin/env python3
"""
FastAPI router for ClaimAssignmentInvestigationAgent.

This router implements two tools:
1. ExaminerAssignmentTool: Assigns a claim to a suitable examiner based on workload and expertise.
2. ClaimInvestigationTool: Conducts an investigation on the assigned claim by collecting evidence and summarizing findings.
"""

from fastapi import APIRouter, Body
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
import logging

# Import shared models from the claims management module.
from models import ToolResponse, InvestigationData

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

router = APIRouter(prefix="/claim_assignment_investigation_agent", tags=["ClaimAssignmentInvestigationAgent"])

# ---------------------------
# Request Models
# ---------------------------
class ExaminerAssignmentRequest(BaseModel):
    model_config = ConfigDict(extra='allow')
    claimId: str = Field(..., description="The unique identifier for the claim to be assigned.")
    examinerPool: str = Field(..., description="Identifier or criteria for filtering potential examiners.")

class ClaimInvestigationRequest(BaseModel):
    model_config = ConfigDict(extra='allow')
    claimId: str = Field(..., description="The unique identifier for the claim under investigation.")
    examinerId: str = Field(..., description="The identifier of the examiner assigned to the claim.")
    investigationData: InvestigationData = Field(..., description="Data collected during the investigation process, including evidence summary and investigation notes.")

# ---------------------------
# Nested Response Models for Tools
# ---------------------------
class AssignmentDetails(BaseModel):
    criteria: str = Field(..., description="Description of examiner selection criteria.")
    timestamp: datetime = Field(..., description="ISO8601 timestamp of the assignment.")

class InvestigationDetails(BaseModel):
    evidenceSummary: str = Field(..., description="Summary of the evidence collected during investigation.")
    notes: str = Field(..., description="Additional investigation notes and observations.")
    timestamp: datetime = Field(..., description="ISO8601 timestamp of the investigation.")

# ---------------------------
# Tool Response Models
# ---------------------------
class ExaminerAssignmentResponse(ToolResponse):
    claimId: str = Field(..., description="The unique identifier for the claim.")
    assignedExaminerId: str = Field(..., description="Identifier of the assigned examiner.")
    assignmentDetails: AssignmentDetails = Field(..., description="Details about the examiner assignment.")

class ClaimInvestigationResponse(ToolResponse):
    claimId: str = Field(..., description="The unique identifier for the claim under investigation.")
    examinerId: str = Field(..., description="Identifier of the examiner involved in the investigation.")
    investigation: InvestigationDetails = Field(..., description="Details of the claim investigation.")

# ---------------------------
# ExaminerAssignmentTool Endpoint
# ---------------------------
@router.post("/examiner_assignment_tool", description="Assigns a claim to a suitable examiner based on workload and expertise.")
def examiner_assignment_tool(
    request: ExaminerAssignmentRequest = Body(..., description="Request parameters including claimId and examinerPool.")
) -> ExaminerAssignmentResponse:
    try:
        logger.info(f"ExaminerAssignmentTool received request: {request}")

        # Validate examinerPool; if missing or empty, request clarification.
        if not request.examinerPool.strip():
            err_msg = f"Please specify the examiner pool or selection criteria for assigning claim {request.claimId}."
            logger.error(err_msg)
            # Return error response with required fields set to empty/default values.
            return ExaminerAssignmentResponse(
                error=True,
                details=err_msg,
                claimId=request.claimId,
                assignedExaminerId="",
                assignmentDetails=AssignmentDetails(criteria="", timestamp=datetime.utcnow())
            )

        # Simulate examiner assignment logic.
        # For demonstration, we generate a pseudo examiner id based on the claimId.
        assigned_examiner_id = "EX-" + request.claimId[-4:]  # simple simulation

        # Compose the assignment details.
        criteria = f"{request.examinerPool}, lowest current workload"
        assignment_timestamp = datetime.utcnow()

        response = ExaminerAssignmentResponse(
            error=False,
            details="Examiner assigned successfully.",
            claimId=request.claimId,
            assignedExaminerId=assigned_examiner_id,
            assignmentDetails=AssignmentDetails(criteria=criteria, timestamp=assignment_timestamp)
        )
        logger.info(f"ExaminerAssignmentTool response: {response}")
        return response
    except Exception as e:
        logger.error("Error in ExaminerAssignmentTool: " + str(e))
        # In error case, return a response with error flag set and empty fields where required.
        return ExaminerAssignmentResponse(
            error=True,
            details=str(e),
            claimId=request.claimId if request and hasattr(request, "claimId") else "",
            assignedExaminerId="",
            assignmentDetails=AssignmentDetails(criteria="", timestamp=datetime.utcnow())
        )

# ---------------------------
# ClaimInvestigationTool Endpoint
# ---------------------------
@router.post("/claim_investigation_tool", description="Conducts an investigation on the claim by gathering evidence and summarizing findings.")
def claim_investigation_tool(
    request: ClaimInvestigationRequest = Body(..., description="Request parameters including claimId, examinerId, and investigationData.")
) -> ClaimInvestigationResponse:
    try:
        logger.info(f"ClaimInvestigationTool received request: {request}")

        # Simulate investigation process.
        investigation_timestamp = datetime.utcnow()

        investigation_details = InvestigationDetails(
            evidenceSummary=request.investigationData.evidenceSummary,
            notes=request.investigationData.notes,
            timestamp=investigation_timestamp
        )

        response = ClaimInvestigationResponse(
            error=False,
            details="Investigation completed successfully.",
            claimId=request.claimId,
            examinerId=request.examinerId,
            investigation=investigation_details
        )
        logger.info(f"ClaimInvestigationTool response: {response}")
        return response
    except Exception as e:
        logger.error("Error in ClaimInvestigationTool: " + str(e))
        return ClaimInvestigationResponse(
            error=True,
            details=str(e),
            claimId=request.claimId if request and hasattr(request, "claimId") else "",
            examinerId=request.examinerId if request and hasattr(request, "examinerId") else "",
            investigation=InvestigationDetails(evidenceSummary="", notes="", timestamp=datetime.utcnow())
        )