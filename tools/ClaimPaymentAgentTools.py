#!/usr/bin/env python3
"""
FastAPI router for the ClaimPaymentAgent.
Processes payments for approved claims by validating input,
simulating payment gateway interactions, and generating confirmation or error reports.
"""

from fastapi import APIRouter, Body
from pydantic import Field, BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
import logging

from models import (
    PaymentProcessingInput,
    ToolResponse,
    PaymentRepository
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

router = APIRouter(prefix="/claim_payment_agent", tags=["ClaimPaymentAgent"])

# In-memory repository instance for storing payment processing results.
payment_repo = PaymentRepository()

class PaymentProcessingResponse(ToolResponse):
    claimId: Optional[str] = Field(None, description="Unique identifier for the claim")
    paymentStatus: Optional[str] = Field(None, description="Status of the payment e.g., Processed, Failed, Pending")
    transactionId: Optional[str] = Field(None, description="Transaction identifier provided by the payment gateway")
    timestamp: Optional[datetime] = Field(None, description="Timestamp when the payment was processed")
    amountPaid: Optional[float] = Field(None, description="The amount paid for the claim")
    errorMessage: Optional[str] = Field(None, description="Detailed error message if the payment failed")
    escalationAdvice: Optional[str] = Field(None, description="Advice for next steps in case of a failure")


@router.post("/payment_processing_tool", description="Connects to a payment gateway to process claim payouts.")
def PaymentProcessingTool(
    request: PaymentProcessingInput = Body(..., description="Payment processing input parameters")
) -> PaymentProcessingResponse:
    """
    Processes the claim payment by validating the payment details,
    checking for duplicate payment processing, simulating a call to a payment gateway,
    and returning a confirmation or error response.
    """
    try:
        logger.info(f"PaymentProcessingTool - Received request: {request}")

        # Validate that payment details are complete.
        account_number = request.paymentDetails.accountNumber.strip()
        routing_number = request.paymentDetails.routingNumber.strip()
        if not account_number:
            error_msg = f"Missing bank account number for claim {request.claimId}."
            logger.error(error_msg)
            return PaymentProcessingResponse(
                error=True,
                details=error_msg,
                claimId=request.claimId,
                paymentStatus="Failed",
                errorMessage="Bank account number is missing.",
                escalationAdvice="Please provide a valid bank account number."
            )
        if not routing_number:
            error_msg = f"Missing routing number for claim {request.claimId}."
            logger.error(error_msg)
            return PaymentProcessingResponse(
                error=True,
                details=error_msg,
                claimId=request.claimId,
                paymentStatus="Failed",
                errorMessage="Routing number is missing.",
                escalationAdvice="Please provide a valid routing number."
            )

        # Check for duplicate payment processing to avoid duplication.
        existing_payment = payment_repo.find_payment_by_claimId(request.claimId)
        if existing_payment is not None:
            msg = f"Duplicate payment processing detected for claim {request.claimId}. Payment already processed."
            logger.info(msg)
            return PaymentProcessingResponse(
                error=True,
                details=msg,
                claimId=request.claimId,
                paymentStatus="Failed",
                errorMessage="Duplicate payment detected.",
                escalationAdvice="If you intend to process the payment again, please confirm explicitly."
            )

        # Simulate payment gateway processing.
        # If the account number or routing number contains invalid tokens, simulate failure.
        if "INVALID" in account_number or "XXXXXXX" in routing_number:
            error_msg = f"Payment gateway processing failed for claim {request.claimId} due to invalid account details."
            logger.error(error_msg)
            return PaymentProcessingResponse(
                error=True,
                details=error_msg,
                claimId=request.claimId,
                paymentStatus="Failed",
                errorMessage="Bank account number or routing number is invalid.",
                escalationAdvice="Please verify and provide correct payment details."
            )

        # Simulate successful payment processing.
        transaction_id = f"TRX{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        timestamp = datetime.utcnow()
        amount_paid = request.paymentDetails.paymentAmount

        # Store the payment in the in-memory repository.
        payment_repo.add_payment(request)

        result_msg = f"Payment processed successfully for claim {request.claimId}."
        logger.info(result_msg)
        return PaymentProcessingResponse(
            error=False,
            details=result_msg,
            claimId=request.claimId,
            paymentStatus="Processed",
            transactionId=transaction_id,
            timestamp=timestamp,
            amountPaid=amount_paid
        )
    except Exception as e:
        err_msg = f"Exception occurred during payment processing for claim {request.claimId}: {str(e)}"
        logger.error(err_msg)
        return PaymentProcessingResponse(
            error=True,
            details=err_msg,
            claimId=request.claimId,
            paymentStatus="Failed",
            errorMessage="An unexpected error occurred.",
            escalationAdvice="Please retry the payment process or contact support."
        )