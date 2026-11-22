import sys
from pathlib import Path
if __name__ == "__main__":
    if len(sys.argv)==2 and sys.argv[1]=="status":
        print(Path("notes/progress.md").read_text(encoding="utf-8-sig"))
    else:
        print("Usage: python scripts.py status")
