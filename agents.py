import os
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain.agents import AgentExecutor, create_tool_calling_agent
from concurrent.futures import ThreadPoolExecutor

# --- 1. Agent Definitions ---

def validate_groq_key(api_key: str, model: str) -> str | None:
    """Attempt a minimal call to Groq to validate the API key and model access.
    Returns an error message string on failure, or None on success.
    """
    try:
        llm = ChatGroq(groq_api_key=api_key, model=model, temperature=0.0)
        # Minimal no-tool call
        chain = ChatPromptTemplate.from_messages([
            ("system", "You are a health check."),
            ("human", "Reply with OK")
        ]) | llm
        _ = chain.invoke({"input": ""})
        return None
    except Exception as e:
        return str(e)

def create_reactive_agent(api_key, model_name, temperature):
    """
    Creates the Reactive Agent (Groq) for fast, direct content drafting.
    This agent is simple and does not use any tools.
    """
    err = validate_groq_key(api_key, model_name)
    if err:
        raise ValueError(f"Groq API key or model '{model_name}' is invalid: {err}")
    
    llm = ChatGroq(
        groq_api_key=api_key,
        model=model_name,
        temperature=temperature
    )
    
    system_prompt = (
        "You are a fast, reactive content drafting agent. Your sole purpose is to "
        "generate a concise, direct, and engaging draft in response to the user's request. "
        "Do not overthink or use external tools. Focus on speed and a clear structure. "
        "The user will provide a topic or idea. Your output should be a draft of a short social media post or a blog outline."
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}")
    ])
    
    # The reactive agent is a simple chain, not a full agent executor
    return prompt | llm

def create_proactive_agent(api_key, model_name, temperature, use_search, tavily_api_key: str | None = None):
    """
    Creates the Proactive Agent (Gemini) for research, refinement, and suggesting next steps.
    This agent uses the web_search tool.
    """
    llm = ChatGoogleGenerativeAI(
        model=model_name,
        temperature=temperature,
        google_api_key=api_key
    )
    
    # Set Tavily API key from runtime if provided
    tools = []
    if use_search and tavily_api_key:
        os.environ["TAVILY_API_KEY"] = tavily_api_key
        try:
            tools = [TavilySearchResults(max_results=5)]
        except Exception:
            # If Tavily init fails (e.g., bad key), proceed without tools
            tools = []
    
    system_prompt = (
        "You are a sophisticated, proactive content strategist. Your task is to analyze "
        "the 'DRAFT' content provided by another agent and refine it. "
        "Your refinement must include:\n"
        "1. **Analysis:** A brief critique of the draft (e.g., 'Good start, but needs data.').\n"
        "2. **Refinement:** The final, polished content. Use the web_search tool to find supporting facts, statistics, or recent trends to enhance the content's credibility, if necessary.\n"
        "3. **Next Steps:** Proactively suggest 2-3 logical next steps for the user (e.g., 'Next, create a diagram for this post,' or 'Run a second agent to translate this content.').\n\n"
        "Your final response MUST be structured clearly with these three sections."
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "DRAFT to refine: {draft_content}\\n\\nOriginal Topic: {original_topic}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    
    agent = create_tool_calling_agent(llm, tools, prompt)
    executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)
    return executor

# --- 3. Parallel Execution Function ---

def run_agents_parallel(prompt, groq_config, gemini_config):
    """
    Runs the reactive and proactive agents in parallel using a ThreadPoolExecutor.
    """
    
    # Unpack configurations
    groq_api_key, groq_model, groq_temp = groq_config
    # gemini_config now includes tavily_key
    gemini_api_key, gemini_model, gemini_temp, use_search, tavily_key = gemini_config
    
    # Function to run the reactive agent
    def run_reactive():
        try:
            # Preflight validate Groq credentials/model
            err = validate_groq_key(groq_api_key, groq_model)
            if err:
                return f"Reactive Agent Error: {err}"
            reactive_chain = create_reactive_agent(groq_api_key, groq_model, groq_temp)
            # Invoke the chain with the user's prompt
            response = reactive_chain.invoke({"input": prompt})
            return response.content
        except Exception as e:
            return f"Reactive Agent Error: {e}"

    # Function to run the proactive agent
    def run_proactive(draft_content):
        try:
            proactive_executor = create_proactive_agent(
                gemini_api_key, gemini_model, gemini_temp, use_search, tavily_key
            )
            # The input to the proactive agent is the draft content from the reactive agent
            response = proactive_executor.invoke({
                "draft_content": draft_content,
                "original_topic": prompt
            })
            # Extract final content robustly across return shapes
            if isinstance(response, dict):
                # common shapes: {"output": str} or {"messages": [...]} or {"output_text": str}
                for k in ("output", "output_text", "final_output"):
                    if k in response:
                        return response[k]
                # Fallback: join any message contents
                if "messages" in response and isinstance(response["messages"], list):
                    texts = []
                    for m in response["messages"]:
                        c = getattr(m, "content", None)
                        if c:
                            texts.append(c if isinstance(c, str) else str(c))
                    if texts:
                        return "\n".join(texts)
                return str(response)
            # AIMessage or similar with .content
            content = getattr(response, "content", None)
            if content:
                return content
            # Plain string fallback
            if isinstance(response, str):
                return response
            return str(response)
        except Exception as e:
            return f"Proactive Agent Error: {e}"

    # Use ThreadPoolExecutor for parallel execution of the first step
    with ThreadPoolExecutor(max_workers=2) as executor:
        # Run the reactive agent first to get the draft
        reactive_future = executor.submit(run_reactive)
        draft_content = reactive_future.result()
        
        # Now run the proactive agent with the draft content
        proactive_future = executor.submit(run_proactive, draft_content)
        proactive_result = proactive_future.result()
        
    return draft_content, proactive_result

# --- 4. Streamlit Integration (Will be done in app.py) ---
# The run_agents_parallel function will be called from the Streamlit app.
