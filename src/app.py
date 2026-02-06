import streamlit as st
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from chatbot import ChatBot
from config import OLLAMA_CONFIG


# Page config
st.set_page_config(
    page_title="PDF Chatbot",
    page_icon="📚",
    layout="centered"
)

# Initialize chatbot
@st.cache_resource
def load_chatbot():
    return ChatBot(config=OLLAMA_CONFIG)


def main():
    st.title("📚 PDF Chatbot")
    st.markdown("Ask questions about your PDF documents")
    
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "chatbot" not in st.session_state:
        with st.spinner("Loading chatbot..."):
            st.session_state.chatbot = load_chatbot()
    
    # Sidebar
    with st.sidebar:
        st.header("About")
        st.markdown("This chatbot answers questions based on your PDF documents.")
        
        if st.button("Clear Chat History"):
            st.session_state.messages = []
            st.session_state.chatbot.clear_history()
            st.rerun()
        
        st.markdown("---")
        st.markdown("**Configuration**")
        st.markdown(f"Model: `{OLLAMA_CONFIG['model']}`")
        st.markdown(f"Base URL: `{OLLAMA_CONFIG['base_url']}`")
        st.markdown(f"Temperature: `{OLLAMA_CONFIG['temperature']}`")
        st.markdown(f"Max Tokens: `{OLLAMA_CONFIG['max_tokens']}`")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Show sources if available
            if message["role"] == "assistant" and "sources" in message and message["sources"]:
                with st.expander("📄 Sources"):
                    for source in set(message["sources"]):
                        st.markdown(f"- {source}")
    
    # Chat input
    if prompt := st.chat_input("Ask a question about your documents..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                answer, sources = st.session_state.chatbot.chat(prompt)
                st.markdown(answer)
                
                # Show sources
                if sources:
                    with st.expander("📄 Sources"):
                        for source in set(sources):
                            st.markdown(f"- {source}")
        
        # Add assistant message
        st.session_state.messages.append({
            "role": "assistant",
            "content": answer,
            "sources": sources
        })


if __name__ == "__main__":
    main()