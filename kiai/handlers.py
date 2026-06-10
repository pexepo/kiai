import asyncio
import io
import json
import logging

from aiogram import Bot, F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import BufferedInputFile, CallbackQuery, Message

from . import db, ordr
from . import keyboards as kb
from .config import MAX_REPLAY_SIZE, RESOLUTIONS, SKINS_PER_PAGE
from .i18n import t

log = logging.getLogger(__name__)
router = Router()

POLL_INTERVAL = 8
POLL_TIMEOUT = 30 * 60


def fmt_settings(lang, s):
    smooth = t(lang, 'smooth_mb') if s['motion_blur'] else t(lang, 'smooth_std')
    return t(lang, 'settings').format(skin=s['skin_name'], res=s['resolution'], smooth=smooth)


@router.message(CommandStart())
async def cmd_start(m: Message):
    lang = db.get_lang(m.from_user.id)
    if not lang:
        await m.answer(t('en', 'choose_lang'), reply_markup=kb.lang_kb())
    else:
        await m.answer(t(lang, 'menu'), reply_markup=kb.menu_kb(lang))


@router.message(Command('app'))
async def cmd_app(m: Message):
    lang = db.get_lang(m.from_user.id) or 'en'
    await m.answer(t(lang, 'app_hint'), reply_markup=kb.app_kb(lang))


@router.callback_query(F.data == 'lang')
async def cb_lang_menu(q: CallbackQuery):
    await q.message.edit_text(t('en', 'choose_lang'), reply_markup=kb.lang_kb())
    await q.answer()


@router.callback_query(F.data.startswith('lang:'))
async def cb_lang(q: CallbackQuery):
    lang = q.data.split(':')[1]
    db.set_lang(q.from_user.id, lang)
    await q.message.edit_text(t(lang, 'menu'), reply_markup=kb.menu_kb(lang))
    await q.answer()


@router.callback_query(F.data == 'menu')
async def cb_menu(q: CallbackQuery):
    lang = db.get_lang(q.from_user.id) or 'en'
    await q.message.edit_text(t(lang, 'menu'), reply_markup=kb.menu_kb(lang))
    await q.answer()


@router.callback_query(F.data == 'render')
async def cb_render(q: CallbackQuery):
    lang = db.get_lang(q.from_user.id) or 'en'
    await q.message.edit_text(t(lang, 'send_replay'), reply_markup=kb.back_kb(lang, 'menu'))
    await q.answer()


@router.callback_query(F.data == 'settings')
async def cb_settings(q: CallbackQuery):
    lang = db.get_lang(q.from_user.id) or 'en'
    s = db.get_settings(q.from_user.id)
    await q.message.edit_text(fmt_settings(lang, s), reply_markup=kb.settings_kb(lang))
    await q.answer()


