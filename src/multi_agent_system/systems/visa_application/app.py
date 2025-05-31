import streamlit as st
from haystack.dataclasses import ChatMessage, ChatRole

from multi_agent_system.systems.visa_application.setup import (
    status_agent,
)

st.set_page_config(page_title="Visa Application System", layout="wide")

st.title("Visa Application System")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    if msg.role == ChatRole.USER:
        st.chat_message("User").markdown(msg.text)
    elif msg.role == ChatRole.ASSISTANT:
        st.chat_message("Assistant").markdown(msg.text)
    elif msg.role == ChatRole.TOOL:
        tool_result = msg.tool_call_result
        if tool_result:
            st.chat_message("Assistant").markdown(
                f"**Tool response:**\n\n{tool_result.result}"
            )


# Chat input
user_input = st.chat_input("Ask about your visa application...")

if user_input:
    user_msg = ChatMessage.from_user(user_input)
    st.session_state.messages.append(user_msg)
    st.chat_message("user").markdown(user_input)

    new_agent, new_messages = status_agent.run(st.session_state.messages)
    st.session_state.messages.extend(new_messages)

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
