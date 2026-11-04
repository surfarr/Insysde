import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for path in (os.path.join(ROOT, "kadane"), os.path.join(ROOT, "app")):
    if path not in sys.path:
        sys.path.insert(0, path)
