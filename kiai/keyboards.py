from aiogram.types import (InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton,
                           ReplyKeyboardMarkup, WebAppInfo)

from .config import RESOLUTIONS, SUPPORTER_URL, WEBAPP_URL
from .i18n import t


def lang_kb():
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text='\ud83c\uddf7\ud83c\uddfa \u0420\u0443\u0441\u0441\u043a\u0438\u0439', callback_data='lang:ru'),
        InlineKeyboardButton(text='\ud83c\uddec\ud83c\udde7 English', callback_data='lang:en'),
    ]])


def menu_kb(lang):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang, 'btn_render'), callback_data='render')],
        [InlineKeyboardButton(text=t(lang, 'btn_settings'), callback_data='settings')],
        [InlineKeyboardButton(text=t(lang, 'btn_supporter'), url=SUPPORTER_URL)],
        [InlineKeyboardButton(text=t(lang, 'btn_lang'), callback_data='lang')],
    ])


def back_kb(lang, target='menu'):
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=t(lang, 'btn_back'), callback_data=target)
    ]])


def app_kb(lang):
    return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[
        KeyboardButton(text=t(lang, 'btn_app'), web_app=WebAppInfo(url=WEBAPP_URL))
    ]])


def settings_kb(lang):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang, 'btn_skin'), callback_data='skins:1')],
        [InlineKeyboardButton(text=t(lang, 'btn_res'), callback_data='resmenu')],
        [InlineKeyboardButton(text=t(lang, 'btn_smooth'), callback_data='smoothmenu')],
        [InlineKeyboardButton(text=t(lang, 'btn_back'), callback_data='menu')],
    ])


def skins_kb(lang, skins, page, max_pages):
    rows = [[InlineKeyboardButton(
        text=(s.get('presentationName') or s.get('skin', '?')),
        callback_data='skin:{}:{}'.format(s['id'], (s.get('presentationName') or s.get('skin', ''))[:20]),
    )] for s in skins]
    nav = []
    if page > 1:
        nav.append(InlineKeyboardButton(text='\u00ab', callback_data=f'skins:{page - 1}'))
    nav.append(InlineKeyboardButton(text=f'{page}/{max_pages}', callback_data='noop'))
    if page < max_pages:
        nav.append(InlineKeyboardButton(text='\u00bb', callback_data=f'skins:{page + 1}'))
    rows.append(nav)
    rows.append([InlineKeyboardButton(text=t(lang, 'btn_back'), callback_data='settings')])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def res_kb(lang):
    rows = [[InlineKeyboardButton(text=r, callback_data=f'res:{r}')] for r in RESOLUTIONS]
    rows.append([InlineKeyboardButton(text=t(lang, 'btn_back'), callback_data='settings')])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def smooth_kb(lang):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang, 'smooth_std'), callback_data='mb:0')],
        [InlineKeyboardButton(text=t(lang, 'smooth_mb'), callback_data='mb:1')],
        [InlineKeyboardButton(text=t(lang, 'btn_back'), callback_data='settings')],
    ])


def supporter_kb(lang):
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=t(lang, 'btn_supporter'), url=SUPPORTER_URL)
    ]])
