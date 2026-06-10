import sqlite3
import time

from .config import COOLDOWN_SECONDS, DB_PATH

DEFAULTS = {'skin': 'default', 'skin_name': 'Default', 'resolution': '1280x720', 'motion_blur': 0}


def _conn():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c


def init():
    with _conn() as c:
        c.execute(
            'CREATE TABLE IF NOT EXISTS users ('
            ' user_id INTEGER PRIMARY KEY,'
            ' lang TEXT,'
            " skin TEXT DEFAULT 'default',"
            " skin_name TEXT DEFAULT 'Default',"
            " resolution TEXT DEFAULT '1280x720',"
            ' motion_blur INTEGER DEFAULT 0,'
            ' last_render INTEGER DEFAULT 0)'
        )


def _ensure(uid):
    with _conn() as c:
        c.execute('INSERT OR IGNORE INTO users (user_id) VALUES (?)', (uid,))


def get_lang(uid):
    with _conn() as c:
        row = c.execute('SELECT lang FROM users WHERE user_id = ?', (uid,)).fetchone()
    return row['lang'] if row and row['lang'] else None


def set_lang(uid, lang):
    _ensure(uid)
    with _conn() as c:
        c.execute('UPDATE users SET lang = ? WHERE user_id = ?', (lang, uid))


def get_settings(uid):
    with _conn() as c:
        row = c.execute('SELECT * FROM users WHERE user_id = ?', (uid,)).fetchone()
    if not row:
        return dict(DEFAULTS)
    return {k: row[k] for k in DEFAULTS}


def set_settings(uid, **kwargs):
    _ensure(uid)
    cols = ', '.join(f'{k} = ?' for k in kwargs)
    with _conn() as c:
        c.execute(f'UPDATE users SET {cols} WHERE user_id = ?', (*kwargs.values(), uid))


def cooldown_remaining(uid):
    with _conn() as c:
        row = c.execute('SELECT last_render FROM users WHERE user_id = ?', (uid,)).fetchone()
    if not row:
        return 0
    left = row['last_render'] + COOLDOWN_SECONDS - int(time.time())
    return max(0, left)


def set_cooldown(uid):
    _ensure(uid)
    with _conn() as c:
        c.execute('UPDATE users SET last_render = ? WHERE user_id = ?', (int(time.time()), uid))
