#!/usr/bin/env python3
"""
FastAPI router for ClaimRegistrationAgent that implements the ClaimDBStorageTool tool.

This endpoint accepts claim registration data, validates the required fields,
checks for duplicate submissions, and stores the claim using an in‐memory repository.
It then returns a confirmation response including the claim summary.
"""

from fastapi import APIRouter, Body
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
import logging

# Importing shared models and repositories from the provided models module.
from models import (
    ToolResponse,
    ClaimRegistrationInput,
    claim_repo,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

router = APIRouter(prefix="/claim_registration_agent", tags=["ClaimRegistrationAgent"])

class ClaimDBStorageToolResponse(ToolResponse):
    claimId: str = Field(..., description="Unique identifier for the claim")
    claimantName: str = Field(..., description="Name of the claimant")
    claimantContact: str = Field(..., description="Contact details of the claimant")
    policyNumber: str = Field(..., description="Policy number associated with the claim")
    incidentDescription: str = Field(..., description="Description of the incident reported in the claim")

@router.post("/claim_db_storage_tool", description="Stores claim data in a database for later retrieval and processing.")
def claim_db_storage_tool(
    request: ClaimRegistrationInput = Body(..., description="Claim registration input data")
) -> ClaimDBStorageToolResponse:
    try:
        missing_fields = []
        if not request.claimId.strip():
            missing_fields.append("claimId")
        if not request.claimantInfo.name.strip():
            missing_fields.append("claimantInfo.name")
        if not request.claimantInfo.contact.strip():
            missing_fields.append("claimantInfo.contact")
        if not request.claimDetails.policyNumber.strip():
            missing_fields.append("claimDetails.policyNumber")
        if not request.claimDetails.incidentDescription.strip():
            missing_fields.append("claimDetails.incidentDescription")
            
        # If any mandatory field is missing or empty, notify the user.
        if missing_fields:
            error_msg = (
                f"Missing or empty fields: {', '.join(missing_fields)}. "
                "Please provide the required information."
            )
            logger.info(f"claim_db_storage_tool: Missing fields detected: {missing_fields}")
            return ClaimDBStorageToolResponse(
                error=True,
                details=error_msg,
                claimId=request.claimId,
                claimantName=request.claimantInfo.name,
                claimantContact=request.claimantInfo.contact,
                policyNumber=request.claimDetails.policyNumber,
                incidentDescription=request.claimDetails.incidentDescription,
            )
        
        # Prevent duplicate submissions by checking if claimId already exists.
        existing_claim = claim_repo.find_by_claimId(request.claimId)
        if existing_claim:
            error_msg = f"Duplicate claimId: {request.claimId}. Claim already registered."
            logger.info(f"claim_db_storage_tool: Duplicate claimId {request.claimId} detected.")
            return ClaimDBStorageToolResponse(
                error=True,
                details=error_msg,
                claimId=request.claimId,
                claimantName=request.claimantInfo.name,
                claimantContact=request.claimantInfo.contact,
                policyNumber=request.claimDetails.policyNumber,
                incidentDescription=request.claimDetails.incidentDescription,
            )
        
        # Save the valid claim into the repository.
        claim_repo.add_claim(request)
        result_msg = f"Claim registered successfully with claimId {request.claimId}."
        logger.info(f"claim_db_storage_tool: Successfully stored claim: {request}")
        return ClaimDBStorageToolResponse(
            error=False,
            details=result_msg,
            claimId=request.claimId,
            claimantName=request.claimantInfo.name,
            claimantContact=request.claimantInfo.contact,
            policyNumber=request.claimDetails.policyNumber,
            incidentDescription=request.claimDetails.incidentDescription,
        )
        
    except Exception as e:
        logger.error("Error in claim_db_storage_tool: " + str(e))
        return ClaimDBStorageToolResponse(
            error=True,
            details=str(e),
            claimId="",
            claimantName="",
            claimantContact="",
            policyNumber="",
            incidentDescription="",
        )