import logging
import os
import json
import re
import azure.functions as func
from openai import AzureOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logger = logging.getLogger("azure-function")
logger.setLevel(logging.INFO)

# OpenAI client
client = AzureOpenAI(
    azure_endpoint="https://chatgpttest45.openai.azure.com/",
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2023-03-15-preview"
)

DEPLOYMENT_ID = "gpt-4o"

# Tool Schemas
tool_schemas = [
    {
        "name": "ClaimRegistrationTool",
        "description": "Register a new insurance claim in the system.",
        "parameters": {
            "type": "object",
            "properties": {
                "claimId": {"type": "string"},
                "claimantInfo": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "contact": {"type": "string"}
                    },
                    "required": ["name", "contact"]
                },
                "claimDetails": {
                    "type": "object",
                    "properties": {
                        "policyNumber": {"type": "string"},
                        "incidentDescription": {"type": "string"}
                    },
                    "required": ["policyNumber", "incidentDescription"]
                }
            },
            "required": ["claimId", "claimantInfo", "claimDetails"]
        }
    },
    {
        "name": "ClaimClosureTool",
        "description": "Close a claim and archive supporting documents.",
        "parameters": {
            "type": "object",
            "properties": {
                "claimId": {"type": "string"},
                "closureNotes": {"type": "string"}
            },
            "required": ["claimId", "closureNotes"]
        }
    },
    {
        "name": "ClaimDecisionTool",
        "description": "Make a decision on a claim based on investigation data.",
        "parameters": {
            "type": "object",
            "properties": {
                "claimId": {"type": "string"},
                "investigationData": {
                    "type": "object",
                    "properties": {
                        "findings": {"type": "string"},
                        "evidenceScore": {"type": "number"},
                        "recommendation": {"type": "string"}
                    },
                    "required": ["findings", "evidenceScore", "recommendation"]
                }
            },
            "required": ["claimId", "investigationData"]
        }
    },
    {
        "name": "ClaimValidationTool",
        "description": "Validate submitted claim information for completeness and eligibility.",
        "parameters": {
            "type": "object",
            "properties": {
                "claimId": {"type": "string"},
                "claimDetails": {
                    "type": "object",
                    "properties": {
                        "policyNumber": {"type": "string"},
                        "incidentDescription": {"type": "string"}
                    },
                    "required": ["policyNumber", "incidentDescription"]
                },
                "investigationData": {
                    "type": "object",
                    "properties": {
                        "findings": {"type": "string"},
                        "evidenceScore": {"type": "number"},
                        "recommendation": {"type": "string"}
                    }
                }
            },
            "required": ["claimId", "claimDetails"]
        }
    },
    {
        "name": "ClaimAssignmentInvestigationTool",
        "description": "Assign an investigator to the claim for further investigation.",
        "parameters": {
            "type": "object",
            "properties": {
                "claimId": {"type": "string"},
                "priority": {"type": "string"}
            },
            "required": ["claimId", "priority"]
        }
    },
    {
        "name": "ClaimPaymentTool",
        "description": "Initiate claim payment to the claimant.",
        "parameters": {
            "type": "object",
            "properties": {
                "claimId": {"type": "string"},
                "amount": {"type": "number"},
                "paymentMethod": {"type": "string"}
            },
            "required": ["claimId", "amount", "paymentMethod"]
        }
    },
    {
        "name": "ClaimNotificationTool",
        "description": "Notify the claimant about the status of their claim.",
        "parameters": {
            "type": "object",
            "properties": {
                "claimId": {"type": "string"},
                "recipient": {"type": "string"},
                "message": {"type": "string"}
            },
            "required": ["claimId", "recipient", "message"]
        }
    }
]

# Load existing claims
with open("claims_data.json", "r") as f:
    claims_dataset = json.load(f)

def save_claim_to_json_file(new_claim):
    try:
        with open("claims_data.json", "r") as f:
            existing_data = json.load(f)
        existing_data.append(new_claim)
        with open("claims_data.json", "w") as f:
            json.dump(existing_data, f, indent=2)
    except Exception as e:
        logger.error(f"Failed to save claim to file: {e}")

def get_claim_input_by_id(claim_id):
    for record in claims_dataset:
        input_data = record.get("input", {})
        if isinstance(input_data, list):
            for item in input_data:
                if item.get("claimId") == claim_id:
                    return item
        else:
            if input_data.get("claimId") == claim_id:
                return input_data
            if "initial_claim_submission" in input_data and input_data["initial_claim_submission"].get("claimId") == claim_id:
                return input_data["initial_claim_submission"]
    return None

def get_follow_up_questions(tool_name, claim_id):
    return {
        "ClaimRegistrationTool": [
            f"Can you validate the claim {claim_id}?",
            f"Assign an investigator for claim {claim_id}."
        ],
        "ClaimValidationTool": [
            f"What is the next step after validating {claim_id}?",
            f"Assign this for investigation: {claim_id}."
        ],
        "ClaimAssignmentInvestigationTool": [
            f"What’s the update from the investigator for {claim_id}?",
            f"Make a decision on claim {claim_id}."
        ],
        "ClaimDecisionTool": [
            f"Initiate payment for claim {claim_id}.",
            f"Can you explain the decision made for {claim_id}?"
        ],
        "ClaimPaymentTool": [
            f"Has the payment been credited for {claim_id}?",
            f"Notify the claimant about the payment for {claim_id}."
        ],
        "ClaimNotificationTool": [
            f"Can I close claim {claim_id} now?",
            f"Send a reminder to the claimant about {claim_id}."
        ],
        "ClaimClosureTool": [
            f"Show me the summary of closed claim {claim_id}.",
            f"Reopen claim {claim_id} if needed."
        ]
    }.get(tool_name, [f"What else can I do with claim {claim_id}?"])

