# 🧠 DecisionCrew: AI-Powered Strategic Analysis & Wargaming

DecisionCrew is an advanced, AI-powered decision support system designed for high-level strategic analysis. It is built to assist a "Captain" (senior decision-maker) by operating in two distinct phases:

1.  **Phase 1: Intelligence Briefing:** The system ingests a high-level intelligence requirement (KIR) from the user. It then uses a multi-agent team to gather and analyze data from Open-Source Intelligence (OSINT), internal databases, and user-uploaded CSV files. The final product is a concise, actionable intelligence briefing modeled after professional intelligence doctrines (BLUF, ACH, Admiralty Code).
2.  **Phase 2: Wargame Simulation:** Based on the generated briefing, the user can propose a course of action. The system then initiates a simulation (Red Team vs. Blue Team) to model the most likely adversarial reactions and strategic outcomes, providing a full analysis of the simulated exchange.

---

## ## Core Features

* **Modular Workflows:** The system's behavior is defined by YAML configuration files (`agents.yaml`, `tasks.yaml`) located in `config/workflows/`. This allows for easy modification and expansion of capabilities.
* **Multi-Source Analysis:**
    * **OSINT:** Gathers real-time, relevant information from the web using tools like `SerperDevTool` and `NewsAPITool`.
    * **Database:** Queries internal structured data (from an SQLite database) for historical context.
    * **CSV as Context:** Analyzes user-uploaded CSV files by reading them as text context, allowing for analysis of bespoke datasets.
* **Professional Doctrine:** Agents are designed to "think" using professional intelligence methodologies:
    * **ACH (Analysis of Competing Hypotheses):** To reduce cognitive bias.
    * **Admiralty Code:** To grade evidence based on source reliability and credibility.
    * **Bayesian Forecasting:** To provide calibrated, probabilistic forecasts.
    * **BLUF (Bottom Line Up Front):** To deliver concise, actionable reports.
* **Wargame Simulation:** A sequential, three-agent (Red, Blue, Game Master) simulation to test hypotheses and strategic moves.
* **Simple UI:** Built with Streamlit for easy interaction, file uploads, and clear presentation of results (including RTL support for Hebrew output).

---

## ## Tech Stack

* **Core Framework:** `crewai` & `langchain`
* **Frontend:** `streamlit`
* **Data Handling:** `pandas`
* **Configuration:** `pyyaml`
* **Tools:** `crewai_tools`, `newsapi-python`, `qdrant-client` (as a dependency)
* **LLM:** `langchain-openai` (defaulting to GPT-4o)

---

## ## Setup & Installation

Follow these steps to set up the project locally.

### 1. Clone the Repository
```bash
# Clone your private repository
git clone [https://github.com/avivreu7/DecisionCrew.git](https://github.com/avivreu7/DecisionCrew.git)
cd DecisionCrew
```

### 2. Create and Activate Virtual Environment
```powershell
# Create the virtual environment
python -m venv venv

# Activate the environment
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies
Make sure your `requirements.txt` file is up-to-date, then run:
```powershell
pip install -r requirements.txt
```

### 4. Set Up Environment Variables
Create a file named `.env` in the root project directory (`DecisionCrew/`) and add your API keys. This file is **critically important** and is protected by `.gitignore`.

```env
# Your OpenAI API Key
OPENAI_API_KEY="sk-..."

# Your Serper.dev API Key (for general web search)
SERPER_API_KEY="..."

# Your NewsAPI.org Key (for recent news)
NEWS_API_KEY="..."

# Your Database URL (if using the DB workflow)
# Example for a file named 'decisioncrew.db' in the 'data' folder
DATABASE_URL="sqlite:///data/decisioncrew.db"

# Optional: Specify the model to use
# MODEL_NAME="gpt-4o"
```

---

## ## How to Run

Ensure your virtual environment (`venv`) is active.

### Running the Application
Use the Streamlit command from the **root directory**:

```powershell
python -m streamlit run ui/app.py
```
This will open the application in your web browser.

### Running the Backend Test
To test the backend logic without the UI, you can use:
```powershell
python -m decisioncrew.main
```
*(Remember to update `main.py` to ask for input or test a specific workflow).*

---

## ## Workflow Overview

The system operates using distinct workflows selected in the UI:

### `osint`
* **Purpose:** Pure Open-Source Intelligence analysis.
* **Agents:** Planner, Collector, Analyst, Forecaster, Writer.
* **Tools:** `SerperDevTool`, `WebsiteSearchTool`, `NewsAPITool`.
* **Process:** Gathers and analyzes fresh web data to answer the KIR.

### `db`
* **Purpose:** Analyzes historical data from the internal SQLite database.
* **Agents:** DB Planner, DB Querier, DB Analyst, DB Writer.
* **Tools:** `db_query_tool`.
* **Process:** Queries the database for patterns, trends, and historical context.

### `combined`
* **Purpose:** The most powerful workflow. Fuses OSINT with user-provided CSV data.
* **Agents:** Combined Planner, OSINT Collector, Combined Analyst, Forecaster, Writer.
* **Tools:** `SerperDevTool`, `WebsiteSearchTool`, `NewsAPITool`.
* **Process:** Reads the uploaded CSV data (first 90 rows) as text context. The Analyst then integrates this data with fresh OSINT findings to create a fused intelligence product.

### `wargames`
* **Purpose:** Simulates a strategic exchange. This workflow is not selected from the dropdown but is triggered *after* an intelligence report is generated.
* **Agents:** Red Team Agent, Blue Team Agent, Game Master.
* **Process:** Takes the intelligence report as context and a user-provided action, then simulates the `Action -> Reaction -> Counter-Reaction` sequence.
