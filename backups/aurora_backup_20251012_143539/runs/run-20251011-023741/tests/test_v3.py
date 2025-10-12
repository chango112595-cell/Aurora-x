import unittest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.create_flask_web_app_app import create_flask_web_app_app

if __name__=='__main__': unittest.main()