# ui/app.py

import streamlit as st
from dotenv import load_dotenv
import os
import pandas as pd
from io import StringIO

# טעינת משתני סביבה
load_dotenv() 

# ייבוא הלוגיקה המרכזית
try:
    from decisioncrew.crews.intelligence_crew import IntelligenceCrew
    # 👇 ייבוא חדש לצוות משחקי המלחמה
    from decisioncrew.crews.wargames_crew import WargamesCrew
except ModuleNotFoundError:
    st.error("Could not find the 'decisioncrew' module. Make sure you run streamlit from the project root directory using 'python -m streamlit run ui/app.py'")
    st.stop() # עצירת הריצה אם המודול לא נמצא

# --- פונקציה לעיצוב RTL ---
def wrap_text_rtl(text):
    """עוטף טקסט ב-HTML ליישור מימין לשמאל"""
    return f"""
    <div style="direction: rtl; text-align: right;">
    {text}
    </div>
    """

# --- הגדרות עמוד ---
st.set_page_config(page_title="DecisionCrew Intelligence", layout="wide")
st.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR_x6BWHAY_h7C6WsLQzICh0wAlQJ0_VqL_Hw&s" , width= 100) # Placeholder logo
st.title("DecisionCrew - מערכת תומכת החלטה מבוססת AI 🧠")

# --- אתחול Session State ---
if 'intelligence_report' not in st.session_state:
    st.session_state.intelligence_report = None
if 'wargame_report' not in st.session_state:
    st.session_state.wargame_report = None

# --- סרגל צד להעלאות ---
csv_context_string = None
with st.sidebar:
    st.header("📂 טעינת קבצי CSV")
    uploaded_file = st.file_uploader("טען קובץ CSV לניתוח:", type=["csv"])
    st.info("הכותרות ו-90 השורות הראשונות של הקובץ יצורפו אוטומטית לקונטקסט של הסוכנים.")
    if uploaded_file is not None:
        try:
            string_data = StringIO(uploaded_file.getvalue().decode('utf-8'))
            df_head = pd.read_csv(string_data, nrows=90)
            csv_context_string = f"--- START OF UPLOADED CSV DATA ('{uploaded_file.name}') ---\n"
            csv_context_string += df_head.to_string()
            csv_context_string += "\n--- END OF UPLOADED CSV DATA ---"
            st.success(f"קובץ '{uploaded_file.name}' נקרא בהצלחה!")
            st.dataframe(df_head)
        except Exception as e:
            st.error(f"שגיאה בקריאת קובץ ה-CSV: {e}")
            csv_context_string = None

# --- חלק 1: ניתוח מודיעין ---
st.header("שלב 1: ניתוח מודיעין")

workflow_dir = os.path.join("config", "workflows")
if os.path.exists(workflow_dir):
     # הסרת 'wargames' מהרשימה הראשית
     available_workflows = [d for d in os.listdir(workflow_dir) if os.path.isdir(os.path.join(workflow_dir, d)) and d != 'wargames']
else:
     available_workflows = ["osint"] # Fallback

selected_workflow = st.selectbox(
    "בחר את סוג הניתוח:",
    available_workflows,
    index=available_workflows.index("combined") if "combined" in available_workflows else 0 
)

topic_input = st.text_area(
    "הזן את שאלת המודיעין לניתוח:", 
    height=100, 
    placeholder="לדוגמה: מה הסבירות לעימות צבאי בין יוון לטורקיה בחודש הקרוב?"
)

if st.button("🚀 הפעל ניתוח מודיעין"):
    st.session_state.intelligence_report = None # איפוס דוחות קודמים
    st.session_state.wargame_report = None      # איפוס דוחות קודמים
    result_placeholder = st.empty() 

    if not topic_input:
        result_placeholder.error("אנא הזן שאלת מודיעין.")
    elif not os.getenv("OPENAI_API_KEY"): 
        result_placeholder.error("מפתח OpenAI API לא הוגדר בקובץ .env")
    else:
        try:
            crew = IntelligenceCrew(workflow_name=selected_workflow)
            run_topic = topic_input
            if csv_context_string:
                 run_topic = f"{topic_input}\n\n{csv_context_string}"
                 st.info(f"מנתח את השאילתה תוך התייחסות לנתונים מקובץ '{uploaded_file.name}'...")

            with st.spinner(f"מעבד את הבקשה באמצעות זרימת עבודה '{selected_workflow}'... זה עשוי לקחת מספר דקות...⏳"):
                result = crew.run(topic=run_topic) 
            
            result_str = str(result)
            if result_str.startswith("An error occurred"):
                result_placeholder.error(f"הריצה נכשלה: {result_str}")
            else: 
                result_placeholder.empty() 
                st.success("ניתוח המודיעין הושלם!")
                # 👇 שמירת הדוח ב-Session State
                st.session_state.intelligence_report = result_str
            
        except Exception as e:
            result_placeholder.error(f"אירעה שגיאה בלתי צפויה במהלך הריצה: {e}")
            st.exception(e) 

# --- הצגת דוח המודיעין (אם קיים) ---
if st.session_state.intelligence_report:
    st.markdown("---")
    st.subheader("📄 תדריך מודיעין:")
    st.markdown(wrap_text_rtl(st.session_state.intelligence_report), unsafe_allow_html=True)
    
    # --- חלק 2: סימולציית משחק מלחמה ---
    st.markdown("---")
    st.header("שלב 2: הפעלת סימולציית משחק מלחמה (אופציונלי)")
    st.info("בהתבסס על הדוח שהתקבל, הזן מהלך שברצונך לדמות.")
    
    wargame_action_input = st.text_input(
        "הזן את המהלך שלך (למשל, 'הטלת סנקציות כלכליות על מדינה X', 'הזזת כוחות לגבול'):",
        placeholder="מה אם נבצע תקיפה אווירית מוגבלת?"
    )
    
    if st.button("👾 הפעל סימולציה"):
        st.session_state.wargame_report = None # איפוס דוח סימולציה קודם
        wargame_placeholder = st.empty()
        
        if not wargame_action_input:
            wargame_placeholder.error("אנא הזן מהלך לסימולציה.")
        else:
            try:
                # אתחול צוות משחק המלחמה
                wargames_crew = WargamesCrew()
                
                with st.spinner("מריץ סימולציית תגובה... 🎲"):
                    # העברת דוח המודיעין והמהלך של המשתמש
                    wargame_result = wargames_crew.run(
                        intelligence_context=st.session_state.intelligence_report,
                        user_action=wargame_action_input
                    )
                
                result_str = str(wargame_result)
                if result_str.startswith("An error occurred"):
                    wargame_placeholder.error(f"הסימולציה נכשלה: {result_str}")
                else: 
                    wargame_placeholder.empty() 
                    st.success("הסימולציה הושלמה!")
                    # 👇 שמירת דוח הסימולציה
                    st.session_state.wargame_report = result_str
                    
            except Exception as e:
                wargame_placeholder.error(f"אירעה שגיאה בלתי צפויה במהלך הסימולציה: {e}")
                st.exception(e)

# --- הצגת דוח משחק המלחמה (אם קיים) ---
if st.session_state.wargame_report:
    st.subheader("🕹️ סיכום משחק המלחמה:")
    st.markdown(wrap_text_rtl(st.session_state.wargame_report), unsafe_allow_html=True)