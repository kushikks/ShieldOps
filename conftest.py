import sys
import os

# Add the project root directory to Python's module path
# This allows pytest to find app.py and ai_service.py regardless of where it's run from
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
