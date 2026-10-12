# Paste this into the PythonAnywhere WSGI file, then change YOURUSERNAME.
import sys

path = "/home/YOURUSERNAME/ASEEL"
if path not in sys.path:
    sys.path.insert(0, path)

from app import app as application
