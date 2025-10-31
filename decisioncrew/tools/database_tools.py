# decisioncrew/tools/database_tools.py

# פונקציית דמה פשוטה כדי למנוע שגיאות ייבוא
# היא תודיע לסוכן שהכלי מנוטרל אם ינסה להשתמש בו
def db_query_tool(*args, **kwargs) -> str:
     """This tool is currently disabled due to validation errors."""
     print("WARNING: 'db_query_tool' was called but is disabled.")
     return "Database tool is currently disabled due to configuration issues."