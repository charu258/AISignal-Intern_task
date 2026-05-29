import streamlit as strl
from pipeline import GenerationPipeline
from engine import ValidationRepairEngine
from runtime import VirtualAppRuntime
from test_suite import run_evaluation_suite

strl.set_page_config(layout="wide", page_title="AI App Compiler Dashboard")

strl.title(" AI Software Compiler & Engine Layer")
strl.caption("Natural Language Prompt → Highly Validated Executable App Architecture Schema")

@strl.cache_resource
def get_engine():
    pipe = GenerationPipeline()
    return ValidationRepairEngine(pipe)

engine = get_engine()

tab1, tab2 = strl.tabs([" Compiler Terminal", " Evaluation Suite Metrics"])

with tab1:
    strl.subheader("Execute Single Compilation")
    user_prompt = strl.text_area(
        "Enter system requirements specification:",
        value="Build a CRM with login, contacts, dashboard, role-based access, and premium plan with payments. Admins can see analytics."
    )
    
    if strl.button("Compile Architecture", type="primary"):
        with strl.spinner("Compiling, validating structural layers, and executing self-healing loops..."):
            try:
                config, retries, logs = engine.compile_and_heal(user_prompt)
                runtime_success = VirtualAppRuntime.simulate_execution(config)
                
                col1, col2, col3 = strl.columns(3)
                col1.metric("Compilation Status", "SUCCESSFUL")
                col2.metric("Self-Heal Iterations", retries)
                col3.metric("Runtime Verification", "PASSED" if runtime_success else "FAILED")
                
                with strl.expander("Inspect Compilation Traces & Lint Logs"):
                    for log in logs:
                        strl.text(log)
                
                strl.subheader("Compiled App Blueprint")
                strl.json(config.model_dump_json())
                
            except Exception as ex:
                strl.error(f"Compilation Pipeline Halted Fatal: {str(ex)}")

with tab2:
    strl.subheader("Stress Testing System Baseline Metrics Suite")
    strl.write("Triggers system design targets covering standard patterns, vague requirements, and conflicting constraints.")
    
    if strl.button("Run Evaluation Test Suite"):
        with strl.spinner("Processing framework regression suite..."):
            metrics_df = run_evaluation_suite()
            strl.dataframe(metrics_df, use_container_width=True)
            
            success_rate = (metrics_df["Status"] == "SUCCESS").mean() * 100
            avg_latency = metrics_df["Latency (s)"].mean()
            
            c1, c2 = strl.columns(2)
            c1.metric("Overall Success Rate (%)", f"{success_rate}%")
            c2.metric("Mean Processing Latency", f"{avg_latency:.2f}s")