def get_general_followups():
    return [
        "Would you like to register a new claim?",
        "Do you want me to fetch details for another claim?"
    ]

def simulate_tool_response(function_name, args):
    if function_name == "ClaimRegistrationTool":
        claim_id = args.get("claimId")
        existing_claim = get_claim_input_by_id(claim_id)
        if existing_claim:
            return f"⚠️ Claim ID {claim_id} has already been registered earlier. Here are the details:\n\n" + \
                   json.dumps(existing_claim, indent=2)
        new_claim = {
            "id": f"auto_{claim_id}",
            "description": "Auto-added from runtime registration.",
            "input": args
        }
        claims_dataset.append(new_claim)
        save_claim_to_json_file(new_claim)
        return f"🟢 Claim {claim_id} has been registered successfully."
    elif function_name == "ClaimClosureTool":
        return f"🔚 Claim {args.get('claimId')} has been closed with notes: {args.get('closureNotes')}."
    elif function_name == "ClaimDecisionTool":
        return f"🟠 Decision made for claim {args.get('claimId')} based on findings: {args['investigationData']['findings']}."
    elif function_name == "ClaimValidationTool":
        return f"🔍 Claim {args.get('claimId')} has been validated for policy {args['claimDetails']['policyNumber']}."
    elif function_name == "ClaimAssignmentInvestigationTool":
        return f"🕵️ Claim {args.get('claimId')} has been assigned for investigation with priority {args.get('priority')}."
    elif function_name == "ClaimPaymentTool":
        return f"💸 Payment of ₹{args.get('amount')} for claim {args.get('claimId')} has been initiated via {args.get('paymentMethod')}."
    elif function_name == "ClaimNotificationTool":
        return f"📢 Notification sent to {args.get('recipient')} regarding claim {args.get('claimId')}: {args.get('message')}"
    return "✅ Tool executed successfully."

def infer_agent_name(tool_name):
    base = tool_name.replace("Tool", "")
    words = []
    word = base[0]
    for c in base[1:]:
        if c.isupper():
            words.append(word.lower())
            word = c
        else:
            word += c
    words.append(word.lower())
    return "_".join(words) + "_agent"

# Azure Function Entry
app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="insurance_agent")
async def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        body = req.get_json()
        user_message = body.get("message", "").strip()
        history = body.get("conversation_history", [])

        logger.info(f"User Message: {user_message}")

        # Step 1: Extract claim ID via GPT
        id_response = client.chat.completions.create(
            model=DEPLOYMENT_ID,
            messages=[
                {"role": "system", "content": "Extract the claimId (e.g., CLM-001) from the user query."},
                {"role": "user", "content": user_message}
            ]
        )
        extracted_claim_id = id_response.choices[0].message.content.strip()
        if not extracted_claim_id.startswith("CLM-") and "CLM-" in user_message:
            match = re.search(r"CLM-[0-9]+", user_message)
            if match:
                extracted_claim_id = match.group(0)

        # Step 2: Setup prompt
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a professional insurance assistant helping users with claim registration, validation, decisions, and payments.\n\n"
                    "Respond in a friendly, professional tone. Use **Markdown** for formatting. Keep it concise and useful."
                )
            }
        ] + history + [{"role": "user", "content": user_message}]

        # Add claim context if available
        claim_context = get_claim_input_by_id(extracted_claim_id)
        if claim_context:
            messages.insert(1, {
                "role": "system",
                "content": f"Claim context for {extracted_claim_id}: {json.dumps(claim_context)}"
            })

        # Step 3: GPT response + tool call
        openai_response = client.chat.completions.create(
            model=DEPLOYMENT_ID,
            messages=messages,
            tools=[{"type": "function", "function": tool} for tool in tool_schemas],
            tool_choice="auto"
        )

        tool_call = openai_response.choices[0].message.tool_calls

        if tool_call:
            function_name = tool_call[0].function.name
            function_args = json.loads(tool_call[0].function.arguments)
            tool_result = simulate_tool_response(function_name, function_args)

            messages.append({"role": "assistant", "content": tool_result})
            final_response = client.chat.completions.create(model=DEPLOYMENT_ID, messages=messages)
            return func.HttpResponse(
                json.dumps({
                    "response": final_response.choices[0].message.content.strip(),
                    "agent": infer_agent_name(function_name),
                    "tool": function_name,
                    "followups": get_follow_up_questions(function_name, extracted_claim_id)[:2]
                }),
                status_code=200,
                mimetype="application/json"
            )
        else:
            fallback_response = client.chat.completions.create(model=DEPLOYMENT_ID, messages=messages)
            return func.HttpResponse(
                json.dumps({
                    "response": fallback_response.choices[0].message.content.strip(),
                    "agent": "general_response_agent",
                    "tool": None,
                    "followups": get_general_followups()
                }),
                status_code=200,
                mimetype="application/json"
            )

    except Exception as e:
        logger.exception("Exception occurred")
        return func.HttpResponse(
            json.dumps({"response": f"❌ Internal error: {str(e)}"}),
            status_code=500,
            mimetype="application/json"
        )
