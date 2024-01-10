import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
WBAPIANALYTPRICEDISC=os.getenv("WBAPIANALYTPRICEDISC", "")
WBAPIMPCONT=os.getenv("WBAPIMPCONT", "")
WBAPISTATISTIC=os.getenv("WBAPISTATISTIC", "")
WBURLGETDETAIL=os.getenv("WBURLGETDETAIL", "")
WBURLGETSTOCKS=os.getenv("WBURLGETSTOCKS", "")
WBURLCURSORLIST=os.getenv("WBURLCURSORLIST", "")
PATH4XLSXFILE=os.getenv("path4xlsxfile", "")
BASE_DIR = Path(__file__).resolve().parent
SQLITE_DB_FILE = BASE_DIR / "db.sqlite3"
TEMPLATES_DIR = BASE_DIR / "templates"

