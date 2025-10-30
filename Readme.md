# 🧠 Dual-Agent AI Content Strategist: Streamlit Showcase
![Demo](https://github.com/nitij-taneja/Reactive-vs-Proactive-Agents/blob/main/dual-agent-ai-content-strategist-streamlit-personal-microsoft-edge-2025-10_bdmLVHc6.gif)

This project is a professional, interactive demonstration of modern agentic AI frameworks, designed to be showcased on platforms like LinkedIn. It highlights key concepts in AI engineering: **Constraint Modeling**, **Task Execution**, **Parallel Processing**, and **Tool Usage** within a practical, real-world application: **Content Strategy and Generation**.

Video: https://drive.google.com/file/d/18NkvcrkhxUuKaDemVEWJkCnZKjomAphC/view?usp=sharing

Live Link: https://reactivevsproactiveagentsbynitijtaneja.streamlit.app/
## Project Files

| File | Description |
| :--- | :--- |
| `app.py` | The main Streamlit application file, handling the UI and parameter passing. |
| `agents.py` | Contains the core LangChain logic, including the definitions for the Reactive and Proactive Agents, the `web_search` tool, and the parallel execution function. |
| `requirements.txt` | List of Python dependencies. |
Built with LangChain, Streamlit, Groq, and Gemini.

## 🚀 Key Features

*   **Dual-Agent System:** Two distinct agents work in tandem to achieve a superior result.
    *   **Reactive Agent (Groq):** Constrained for **speed** and **drafting**. Uses the high-speed Groq API (Llama3) to quickly generate a content draft.
    *   **Proactive Agent (Gemini):** Constrained for **quality** and **strategy**. Uses the Gemini API to refine the draft, perform fact-checking via web search, and suggest strategic next steps.
*   **Live Parameter Tuning:** Users can adjust model parameters (Temperature, Model choice) for both the Groq and Gemini agents live on the Streamlit sidebar, showcasing the impact of configuration on agent behavior.
*   **Parallel Execution:** The agents' outputs are displayed side-by-side, demonstrating an efficient AI pipeline where the fast agent's output is immediately fed to the strategic agent.
*   **Guided Walkthrough:** The application includes a dedicated section explaining the AI pipeline, the constraints of each agent, and the logic behind tool usage, making the complex process transparent and educational.
*   **Web Search Integration:** The Proactive Agent can utilize the Tavily API (with DuckDuckGo fallback) to perform real-time research, adding credibility and freshness to the generated content.

## 🛠️ Setup and Installation

### Prerequisites

*   Python 3.9+
*   API Keys for **Gemini**, **Groq**, and **Tavily**. You will paste these into the app UI at runtime. No `.env` is used.

### Steps

1.  **Clone the repository** (or create the files as provided):

    \`\`\`bash
    git clone [YOUR_REPO_URL]
    cd dual_agent_showcase
    \`\`\`

2.  **Install dependencies:**

    \`\`\`bash
    pip install -r requirements.txt
    \`\`\`

3.  **Run the Streamlit application:**

    \`\`\`bash
    streamlit run app.py
    \`\`\`

## Usage

1. Start the app: `streamlit run app.py`.
2. In the left sidebar, paste your API keys into:
   - Gemini API Key
   - Groq API Key
   - Tavily API Key (only if you enable Web Search)
3. Choose models and temperatures.
   - Groq models: `llama-3.1-8b-instant`, `llama-3.3-70b-versatile`.
   - Gemini models: `gemini-2.5-flash`, `gemini-2.5-pro`.
4. Enter a topic and click “Run Dual Agents”.
5. Keys are not stored and are cleared after each run.


