import sys
import os
from mangum import Mangum

# Add the project root to sys.path to import from backend
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.app import app

handler = Mangum(app)