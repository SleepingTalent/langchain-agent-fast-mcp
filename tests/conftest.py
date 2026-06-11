import sys
from pathlib import Path

# Make frontend/ importable as a flat namespace in tests (mirrors how Streamlit runs app.py)
sys.path.insert(0, str(Path(__file__).parent.parent / "frontend"))
