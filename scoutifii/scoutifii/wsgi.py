import os
import pathlib
import dotenv
from django.core.wsgi import get_wsgi_application

CURRENT_DIR = pathlib.Path(__file__).resolve().parent
BASE_DIR = CURRENT_DIR.parent
ENV_PATH_FILE = BASE_DIR / '.env'

dotenv.load_dotenv(str(ENV_PATH_FILE))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'scoutifii.settings')

application = get_wsgi_application()
