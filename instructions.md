# Claims Management BPMN Process — User Testing Instructions

This guide provides step-by-step instructions for interacting with the Claims Management Process via Teams or Copilot, targeting realistic test scenarios using the provided sample inputs. You will test each stage and agent in the BPMN workflow, helping validate data capture, validation, assignment, investigation, decision, payment, notifications, and claim closure.

---

## Table of Contents

1. [Overview of the BPMN Process](#overview)
2. [Testing Scenarios](#testing-scenarios)
   - [Scenario 1: Valid Auto Claim (End-to-End Happy Path)](#scenario-1-valid-auto-claim)
   - [Scenario 2: Incomplete Health Claim (Request Additional Info Loop)](#scenario-2-incomplete-health-claim)
   - [Scenario 3: Rejected Home Claim (Fraud Suspected)](#scenario-3-rejected-home-claim)
   - [Scenario 4: Multi-Stage Auto Claim (Missing Data, Then Approved)](#scenario-4-multi-stage-auto-claim)
   - [Scenario 5: Payment Failure Claim](#scenario-5-payment-failure-claim)
   - [Scenario 6: Duplicate Claim Submissions](#scenario-6-duplicate-claim-submissions)
3. [Instructions for Using Example Inputs](#instructions-for-using-example-inputs)
4. [Agent-Specific Instructions](#agent-specific-instructions)

---

<a name="overview"></a>
## 1. Overview of the BPMN Process

The Claims Management BPMN process involves these major steps:

- **Claim Received → Register Claim → Validate Claim**
    - If incomplete: Loop to Request Additional Info
    - If complete: Proceed to assignment
- **Assign Claim to Examiner → Investigate Claim → Claim Decision (Approve/Reject)**
- **Approved: Process Payment → Notify Claimant (Approval)**
- **Rejected: Notify Claimant (Rejection)**
- **Close Claim → Claim Completed**

Agents are triggered at specific steps and respond according to their instructions.

---

<a name="testing-scenarios"></a>
## 2. Testing Scenarios

### <a name="scenario-1-valid-auto-claim"></a>
#### Scenario 1: Valid Auto Claim (End-to-End Happy Path)

**Purpose:** Test entire workflow from claim registration through payment and closure with all data present.

**Input:**
yaml
claimId: "CLM-001"
claimantInfo:
  name: "Alice Johnson"
  contact: "alice.johnson@email.com"
claimDetails:
  policyNumber: "AUTO-123456"
  incidentDescription: "Rear-ended at traffic lights. Police report attached."
paymentDetails:
  paymentAmount: 2200.00
  accountNumber: "1111222233334444"
  routingNumber: "026009593"


**Instructions:**

1. **Register claim** via Teams/Copilot using the input above.
2. **Validate claim**—verify that all fields are complete.
3. **Assign to examiner**—specify auto or general pool if prompted.
4. **Provide investigation findings** (simulate examiner inputs if asked).
5. **Proceed to decision**—expect approval.
6. **Trigger payment**—provide payment details.
7. **Notify claimant**—check for personalized notification.
8. **Close claim**—confirm all documents and closure notes.

---

### <a name="scenario-2-incomplete-health-claim"></a>
#### Scenario 2: Incomplete Health Claim (Request Additional Info Loop)

**Purpose:** Test agent/system response to missing key field, and that looping/clarification works.

**Input:**
yaml
claimId: "CLM-002"
claimantInfo:
  name: "Robert Smith"
  contact: "robert.smith@email.com"
claimDetails:
  policyNumber: "HEALTH-654321"
  incidentDescription: ""


**Instructions:**

1. **Register claim** using the above info.
2. Observe the **validation agent** prompt for the missing incident description.
3. **Reply** with a correction, e.g., `Incident description: "Hospitalized for appendicitis on 2024-06-10."`
4. Continue process as in Scenario 1 once all fields are present.

---

### <a name="scenario-3-rejected-home-claim"></a>
#### Scenario 3: Rejected Home Claim (Fraud Suspected)

**Purpose:** Test investigation, rejection, and fraud/escalation scenario.

**Input:**
yaml
claimId: "CLM-003"
claimantInfo:
  name: "Ella Martinez"
  contact: "ella.martinez@email.com"
claimDetails:
  policyNumber: "HOME-543210"
  incidentDescription: "Claim for water damage. No supporting documentation provided."
investigationData:
  evidenceSummary: "Inspection found no damage; claimant unable to provide photos or invoices."
  notes: "Discrepancy between claimed damages and actual site visit."


**Instructions:**

1. **Register claim** with initial data.
2. For investigation, **enter findings** as shown above when prompted.
3. At the **decision stage**, expect a "Rejected" or "Escalate" outcome (simulate adverse decision).
4. Verify that notification includes a reason and offers support contact.
5. Attempt closure, ensuring all actions are properly logged.

---

### <a name="scenario-4-multi-stage-auto-claim"></a>
#### Scenario 4: Multi-Stage Auto Claim (Missing Data, Then Approved)

**Purpose:** Test claim with initially missing data, simulate loop for additional info, then successful approval/payment.

**Inputs:**
**Step 1: Submit with missing policy number**
yaml
claimId: "CLM-004"
claimantInfo:
  name: "Mohamed El Amin"
  contact: "amin.mohamed@email.com"
claimDetails:
  policyNumber: ""
  incidentDescription: "Minor collision while parked."

**Step 2: Complete missing field**
yaml
policyNumber: "AUTO-009876"

**Step 3: Payment details**
yaml
paymentAmount: 500.00
accountNumber: "1234000043210000"
routingNumber: "011000138"


**Instructions:**

1. **Register claim** with missing policy number.
2. Respond to validation agent’s prompt for missing data with Step 2 input.
3. Proceed with assignment, investigation, and approval as in Scenario 1.
4. Complete payment with Step 3 input.
5. Confirm notification and claim closure at end.

---

### <a name="scenario-5-payment-failure-claim"></a>
#### Scenario 5: Payment Failure Claim

**Purpose:** Test agent/system response to payment processing failure due to invalid account/routing.

**Input:**
yaml
claimId: "CLM-005"
claimantInfo:
  name: "Linda Wu"
  contact: "linda.wu@email.com"
claimDetails:
  policyNumber: "AUTO-999998"
  incidentDescription: "Fender bender, clear liability."
paymentDetails:
  paymentAmount: 350.00
  accountNumber: "INVALID123"
  routingNumber: "XXXXXXX"


**Instructions:**

1. Complete all upstream steps (registration, validation, investigation, approval).
2. Provide payment details as above; expect the payment agent to reject due to invalid input.
3. Observe the error message; respond with corrected payment details if prompted.
4. Resume process after resolution.

---

### <a name="scenario-6-duplicate-claim-submissions"></a>
#### Scenario 6: Duplicate Claim Submissions

**Purpose:** Test system/agent handling and user experience with multiple, identical claims.

**Input:**
yaml
- claimId: "CLM-006"
  claimantInfo:
    name: "Lucas Brown"
    contact: "lucas.brown@email.com"
  claimDetails:
    policyNumber: "AUTO-321654"
    incidentDescription: "Broken windshield from hailstorm."
- claimId: "CLM-007"
  claimantInfo:
    name: "Lucas Brown"
    contact: "lucas.brown@email.com"
  claimDetails:
    policyNumber: "AUTO-321654"
    incidentDescription: "Broken windshield from hailstorm."


**Instructions:**

1. **Submit both claims simultaneously** (in batch, if supported).
2. Observe if system detects duplicate or flags for review.
3. Note if the agent prompts for user intent regarding the duplicate.
4. Respond as indicated and check audit trails for both claims.

---

<a name="instructions-for-using-example-inputs"></a>
## 3. Instructions for Using Example Inputs

- Copy/paste exact YAML or JSON blocks into your Teams/Copilot interface as appropriate for the workflow step.
- Answer prompts from agents with corrections, confirmations, or further details as required.
- For any missing, invalid, or ambiguous data, provide only what is needed to proceed.

---

<a name="agent-specific-instructions"></a>
## 4. Agent-Specific Instructions

### **Registration (ClaimRegistrationAgent):**
- Provide all required claimant and claim details.
- Confirm details before registration is finalized. Use agent prompts to add or correct data.
- Example complete input:
    yaml
    claimId: "CLM-001"
    claimantInfo:
      name: "Alice Johnson"
      contact: "alice.johnson@email.com"
    claimDetails:
      policyNumber: "AUTO-123456"
      incidentDescription: "Rear-ended at traffic lights."
    

### **Validation (ClaimValidationAgent):**
- Monitor for missing or invalid fields after claim registration.
- Supply only missing/corrected fields when prompted (e.g., "incident description").
- Validate that status is set to "VALID" before proceeding.

### **Assignment & Investigation (ClaimAssignmentInvestigationAgent):**
- Specify assignment criteria (e.g., examiner pool) if prompted.
- If asked, detail evidence summary and investigation notes.

### **Decision Making (ClaimDecisionAgent):**
- On receiving investigation feedback, await structured JSON with decision, rationale, and follow-up.
- If "Additional Info Required" or "Escalate", provide further data or expert review as instructed.

### **Payment Processing (ClaimPaymentAgent):**
- Provide full payment details; handle batch inputs or error corrections as per agent prompts.
- Review and acknowledge payment confirmations or error diagnostics.

### **Notification (ClaimNotificationAgent):**
- Confirm claimant contact info and ensure approved/rejected messages are sent.
- Edit or request revised notifications if needed.

### **Claim Closure (ClaimClosureAgent):**
- Ensure all preceding steps are completed and documented before closure.
- Supply closure notes, if requested, summarizing final state.

---

## Sample User Prompts

- "Register a new claim for Alice Johnson, email alice.johnson@email.com, policy AUTO-123456, incident: rear-ended at traffic lights."
- "Please update incident description for claim CLM-002: Hospitalized for appendicitis."
- "Assign claim CLM-004 from the Auto examiner pool."
- "Process payment for claim CLM-005 using provided details."
- "Notify Lucas Brown regarding claim CLM-006—if duplicate, please prompt for handling."
- "Close claim CLM-001 with note: All steps completed, claimant paid and notified."

---

## Notes

- For each step, respond to agent queries and prompts thoroughly and accurately.
- Always confirm and record claim actions, especially when handling corrections, additional info, or exceptions.
- Maintain privacy and compliance with sensitive data throughout.
- Use agents’ structured output formats for validation at every stage.

---

**End of Instructions**