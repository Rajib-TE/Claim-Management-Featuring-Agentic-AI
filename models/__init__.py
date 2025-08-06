#!/usr/bin/env python3
"""
Pydantic models for the Claims Management Process.

This module defines the data structures shared across FastAPI routers 
and various agents in the claims management BPMN process.

Models include representations for claim registration,
validation, payment processing, decision making, notification, and closure.
Also included is an in‐memory repository class for simulating persistent storage.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime


# ------------------------------
# Generic Tool Response Model
# ------------------------------
class ToolResponse(BaseModel):
    error: bool = Field(..., description="Indicates if an error occurred")
    details: str = Field(..., description="Details about the error")


# ------------------------------
# Basic Claim Information Models
# ------------------------------
class ClaimantInfo(BaseModel):
    name: str = Field(..., description="Name of the claimant")
    contact: str = Field(..., description="Contact details of the claimant")


class ClaimDetails(BaseModel):
    policyNumber: str = Field(..., description="The policy number associated with the claim")
    incidentDescription: str = Field(..., description="Description of the incident reported in the claim")


class PaymentDetails(BaseModel):
    paymentAmount: float = Field(..., description="The amount to be paid for the claim")
    accountNumber: str = Field(..., description="Bank account number for payment")
    routingNumber: str = Field(..., description="Bank routing number for payment")


class InvestigationData(BaseModel):
    evidenceSummary: str = Field(..., description="Summary of the evidence collected during investigation")
    notes: str = Field(..., description="Additional investigation notes and observations")


class AdditionalInfoResponse(BaseModel):
    policyNumber: Optional[str] = Field(None, description="Updated policy number if provided later")
    incidentDescription: Optional[str] = Field(None, description="Updated incident description if provided later")


# ------------------------------
# Input Models for Various Process Steps
# ------------------------------
class ClaimRegistrationInput(BaseModel):
    claimId: str = Field(..., description="Unique identifier for the claim")
    claimantInfo: ClaimantInfo = Field(..., description="Information about the claimant")
    claimDetails: ClaimDetails = Field(..., description="Claim details submitted during registration")
    paymentDetails: Optional[PaymentDetails] = Field(
        None, description="Optional payment details provided during registration"
    )


class MultiStageClaimInput(BaseModel):
    """
    For claims that undergo multiple stages.
    Contains the initial submission, optional additional info response,
    and updated payment details.
    """
    initial_claim_submission: ClaimRegistrationInput = Field(
        ..., description="Initial claim submission data"
    )
    additional_info_response: Optional[AdditionalInfoResponse] = Field(
        None, description="Additional information provided to complete the claim"
    )
    paymentDetails: Optional[PaymentDetails] = Field(
        None, description="Payment details provided after claim approval or update"
    )


class ClaimValidationInput(BaseModel):
    claimId: str = Field(..., description="Unique identifier for the claim")
    claimDetails: ClaimDetails = Field(..., description="Claim details to be validated")
    investigationData: Optional[InvestigationData] = Field(
        None, description="Investigation data available during validation (if any)"
    )


class ClaimDecisionInput(BaseModel):
    claimId: str = Field(..., description="Unique identifier for the claim")
    investigationData: InvestigationData = Field(
        ..., description="Investigation report details for decision making"
    )
    claimDetails: Optional[ClaimDetails] = Field(
        None, description="Original claim details as registered (optional)"
    )
    additionalContext: Optional[str] = Field(
        None, description="Any additional context provided with the decision request"
    )
    userCorrectionsOrQuestions: Optional[str] = Field(
        None, description="User corrections or queries regarding the claim"
    )


class PaymentProcessingInput(BaseModel):
    claimId: str = Field(..., description="Unique identifier for the claim")
    paymentDetails: PaymentDetails = Field(
        ..., description="Payment details necessary for processing the claim payout"
    )


class DuplicateClaimSubmissionInput(BaseModel):
    claims: List[ClaimRegistrationInput] = Field(
        ..., description="List of claim submissions to check for duplicates"
    )


class ClaimClosureInput(BaseModel):
    claimId: str = Field(..., description="Unique identifier for the claim to be closed")
    closureNotes: Optional[str] = Field(
        None, description="Optional notes regarding the closure of the claim"
    )


class ClaimNotificationInput(BaseModel):
    claimId: str = Field(..., description="Unique identifier for the claim")
    claimantContact: str = Field(..., description="Contact details of the claimant (email or phone)")
    outcome: str = Field(..., description="Outcome of the claim (e.g., approved or rejected)")
    claimantName: Optional[str] = Field(None, description="Name of the claimant for personalization")
    rejectionReason: Optional[str] = Field(
        None, description="Reason for rejection, if applicable"
    )


# ------------------------------
# In-Memory Repository Classes
# ------------------------------
class ClaimRepository:
    """
    A repository class to simulate storage and retrieval of claim registrations.
    """

    def __init__(self):
        self._claims: List[ClaimRegistrationInput] = []

    def add_claim(self, claim: ClaimRegistrationInput) -> None:
        self._claims.append(claim)

    def get_all_claims(self) -> List[ClaimRegistrationInput]:
        return self._claims

    def find_by_claimId(self, claimId: str) -> Optional[ClaimRegistrationInput]:
        for claim in self._claims:
            if claim.claimId == claimId:
                return claim
        return None

    def delete_by_claimId(self, claimId: str) -> None:
        self._claims = [claim for claim in self._claims if claim.claimId != claimId]


class PaymentRepository:
    """
    A repository class to simulate storing payment processing results.
    """
    def __init__(self):
        self._payments: List[PaymentProcessingInput] = []

    def add_payment(self, payment: PaymentProcessingInput) -> None:
        self._payments.append(payment)

    def get_all_payments(self) -> List[PaymentProcessingInput]:
        return self._payments

    def find_payment_by_claimId(self, claimId: str) -> Optional[PaymentProcessingInput]:
        for payment in self._payments:
            if payment.claimId == claimId:
                return payment
        return None

    def delete_payment_by_claimId(self, claimId: str) -> None:
        self._payments = [p for p in self._payments if p.claimId != claimId]


class ClosureRepository:
    """
    A repository class to simulate storing claim closure records.
    """
    def __init__(self):
        self._closures: List[ClaimClosureInput] = []

    def add_closure(self, closure: ClaimClosureInput) -> None:
        self._closures.append(closure)

    def get_all_closures(self) -> List[ClaimClosureInput]:
        return self._closures

    def find_closure_by_claimId(self, claimId: str) -> Optional[ClaimClosureInput]:
        for closure in self._closures:
            if closure.claimId == claimId:
                return closure
        return None

    def delete_closure_by_claimId(self, claimId: str) -> None:
        self._closures = [c for c in self._closures if c.claimId != claimId]


# ------------------------------
# Repository Seeding Data
# ------------------------------
# Seeding ClaimRepository with one valid claim as an example.
claim_repo = ClaimRepository()
claim_repo.add_claim(
    ClaimRegistrationInput(
        claimId="CLM-001",
        claimantInfo=ClaimantInfo(name="Alice Johnson", contact="alice.johnson@email.com"),
        claimDetails=ClaimDetails(
            policyNumber="AUTO-123456",
            incidentDescription="Rear-ended at traffic lights. Police report attached."
        ),
        paymentDetails=PaymentDetails(
            paymentAmount=2200.00,
            accountNumber="1111222233334444",
            routingNumber="026009593"
        )
    )
)

# Note: The above seeding is provided only for testing purposes.
# Additional repositories (PaymentRepository, ClosureRepository) can be similarly seeded if needed.

# End of module.