import aiohttp

from .config import ORDR_API, ORDR_API_KEY, SKINS_PER_PAGE

# Best-effort mapping of o!rdr error codes to i18n keys.
# Unknown codes fall back to 'ordr_e_unknown' and the raw o!rdr
# message is always relayed to the user for full transparency.
ERROR_KEYS = {
    2: 'ordr_e_emergency',
    5: 'ordr_e_download',
    6: 'ordr_e_parse',
    7: 'ordr_e_empty',
    8: 'ordr_e_gamemode',
    9: 'ordr_e_mods',
    15: 'ordr_e_beatmap',
    16: 'ordr_e_server',
    23: 'ordr_e_banned',
    24: 'ordr_e_banned',
    29: 'ordr_e_ratelimit',
}


class OrdrError(Exception):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code
        self.message = message


async def submit_render(replay: bytes, filename: str, username: str, settings: dict) -> dict:
    form = aiohttp.FormData()
    form.add_field('replayFile', replay, filename=filename, content_type='application/octet-stream')
    form.add_field('username', (username or 'Kiai Render')[:32])
    form.add_field('resolution', settings['resolution'])
    form.add_field('skin', str(settings['skin']))
    form.add_field('verificationKey', ORDR_API_KEY)
    if settings.get('motion_blur'):
        form.add_field('motionBlur960fps', 'true')
    async with aiohttp.ClientSession() as sess:
        async with sess.post(f'{ORDR_API}/renders', data=form) as r:
            data = await r.json(content_type=None) or {}
            if r.status != 201 or 'renderID' not in data:
                raise OrdrError(data.get('errorCode', -1), data.get('message', f'HTTP {r.status}'))
            return data


async def get_render(render_id: int):
    async with aiohttp.ClientSession() as sess:
        async with sess.get(f'{ORDR_API}/renders', params={'renderID': render_id}) as r:
            data = await r.json(content_type=None) or {}
    renders = data.get('renders') or []
    return renders[0] if renders else None


async def get_skins(page: int = 1):
    async with aiohttp.ClientSession() as sess:
        async with sess.get(f'{ORDR_API}/skins', params={'page': page, 'pageSize': SKINS_PER_PAGE}) as r:
            data = await r.json(content_type=None) or {}
    return data.get('skins') or [], data.get('maxSkins', 0)
