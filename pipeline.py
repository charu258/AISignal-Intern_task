import json
from openai import OpenAI
from schemas import UserIntent, CompiledAppConfig

client = OpenAI()

class GenerationPipeline:
    def __init__(self, model: str = "gpt-4o-mini"):
        self.model = model

    def stage_1_extract_intent(self, user_prompt: str) -> UserIntent:
        """Parses vague user text into clean entities and roles.""" [cite: 24, 25]
        response = client.beta.chat.completions.parse(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a product analyst compiler. Extract structural requirements from natural language."},
                {"role": "user", "content": user_prompt}
            ],
            response_format=UserIntent,
            temperature=0.0
        )
        return response.choices[0].message.parsed

    def stage_2_3_4_compile_system(self, intent: UserIntent, context_history: str = "") -> CompiledAppConfig:
        """Translates structural intent into a fully realized architecture blueprint across layers.""" [cite: 26, 28, 31, 37]
        system_prompt = (
            "You are a Senior Systems Architect and software compiler. Generate a highly integrated, production-grade schema architecture "
            "based strictly on the extracted structural intent. Ensure strict relational mapping: UI components must map exactly to defined API "
            "endpoints, and API endpoints must cleanly match the structural entity names and attributes of your database columns." [cite: 46, 48, 49]
        )
        
        user_content = f"Target Intent: {intent.model_dump_json(indent=2)}"
        if context_history:
            user_content += f"\n\nCRITICAL FIX REQUIRED: Your previous iteration failed compilation due to these explicit errors:\n{context_history}\nFix the mismatch and regenerate perfectly conforming schemas."

        response = client.beta.chat.completions.parse(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            response_format=CompiledAppConfig,
            temperature=0.0
        )
        return response.choices[0].message.parsed