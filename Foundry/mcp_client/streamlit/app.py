"""
AI Foundry Chat - Streamlit Interface

A web-based chat interface for AI Foundry agents using Streamlit.
Features:
- Agent name input
- Chat interface with conversation history
- Real-time display of agent metadata (Agent ID, Thread ID, Message Count)
"""

import streamlit as st
import sys
import os
from typing import List, Dict, Optional

# Add the parent directory to the path to import ai_foundry_agent
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from ai_foundry_agent import invoke_agent
except ImportError as e:
    st.error(f"❌ Error importing ai_foundry_agent: {e}")
    st.error("Make sure the ai_foundry_agent package is available")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="AI Foundry Chat",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "agent_name" not in st.session_state:
    st.session_state.agent_name = ""

if "agent_id" not in st.session_state:
    st.session_state.agent_id = ""

if "thread_id" not in st.session_state:
    st.session_state.thread_id = ""

if "message_count" not in st.session_state:
    st.session_state.message_count = 0

if "chat_started" not in st.session_state:
    st.session_state.chat_started = False

def send_message_to_agent(agent_name: str, user_message: str, thread_id: Optional[str] = None) -> Dict:
    """Send a message to the AI Foundry agent"""
    try:
        result = invoke_agent(agent_name, user_message, thread_id=thread_id)
        return result
    except Exception as e:
        return {
            "error": str(e),
            "agent_name": agent_name,
            "thread_id": thread_id,
            "response": [
                {
                    "role": "ERROR",
                    "content": f"Failed to send message: {str(e)}"
                }
            ]
        }

def display_chat_message(role: str, content: str):
    """Display a chat message with appropriate styling"""
    if role.upper() == "USER":
        with st.chat_message("user"):
            st.write(content)
    elif role.upper() == "ASSISTANT":
        with st.chat_message("assistant"):
            st.write(content)
    elif role.upper() == "ERROR":
        with st.chat_message("assistant"):
            st.error(content)

def main():
    """Main Streamlit application"""
    
    # Title and header
    st.title("🤖 AI Foundry Chat Interface")
    st.markdown("---")
    
    # Create layout with columns
    chat_col, info_col = st.columns([3, 1])
    
    with info_col:
        st.subheader("📊 Session Info")
        
        # Agent name input
        agent_name_input = st.text_input(
            "Agent Name:",
            value=st.session_state.agent_name,
            placeholder="Enter the Agent Name",
            help="Enter the name of the AI Foundry agent to chat with"
        )
        
        # Update agent name if changed
        if agent_name_input != st.session_state.agent_name:
            st.session_state.agent_name = agent_name_input
            # Reset chat if agent name changed
            if st.session_state.chat_started:
                st.session_state.messages = []
                st.session_state.agent_id = ""
                st.session_state.thread_id = ""
                st.session_state.message_count = 0
                st.session_state.chat_started = False
                st.rerun()
        
        st.markdown("---")
        
        # Display session information
        if st.session_state.agent_name:
            st.markdown("**Agent Name:**")
            st.code(st.session_state.agent_name)
        else:
            st.markdown("**Agent Name:** *Not set*")
        
        if st.session_state.agent_id:
            st.markdown("**Agent ID:**")
            st.code(st.session_state.agent_id)
        else:
            st.markdown("**Agent ID:** *Not available*")
        
        if st.session_state.thread_id:
            st.markdown("**Thread ID:**")
            st.code(st.session_state.thread_id)
        else:
            st.markdown("**Thread ID:** *Not started*")
        
        st.markdown("**Message Count:**")
        st.code(str(st.session_state.message_count))
        
        st.markdown("---")
        
        # Clear chat button
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.agent_id = ""
            st.session_state.thread_id = ""
            st.session_state.message_count = 0
            st.session_state.chat_started = False
            st.rerun()
        
        # Instructions
        st.markdown("---")
        st.markdown("**Instructions:**")
        st.markdown("""
        1. Enter an agent name above
        2. Type your message in the chat
        3. View conversation history
        4. Monitor session info on the right
        """)
    
    with chat_col:
        st.subheader("💬 Chat")
        
        # Check if agent name is provided
        if not st.session_state.agent_name.strip():
            st.warning("⚠️ Please enter an agent name in the sidebar to start chatting.")
            return
        
        # Display chat history
        for message in st.session_state.messages:
            display_chat_message(message["role"], message["content"])
        
        # Chat input
        user_input = st.chat_input("Type your message here...")
        
        if user_input:
            # Add user message to chat history
            st.session_state.messages.append({"role": "USER", "content": user_input})
            
            # Display user message
            with st.chat_message("user"):
                st.write(user_input)
            
            # Send message to agent
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    result = send_message_to_agent(
                        st.session_state.agent_name,
                        user_input,
                        thread_id=st.session_state.thread_id if st.session_state.thread_id else None
                    )
                
                # Handle response
                if "error" in result:
                    error_msg = f"Error: {result['error']}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "ERROR", "content": error_msg})
                else:
                    # Update session information
                    st.session_state.agent_id = result.get("agent_id", "")
                    st.session_state.thread_id = result.get("thread_id", "")
                    st.session_state.chat_started = True
                    
                    # Process response messages
                    for msg in result.get("response", []):
                        role = msg.get("role", "UNKNOWN")
                        content = msg.get("content", "")
                        
                        if role.upper() == "ASSISTANT":
                            st.write(content)
                            st.session_state.messages.append({"role": "ASSISTANT", "content": content})
                        elif role.upper() == "ERROR":
                            st.error(content)
                            st.session_state.messages.append({"role": "ERROR", "content": content})
                    
                    # Update message count
                    st.session_state.message_count += 1
            
            # Force rerun to update the sidebar info
            st.rerun()

if __name__ == "__main__":
    main()