@router.callback_query(F.data.startswith('skins:'))
async def cb_skins(q: CallbackQuery):
    lang = db.get_lang(q.from_user.id) or 'en'
    page = int(q.data.split(':')[1])
    try:
        skins, total = await ordr.get_skins(page)
    except Exception:
        log.exception('skin list failed')
        await q.answer(t(lang, 'err_skins'), show_alert=True)
        return
    max_pages = max(1, -(-total // SKINS_PER_PAGE))
    await q.message.edit_text(t(lang, 'choose_skin'), reply_markup=kb.skins_kb(lang, skins, page, max_pages))
    await q.answer()


@router.callback_query(F.data.startswith('skin:'))
async def cb_skin(q: CallbackQuery):
    lang = db.get_lang(q.from_user.id) or 'en'
    _, skin_id, name = q.data.split(':', 2)
    db.set_settings(q.from_user.id, skin=skin_id, skin_name=name or skin_id)
    s = db.get_settings(q.from_user.id)
    await q.message.edit_text(fmt_settings(lang, s), reply_markup=kb.settings_kb(lang))
    await q.answer(t(lang, 'saved'))


@router.callback_query(F.data == 'resmenu')
async def cb_res_menu(q: CallbackQuery):
    lang = db.get_lang(q.from_user.id) or 'en'
    await q.message.edit_text(t(lang, 'choose_res'), reply_markup=kb.res_kb(lang))
    await q.answer()


@router.callback_query(F.data.startswith('res:'))
async def cb_res(q: CallbackQuery):
    lang = db.get_lang(q.from_user.id) or 'en'
    val = q.data.split(':')[1]
    if val in RESOLUTIONS:
        db.set_settings(q.from_user.id, resolution=val)
    s = db.get_settings(q.from_user.id)
    await q.message.edit_text(fmt_settings(lang, s), reply_markup=kb.settings_kb(lang))
    await q.answer(t(lang, 'saved'))


@router.callback_query(F.data == 'smoothmenu')
async def cb_smooth_menu(q: CallbackQuery):
    lang = db.get_lang(q.from_user.id) or 'en'
    await q.message.edit_text(t(lang, 'choose_smooth'), reply_markup=kb.smooth_kb(lang))
    await q.answer()


@router.callback_query(F.data.startswith('mb:'))
async def cb_mb(q: CallbackQuery):
    lang = db.get_lang(q.from_user.id) or 'en'
    db.set_settings(q.from_user.id, motion_blur=int(q.data.split(':')[1]))
    s = db.get_settings(q.from_user.id)
    await q.message.edit_text(fmt_settings(lang, s), reply_markup=kb.settings_kb(lang))
    await q.answer(t(lang, 'saved'))


@router.callback_query(F.data == 'noop')
async def cb_noop(q: CallbackQuery):
    await q.answer()


@router.message(F.web_app_data)
async def on_webapp(m: Message):
    lang = db.get_lang(m.from_user.id) or 'en'
    try:
        data = json.loads(m.web_app_data.data)
        res = data.get('resolution')
        if res in RESOLUTIONS:
            db.set_settings(m.from_user.id, resolution=res)
        db.set_settings(m.from_user.id, motion_blur=1 if data.get('motionBlur') else 0)
        skin = (data.get('skin') or '').strip()
        if skin:
            db.set_settings(m.from_user.id, skin=skin, skin_name=skin[:24])
    except Exception:
        return await m.answer(t(lang, 'err_webapp'))
    s = db.get_settings(m.from_user.id)
    await m.answer(t(lang, 'webapp_saved') + '\n\n' + fmt_settings(lang, s), reply_markup=kb.menu_kb(lang))


@router.message(F.document)
async def on_replay(m: Message, bot: Bot):
    lang = db.get_lang(m.from_user.id) or 'en'
    doc = m.document
    name = (doc.file_name or '').lower()
    if not name.endswith('.osr'):
        return await m.answer(t(lang, 'err_not_osr'))
    if doc.file_size and doc.file_size > MAX_REPLAY_SIZE:
        return await m.answer(t(lang, 'err_too_big'))
    left = db.cooldown_remaining(m.from_user.id)
    if left > 0:
        mins, secs = divmod(left, 60)
        return await m.answer(t(lang, 'cooldown').format(mins=mins, secs=secs))

    buf = io.BytesIO()
    try:
        await bot.download(doc, destination=buf)
    except Exception:
        log.exception('telegram download failed')
        return await m.answer(t(lang, 'err_download'))
    data = buf.getvalue()
    # Minimal .osr sanity check: first byte is the gamemode (0-3).
    if len(data) < 16 or data[0] > 3:
        return await m.answer(t(lang, 'err_corrupted'))

    s = db.get_settings(m.from_user.id)
    status = await m.answer(t(lang, 'submitting'))
    try:
        resp = await ordr.submit_render(data, doc.file_name, m.from_user.first_name, s)
    except ordr.OrdrError as e:
        key = ordr.ERROR_KEYS.get(e.code, 'ordr_e_unknown')
        return await status.edit_text(t(lang, 'err_ordr').format(reason=t(lang, key), detail=e.message))
    except Exception:
        log.exception('ordr submit failed')
        return await status.edit_text(t(lang, 'err_network'))

    db.set_cooldown(m.from_user.id)
    render_id = resp['renderID']
    await status.edit_text(t(lang, 'submitted').format(rid=render_id))
    asyncio.create_task(track_render(status, lang, render_id))


async def track_render(status: Message, lang: str, render_id: int):
    last_text = ''
    waited = 0
    while waited < POLL_TIMEOUT:
        await asyncio.sleep(POLL_INTERVAL)
        waited += POLL_INTERVAL
        try:
            r = await ordr.get_render(render_id)
        except Exception:
            continue
        if not r:
            continue
        progress = r.get('progress') or ''
        video = r.get('videoUrl') or ''
        if video:
            return await deliver_video(status, lang, render_id, video)
        if 'fail' in progress.lower():
            return await status.edit_text(t(lang, 'failed').format(detail=progress))
        text = t(lang, 'progress').format(progress=progress, rid=render_id)
        if text != last_text:
            last_text = text
            try:
                await status.edit_text(text)
            except Exception:
                pass
    try:
        await status.edit_text(t(lang, 'timeout').format(rid=render_id))
    except Exception:
        pass


async def deliver_video(status: Message, lang: str, render_id: int, video_url: str):
    """Send the finished render as a real video in chat. o!rdr's videoUrl is a
    watch page, so resolve the direct mp4 first (avoids the empty-video bug),
    download it and attach it. Fall back to a plain link if it is too big."""
    direct = await ordr.resolve_direct_video(render_id, video_url)
    data = await ordr.download_video(direct)
    if data:
        try:
            await status.answer_video(
                video=BufferedInputFile(data, filename=f'kiai_render_{render_id}.mp4'),
                caption=t(lang, 'done').format(url=video_url),
                supports_streaming=True,
                reply_markup=kb.supporter_kb(lang),
            )
            try:
                await status.delete()
            except Exception:
                pass
            return
        except Exception:
            log.exception('video send failed, falling back to link')
    await status.edit_text(t(lang, 'done').format(url=video_url),
                           reply_markup=kb.supporter_kb(lang))


@router.message()
async def fallback(m: Message):
    lang = db.get_lang(m.from_user.id)
    if not lang:
        return await m.answer(t('en', 'choose_lang'), reply_markup=kb.lang_kb())
    await m.answer(t(lang, 'menu'), reply_markup=kb.menu_kb(lang))
