"""This module implements the agents as well as their tools for the Visa Application System."""

from typing import Annotated
from datetime import datetime
import random

from multi_agent_system.agents import SwarmAgent
from multi_agent_system.providers import LLMProvider


HANDOFF_TEMPLATE = "Transferred to: {agent_name}. Adopt persona immediately."

status_agent_instructions = (
    "You are a Status Agent at German Embassy in Iran. "
    "1. Help the applicant with his application's status and executing cancellations. "
    "2. Ask for basic information like name and tracking number. "
    "3. If the status is 'REJECTED', inform the applicant about the reason. "
    "4. If the status is 'CANCELLED', inform the applicant about the cancellation date. "
    "5. If the applicant requires about cancellation of his application, ask for the tracking number and process the cancellation. "
    "6. Only after a successful cancellation, tell them that they cannot apply for the same visa type again within 6 months. "
    "7. If the applicant is interested in the fees for different types of visas, send him to Finance Agent. "
    "8. If the applicant is interested in the necessary application documents, send him to Eligibility Agent. "
    "9. Make tool calls only if necessary and make sure to provide the right arguments."
)


def check_status(
    applicant_name: Annotated[str, "The name of the applicant to check the status for"],
    tracking_number: Annotated[
        str, "The tracking number of the application to check the status for"
    ],
) -> str:
    status = random.choice(range(0, 5))

    # Base message
    message = (
        f"Report: Applicant '{applicant_name}' with tracking number '{tracking_number}' found successfully.\n"
        f"Application Status: {status}."
    )

    # Append specific notes based on the status
    if status == "REJECTED":
        message += " Reason: Missing documents. Please contact the Eligibility Agent."
    elif status == "CANCELLED":
        cancellation_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message += f" Note: The application was cancelled on {cancellation_time}."

    return message


# A tool that enables the agent to complete a task
def execute_cancellation(
    tracking_number: Annotated[str, "The tracking number of the application to cancel"],
) -> str:
    """Only call this if explicitly asked to."""
    print("Tracking number for cancellation:", tracking_number)
    confirm = input("Confirm cancellation? (y/n): ").strip().lower()
    if confirm == "y":
        print("Cancellation confirmed.")
        return f"Cancellation for tracking number {tracking_number} has been successfully processed!"
    else:
        print("Cancellation aborted.")
        return "Cancellation aborted."


# A transfer call to another agent
def transfer_to_eligibility() -> str:
    """Pass to this agent for anything related to required documents for a visa"""
    return HANDOFF_TEMPLATE.format(agent_name="Eligibility Agent")


# A transfer call to another agent
def transfer_to_finance() -> str:
    """Pass to this agent for anything related to finances and fees"""
    return HANDOFF_TEMPLATE.format(agent_name="Finance Agent")


status_agent = SwarmAgent(
    name="Status Agent",  # Name of the agent in the system
    llm=LLMProvider.connect("openai"),
    instructions=status_agent_instructions,
    functions=[
        check_status,
        execute_cancellation,
        transfer_to_eligibility,
        transfer_to_finance,
    ],
)
