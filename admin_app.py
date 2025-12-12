import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT_DIR))

import streamlit as st

st.set_page_config(page_title="Admin Dashboard", layout="wide")

admin_dashboard_file = ROOT_DIR / "app" / "admin_dashboard" / "app.py"

with open(admin_dashboard_file, "r", encoding="utf-8") as f:
    code = compile(f.read(), str(admin_dashboard_file), "exec")
    exec(code)
