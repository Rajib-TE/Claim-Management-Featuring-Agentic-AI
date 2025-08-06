import logging
import os
import json
import azure.functions as func
from openai import AzureOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logger = logging.getLogger("azure-function")
logger.setLevel(logging.INFO)

# OpenAI client setup
client = AzureOpenAI(
    azure_endpoint="https://chatgpttest45.openai.azure.com/",
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2023-03-15-preview"
)

DEPLOYMENT_ID = "gpt-4o"

# --------------------------
# Tool Schemas: All 7 tools
# --------------------------
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

# --------------------------
# Simulated Tool Responses
# --------------------------
def simulate_tool_response(function_name, args):
    if function_name == "ClaimRegistrationTool":
        return f"🟢 Claim {args.get('claimId')} has been registered successfully."
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

# --------------------------
# Azure Function Entry Point
# --------------------------
app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="insurance_agent")
async def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        body = req.get_json()
        user_message = body.get("message", "").strip()
        logger.info(f"User Message: {user_message}")

        # Step 1: Tool selection
        openai_response = client.chat.completions.create(
            model=DEPLOYMENT_ID,
            messages=[
                {"role": "system", "content": "You are a helpful insurance assistant."},
                {"role": "user", "content": user_message}
            ],
            tools=[{"type": "function", "function": tool} for tool in tool_schemas],
            tool_choice="auto"
        )

        tool_call = openai_response.choices[0].message.tool_calls

        # Step 2: If tool was selected
        if tool_call:
            function_name = tool_call[0].function.name
            function_args = json.loads(tool_call[0].function.arguments)
            logger.info(f"Tool to call: {function_name}")
            logger.info(f"Args: {function_args}")

            tool_result = simulate_tool_response(function_name, function_args)

            # Step 3: Natural language explanation
            final_response = client.chat.completions.create(
                model=DEPLOYMENT_ID,
                messages=[
                    {"role": "system", "content": "You are a helpful insurance assistant. Explain the result in natural language."},
                    {"role": "user", "content": f"User asked: {user_message}"},
                    {"role": "assistant", "content": tool_result}
                ]
            )

            return func.HttpResponse(
                json.dumps({"response": final_response.choices[0].message.content.strip()}),
                status_code=200,
                mimetype="application/json"
            )

        else:
            logger.warning("No tool was triggered.")
            return func.HttpResponse(
                json.dumps({"response": "⚠️ No tool was selected for this query. Please check your input or tool configuration."}),
                status_code=200,
                mimetype="application/json"
            )

    except Exception as e:
        logger.exception("Internal error")
        return func.HttpResponse(
            json.dumps({"response": f"❌ Internal error: {str(e)}"}),
            status_code=500,
            mimetype="application/json"
        )
