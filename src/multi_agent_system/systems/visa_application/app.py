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
        st.chat_message("user").markdown(msg.text)
    elif msg.role == ChatRole.ASSISTANT:
        st.chat_message("assistant").markdown(msg.text)
    elif msg.role == ChatRole.TOOL:
        tool_result = msg.tool_call_result
        if tool_result:
            st.chat_message("assistant").markdown(
                f"**Tool response:**\n\n{tool_result.result}"
            )


# Chat input
user_input = st.chat_input("Ask about your visa application...")

if user_input:
    user_msg = ChatMessage.from_user(user_input)
    st.session_state.messages.append(user_msg)
    st.chat_message("user").markdown(user_input)

    # Run agent
    new_agent, new_messages = agent.run(st.session_state.messages)
    st.session_state.messages.extend(new_messages)

    # Update agent if it changed
    if new_agent != st.session_state.current_agent_name:
        st.session_state.current_agent_name = new_agent
        st.markdown(f"🆕 **Switched to: {new_agent}**")

    # Display agent messages
    for i, msg in enumerate(new_messages):
        print(f"[DEBUG] Message {i}: role={msg.role}, text={msg.text}")
        if msg.role == ChatRole.ASSISTANT:
            st.chat_message("assistant").markdown(msg.text)
        elif msg.role == ChatRole.TOOL:
            tool_result = msg.tool_call_result
            if tool_result:
                st.chat_message("assistant").markdown(
                    f"**Tool response:**\n\n{tool_result.result}"
                )
