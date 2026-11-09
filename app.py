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

