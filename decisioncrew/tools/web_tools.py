# decisioncrew/tools/web_tools.py

# אנחנו משאירים רק את הכלים המובנים והסטנדרטיים שעובדים
from crewai_tools import SerperDevTool, WebsiteSearchTool

# --- כלים סטנדרטיים ---
web_search_tool = SerperDevTool()
website_search_tool = WebsiteSearchTool()

# --- כל הכלים המותאמים אישית (NewsAPI, Telegram) הוסרו מכאן ---