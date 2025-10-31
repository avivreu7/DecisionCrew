# decisioncrew/main.py

from dotenv import load_dotenv
from decisioncrew.crews.intelligence_crew import IntelligenceCrew

# טעינת משתני סביבה (API Keys) מהקובץ .env
# חשוב שזה יקרה לפני כל דבר אחר
load_dotenv()

def main():
    """
    הפונקציה הראשית להרצת בדיקה של המערכת מהטרמינל.
    """
    print("--- Starting DecisionCrew OSINT Workflow ---")
    
    # הגדרת נושא המחקר לבדיקה
    topic = input("הזן את שאלת המודיעין לניתוח: ")
    
    print(f"Research Topic: {topic}")
    print("Initializing Intelligence Crew...")
    
    # יצירת מופע של הצוות עם זרימת העבודה של OSINT
    crew = IntelligenceCrew(workflow_name="osint")
    
    # הרצת התהליך
    result = crew.run(topic)
    
    # הדפסת התוצאה הסופית
    print("\n\n--- FINAL REPORT ---")
    print("--------------------")
    print(result)

if __name__ == "__main__":
    main()