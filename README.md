# Streamlit OpenAI Chatbot

A minimal ChatGPT-style chatbot that streams replies from the OpenAI Responses API.

## Run it

1. Create and activate a virtual environment (optional, but recommended).
2. Install dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

3. Provide an API key for the current PowerShell session:

   ```powershell
   $env:OPENAI_API_KEY = "your_openai_api_key"
   ```

4. Start the app:

   ```powershell
   streamlit run app.py
   ```

You may instead paste the key in the app sidebar for the current browser session, or set it in Streamlit secrets. This uses the OpenAI API, so it requires an API key with API access; a ChatGPT subscription alone does not supply one. The default model is `gpt-4.1-mini`; change it in the sidebar if your account uses another model.

Never commit a real API key. See `.env.example` for the expected environment variable name.
