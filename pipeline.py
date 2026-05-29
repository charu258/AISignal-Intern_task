import json
from google import genai
from google.genai import types
from schemas import UserIntent, CompiledAppConfig

import os
import streamlit as st

# Check environment variables first (like Streamlit secrets), 
# otherwise look for a key saved in the Streamlit UI session state
api_key = os.environ.get("GEMINI_API_KEY") or st.session_state.get("user_api_key")

# Pass the key to the client. If it's missing, pass a dummy string 
# so it boots safely instead of crashing the whole container!
client = genai.Client(api_key=api_key or "MISSING_KEY")

class GenerationPipeline:
    def __init__(self, model: str = "gemini-2.5-flash"):
        self.model = model

    def stage_1_extract_intent(self, user_prompt: str) -> UserIntent:
        """Parses vague user text into clean entities and roles."""
        response = client.models.generate_content(
            model=self.model,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction="You are a product analyst compiler. Extract structural requirements from natural language.",
                response_mime_type="application/json",
                response_schema=UserIntent,
                temperature=0.0
            ),
        )
        return UserIntent.model_validate_json(response.text)

    def stage_2_3_4_compile_system(self, intent: UserIntent, context_history: str = "") -> CompiledAppConfig:
        """Translates structural intent into a fully realized architecture blueprint across layers."""
        system_instruction = (
            "You are a Senior Systems Architect and software compiler. Generate a highly integrated, production-grade schema architecture "
            "based strictly on the extracted structural intent. Ensure strict relational mapping: UI components must map exactly to defined API "
            "endpoints, and API endpoints must cleanly match the structural entity names and attributes of your database columns."
        )
        
        user_content = f"Target Intent: {intent.model_dump_json(indent=2)}"
        if context_history:
            user_content += f"\n\nCRITICAL FIX REQUIRED: Your previous iteration failed compilation due to these explicit errors:\n{context_history}\nFix the mismatch and regenerate perfectly conforming schemas."

        response = client.models.generate_content(
            model=self.model,
            contents=user_content,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json",
                response_schema=CompiledAppConfig,
                temperature=0.0
            ),
        )
        return CompiledAppConfig.model_validate_json(response.text)