import os
import sys

# Add project root and backend folder to sys.path for Vercel Python runtime
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
backend_dir = os.path.join(project_root, "backend")

if project_root not in sys.path:
    sys.path.insert(0, project_root)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from backend.main import app

# Vercel Serverless Function entry point
__all__ = ["app"]
