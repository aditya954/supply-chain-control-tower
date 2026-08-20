"""DockVision — mobile truck load capture + utilization dashboard."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import streamlit as st

st.set_page_config(
    page_title="DockVision",
    page_icon=":material/local_shipping:",
    layout="wide",
    initial_sidebar_state="collapsed",
)

pages = st.navigation(
    [
        st.Page("app_pages/capture.py", title="Capture", icon=":material/photo_camera:"),
        st.Page("app_pages/dashboard.py", title="Dashboard", icon=":material/dashboard:"),
    ]
)
pages.run()
