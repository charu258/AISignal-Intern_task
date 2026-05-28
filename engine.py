import time
from pipeline import GenerationPipeline
from schemas import CompiledAppConfig
from typing import List, Tuple

class ValidationRepairEngine:
    def __init__(self, pipeline: GenerationPipeline, max_retries: int = 3):
        self.pipeline = pipeline
        self.max_retries = max_retries

    def verify_cross_layer_integrity(self, config: CompiledAppConfig) -> List[str]:
        """Runs explicit linting checks matching cross-layer business rules."""
        errors = []
        
        valid_db_tables = {table.table_name.lower() for table in config.database_schema.tables}
        valid_api_paths = {endpoint.path.lower() for endpoint in config.api_schema.endpoints}
        valid_roles = {role.lower() for role in config.intent_snapshot.user_roles}
        
        for page in config.ui_schema.pages:
            for role in page.allowed_roles:
                if role.lower() not in valid_roles:
                    errors.append(f"UI Page '{page.page_name}' allows undefined role '{role}'. Valid roles: {config.intent_snapshot.user_roles}")
            
            for comp in page.components:
                if comp.maps_to_api_endpoint.lower() not in valid_api_paths:
                    errors.append(f"UI Component '{comp.label}' targets non-existent endpoint path '{comp.maps_to_api_endpoint}'.")
                    
        return errors

    def compile_and_heal(self, raw_prompt: str) -> Tuple[CompiledAppConfig, int, List[str]]:
        """Orchestrates sequential execution inside an autonomous self-correction retry loop with rate limit backoff."""
        logs = []
        retry_count = 0
        
        # Guard Stage 1 against Rate Limits
        for delay in [2, 4, 8]:
            try:
                intent = self.pipeline.stage_1_extract_intent(raw_prompt)
                break
            except Exception as e:
                if "429" in str(e) or "503" in str(e):
                    logs.append(f"Server busy/throttled on Stage 1. Backing off for {delay}s...")
                    time.sleep(delay)
                else:
                    raise e
        else:
            raise Exception("Stage 1 failed permanently due to persistent API rate limits.")

        logs.append("Stage 1 completed: System intent extracted.")
        
        error_context = ""
        backoff_delay = 3  # Initial backoff timer for structural healing layer
        
        while retry_count <= self.max_retries:
            try:
                config = self.pipeline.stage_2_3_4_compile_system(intent, context_history=error_context)
                integrity_errors = self.verify_cross_layer_integrity(config)
                
                if not integrity_errors:
                    logs.append(f"Compilation Successful after {retry_count} self-heal cycles.")
                    return config, retry_count, logs
                
                retry_count += 1
                error_context = "\n".join([f"- {err}" for err in integrity_errors])
                logs.append(f"Heal Cycle {retry_count}: Integrity failure detected:\n{error_context}")
                
            except Exception as e:
                # Catch Rate Limits or Server Unavailable exceptions cleanly
                if "429" in str(e) or "503" in str(e):
                    logs.append(f"Rate limit or 503 hit during architecture layer compilation. Sleeping for {backoff_delay}s...")
                    time.sleep(backoff_delay)
                    backoff_delay *= 2  # Double the wait time for the next hiccup
                    continue  # Retry the exact same state without consuming a structural retry budget
                
                retry_count += 1
                error_context = f"Parser Error: Malformed structure metadata generated - {str(e)}"
                logs.append(f"Heal Cycle {retry_count} Exception caught: {str(e)}")
                
        raise Exception(f"Compilation Failed. System could not clear integrity constraints within limit. Errors: {error_context}")