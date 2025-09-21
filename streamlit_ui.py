import streamlit as st
from perplexity_backend import initialize_perplexity_system, handle_user_query

# Set API key from Streamlit secrets
import os
os.environ["PERPLEXITY_API_KEY"] = st.secrets["PERPLEXITY_API_KEY"]

# Page configuration
st.title("KDijagnostika Customer Support")
st.write("Welcome to KDijagnostika Customer Support. Ask about automotive diagnostics, Delphi/Autocom interfaces, troubleshooting, and more!")

# Initialize session state for Perplexity system
if "perplexity_client" not in st.session_state:
    st.session_state["perplexity_client"], st.session_state["chat_history"] = initialize_perplexity_system()

# Initialize messages for UI display
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# User input
user_input = st.chat_input("Ask me about automotive diagnostics...")

if user_input:
    # Add user message to UI messages
    st.session_state["messages"].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    # Show loading spinner while processing
    with st.spinner("Searching and analyzing..."):
        # Get response from Perplexity
        response, updated_history = handle_user_query(
            st.session_state["perplexity_client"], 
            user_input, 
            st.session_state["chat_history"]
        )

    # Update chat history
    st.session_state["chat_history"] = updated_history

    # Add assistant response to UI messages
    st.session_state["messages"].append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.write(response)

# Sidebar with additional options
with st.sidebar:
    st.header("Chat Options")
    
    if st.button("Clear Chat History"):
        st.session_state["messages"] = []
        st.session_state["chat_history"] = []
        st.rerun()
    
    st.markdown("---")
    st.markdown("Real-time web search for automotive diagnostics")