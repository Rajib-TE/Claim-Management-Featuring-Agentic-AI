#!/usr/bin/env python3
"""
FastAPI router for ClaimValidationAgent, which validates claim details and, if incomplete,
generates a request for additional information.
"""

from fastapi import APIRouter, Body
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
import logging

from models import (
    ToolResponse,
    ClaimDetails,
    ClaimValidationInput,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

router = APIRouter(prefix="/claim_validation_agent", tags=["ClaimValidationAgent"])


# ------------------------------
# Response Models
# ------------------------------
class ClaimValidatorToolResponse(ToolResponse):
    claimId: str = Field(..., description="Unique identifier for the claim")
    status: str = Field(..., description="Validation status: VALID if complete, INVALID if incomplete")
    log: str = Field(..., description="Detailed log of the validation process")
    missingFields: Optional[str] = Field(None, description="Comma separated list of missing or incomplete fields")
    additionalInformationRequest: Optional[str] = Field(
        None, description="Request message for additional information if the claim is incomplete"
    )


class MissingFields(BaseModel):
    model_config = ConfigDict(extra='allow')
    fields: str = Field(..., description="Comma separated list of missing or incomplete fields")


class AdditionalInfoRequestToolInput(BaseModel):
    model_config = ConfigDict(extra='allow')
    claimId: str = Field(..., description="Unique identifier for the claim")
    missingFields: MissingFields = Field(..., description="Missing or incomplete fields details")


class AdditionalInfoRequestToolResponse(ToolResponse):
    claimId: str = Field(..., description="Unique identifier for the claim")
    missingFields: str = Field(..., description="Comma separated list of missing or incomplete fields")
    additionalInformationRequest: str = Field(..., description="Request message for additional information")
    log: str = Field(..., description="Log entry for the additional information request")


# ------------------------------
# ClaimValidatorTool Endpoint
# ------------------------------
@router.post("/claimvalidatortool", description="Checks claim data against business rules to assert completeness and correctness.")
def ClaimValidatorTool(
    request: ClaimValidationInput = Body(..., description="The claim details to be validated.")
) -> ClaimValidatorToolResponse:
    try:
        logger.info(f"ClaimValidatorTool received request: {request.json()}")
        missing_fields = []
        # Check if policyNumber is present and non-empty
        if not request.claimDetails.policyNumber or request.claimDetails.policyNumber.strip() == "":
            missing_fields.append("policyNumber")
        # Check if incidentDescription is present and non-empty
        if not request.claimDetails.incidentDescription or request.claimDetails.incidentDescription.strip() == "":
            missing_fields.append("incidentDescription")
        
        # Build log message parts
        log_messages = []
        if request.claimDetails.policyNumber and request.claimDetails.policyNumber.strip() != "":
            log_messages.append("policyNumber present and valid.")
        else:
            log_messages.append("policyNumber missing or empty.")
        if request.claimDetails.incidentDescription and request.claimDetails.incidentDescription.strip() != "":
            log_messages.append("incidentDescription present and valid.")
        else:
            log_messages.append("incidentDescription missing or empty.")
        
        # Include investigation data log if available
        if request.investigationData:
            log_messages.append("Investigation data provided.")
        
        log_entry = " ".join(log_messages)
        
        if missing_fields:
            missing_fields_str = ", ".join(missing_fields)
            additional_request = ""
            if len(missing_fields) == 1:
                additional_request = f"Please provide the missing field: {missing_fields_str} for claim {request.claimId}."
            else:
                additional_request = f"Please provide the missing fields: {missing_fields_str} for claim {request.claimId}."
            response = ClaimValidatorToolResponse(
                error=False,
                details="Claim validation completed with missing fields.",
                claimId=request.claimId,
                status="INVALID",
                log=log_entry + " Additional information request generated.",
                missingFields=missing_fields_str,
                additionalInformationRequest=additional_request
            )
            logger.info(f"ClaimValidatorTool response: {response.json()}")
            return response
        else:
            response = ClaimValidatorToolResponse(
                error=False,
                details="Claim validation successful.",
                claimId=request.claimId,
                status="VALID",
                log=log_entry + " All required fields are present and valid.",
                missingFields=None,
                additionalInformationRequest=None
            )
            logger.info(f"ClaimValidatorTool response: {response.json()}")
            return response
    except Exception as e:
        logger.error("Error in ClaimValidatorTool: " + str(e))
        return ClaimValidatorToolResponse(
            error=True,
            details=str(e),
            claimId=request.claimId if request and request.claimId else "unknown",
            status="ERROR",
            log="An error occurred during claim validation.",
            missingFields=None,
            additionalInformationRequest=None
        )


# ------------------------------
# AdditionalInfoRequestTool Endpoint
# ------------------------------
@router.post("/additionalinforequesttool", description="Generates and sends requests for additional information when the claim is incomplete.")
def AdditionalInfoRequestTool(
    request: AdditionalInfoRequestToolInput = Body(..., description="Input parameters for additional information request.")
) -> AdditionalInfoRequestToolResponse:
    try:
        logger.info(f"AdditionalInfoRequestTool received request: {request.json()}")
        # Craft additional information request message based on missing fields provided.
        additional_request_message = ""
        fields = request.missingFields.fields
        if fields:
            additional_request_message = f"Please provide the following missing information for claim {request.claimId}: {fields}."
        else:
            additional_request_message = f"No specific missing fields provided for claim {request.claimId}. Please verify your submission."
        
        log_entry = f"Additional info request generated for claim {request.claimId} for missing fields: {fields}."
        
        response = AdditionalInfoRequestToolResponse(
            error=False,
            details="Additional information request generated successfully.",
            claimId=request.claimId,
            missingFields=fields,
            additionalInformationRequest=additional_request_message,
            log=log_entry
        )
        logger.info(f"AdditionalInfoRequestTool response: {response.json()}")
        return response
    except Exception as e:
        logger.error("Error in AdditionalInfoRequestTool: " + str(e))
        return AdditionalInfoRequestToolResponse(
            error=True,
            details=str(e),
            claimId=request.claimId if request and request.claimId else "unknown",
            missingFields="",
            additionalInformationRequest="",
            log="An error occurred while generating additional information request."
        )