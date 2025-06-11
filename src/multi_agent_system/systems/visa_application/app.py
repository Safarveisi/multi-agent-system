import streamlit as st
from haystack.dataclasses import ChatMessage, ChatRole

from multi_agent_system.systems.visa_application.setup import (
    eligibility_agent,
    finance_agent,
    status_agent,
)

agents = {
    agent.name: agent for agent in [status_agent, eligibility_agent, finance_agent]
}

st.set_page_config(page_title="Visa Application Assistant", layout="wide")

st.title("Visa Application Assistant")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "current_agent_name" not in st.session_state:
    st.session_state.current_agent_name = "Status Agent"

agent = agents[st.session_state.current_agent_name]

# Display chat history
for msg in st.session_state.messages:
    if msg.role == ChatRole.USER:
        st.chat_message("User").markdown(msg.text)
    else:  # If the role is not USER, it must be ASSISTANT or TOOL
        if msg.text:  # Only display if there's text
            st.chat_message("Assistant").markdown(
                msg.text
            )  # Skip TOOL messages for now

# Chat input
user_input = st.chat_input(
    "Ask visa related questions (e.g. 'What is the status of my application?')"
)

if user_input:
    st.session_state.messages.append(ChatMessage.from_user(user_input))
    st.chat_message("User").markdown(user_input)

    # Run agent
    run_result = agent.run(st.session_state.messages)
    if run_result["current_agent_message"] is not None:  # It may be a tool call
        st.chat_message("Assistant").markdown(run_result["current_agent_message"])

    # Update messages and agent
    new_agent_name, new_messages = (
        run_result["new_agent_name"],
        run_result["new_messages"],
    )

    if new_messages and new_messages[-1].role == ChatRole.TOOL:
        run_result = agent.run(st.session_state.messages + new_messages)
        st.session_state.messages.extend(run_result["new_messages"])
        st.session_state.messages.extend(new_messages)
        st.chat_message("Assistant").markdown(run_result["current_agent_message"])
        if st.session_state.current_agent_name != new_agent_name:
            st.session_state.current_agent_name = new_agent_name
            agent = agents[st.session_state.current_agent_name]

            run_result = agent.run(st.session_state.messages)
            st.session_state.messages.extend(run_result["new_messages"])
            st.chat_message("Assistant").markdown(run_result["current_agent_message"])
    else:
        st.session_state.messages.extend(new_messages)
