"""
This module implements the agents as well as
their tools for the Visa Application system.
"""

import random
from datetime import datetime
from typing import Annotated

from haystack.utils import Secret

from multi_agent_system.agents import SwarmAgent
from multi_agent_system.providers import LLMProvider

APPLICATION_STATUS = ["IN PROCESS", "APPROVED", "REJECTED", "CANCELLED"]
REJECTION_REASONS = [
    "missing documents",
    "security check was not successful",
    "bank account balance was not enough",
]
HANDOFF_TEMPLATE = "Transferred to: {agent_name}. Adopt persona immediately."


# Define the tools that the agents can use
def check_status(
    applicant_name: Annotated[str, "The name of the applicant to check the status for"],
    tracking_number: Annotated[
        str, "The tracking number of the application to check the status for"
    ],
) -> str:
    status = random.choice(APPLICATION_STATUS)
    rejection_reason = random.choice(REJECTION_REASONS)

    # Base message
    message = (
        f"Report: Applicant '{applicant_name}' with "
        f"tracking number '{tracking_number}' found successfully.\n"
        f"Application Status: {status}."
    )

    # Append specific notes based on the status
    if status == "REJECTED":
        message += f" Reason: {rejection_reason}. Please contact the Eligibility Agent."
    elif status == "CANCELLED":
        cancellation_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message += f" Note: The application was cancelled on {cancellation_time}."

    return message


def execute_cancellation(
    tracking_number: Annotated[str, "The tracking number of the application to cancel"],
) -> str:
    """Only call this if explicitly asked to."""
    print("Tracking number for cancellation:", tracking_number)
    confirm = input("Confirm cancellation? (y/n): ").strip().lower()
    if confirm == "y":
        print("Cancellation confirmed.")
        return (
            f"Cancellation for tracking number {tracking_number} "
            "has been successfully processed!"
        )
    else:
        print("Cancellation aborted.")
        return "Cancellation aborted."


def transfer_to_status() -> str:
    """Pass to this agent for anything related to application status"""
    return HANDOFF_TEMPLATE.format(agent_name="Status Agent")


def transfer_to_eligibility() -> str:
    """Pass to this agent for anything related to required documents for a visa"""
    return HANDOFF_TEMPLATE.format(agent_name="Eligibility Agent")


def transfer_to_finance() -> str:
    """Pass to this agent for anything related to finances and fees"""
    return HANDOFF_TEMPLATE.format(agent_name="Finance Agent")


def calculate_fees(visa_type: Annotated[str, "The name of visa type"]) -> str:
    visa_type_lowered = visa_type.lower()
    calculated_fee = {
        "student": "The fee for a student visa is 500 Euro",
        "work": "The fee for a work visa is 1000 Euro",
        "tourist": "The fee for a tourist visa is 200 Euro",
    }
    
    return calculated_fee.get(
        visa_type_lowered,
        "The provided visa type is not recognized. "
        "Please enter one of the following: 'student', 'work', or 'tourist'."
    )


# Introduce the LLM provider and connect to it
provider = "openai"
params = {
    "api_key": Secret.from_env_var("API_KEY_OPENAI"),
    "model": "gpt-4o-mini",
}

llm = LLMProvider(provider=provider).connect(**params)

# Define the agents with their respective instructions and tools
status_agent = SwarmAgent(
    name="Status Agent",
    llm=llm,
    instructions=(
        "You are a Status Agent at German Embassy in Iran. "
        "1. Help the applicant with his application's status "
        "and executing cancellations. "
        "2. Ask for basic information like name and tracking number. "
        "3. If the status is 'REJECTED', inform the applicant about the reason. "
        "4. If the status is 'CANCELLED', inform the applicant "
        "about the cancellation date. "
        "5. If the applicant requires about cancellation of "
        "his application, ask for the tracking number "
        "and process the cancellation. "
        "6. Only after a successful cancellation, tell them "
        "that they cannot apply "
        "for the same visa type again within 6 months. "
        "7. If the applicant is interested in the fees for "
        "different types of visas, "
        "send him to Finance Agent. "
        "8. If the applicant is interested in the necessary "
        "application documents, send him to Eligibility Agent. "
        "9. Make tool calls only if necessary and make sure to provide "
        "the right arguments."
    ),
    functions=[
        check_status,
        execute_cancellation,
        transfer_to_eligibility,
        transfer_to_finance,
    ],
)

eligibility_agent = SwarmAgent(
    name="Eligibility Agent",
    llm=llm,
    instructions=(
        "You are an Eligibility Agent at the German Embassy in Iran. "
        "1. Provide the applicant with the list of necessary application documents. "
        "2. There are three types of visa ('student', 'work', 'tourist') and for "
        "each you can make up a list of required documents. "
        "3. Ask for the type of visa before generating any response. "
        "4. If the applicant asks questions related to status of his application, "
        "send him to Status Agent. "
        "5. If the applicant is interested in the fees for different types of visas, "
        "send him to Finance Agent. "
        "6. Make tool calls only if necessary."
    ),
    functions=[transfer_to_status, transfer_to_finance],
)

finance_agent = SwarmAgent(
    name="Finance Agent",
    llm=llm,
    instructions=(
        "You are a Finance Agent at the German Embassy in Iran. "
        "1. You provide the applicant with information about fees "
        "(in Euro) for different types of visas. "
        "2. Ask for the type of the visa the applicant applied for. "
        "It could be of type 'student', 'work', or 'tourist'. "
        "3. Do not make up fees for visa types and always make proper "
        "tool calls to calculate the fee. "
        "4. If the provided visa type by the applicant is not among the "
        "three, ask again the user to enter the visa type. "
        "5. If applicant is interested in the status of his "
        "application, send him to Status Agent. "
        "6. If the applicant looks for application "
        "documents, send him to Eligibility Agent. "
        "7. Make tool calls only if necessary and make sure "
        "to provide the right arguments. "
        "8. Always return a reponse to the applicant "
        "whenever he asks a question."
    ),
    functions=[transfer_to_status, transfer_to_eligibility, calculate_fees],
)
