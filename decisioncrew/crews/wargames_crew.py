# decisioncrew/crews/wargames_crew.py

import yaml
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
import os

class WargamesCrew:
    def __init__(self):
        # זרימת העבודה של משחקי מלחמה היא קבועה
        self.workflow_name = "wargames"
        self.config_path = os.path.join("config", "workflows", self.workflow_name) + os.sep
        self._load_configs()
        model_name = os.getenv("MODEL_NAME", "gpt-4o") 
        self.llm = ChatOpenAI(model=model_name)

    def _load_configs(self):
        """טוען את קבצי התצורה של הסוכנים והמשימות מה-YAML."""
        agents_file = os.path.join(self.config_path, "agents.yaml")
        tasks_file = os.path.join(self.config_path, "tasks.yaml")
        try:
            with open(agents_file, 'r', encoding='utf-8') as f:
                self.agents_config = yaml.safe_load(f)
            with open(tasks_file, 'r', encoding='utf-8') as f:
                self.tasks_config = yaml.safe_load(f)
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Configuration files not found for workflow '{self.workflow_name}'. Searched in: {self.config_path}") from e
        except yaml.YAMLError as e:
             raise ValueError(f"Error parsing YAML file in {self.config_path}: {e}") from e
        
        if not self.agents_config:
             raise ValueError(f"Agents configuration file '{agents_file}' is empty or invalid.")
        if not self.tasks_config:
             raise ValueError(f"Tasks configuration file '{tasks_file}' is empty or invalid.")

    def _get_tools_map(self):
        """
        מחזיר מפת כלים. כרגע אין כלים מיוחדים למשחקי מלחמה, 
        אך ניתן להוסיף בעתיד (למשל, כלי "הטלת קובייה" להסתברות).
        """
        return {} # התחלה פשוטה ללא כלים

    def setup_crew(self, intelligence_context: str, user_action: str):
        """מרכיב את הצוות על בסיס התצורה שנטענה."""
        
        tools_map = self._get_tools_map()
        
        # יצירת סוכנים
        agents = {}
        for name, config in self.agents_config.items():
            agent_tools_config = config.get("tools", [])
            agent_tools = [tools_map[tool_name] for tool_name in agent_tools_config if tool_name in tools_map]
            
            try:
                agents[name] = Agent(
                    role=config.get('role'), 
                    goal=config.get('goal'),
                    backstory=config.get('backstory'),
                    allow_delegation=config.get('allow_delegation', False),
                    tools=agent_tools, 
                    llm=self.llm,
                    verbose=config.get('verbose', True) 
                )
            except Exception as e:
                 raise ValueError(f"Error creating agent '{name}': {e}.")

        # יצירת משימות
        tasks = {}
        for name, config in self.tasks_config.items():
            description_template = config.get('description')
            try:
                 # מילוי כל הפלייסהולדרים שהגדרנו ב-YAML
                 description = description_template.format(
                     intelligence_context=intelligence_context,
                     user_action=user_action
                 )
            except KeyError as e:
                 print(f"Warning: Placeholder '{e}' in task '{name}' description could not be filled. Using raw description.")
                 description = description_template 
            
            agent_name = config.get('agent')
            if not agent_name or agent_name not in agents:
                 print(f"Warning: Agent '{agent_name}' for task '{name}' not found. Skipping task.")
                 continue 

            tasks[name] = Task(
                description=description,
                expected_output=config.get('expected_output'), 
                agent=agents[agent_name] 
            )

        # קישור קונטקסט
        for name, config in self.tasks_config.items():
             if name in tasks and 'context' in config and config['context'] is not None:
                context_tasks = [tasks[task_name] for task_name in config['context'] if task_name in tasks]
                if context_tasks: 
                    tasks[name].context = context_tasks

        valid_tasks = list(tasks.values())
        if not valid_tasks:
            raise ValueError("No valid wargame tasks were created.")

        # הרכבת הצוות
        try:
            self.crew = Crew(
                agents=list(agents.values()),
                tasks=valid_tasks, 
                process=Process.sequential, 
                verbose=True 
            )
        except Exception as e:
             raise ValueError(f"Error creating Wargames Crew object: {e}.")


    def run(self, intelligence_context: str, user_action: str):
        """מריץ את צוות משחק המלחמה ומחזיר את התוצאה."""
        try:
            self.setup_crew(intelligence_context, user_action) 
            if not hasattr(self, 'crew') or not self.crew:
                 raise RuntimeError("Wargames Crew object was not created.")
                 
            # העברת המשתנים כקלט ל-kickoff
            result = self.crew.kickoff(inputs={
                'intelligence_context': intelligence_context,
                'user_action': user_action
            })
            return result
        except Exception as e:
            print(f"Error during wargames crew execution: {e}")
            return f"An error occurred during wargames execution: {e}"