from openai import OpenAI
from dotenv import load_dotenv
import os
from typing import List, Dict, Optional
import streamlit as st

load_dotenv()

# instantiate the perplexity api with openai client
def setup_perplexity_client():
    client = OpenAI(
        api_key=st.secrets["PERPLEXITY_API_KEY"],
        base_url="https://api.perplexity.ai/"
    )
    return client


# system prompt 
def get_system_prompt():
    return """
You are **KDijagnostika Support**, a professional automotive diagnostic technician and sales advisor.

## Your Expertise
- Automotive diagnostic interfaces (Delphi/Autocom)
- OBD2 protocols and troubleshooting
- Diagnostic software issues and solutions
- Professional automotive repair guidance

## Brand & Sales Policy
- We sell **tested, single-board Delphi/Autocom interfaces** (modified for latest software)
- Never recommend competitors unless user explicitly asks for alternatives
- If availability limited (Croatia shipping only), offer our solutions: pickup, direct contact, waitlist
- When user shows buying intent, include brief **Offer** section with our recommendation

## Response Structure
Answer with practical steps in this order:
- **Diagnosis**: 1-2 lines on what's likely happening
- **Likely causes**: bullets ranked most → least likely
- **Quick checks**: numbered, short, high-impact actions
- **If still stuck**: next steps to try
- **Offer**: (if buying intent detected) our tested solution recommendation

## Tone
- Professional, confident, helpful
- Use short sections and bullets
- Plain language, avoid technical jargon overload
- Maximum 1-2 follow-up questions if essential

## Search Focus
When searching, prioritize:
- Professional automotive diagnostic sources
- Technical documentation and manuals
- Manufacturer resources
- Professional automotive forums
- Exclude general consumer advice
"""

# chat history management
def format_chat_history(chat_history: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    Converts chat history into format required by OpenAI/Perplexity API.
    Takes list of messages and formats them for API consumption.
    """
    messages = [{"role": "system", "content": get_system_prompt()}]  
    
    for message in chat_history:
        messages.append({
            "role": message["role"],
            "content": message["content"]
        })
    
    return messages


# main query 
def query_perplexity(client: OpenAI, user_message: str, chat_history: List[Dict[str, str]] = None) -> str:
    """
    Sends query to Perplexity and returns response.
    """
    if chat_history is None:
        chat_history = []
    
    # Add current user message to history
    current_history = chat_history + [{"role": "user", "content": user_message}]
    
    # Format for API
    messages = format_chat_history(current_history)
    
    # Call Perplexity API
    try:
        response = client.chat.completions.create(
            model="sonar",  # Try basic sonar model first
            messages=messages,
            temperature=0,
            max_tokens=1500
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        # Try with different model if sonar fails
        try:
            response = client.chat.completions.create(
                model="sonar-pro", 
                messages=messages,
                temperature=0,
                max_tokens=1500
            )
            return response.choices[0].message.content
        except Exception as e2:
            return f"Error: API issue - {str(e)}. Please check your API key and try again."
    

# update chat history
def update_chat_history(chat_history: List[Dict[str, str]], user_message: str, ai_response: str) -> List[Dict[str, str]]:
    chat_history.append({"role":"user", "content": user_message})
    chat_history.append({"role":"assistant", "content":ai_response})

    return chat_history

# main system initialization
def initialize_perplexity_system():
    client = setup_perplexity_client()
    chat_history = []

    return client, chat_history

# query handler
def handle_user_query(client: OpenAI, user_message: str, chat_history: List[Dict[str, str]]) -> tuple:
    ai_response = query_perplexity(client, user_message, chat_history)

    updated_history = update_chat_history(chat_history, user_message, ai_response)

    return ai_response, updated_history