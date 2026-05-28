import time
import pandas as pd
from pipeline import GenerationPipeline
from engine import ValidationRepairEngine
from runtime import VirtualAppRuntime

# Ground truth test harness
TEST_DATASET = [
    {"type": "Standard", "prompt": "Build a CRM with login, contacts, dashboard, role-based access, and premium plan with payments. Admins can see analytics."}, 
    {"type": "Standard", "prompt": "Build an E-commerce store with product catalogs, shopping carts, Stripe checkouts, inventory tracking tables, and a vendor management portal."},
    {"type": "Vague", "prompt": "Make an app to manage my local sports club tracking people and schedules."}, 
    {"type": "Conflict", "prompt": "Create an anonymous messaging platform but require absolute verified admin phone numbers to view every message route."},
    {"type": "Incomplete", "prompt": "Build a project manager tool with kanban cards."} 
]

def run_evaluation_suite():
    pipeline = GenerationPipeline()
    engine = ValidationRepairEngine(pipeline)
    
    results = []
    
    for item in TEST_DATASET:
        start_time = time.time()
        status = "SUCCESS"
        retries = 0
        
        try:
            config, retries, logs = engine.compile_and_heal(item["prompt"])
            execution_passed = VirtualAppRuntime.simulate_execution(config)
            if not execution_passed:
                status = "RUNTIME_CRASH"
        except Exception as e:
            status = f"FAILED: {str(e)}"
            
        latency = time.time() - start_time
        results.append({
            "Prompt Type": item["type"],
            "Status": status,
            "Retries Required": retries,
            "Latency (s)": round(latency, 2)
        })
        
        # Mandatory 6-second pause to respect Gemini's Free Tier Rate Limits (15 RPM)
        time.sleep(6) 
        
    df = pd.DataFrame(results)
    return df