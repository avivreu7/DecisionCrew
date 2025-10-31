# decisioncrew/crews/intelligence_crew.py

import yaml
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
import os

# Import all tools
try:
    # 👇 שימו לב לייבוא המצומצם
    from decisioncrew.tools.web_tools import (
        web_search_tool, 
        website_search_tool, 
        # news_api_tool - REMOVED
        # telegram_search_tool - REMOVED
    )
    from decisioncrew.tools.database_tools import db_query_tool # מייבא את כלי הדמה
    # 👇 הסרנו את הייבוא של כלי ה-CSV
    # from decisioncrew.tools.file_tools import csv_query_tool, inspect_csv_tool 
except ImportError as e:
    raise ImportError(f"Could not import tools. Check tool file paths and ensure no errors within them: {e}")

class IntelligenceCrew:
    def __init__(self, workflow_name: str):
        self.workflow_name = workflow_name
        self.config_path = os.path.join("config", "workflows", self.workflow_name) + os.sep
        if not os.path.exists(self.config_path):
             raise FileNotFoundError(f"Workflow configuration directory not found: {self.config_path}")
             
        self._load_configs()
        model_name = os.getenv("MODEL_NAME", "gpt-4o") 
        try:
            self.llm = ChatOpenAI(model=model_name)
        except Exception as e:
            raise ValueError(f"Failed to initialize the language model (model: {model_name}). Check API key and configuration. Error: {e}")

    def _load_configs(self):
        """Loads agent and task configuration files from YAML."""
        agents_file = os.path.join(self.config_path, "agents.yaml")
        tasks_file = os.path.join(self.config_path, "tasks.yaml")
        try:
            with open(agents_file, 'r', encoding='utf-8') as f:
                self.agents_config = yaml.safe_load(f)
            with open(tasks_file, 'r', encoding='utf-8') as f:
                self.tasks_config = yaml.safe_load(f)
        except FileNotFoundError as e:
            missing_file = "agents.yaml" if "agents.yaml" in str(e) else "tasks.yaml"
            raise FileNotFoundError(f"{missing_file} not found for workflow '{self.workflow_name}' in: {self.config_path}") from e
        except yaml.YAMLError as e:
             raise ValueError(f"Error parsing YAML file in {self.config_path}: {e}") from e
        
        if not self.agents_config:
             raise ValueError(f"Agents configuration file '{agents_file}' is empty or invalid.")
        if not self.tasks_config:
             raise ValueError(f"Tasks configuration file '{tasks_file}' is empty or invalid.")

    def _get_tools_map(self):
        """Maps tool names (as strings in YAML) to their actual tool function objects."""
        # 👇 מפת כלים מצומצמת מאוד
        tool_map = {
            "serper_dev_tool": web_search_tool,
            "website_search_tool": website_search_tool,
            "db_query_tool": db_query_tool, # מצביע לכלי הדמה
        }
        # (הסרנו את כל הכלים הבעייתיים)
        return tool_map

    def setup_crew(self, topic: str):
        """Assembles the crew based on the loaded configuration for the specific workflow."""
        
        tools_map = self._get_tools_map()
        
        # Create Agents
        agents = {}
        if not self.agents_config: 
             raise ValueError(f"Agents configuration is empty or invalid for workflow '{self.workflow_name}'. Check agents.yaml.")
             
        for name, config in self.agents_config.items():
            if not isinstance(config, dict): 
                print(f"Warning: Invalid config format for agent '{name}'. Skipping.")
                continue
            
            agent_tools_config = config.get("tools", [])
            agent_tools = []
            for tool_name in agent_tools_config:
                if tool_name in tools_map:
                    agent_tools.append(tools_map[tool_name])
                else:
                    # זו אזהרה חשובה - היא תופיע אם שכחנו להסיר כלי מה-YAML
                    print(f"\n\nERROR: Tool '{tool_name}' for agent '{name}' NOT FOUND in tool map. Check tool definition and _get_tools_map().\n\n")
            
            try:
                agents[name] = Agent(
                    role=config.get('role', f'Agent {name} Role Missing'), 
                    goal=config.get('goal', f'Agent {name} Goal Missing'),
                    backstory=config.get('backstory', f'Agent {name} Backstory Missing'),
                    allow_delegation=config.get('allow_delegation', False),
                    tools=agent_tools, # הרשימה תכיל רק כלים קיימים
                    llm=self.llm,
                    verbose=config.get('verbose', True) 
                )
            except Exception as e:
                 raise ValueError(f"Error creating agent '{name}': {e}. Check YAML configuration and tool definitions.")

        # Create Tasks
        tasks = {}
        if not self.tasks_config: 
            raise ValueError(f"Tasks configuration file is empty or invalid for workflow '{self.workflow_name}'. Check tasks.yaml.")
            
        for name, config in self.tasks_config.items():
            if not isinstance(config, dict): 
                print(f"Warning: Invalid config format for task '{name}'. Skipping.")
                continue

            description_template = config.get('description')
            if description_template:
                 try:
                     description = description_template.format(topic=topic)
                 except KeyError as e:
                     print(f"Warning: Placeholder '{e}' in task '{name}' description could not be filled. Using raw description.")
                     description = description_template 
            else:
                 print(f"Warning: Task '{name}' has no description. Skipping.")
                 continue

            agent_name = config.get('agent')
            if not agent_name or agent_name not in agents:
                 print(f"Warning: Agent '{agent_name}' specified for task '{name}' not found. Skipping task.")
                 continue 

            tasks[name] = Task(
                description=description,
                expected_output=config.get('expected_output', 'Default Expected Output'), 
                agent=agents[agent_name] 
            )

        # Link context between tasks
        for name, config in self.tasks_config.items():
             if name in tasks and 'context' in config and config['context'] is not None:
                context_tasks = []
                context_list = config['context'] if isinstance(config['context'], list) else [config['context']] 
                
                for task_name in context_list:
                    if task_name in tasks:
                        context_tasks.append(tasks[task_name])
                    else:
                        print(f"Warning: Context task '{task_name}' for task '{name}' does not exist. Skipping context link.")
                
                if context_tasks: 
                    tasks[name].context = context_tasks

        valid_tasks = list(tasks.values())
        if not valid_tasks:
            raise ValueError("No valid tasks were created. Check agent assignments and descriptions in tasks.yaml.")

        # Assemble the Crew
        try:
            self.crew = Crew(
                agents=list(agents.values()),
                tasks=valid_tasks, 
                process=Process.sequential, 
                verbose=True 
            )
        except Exception as e:
             raise ValueError(f"Error creating Crew object: {e}. Check agent/task definitions.")


    def run(self, topic: str):
        """Runs the crew with the given topic and returns the result."""
        try:
            self.setup_crew(topic) 
            if not hasattr(self, 'crew') or not self.crew:
                 raise RuntimeError("Crew object was not successfully created during setup.")
                 
            result = self.crew.kickoff(inputs={'topic': topic})
            return result
        except Exception as e:
            print(f"Error during crew execution for workflow '{self.workflow_name}': {e}")
            return f"An error occurred during crew execution: {e}"