import unittest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.validate_email_regex_tests import validate_email_regex_tests

if __name__=='__main__': unittest.main()