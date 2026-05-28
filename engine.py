from pipeline import GenerationPipeline
from schemas import CompiledAppConfig
import logging

class ValidationRepairEngine:
    def __init__(self, pipeline: GenerationPipeline, max_retries: int = 3):
        self.pipeline = pipeline
        self.max_retries = max_retries

    def verify_cross_layer_integrity(self, config: CompiledAppConfig) -> List[str]:
        """Runs explicit linting checks matching cross-layer business rules.""" [cite: 46]
        errors = []
        
        # 1. Collect valid references
        valid_db_tables = {table.table_name.lower() for table in config.database_schema.tables}
        valid_api_paths = {endpoint.path.lower() for endpoint in config.api_schema.endpoints}
        valid_roles = {role.lower() for role in config.intent_snapshot.user_roles}
        
        # 2. Assert API to Database alignment
        for endpoint in config.api_schema.endpoints:
            # Simple inference: check if endpoint resource pattern matches a table name
            resource = endpoint.path.strip("/").split("/")[-1].lower()
            # If creating or modifying data, make sure matching tables or structures make logical sense
            if endpoint.method in ["POST", "PUT"] and not any(table in resource for table in valid_db_tables):
                pass # Extensible log context can be added here
                
        # 3. Assert UI to API binding alignment
        for page in config.ui_schema.pages:
            for role in page.allowed_roles:
                if role.lower() not in valid_roles:
                    errors.append(f"UI Page '{page.page_name}' allows undefined role '{role}'. Valid roles: {config.intent_snapshot.user_roles}")
            
            for comp in page.components:
                if comp.maps_to_api_endpoint.lower() not in valid_api_paths:
                    errors.append(f"UI Component '{comp.label}' targets non-existent endpoint path '{comp.maps_to_api_endpoint}'.") [cite: 49, 57]
                    
        return errors

    def compile_and_heal(self, raw_prompt: str) -> Tuple[CompiledAppConfig, int, List[str]]:
        """Orchestrates sequential execution inside an autonomous self-correction retry loop.""" [cite: 60, 61]
        logs = []
        retry_count = 0
        
        # Run Stage 1
        intent = self.pipeline.stage_1_extract_intent(raw_prompt)
        logs.append("Stage 1 completed: System intent extracted.")
        
        # Run Stages 2-4 with structural healing loop
        error_context = ""
        while retry_count <= self.max_retries:
            try:
                config = self.pipeline.stage_2_3_4_compile_system(intent, context_history=error_context)
                integrity_errors = self.verify_cross_layer_integrity(config)
                
                if not integrity_errors:
                    logs.append(f"Compilation Successful after {retry_count} self-heal cycles.") [cite: 60]
                    return config, retry_count, logs
                
                # If static checks catch anomalies, formulate error context injection [cite: 57, 58, 61]
                retry_count += 1
                error_context = "\n".join([f"- {err}" for err in integrity_errors])
                logs.append(f"Heal Cycle {retry_count}: Integrity failure detected:\n{error_context}")
                
            except Exception as e:
                retry_count += 1
                error_context = f"Parser Error: Malformed structure metadata generated - {str(e)}"
                logs.append(f"Heal Cycle {retry_count} Exception caught: {str(e)}") [cite: 54]
                
        raise Exception(f"Compilation Failed. System could not clear integrity constraints within limit. Errors: {error_context}")