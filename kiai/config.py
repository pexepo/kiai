import os

# Tokens: defaults are baked in per project owner's request,
# but can always be overridden via environment variables.
BOT_TOKEN = os.getenv('BOT_TOKEN', '8561860190:AAHq9BJBkPdsFa6nnNuJ-e7bo_AktCYIkPE')
ORDR_API_KEY = os.getenv('ORDR_API_KEY', 'U4RcAeGwt8WJzsD4gsSrzcCeH30zIW4Y')

ORDR_API = 'https://apis.issou.best/ordr'
SUPPORTER_URL = 'https://osu.ppy.sh/store/products/supporter-tag?target=pex'
WEBAPP_URL = os.getenv('WEBAPP_URL', 'https://burmalda-group1.gitlab.io/burmalda-project/')

DB_PATH = os.getenv('DB_PATH', 'kiai.db')
COOLDOWN_SECONDS = int(os.getenv('COOLDOWN_SECONDS', 15 * 60))
MAX_REPLAY_SIZE = 10 * 1024 * 1024  # 10 MB

RESOLUTIONS = ('960x540', '1280x720', '1920x1080')
SKINS_PER_PAGE = 8
