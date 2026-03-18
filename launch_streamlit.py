"""
Local dev launcher for Lpp Media Analisis dashboard.
Run: python launch_streamlit.py
"""
import subprocess, sys, os

os.chdir(os.path.dirname(os.path.abspath(__file__)))
subprocess.run([sys.executable, "-m", "streamlit", "run", "dashboard/app.py", "--server.port=8501"])
