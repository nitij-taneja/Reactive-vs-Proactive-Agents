import streamlit as st
import os

# --- Configuration ---
# Do not load from .env. Users will paste keys in the UI each run.
GEMINI_API_KEY = ""
GROQ_API_KEY = ""
TAVILY_API_KEY = ""

# Set page configuration
st.set_page_config(
    page_title="Dual-Agent AI Content Strategist",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Pre-clear sensitive widget keys before rendering any widgets
if st.session_state.get("__clear_keys__", False):
    for k in ("gemini_key_input", "groq_key_input", "tavily_key_input"):
        if k in st.session_state:
            del st.session_state[k]
    st.session_state["__clear_keys__"] = False

# --- Sidebar for API Keys and Parameters ---
with st.sidebar:
    st.title("⚙️ Configuration & Parameters")

    # API Key Inputs (pre-filled with user's keys)
    st.header("API Keys")
    st.text_input("Gemini API Key", type="password", value="", key="gemini_key_input")
    st.text_input("Groq API Key", type="password", value="", key="groq_key_input")
    st.text_input("Tavily API Key", type="password", value="", key="tavily_key_input")
    
    # Live Parameter Adjustment
    st.header("Agent Parameters")
    
    # Groq (Reactive) Agent Parameters
    st.subheader("Reactive Agent (Groq)")
    groq_model = st.selectbox(
        "Model",
        ["llama-3.1-8b-instant", "llama-3.3-70b-versatile"],
        key="groq_model",
        index=0,
    )
    groq_temp = st.slider("Temperature", 0.0, 1.0, 0.3, 0.1, key="groq_temp")
    
    # Gemini (Proactive) Agent Parameters
    st.subheader("Proactive Agent (Gemini)")
    gemini_model = st.selectbox("Model", ["gemini-2.5-flash", "gemini-2.5-pro"], key="gemini_model", index=0)
    gemini_temp = st.slider("Temperature", 0.0, 1.0, 0.7, 0.1, key="gemini_temp")
    
    # Web Search Toggle
    st.header("Tools")
    use_web_search = st.checkbox("Enable Web Search (Tavily/DuckDuckGo)", value=True, key="use_search")

# --- Main App Title and Description ---
st.title("🧠 Dual-Agent AI Content Strategist")
st.markdown("""
A demonstration of a **Reactive Agent** (Groq) for rapid content drafting and a **Proactive Agent** (Gemini) for research-backed refinement and strategy.
Showcasing parallel execution, live parameter tuning, and tool usage in an agentic workflow.
""")

# Footer branding
st.markdown("---")
st.markdown("<div style='text-align:center; font-weight:bold;'>Powered by Nitij Taneja</div>", unsafe_allow_html=True)

# --- Agent Logic ---
import importlib
import agents as agents_module

# --- Input and Execution ---
user_prompt = st.text_area("Enter your content idea or topic:", "The future of serverless computing and its impact on startups.", height=100)

if st.button("🚀 Run Dual Agents"):
    if not user_prompt:
        st.error("Please enter a content idea to run the agents.")
    else:
        # Helper to sanitize keys copied with quotes/spaces
        def _sanitize(key: str) -> str:
            if key is None:
                return ""
            return key.strip().strip('"').strip("'")

        # Sanitize keys from sidebar
        gemini_key = _sanitize(st.session_state.gemini_key_input)
        groq_key = _sanitize(st.session_state.groq_key_input)
        tavily_key = _sanitize(st.session_state.tavily_key_input) if st.session_state.use_search else ""

        # Check for API keys
        if not gemini_key or not groq_key or (st.session_state.use_search and not tavily_key):
            st.error("Please ensure all necessary API keys are provided in the sidebar.")
        else:
            with st.spinner("Agents are working..."):
                # Prepare configurations from Streamlit state
                groq_config = (
                    groq_key,
                    st.session_state.groq_model,
                    st.session_state.groq_temp
                )
                gemini_config = (
                    gemini_key,
                    st.session_state.gemini_model,
                    st.session_state.gemini_temp,
                    st.session_state.use_search,
                    tavily_key,
                )
                
                # Reload agents module to avoid stale state and import issues
                try:
                    agents_module = importlib.reload(agents_module)
                    reactive_result, proactive_result = agents_module.run_agents_parallel(
                        user_prompt,
                        groq_config,
                        gemini_config
                    )
                except Exception as e:
                    st.error(f"Failed to run agents: {e}")
                    st.stop()
                
                # Store results in session state to maintain output after re-run
                st.session_state.reactive_result = reactive_result
                st.session_state.proactive_result = proactive_result
                st.session_state.last_prompt = user_prompt

                # Schedule clearing of sensitive keys on next run (must happen before widgets render)
                st.session_state["__clear_keys__"] = True
                st.rerun()

# --- Parallel Output Sections ---
if "reactive_result" in st.session_state:
    st.subheader(f"Results for: *{st.session_state.last_prompt}*")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"Agent 1: Reactive Draft (Groq - Model: {st.session_state.groq_model}, Temp: {st.session_state.groq_temp})")
        st.markdown(st.session_state.reactive_result) # Use markdown for better display of content
        
    with col2:
        st.info(f"Agent 2: Proactive Refinement (Gemini - Model: {st.session_state.gemini_model}, Temp: {st.session_state.gemini_temp}, Search: {'Enabled' if st.session_state.use_search else 'Disabled'})")
        st.markdown(st.session_state.proactive_result) # Use markdown for better display of content

# --- Guided Walkthrough & Agent Tracing ---
st.markdown("---")
st.header("💡 Guided Walkthrough & Agent Tracing")
st.markdown("""
This section demonstrates the **AI Pipeline** and **Constraint Modeling** in action.

### 1. Constraint Modeling & Parallel Execution
- **Reactive Agent (Groq):** Constrained to be **fast** and **draft-focused**. It runs independently and in parallel to the Proactive Agent's initial thought process.
- **Proactive Agent (Gemini):** Constrained to be **strategic** and **research-backed**. It takes the draft from the Reactive Agent as its *primary input* for refinement.

### 2. Task Execution & Tool Usage
- **Reactive Agent:** Task is **'Generate Draft'**. No tools are used to ensure maximum speed.
- **Proactive Agent:** Task is **'Refine and Strategize'**.
    - **Tool Check:** It first decides if it needs to use the web search tool (Tavily/DuckDuckGo) based on the prompt and the draft content.
    - **Execution:** If a search is needed, it executes the `web_search` tool to gather facts.
    - **Final Output:** It then produces its final structured output: **Analysis, Refinement, and Next Steps**.

*Note: For a full, live trace of the Proactive Agent's tool-use reasoning, check the console output where `verbose=True` is set in the agent executor.*
""")
