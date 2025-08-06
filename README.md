
Insurance Claim Conversation Flow – Story Style (Updated)
 

🟢 Step 1: Claim Registration
Q1. 💬 "Hi, I need to file a new insurance claim. My claim ID is CLM-001. I'm Alice Johnson, and my phone number is 9876543210. My policy number is AUTO-123456. I had a rear-end accident at a traffic signal. A police report is attached."

➡ Triggers: ClaimRegistrationTool
✅ Includes: claimId, claimantInfo, claimDetails

🟡 Step 2: Claim Validation
Q2. 💬 "Can you validate the claim CLM-001 with policy number AUTO-123456 and incident: 'Rear-ended at traffic lights. Police report attached.'?"

➡ Triggers: ClaimValidationTool
✅ Includes: claimId, claimDetails

🟠 Step 3: Claim Assignment for Investigation
Q3. 💬 "Assign an investigator for claim CLM-001. This is urgent, so mark the priority as high."

➡ Triggers: ClaimAssignmentInvestigationTool
✅ Includes: claimId, priority: "high"

🔍 Step 4: Claim Decision
Q4. 💬 "Please make a decision for claim CLM-001. Findings show moderate bumper damage, the evidence score is 8.7, and the recommendation is to approve the claim."

➡ Triggers: ClaimDecisionTool
✅ Includes: claimId, investigationData (findings, score, recommendation)

💸 Step 5: Claim Payment
Q5. 💬 "Initiate a payment for claim CLM-001. The approved amount is ₹2200, and the payment should be made via NEFT."

➡ Triggers: ClaimPaymentTool
✅ Includes: claimId, amount, paymentMethod: "NEFT"


📢 Step 6: Claim Notification
Q6. 💬 "Notify Alice Johnson that claim CLM-001 has been approved and ₹2200 has been processed via NEFT."

➡ Triggers: ClaimNotificationTool
✅ Includes: claimId, recipient: "Alice Johnson", message

🔚 Step 7: Claim Closure
Q7. 💬 "Please close claim CLM-001. Add the following closure note: 'Payment completed and documents have been archived successfully.'"

➡ Triggers: ClaimClosureTool
✅ Includes: claimId, closureNotes

		
		FSI Agentic - Insurance - Key Updates: (08/04 - IST)
		 
		Webapp link: FSI 2 Demo - Landing Page
			1. Endpoint Integration:
				○ Successfully integrated the endpoint for the Insurance scenario. (Follow below updated flow)
				○ Note: Please ask only relevant questions to complete the flow. 
					§ Avoid random or out-of-sequence questions.
					§ Do not repeat prefilled questions already shown in the webapp UI (these need to be updated, Informed to Prince).
			2. Response Enhancements:
				○ Endpoint responses now include two new parameters: 
					§ agent_name
					§ tool_name
				○ These help identify which agent/tool generated the response. 
				○ Use browser inspection tools to view these parameters.
				○ Plan needed to display them in the webapp UI (similar to how it's done in Stealth Hub).
			3. Web App Updates require:
				○  UI enhancements including an updated default message for the copilot.
				○  Introduce a structured sequence of follow-up questions to guide user flow.
				○  Create a dedicated subpage for Insurance Assistant, similar to the existing Retail Banking assistant page.
		
	
	
![Uploading image.png…]()
