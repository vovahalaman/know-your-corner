"""Streamlit chat frontend for Know Your Corner."""

import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from google import genai

load_dotenv(Path(__file__).resolve().parent / ".env")

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
MODEL = "gemini-3.5-flash-lite"

st.set_page_config(page_title="Know Your Corner", layout="centered")
st.title("Know Your Corner")
st.caption("Your AI guide to finding the perfect neighborhood in Lisbon")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask me about living in Lisbon..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # build Gemini history from session state
    gemini_history = [
        genai.types.Content(
            role=m["role"] if m["role"] == "user" else "model",
            parts=[genai.types.Part(text=m["content"])],
        )
        for m in st.session_state.messages
    ]

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = client.models.generate_content(
                model=MODEL,
                contents=gemini_history,
                config=genai.types.GenerateContentConfig(
                    system_instruction=(
                        "You are a friendly chat-bot who helps students "
                        "find the best place to live in Lisbon based on their needs. "
                        "Be concise but helpful. If you don't know something specific, "
                        "say so honestly."
                    ),
                ),
            )
            assistant_reply = response.text
            st.markdown(assistant_reply)

    st.session_state.messages.append({"role": "assistant", "content": assistant_reply})
