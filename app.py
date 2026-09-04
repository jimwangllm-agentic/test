"""A minimal streaming chat app powered by Streamlit and the OpenAI API."""

import os
from collections.abc import Iterator

import streamlit as st
from openai import OpenAI, OpenAIError


st.set_page_config(page_title="OpenAI Chat", page_icon="💬")
st.title("💬 OpenAI Chat")
st.caption("A simple Streamlit chatbot with streamed responses.")


def configured_api_key() -> str | None:
    """Get the API key from the environment or Streamlit secrets."""
    return os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")


def response_text_stream(client: OpenAI, messages: list[dict[str, str]]) -> Iterator[str]:
    """Yield text deltas from an OpenAI Responses API stream."""
    stream = client.responses.create(
        model=st.session_state.model,
        instructions="You are a helpful, concise assistant.",
        input=messages,
        stream=True,
    )
    for event in stream:
        if event.type == "response.output_text.delta":
            yield event.delta


if "messages" not in st.session_state:
    st.session_state.messages = []
if "model" not in st.session_state:
    st.session_state.model = "gpt-4.1-mini"

with st.sidebar:
    st.header("Settings")
    st.session_state.model = st.text_input("Model", value=st.session_state.model)
    sidebar_key = st.text_input("OpenAI API key", type="password")
    st.caption("Prefer `OPENAI_API_KEY` in your environment or Streamlit secrets.")
    if st.button("Clear chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

api_key = configured_api_key() or sidebar_key

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask me anything"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    if not api_key:
        with st.chat_message("assistant"):
            st.error("Add an OpenAI API key in the sidebar or set OPENAI_API_KEY, then try again.")
    elif not st.session_state.model.strip():
        with st.chat_message("assistant"):
            st.error("Enter a model name in the sidebar.")
    else:
        with st.chat_message("assistant"):
            try:
                reply = st.write_stream(
                    response_text_stream(OpenAI(api_key=api_key), st.session_state.messages)
                )
                st.session_state.messages.append({"role": "assistant", "content": reply})
            except OpenAIError as error:
                st.error(f"OpenAI API error: {error}")
