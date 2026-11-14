"""Streamlit chat frontend for Know Your Corner."""

import streamlit as st

from know_your_corner import agent

st.set_page_config(page_title="Know Your Corner", layout="centered")
st.title("Know Your Corner")
st.caption("Your AI guide to finding the perfect neighborhood in Lisbon")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "interaction_id" not in st.session_state:
    st.session_state.interaction_id = None

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask me about living in Lisbon..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            turn = agent.handle(prompt, st.session_state.interaction_id)
        st.markdown(turn.text)

    st.session_state.interaction_id = turn.interaction_id
    st.session_state.messages.append({"role": "assistant", "content": turn.text})