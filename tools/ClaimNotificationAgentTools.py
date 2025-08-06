#!/usr/bin/env python3
"""
FastAPI router for the ClaimNotificationAgent.

This router defines an endpoint to send notifications to claimants regarding the outcome of their claim.
The endpoint utilizes the NotificationSendingTool to forward the notification details such as claimId,
claimantContact, and the composed message.
"""

from fastapi import APIRouter, Body, Query
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
import logging

from models import ToolResponse  # Base tool response used for subclassing

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

router = APIRouter(prefix="/claim_notification_agent", tags=["ClaimNotificationAgent"])

# ------------------------------
# Request and Response Models
# ------------------------------

class NotificationSendingToolRequest(BaseModel):
    model_config = ConfigDict(extra='allow')
    claimId: str = Field(..., description="The unique identifier for the claim.")
    claimantContact: str = Field(..., description="The contact details for the claimant (email or phone number).")
    message: str = Field(..., description="The notification message to be sent to the claimant.")


class NotificationSendingToolResponse(ToolResponse):
    notificationStatus: Optional[str] = Field(
        None, description="Status message confirming the notification sending outcome."
    )


# ------------------------------
# Endpoint Implementation
# ------------------------------

@router.post("/notification_sending_tool", description="Sends email or SMS notifications to claimants regarding claim status.")
def NotificationSendingTool(
    request: NotificationSendingToolRequest = Body(..., description="Request containing claim notification details")
) -> NotificationSendingToolResponse:
    """
    Sends a claim notification (email or SMS) to the claimant as per the provided details.
    
    Returns:
        NotificationSendingToolResponse: Contains the status of the notification operation.
    """
    try:
        # Log the incoming request
        logger.info(f"NotificationSendingTool input: {request.json()}")
        
        # Simulate notification sending logic.
        # In a real implementation, this is where an email/SMS service API would be called.
        # For demonstration, we pretend the notification is sent successfully.
        confirmation_message = (f"Notification for claim {request.claimId} sent successfully "
                                f"to {request.claimantContact}.")
        logger.info(f"NotificationSendingTool output: {confirmation_message}")

        return NotificationSendingToolResponse(
            error=False,
            details="Notification sent successfully.",
            notificationStatus=confirmation_message
        )
    except Exception as e:
        logger.error("Error in NotificationSendingTool: " + str(e))
        return NotificationSendingToolResponse(
            error=True,
            details=f"Failed to send notification: {str(e)}",
            notificationStatus=None
        )