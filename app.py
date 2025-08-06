#!/usr/bin/env python3
"""
Main FastAPI app to handle insurance claim processing using OpenAI function calls and agent routers.
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import logging
import os
from openai import AzureOpenAI
from dotenv import load_dotenv 
from tools.ClaimRegistrationAgentTools import router as ClaimRegistrationAgentTools
from tools.ClaimAssignmentInvestigationAgentTools import router as ClaimAssignmentInvestigationAgentTools
from tools.ClaimDecisionAgentTools import router as ClaimDecisionAgentTools
from tools.ClaimPaymentAgentTools import router as ClaimPaymentAgentTools
from tools.ClaimClosureAgentTools import router as ClaimClosureAgentTools
from tools.ClaimNotificationAgentTools import router as ClaimNotificationAgentTools
from tools.ClaimValidationAgentTools import router as ClaimValidationAgentTools

# Load environment variables
load_dotenv()

# Setup logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app")

# --------------------------
# FastAPI App Initialization
# --------------------------
app = FastAPI(title="Insurance Claim AI Agent System")

# --------------------------
# CORS
# --------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------
# OpenAI Client Configuration
# -------------------------- 
client = AzureOpenAI(
    azure_endpoint="https://chatgpttest45.openai.azure.com/",
    api_key='9dcb9b4900584019ab8f2c23eb8643d7',
    api_version='2023-03-15-preview',
)

DEPLOYMENT_ID = "gpt-4o"

# --------------------------
# Include Routers
# --------------------------
app.include_router(ClaimRegistrationAgentTools)
logger.info("✅ Included router from: ClaimRegistrationAgentTools")

app.include_router(ClaimAssignmentInvestigationAgentTools)
logger.info("✅ Included router from: ClaimAssignmentInvestigationAgentTools")

app.include_router(ClaimDecisionAgentTools)
logger.info("✅ Included router from: ClaimDecisionAgentTools")

app.include_router(ClaimPaymentAgentTools)
logger.info("✅ Included router from: ClaimPaymentAgentTools")

app.include_router(ClaimClosureAgentTools)
logger.info("✅ Included router from: ClaimClosureAgentTools")

app.include_router(ClaimNotificationAgentTools)
logger.info("✅ Included router from: ClaimNotificationAgentTools")

app.include_router(ClaimValidationAgentTools)
logger.info("✅ Included router from: ClaimValidationAgentTools")

# --------------------------
# /ask endpoint
# --------------------------
from fastapi.testclient import TestClient
import json

client_internal = TestClient(app)

@app.post("/ask")
async def ask(request: Request):
    try:
        body = await request.json()
        user_message = body.get("message", "").strip()
        logger.info(f"📩 User question: {user_message}")

        response = client.chat.completions.create(
            model=DEPLOYMENT_ID,
            messages=[
                {"role": "system", "content": "You are a helpful insurance assistant."},
                {"role": "user", "content": user_message}
            ],
            tools=[
                {
                    "type": "function",
                    "function": {
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
                    }
                },
                {
                    "type": "function",
                    "function": {
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
                    }
                },
                {
                    "type": "function",
                    "function": {
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
                    }
                },
                {
                    "type": "function",
                    "function": {
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
                                    },
                                    "required": []
                                }
                            },
                            "required": ["claimId", "claimDetails"]
                        }
                    }
                }
            ],
            tool_choice="auto"
        )

        if not response.choices or not response.choices[0].message.tool_calls:
            return {"message": "🛑 Sorry, I couldn't understand the request. Could you rephrase?"}

        tool_call = response.choices[0].message.tool_calls[0]
        function_name = tool_call.function.name
        function_args = json.loads(tool_call.function.arguments)

        logger.info(f"🛠️ Tool to call: {function_name}")
        logger.info(f"📦 Payload: {function_args}")

        return {
            "function_name": function_name,
            "payload": function_args
        }

    except Exception as e:
        logger.exception("Internal error")
        return JSONResponse(
            content={"message": f"❌ Internal error: {str(e)}"},
            status_code=500
        )

# --------------------------
# Run with Uvicorn
# --------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
