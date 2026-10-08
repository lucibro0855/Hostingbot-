# -*- coding: utf-8 -*-
import asyncio
import os
import sys
import html as html_lib
import zipfile
import tempfile
import shutil
import time
import sqlite3
import logging
import re
import atexit
import signal
import threading
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

os.environ["PYTHONIOENCODING"] = "utf-8"

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

import psutil
import requests
from aiogram import Bot, Dispatcher, F, Router, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode, ChatMemberStatus
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton,
    FSInputFile,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

# --- Flask Keep Alive ---
from flask import Flask
from threading import Thread as FlaskThread

flask_app = Flask(__name__)


@flask_app.route('/')
def home():
    return "bot is running...."


def run_flask():
    port = int(os.environ.get("PORT", 8080))
    flask_app.run(host='0.0.0.0', port=port)


def keep_alive():
    t = FlaskThread(target=run_flask)
    t.daemon = True
    t.start()
    print("Flask Keep-Alive server started.")


# --- Configuration ---
TOKEN = "8824814752:AAFXUYRDTfb6MyIvZtH_VITuLS9vSSs54TE"
OWNER_ID = 5339638465
ADMIN_ID = 5339638465
YOUR_USERNAME = '@lucifer_b0lte'
UPDATE_CHANNEL = '@lucifer_adss'
FORCE_JOIN_CHANNELS = {
    "@lucifer_adss": "𝐉𝐎𝐈𝐍",
}

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_BOTS_DIR = os.path.join(BASE_DIR, 'upload_bots')
IROTECH_DIR = os.path.join(BASE_DIR, 'inf')
DATABASE_PATH = os.path.join(IROTECH_DIR, 'bot_data.db')

FREE_USER_LIMIT = 150
SUBSCRIBED_USER_LIMIT = 350
ADMIN_LIMIT = 500
OWNER_LIMIT = float('inf')

os.makedirs(UPLOAD_BOTS_DIR, exist_ok=True)
os.makedirs(IROTECH_DIR, exist_ok=True)

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Premium Emoji IDs ---
PREMIUM_EMOJI_IDS = {
    "✅": "5444987348334965906", "❌": "5447647474984449520", "🔥": "5116414868357907335",
    "⚡": "5219943216781995020", "💳": "5447453226498552490", "💠": "5870498447068502918",
    "📝": "5343649643685240676", "🌐": "5447602197439218445", "📊": "5445146408153806223",
    "📦": "5303102515301083665", "📋": "4904936030232117798", "⏳": "5258113901106580375",
    "🚀": "4904936030232117798", "⚠️": "4915853119839011973", "💎": "5343636681473935403",
    "👋": "5134476056241112076", "💡": "5301275719681190738", "📈": "5134457377428341766",
    "🔢": "5444931419270839381", "🔌": "5120722716260828125", "⭐️": "5172716095697584957",
    "🆓": "5406756500108501710", "👑": "6266995104687330978", "🔍": "5258396243666681152",
    "⏱️": "5343927661213279013", "💥": "5122933683820430249", "🆔": "5447311106030726740",
    "👤": "5445174334031166029", "📅": "5343927661213279013", "🔄": "5454245266305604993",
    "🏦": "5445408306669582934", "🥰": "5444931419270839381", "😱": "5447181973544008180",
    "🔷": "5258024802010026053", "🔑": "5454386656628991407", "📆": "5343927661213279013",
    "👥": "5454371323595744068", "🥕": "5447653032672129347", "➡️": "5445350109862720603",
    "🦉": "5123344136665039833", "🍑": "5445408306669582934", "💪": "5305622454218024328",
    "🌝": "5341684837881235158", "📁": "5444908424015934570", "ℹ️": "5289930378885214069",
    "💀": "5231338559587257737", "📢": "5116445341150872576", "💰": "5116648080787112958",
    "🔘": "5219901967916084166", "🔗": "5447479640547428304", "👇": "5122933683820430249",
    "📌": "5447187153274567373", "🍳": "5305622454218024328", "💸": "5283232570660634549",
    "🎉": "5172632227871196306", "🎁": "5283031441637148958", "🚫": "5116151848855667552",
    "🛒": "5447319442562251569", "🔧": "4904936030232117798", "⛔️": "5275969776668134187",
    "🥲": "4904468402782864209", "☠️": "5231338559587257737", "🛡": "5219672809936006424",
    "📸": "5445344161333015312", "💬": "5447510826304959724", "😺": "5118590136149345664",
    "🌍": "5303440357428586778", "🔹": "5429436388447655367", "📹": "5445158077579952110",
    "📡": "5447448489149625830", "🌟": "5310224206732996002", "📍": "5447187153274567373",
    "🔐": "5258476306152038031", "😇": "6321225560789877992", "👌": "5445350109862720603",
    "⭐": "6267298050205553492", "🍭": "6267152480878990865", "⚙️": "5258023599419171861",
    "⛔": "4918014360267260850", "📥": "5350747347724810871", "💵": "5350711759625795085",
    "📂": "5444908424015934570", "🛠️": "5348239232852836489",
    "🟢": "5444987348334965906", "🔴": "5447647474984449520", "🔒": "5258476306152038031",
    "🔓": "5454386656628991407", "🔙": "5445350109862720603", "➕": "5444987348334965906",
    "➖": "5447647474984449520", "🗑️": "5447647474984449520", "📜": "4904936030232117798",
    "🎛": "5258023599419171861", "🎯": "5122933683820430249", "🎨": "5310224206732996002",
    "📤": "5444908424015934570", "🚦": "5219901967916084166", "🆕": "5444987348334965906",
}


def premium_emoji(text: str) -> str:
    """Replace emojis with premium <tg-emoji> tags."""
    if not text:
        return text
    result = str(text)
    for emoji in sorted(PREMIUM_EMOJI_IDS.keys(), key=len, reverse=True):
        eid = PREMIUM_EMOJI_IDS[emoji]
        result = result.replace(emoji, f'<tg-emoji emoji-id="{eid}">{emoji}</tg-emoji>')
    return result


def esc(s):
    if s is None:
        return ""
    return html_lib.escape(str(s))


def get_emoji_id(emoji: str):
    """For button icons."""
    v = PREMIUM_EMOJI_IDS.get(emoji)
    return int(v) if v else None


# --- Data structures ---
bot_scripts = {}
user_subscriptions = {}
user_files = {}
active_users = set()
admin_ids = {ADMIN_ID, OWNER_ID}
bot_locked = False
bot_scripts_lock = threading.Lock()
DB_LOCK = threading.Lock()

# --- Bot & Dispatcher ---
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())
router = Router()
dp.include_router(router)

MAIN_LOOP = None


# --- Force Join ---
async def is_user_joined_all(user_id: int) -> bool:
    try:
        for ch in FORCE_JOIN_CHANNELS.keys():
            member = await bot.get_chat_member(ch, user_id)
            if member.status not in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR,
                                     ChatMemberStatus.CREATOR]:
                return False
        return True
    except Exception as e:
        logger.warning(f"Force join check error {user_id}: {e}")
        return False


async def send_force_join_msg(chat_id: int):
    b = InlineKeyboardBuilder()
    for ch, name in FORCE_JOIN_CHANNELS.items():
        b.button(text=name, url=f"https://t.me/{ch.replace('@', '')}",
                 style="primary", icon=get_emoji_id("📢"))
    b.button(text="✅ Joined All", callback_data="force_join_check",
             style="success", icon=get_emoji_id("✅"))
    b.adjust(1)
    await bot.send_message(chat_id, premium_emoji("𝐉𝐎𝐈𝐍 𝐀𝐋𝐋 𝐂𝐇𝐀𝐍𝐍𝐄𝐋 𝐓𝐎 𝐔𝐒𝐄 𝐌𝐄 🤍🌙:"),
                           reply_markup=b.as_markup())


# --- Database ---
def init_db():
    logger.info(f"Initializing DB: {DATABASE_PATH}")
    try:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS subscriptions
                     (user_id INTEGER PRIMARY KEY, expiry TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS user_files
                     (user_id INTEGER, file_name TEXT, file_type TEXT,
                      PRIMARY KEY (user_id, file_name))''')
        c.execute('''CREATE TABLE IF NOT EXISTS active_users
                     (user_id INTEGER PRIMARY KEY)''')
        c.execute('''CREATE TABLE IF NOT EXISTS admins
                     (user_id INTEGER PRIMARY KEY)''')
        c.execute('INSERT OR IGNORE INTO admins (user_id) VALUES (?)', (OWNER_ID,))
        if ADMIN_ID != OWNER_ID:
            c.execute('INSERT OR IGNORE INTO admins (user_id) VALUES (?)', (ADMIN_ID,))
        conn.commit()
        conn.close()
        logger.info("DB initialized.")
    except Exception as e:
        logger.error(f"DB init err: {e}", exc_info=True)


def load_data():
    logger.info("Loading data...")
    try:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute('SELECT user_id, expiry FROM subscriptions')
        for user_id, expiry in c.fetchall():
            try:
                user_subscriptions[user_id] = {'expiry': datetime.fromisoformat(expiry)}
            except ValueError:
                logger.warning(f"Invalid expiry for {user_id}")
        c.execute('SELECT user_id, file_name, file_type FROM user_files')
        for uid, fn, ft in c.fetchall():
            user_files.setdefault(uid, []).append((fn, ft))
        c.execute('SELECT user_id FROM active_users')
        active_users.update(uid for (uid,) in c.fetchall())
        c.execute('SELECT user_id FROM admins')
        admin_ids.update(uid for (uid,) in c.fetchall())
        conn.close()
        logger.info(f"Loaded: {len(active_users)} users, {len(admin_ids)} admins.")
    except Exception as e:
        logger.error(f"Load err: {e}", exc_info=True)


init_db()
load_data()


def save_user_file(uid, fn, ft='py'):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            c.execute('INSERT OR REPLACE INTO user_files VALUES (?, ?, ?)', (uid, fn, ft))
            conn.commit()
            if uid not in user_files:
                user_files[uid] = []
            user_files[uid] = [(n, t) for n, t in user_files[uid] if n != fn]
            user_files[uid].append((fn, ft))
        except Exception as e:
            logger.error(f"save file err: {e}")
        finally:
            conn.close()


def remove_user_file_db(uid, fn):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            c.execute('DELETE FROM user_files WHERE user_id=? AND file_name=?', (uid, fn))
            conn.commit()
            if uid in user_files:
                user_files[uid] = [f for f in user_files[uid] if f[0] != fn]
                if not user_files[uid]:
                    del user_files[uid]
        except Exception as e:
            logger.error(f"remove file err: {e}")
        finally:
            conn.close()


def add_active_user(uid):
    active_users.add(uid)
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            c.execute('INSERT OR IGNORE INTO active_users VALUES (?)', (uid,))
            conn.commit()
        except Exception as e:
            logger.error(f"add active err: {e}")
        finally:
            conn.close()


def save_subscription(uid, expiry):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            c.execute('INSERT OR REPLACE INTO subscriptions VALUES (?, ?)', (uid, expiry.isoformat()))
            conn.commit()
            user_subscriptions[uid] = {'expiry': expiry}
        except Exception as e:
            logger.error(f"save sub err: {e}")
        finally:
            conn.close()


def remove_subscription_db(uid):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            c.execute('DELETE FROM subscriptions WHERE user_id=?', (uid,))
            conn.commit()
            user_subscriptions.pop(uid, None)
        except Exception as e:
            logger.error(f"remove sub err: {e}")
        finally:
            conn.close()


def add_admin_db(aid):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            c.execute('INSERT OR IGNORE INTO admins VALUES (?)', (aid,))
            conn.commit()
            admin_ids.add(aid)
        except Exception as e:
            logger.error(f"add admin err: {e}")
        finally:
            conn.close()


def remove_admin_db(aid):
    if aid == OWNER_ID:
        return False
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            c.execute('DELETE FROM admins WHERE user_id=?', (aid,))
            conn.commit()
            admin_ids.discard(aid)
            return c.rowcount > 0
        except Exception as e:
            logger.error(f"remove admin err: {e}")
            return False
        finally:
            conn.close()


# --- Helpers ---
def get_user_folder(uid):
    p = os.path.join(UPLOAD_BOTS_DIR, str(uid))
    os.makedirs(p, exist_ok=True)
    return p


def get_user_file_limit(uid):
    if uid == OWNER_ID: return OWNER_LIMIT
    if uid in admin_ids: return ADMIN_LIMIT
    if uid in user_subscriptions and user_subscriptions[uid]['expiry'] > datetime.now():
        return SUBSCRIBED_USER_LIMIT
    return FREE_USER_LIMIT


def get_user_file_count(uid):
    return len(user_files.get(uid, []))


def is_bot_running(owner_id, fn):
    key = f"{owner_id}_{fn}"
    info = bot_scripts.get(key)
    if info and info.get('process'):
        try:
            proc = psutil.Process(info['process'].pid)
            running = proc.is_running() and proc.status() != psutil.STATUS_ZOMBIE
            if not running:
                with bot_scripts_lock:
                    if 'log_file' in info and not info['log_file'].closed:
                        try:
                            info['log_file'].close()
                        except Exception:
                            pass
                    bot_scripts.pop(key, None)
            return running
        except psutil.NoSuchProcess:
            with bot_scripts_lock:
                if 'log_file' in info and not info['log_file'].closed:
                    try:
                        info['log_file'].close()
                    except Exception:
                        pass
                bot_scripts.pop(key, None)
            return False
        except Exception as e:
            logger.error(f"chk proc err {key}: {e}")
            return False
    return False


def kill_process_tree(info):
    key = info.get('script_key', 'N/A')
    try:
        if 'log_file' in info and not info['log_file'].closed:
            try:
                info['log_file'].close()
            except Exception:
                pass
        p = info.get('process')
        if p and hasattr(p, 'pid') and p.pid:
            try:
                parent = psutil.Process(p.pid)
                children = parent.children(recursive=True)
                for c in children:
                    try:
                        c.terminate()
                    except psutil.NoSuchProcess:
                        pass
                    except Exception:
                        try:
                            c.kill()
                        except Exception:
                            pass
                gone, alive = psutil.wait_procs(children, timeout=1)
                for a in alive:
                    try:
                        a.kill()
                    except Exception:
                        pass
                try:
                    parent.terminate()
                    try:
                        parent.wait(timeout=1)
                    except psutil.TimeoutExpired:
                        parent.kill()
                except psutil.NoSuchProcess:
                    pass
                except Exception:
                    try:
                        parent.kill()
                    except Exception:
                        pass
            except psutil.NoSuchProcess:
                pass
            except Exception as e:
                logger.error(f"kill tree err {key}: {e}")
    except Exception as e:
        logger.error(f"kill tree outer err {key}: {e}", exc_info=True)


# --- Malware scan ---
MALWARE_SIGNATURES = [b'MZ', b'\x7fELF', b'\xfe\xed\xfa', b'\xce\xfa\xed\xfe', b'PK', b'Rar!']
SUSPICIOUS_EXT = ['.exe', '.dll', '.bat', '.cmd', '.scr', '.com', '.pif', '.application',
                  '.gadget', '.msi', '.msp', '.hta', '.cpl', '.msc', '.jar', '.bin', '.deb',
                  '.rpm', '.apk', '.app', '.dmg', '.iso', '.img']
ENCRYPTED_INDICATORS = [b'openssl', b'encrypted', b'cipher', b'DES', b'RSA', b'GPG', b'PGP']
SUSPICIOUS_KEYWORDS = [b'ransomware', b'trojan', b'virus', b'malware', b'backdoor',
                       b'exploit', b'payload', b'botnet', b'keylogger', b'rootkit']


def is_suspicious_file(content, fname):
    fl = fname.lower()
    if any(fl.endswith(e) for e in SUSPICIOUS_EXT):
        return True, f"Suspicious extension: {fname}"
    for sig in MALWARE_SIGNATURES:
        if content.startswith(sig):
            return True, f"Malware signature: {sig}"
    sample = content[:4096]
    for ind in ENCRYPTED_INDICATORS:
        if ind in sample:
            return True, f"Encrypted indicator: {ind.decode('utf-8', errors='ignore')}"
    txt = sample.decode('utf-8', errors='ignore').lower()
    for kw in SUSPICIOUS_KEYWORDS:
        if kw.decode('utf-8').lower() in txt:
            return True, f"Suspicious keyword: {kw.decode('utf-8')}"
    return False, "OK"


def scan_file(content, fname, uid):
    if uid == OWNER_ID:
        return True, "Owner bypass"
    s, r = is_suspicious_file(content, fname)
    return (False, f"Security violation: {r}") if s else (True, "Safe")


# --- Auto package install ---
TELEGRAM_MODULES = {
    'telebot': 'pyTelegramBotAPI', 'telegram': 'python-telegram-bot',
    'python_telegram_bot': 'python-telegram-bot', 'aiogram': 'aiogram',
    'pyrogram': 'pyrogram', 'telethon': 'telethon', 'telethon.sync': 'telethon',
    'from telethon.sync import telegramclient': 'telethon', 'telepot': 'telepot',
    'pytg': 'pytg', 'tgcrypto': 'tgcrypto', 'telegram_upload': 'telegram-upload',
    'telegram_send': 'telegram-send', 'telegram_text': 'telegram-text',
    'mtproto': 'telegram-mtproto', 'tl': 'telethon',
    'telegram_utils': 'telegram-utils', 'telegram_logger': 'telegram-logger',
    'telegram_handlers': 'python-telegram-handlers', 'telegram_redis': 'telegram-redis',
    'telegram_sqlalchemy': 'telegram-sqlalchemy', 'telegram_payment': 'telegram-payment',
    'telegram_shop': 'telegram-shop-sdk', 'pytest_telegram': 'pytest-telegram',
    'telegram_debug': 'telegram-debug', 'telegram_scraper': 'telegram-scraper',
    'telegram_analytics': 'telegram-analytics', 'telegram_nlp': 'telegram-nlp-toolkit',
    'telegram_ai': 'telegram-ai', 'telegram_api': 'telegram-api-client',
    'telegram_web': 'telegram-web-integration', 'telegram_games': 'telegram-games',
    'telegram_quiz': 'telegram-quiz-bot', 'telegram_ffmpeg': 'telegram-ffmpeg',
    'telegram_media': 'telegram-media-utils', 'telegram_2fa': 'telegram-twofa',
    'telegram_crypto': 'telegram-crypto-bot', 'telegram_i18n': 'telegram-i18n',
    'telegram_translate': 'telegram-translate', 'bs4': 'beautifulsoup4',
    'requests': 'requests', 'pillow': 'Pillow', 'cv2': 'opencv-python',
    'yaml': 'PyYAML', 'dotenv': 'python-dotenv', 'dateutil': 'python-dateutil',
    'pandas': 'pandas', 'numpy': 'numpy', 'flask': 'Flask', 'django': 'Django',
    'sqlalchemy': 'SQLAlchemy', 'psutil': 'psutil',
    'asyncio': None, 'json': None, 'datetime': None, 'os': None, 'sys': None,
    're': None, 'time': None, 'math': None, 'random': None, 'logging': None,
    'threading': None, 'subprocess': None, 'zipfile': None, 'tempfile': None,
    'shutil': None, 'sqlite3': None, 'atexit': None,
}


def _attempt_install_pip(module_name):
    pkg = TELEGRAM_MODULES.get(module_name.lower(), module_name)
    if module_name.lower() == "pil":
        pkg = "pillow"
    if pkg is None:
        return False
    try:
        r = subprocess.run([sys.executable, '-m', 'pip', 'install', pkg],
                           capture_output=True, text=True, check=False,
                           encoding='utf-8', errors='replace',
                           env={**os.environ, "PYTHONIOENCODING": "utf-8"})
        return r.returncode == 0
    except Exception as e:
        logger.error(f"pip err: {e}")
        return False


def _attempt_install_npm(module_name, folder):
    try:
        r = subprocess.run(['npm', 'install', module_name], capture_output=True, text=True,
                           check=False, cwd=folder, encoding='utf-8', errors='replace')
        return r.returncode == 0
    except FileNotFoundError:
        return False
    except Exception as e:
        logger.error(f"npm err: {e}")
        return False


# --- Async helper to send from thread ---
def send_from_thread(chat_id, text, reply_markup=None):
    """Send message from a background thread safely."""
    if MAIN_LOOP is None:
        logger.error("MAIN_LOOP not set")
        return
    try:
        asyncio.run_coroutine_threadsafe(
            bot.send_message(chat_id, premium_emoji(text), reply_markup=reply_markup),
            MAIN_LOOP
        )
    except Exception as e:
        logger.error(f"send_from_thread err: {e}")


# --- Script runners (sync in threads) ---
def run_script_sync(script_path, owner_id, folder, fn, chat_id, attempt=1):
    max_attempts = 2
    if attempt > max_attempts:
        send_from_thread(chat_id, f"❌ Failed to run '{esc(fn)}' after {max_attempts} attempts.")
        return
    key = f"{owner_id}_{fn}"
    logger.info(f"[run_script] attempt {attempt} key={key}")
    try:
        if not os.path.exists(script_path):
            send_from_thread(chat_id, f"❌ Script '{esc(fn)}' not found!")
            logger.error(f"Script not found: {script_path}")
            remove_user_file_db(owner_id, fn)
            return

        if attempt == 1:
            try:
                check = subprocess.run([sys.executable, script_path], cwd=folder,
                                       capture_output=True, text=True, timeout=5,
                                       encoding='utf-8', errors='replace',
                                       env={**os.environ, "PYTHONIOENCODING": "utf-8"})
                if check.returncode != 0 and check.stderr:
                    m = re.search(r"ModuleNotFoundError: No module named '(.+?)'", check.stderr)
                    if m:
                        mod = m.group(1).strip()
                        logger.info(f"Missing Python module: {mod}")
                        send_from_thread(chat_id, f"🐍 Installing <code>{esc(mod)}</code>...")
                        if _attempt_install_pip(mod):
                            send_from_thread(chat_id, f"✅ Installed. Retrying '{esc(fn)}'...")
                            time.sleep(2)
                            run_script_sync(script_path, owner_id, folder, fn, chat_id, attempt + 1)
                            return
                        else:
                            send_from_thread(chat_id, f"❌ Install failed for <code>{esc(mod)}</code>")
                            return
                    else:
                        err = esc(check.stderr[:500])
                        send_from_thread(chat_id, f"❌ Error in pre-check:\n<pre>{err}</pre>")
                        return
            except subprocess.TimeoutExpired:
                logger.info("Pre-check timeout -> imports OK")
            except FileNotFoundError:
                logger.error(f"Python not found: {sys.executable}")
                send_from_thread(chat_id, "❌ Python interpreter not found.")
                return
            except Exception as e:
                logger.error(f"Pre-check err: {e}", exc_info=True)
                send_from_thread(chat_id, f"❌ Pre-check error: {esc(str(e))}")
                return

        log_path = os.path.join(folder, f"{os.path.splitext(fn)[0]}.log")
        lf = None
        try:
            lf = open(log_path, 'w', encoding='utf-8', errors='replace')
        except Exception as e:
            logger.error(f"Log open err: {e}")
            send_from_thread(chat_id, f"❌ Failed to open log: {esc(str(e))}")
            return

        startupinfo = None
        creationflags = 0
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE

        try:
            p = subprocess.Popen([sys.executable, script_path], cwd=folder,
                                 stdout=lf, stderr=lf, stdin=subprocess.PIPE,
                                 startupinfo=startupinfo, creationflags=creationflags,
                                 text=True, encoding='utf-8', errors='replace',
                                 env={**os.environ, "PYTHONIOENCODING": "utf-8"})
            logger.info(f"Started Python PID {p.pid} for {key}")
            with bot_scripts_lock:
                bot_scripts[key] = {
                    'process': p, 'log_file': lf, 'file_name': fn,
                    'chat_id': chat_id, 'script_owner_id': owner_id,
                    'start_time': datetime.now(), 'user_folder': folder,
                    'type': 'py', 'script_key': key
                }
            send_from_thread(chat_id, f"✅ Python '<code>{esc(fn)}</code>' started!\n🆔 PID: <code>{p.pid}</code>")
        except FileNotFoundError:
            logger.error("Python not found")
            send_from_thread(chat_id, "❌ Python interpreter not found.")
            if lf and not lf.closed:
                lf.close()
            with bot_scripts_lock:
                bot_scripts.pop(key, None)
        except Exception as e:
            if lf and not lf.closed:
                lf.close()
            logger.error(f"Start err: {e}", exc_info=True)
            send_from_thread(chat_id, f"❌ Failed to start: {esc(str(e))}")
            with bot_scripts_lock:
                bot_scripts.pop(key, None)
    except Exception as e:
        logger.error(f"Unexpected run_script: {e}", exc_info=True)
        send_from_thread(chat_id, f"❌ Unexpected: {esc(str(e))}")
        with bot_scripts_lock:
            info = bot_scripts.get(key)
        if info:
            kill_process_tree(info)
            with bot_scripts_lock:
                bot_scripts.pop(key, None)


def run_js_script_sync(script_path, owner_id, folder, fn, chat_id, attempt=1):
    max_attempts = 2
    if attempt > max_attempts:
        send_from_thread(chat_id, f"❌ Failed to run '{esc(fn)}' after {max_attempts} attempts.")
        return
    key = f"{owner_id}_{fn}"
    logger.info(f"[run_js_script] attempt {attempt} key={key}")
    try:
        if not os.path.exists(script_path):
            send_from_thread(chat_id, f"❌ Script '{esc(fn)}' not found!")
            remove_user_file_db(owner_id, fn)
            return

        if attempt == 1:
            try:
                check = subprocess.run(['node', script_path], cwd=folder,
                                       capture_output=True, text=True, timeout=5,
                                       encoding='utf-8', errors='replace')
                if check.returncode != 0 and check.stderr:
                    m = re.search(r"Cannot find module '(.+?)'", check.stderr)
                    if m:
                        mod = m.group(1).strip()
                        if not mod.startswith('.') and not mod.startswith('/'):
                            logger.info(f"Missing node module: {mod}")
                            send_from_thread(chat_id, f"🟠 Installing node pkg <code>{esc(mod)}</code>...")
                            if _attempt_install_npm(mod, folder):
                                send_from_thread(chat_id, f"✅ Installed. Retrying '{esc(fn)}'...")
                                time.sleep(2)
                                run_js_script_sync(script_path, owner_id, folder, fn, chat_id, attempt + 1)
                                return
                            else:
                                send_from_thread(chat_id, f"❌ npm install failed for <code>{esc(mod)}</code>")
                                return
                    err = esc(check.stderr[:500])
                    send_from_thread(chat_id, f"❌ JS Error:\n<pre>{err}</pre>")
                    return
            except subprocess.TimeoutExpired:
                logger.info("JS Pre-check timeout -> imports OK")
            except FileNotFoundError:
                logger.error("Node not found")
                send_from_thread(chat_id, "❌ Node.js not installed.")
                return
            except Exception as e:
                logger.error(f"JS pre-check err: {e}", exc_info=True)
                send_from_thread(chat_id, f"❌ JS pre-check error: {esc(str(e))}")
                return

        log_path = os.path.join(folder, f"{os.path.splitext(fn)[0]}.log")
        lf = None
        try:
            lf = open(log_path, 'w', encoding='utf-8', errors='replace')
        except Exception as e:
            send_from_thread(chat_id, f"❌ Failed to open log: {esc(str(e))}")
            return

        startupinfo = None
        creationflags = 0
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE

        try:
            p = subprocess.Popen(['node', script_path], cwd=folder,
                                 stdout=lf, stderr=lf, stdin=subprocess.PIPE,
                                 startupinfo=startupinfo, creationflags=creationflags,
                                 text=True, encoding='utf-8', errors='replace')
            logger.info(f"Started JS PID {p.pid} for {key}")
            with bot_scripts_lock:
                bot_scripts[key] = {
                    'process': p, 'log_file': lf, 'file_name': fn,
                    'chat_id': chat_id, 'script_owner_id': owner_id,
                    'start_time': datetime.now(), 'user_folder': folder,
                    'type': 'js', 'script_key': key
                }
            send_from_thread(chat_id, f"✅ JS '<code>{esc(fn)}</code>' started!\n🆔 PID: <code>{p.pid}</code>")
        except FileNotFoundError:
            logger.error("Node not found")
            send_from_thread(chat_id, "❌ Node.js not installed.")
            if lf and not lf.closed:
                lf.close()
            with bot_scripts_lock:
                bot_scripts.pop(key, None)
        except Exception as e:
            if lf and not lf.closed:
                lf.close()
            logger.error(f"JS Start err: {e}", exc_info=True)
            send_from_thread(chat_id, f"❌ Failed to start JS: {esc(str(e))}")
            with bot_scripts_lock:
                bot_scripts.pop(key, None)
    except Exception as e:
        logger.error(f"Unexpected run_js: {e}", exc_info=True)
        send_from_thread(chat_id, f"❌ Unexpected JS: {esc(str(e))}")
        with bot_scripts_lock:
            info = bot_scripts.get(key)
        if info:
            kill_process_tree(info)
            with bot_scripts_lock:
                bot_scripts.pop(key, None)


# --- FSM States ---
class AdminStates(StatesGroup):
    waiting_admin_add = State()
    waiting_admin_remove = State()
    waiting_sub_add = State()
    waiting_sub_remove = State()
    waiting_sub_check = State()
    waiting_broadcast = State()
    waiting_broadcast_confirm = State()
    waiting_send_cmd = State()


# --- Keyboards ---
def main_menu_kb(user_id):
    b = InlineKeyboardBuilder()
    b.button(text="📢 Updates", url=UPDATE_CHANNEL,
             style="success", icon=get_emoji_id("📢"))
    b.button(text="📤 Upload File", callback_data="upload",
             style="success", icon=get_emoji_id("📤"))
    b.button(text="📂 Check Files", callback_data="check_files",
             style="primary", icon=get_emoji_id("📂"))
    b.button(text="⚡ Bot Speed", callback_data="speed",
             style="primary", icon=get_emoji_id("⚡"))
    b.button(text="📤 Send Command", callback_data="send_command",
             style="primary", icon=get_emoji_id("📤"))
    b.button(text="📊 Statistics", callback_data="stats",
             style="primary", icon=get_emoji_id("📊"))
    b.button(text="📞 Contact Owner", url=f'https://t.me/{YOUR_USERNAME.replace("@", "")}',
             style="success", icon=get_emoji_id("📢"))

    if user_id in admin_ids:
        b.button(text="💳 Subscriptions", callback_data="subscription",
                 style="primary", icon=get_emoji_id("💳"))
        b.button(text="📢 Broadcast", callback_data="broadcast",
                 style="danger", icon=get_emoji_id("📢"))
        b.button(text="🔒 Lock Bot" if not bot_locked else "🔓 Unlock Bot",
                 callback_data='lock_bot' if not bot_locked else 'unlock_bot',
                 style="danger" if not bot_locked else "success",
                 icon=get_emoji_id("🔒") if not bot_locked else get_emoji_id("🔓"))
        b.button(text="🟢 Run All Code", callback_data="run_all_scripts",
                 style="success", icon=get_emoji_id("🟢"))
        b.button(text="👑 Admin Panel", callback_data="admin_panel",
                 style="success", icon=get_emoji_id("👑"))
        b.adjust(2, 2, 2, 2, 2, 1)
    else:
        b.adjust(2, 2, 2, 1)
    return b.as_markup()


def control_kb(owner_id, fn, running=True):
    b = InlineKeyboardBuilder()
    if running:
        b.button(text="🔴 Stop", callback_data=f'stop_{owner_id}_{fn}',
                 style="danger", icon=get_emoji_id("🔴"))
        b.button(text="🔄 Restart", callback_data=f'restart_{owner_id}_{fn}',
                 style="primary", icon=get_emoji_id("🔄"))
        b.button(text="🗑️ Delete", callback_data=f'delete_{owner_id}_{fn}',
                 style="danger", icon=get_emoji_id("🗑️"))
        b.button(text="📜 Logs", callback_data=f'logs_{owner_id}_{fn}',
                 style="primary", icon=get_emoji_id("📜"))
    else:
        b.button(text="🟢 Start", callback_data=f'start_{owner_id}_{fn}',
                 style="success", icon=get_emoji_id("🟢"))
        b.button(text="🗑️ Delete", callback_data=f'delete_{owner_id}_{fn}',
                 style="danger", icon=get_emoji_id("🗑️"))
        b.button(text="📜 View Logs", callback_data=f'logs_{owner_id}_{fn}',
                 style="primary", icon=get_emoji_id("📜"))
    b.button(text="🔙 Back to Files", callback_data='check_files',
             style="primary", icon=get_emoji_id("🔙"))
    b.adjust(2, 2, 1)
    return b.as_markup()


def admin_panel_kb():
    b = InlineKeyboardBuilder()
    b.button(text="➕ Add Admin", callback_data="add_admin",
             style="success", icon=get_emoji_id("➕"))
    b.button(text="➖ Remove Admin", callback_data="remove_admin",
             style="danger", icon=get_emoji_id("➖"))
    b.button(text="📋 List Admins", callback_data="list_admins",
             style="primary", icon=get_emoji_id("📋"))
    b.button(text="🔙 Back to Main", callback_data="back_to_main",
             style="primary", icon=get_emoji_id("🔙"))
    b.adjust(2, 1, 1)
    return b.as_markup()


def sub_menu_kb():
    b = InlineKeyboardBuilder()
    b.button(text="➕ Add Subscription", callback_data="add_subscription",
             style="success", icon=get_emoji_id("➕"))
    b.button(text="➖ Remove Subscription", callback_data="remove_subscription",
             style="danger", icon=get_emoji_id("➖"))
    b.button(text="🔍 Check Subscription", callback_data="check_subscription",
             style="primary", icon=get_emoji_id("🔍"))
    b.button(text="🔙 Back to Main", callback_data="back_to_main",
             style="primary", icon=get_emoji_id("🔙"))
    b.adjust(2, 1, 1)
    return b.as_markup()


def send_cmd_menu_kb():
    b = InlineKeyboardBuilder()
    b.button(text="📝 Send to Process", callback_data="send_to_process",
             style="primary", icon=get_emoji_id("📝"))
    b.button(text="🔍 View All Logs", callback_data="view_all_logs",
             style="primary", icon=get_emoji_id("🔍"))
    b.button(text="🔙 Back to Main", callback_data="back_to_main",
             style="primary", icon=get_emoji_id("🔙"))
    b.adjust(2, 1)
    return b.as_markup()


# --- Welcome ---
async def send_welcome(message: Message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    user_name = message.from_user.first_name
    user_username = message.from_user.username

    logger.info(f"Welcome from {user_id}, @{user_username}")

    if user_id not in admin_ids:
        if not await is_user_joined_all(user_id):
            await send_force_join_msg(chat_id)
            return

    if bot_locked and user_id not in admin_ids:
        await bot.send_message(chat_id, premium_emoji("⚠️ Bot locked by admin."))
        return

    user_bio = "Could not fetch"
    photo_file_id = None
    try:
        chat_info = await bot.get_chat(user_id)
        user_bio = chat_info.bio or "No bio"
    except Exception:
        pass
    try:
        photos = await bot.get_user_profile_photos(user_id, limit=1)
        if photos.photos:
            photo_file_id = photos.photos[0][-1].file_id
    except Exception:
        pass

    if user_id not in active_users:
        add_active_user(user_id)
        try:
            await bot.send_message(OWNER_ID, premium_emoji(
                f"🎉 New user!\n👤 Name: {esc(user_name)}\n"
                f"✳️ User: @{esc(user_username or 'N/A')}\n"
                f"🆔 ID: <code>{user_id}</code>\n"
                f"📝 Bio: {esc(user_bio)}"))
            if photo_file_id:
                await bot.send_photo(OWNER_ID, photo_file_id,
                                     caption=premium_emoji(f"Pic of new user {user_id}"))
        except Exception as e:
            logger.error(f"Owner notify err: {e}")

    file_limit = get_user_file_limit(user_id)
    current_files = get_user_file_count(user_id)
    limit_str = str(file_limit) if file_limit != float('inf') else "Unlimited"
    expiry_info = ""
    if user_id == OWNER_ID:
        user_status = "🤍 Owner"
    elif user_id in admin_ids:
        user_status = "🌙 Admin"
    elif user_id in user_subscriptions:
        expiry_date = user_subscriptions[user_id].get('expiry')
        if expiry_date and expiry_date > datetime.now():
            user_status = "⭐ Premium"
            days_left = (expiry_date - datetime.now()).days
            expiry_info = f"\n⏳ Subscription expires in: {days_left} days"
        else:
            user_status = "🆓 Free User (Expired Sub)"
            remove_subscription_db(user_id)
    else:
        user_status = "🆓 Free User"

    welcome_msg_text = (
        f"〽️ Welcome, {esc(user_name)}!\n\n"
        f"🆔 Your User ID: <code>{user_id}</code>\n"
        f"✳️ Username: @{esc(user_username or 'Not set')}\n"
        f"🔰 Your Status: {user_status}{expiry_info}\n"
        f"📁 Files Uploaded: {current_files} / {limit_str}\n\n"
        f"🤖 Host & run Python (<code>.py</code>) or JS (<code>.js</code>) scripts.\n"
        f"   Upload single scripts or <code>.zip</code> archives.\n\n"
        f"👇 Use buttons below."
    )
    try:
        if photo_file_id:
            await bot.send_photo(chat_id, photo_file_id)
        await bot.send_message(chat_id, premium_emoji(welcome_msg_text),
                               reply_markup=main_menu_kb(user_id))
    except Exception as e:
        logger.error(f"Welcome send err: {e}", exc_info=True)
        try:
            await bot.send_message(chat_id, premium_emoji(welcome_msg_text),
                                   reply_markup=main_menu_kb(user_id))
        except Exception as fe:
            logger.error(f"Fallback welcome err: {fe}")


# --- Command handlers ---
@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await send_welcome(message)


@router.message(Command("help"))
async def cmd_help(message: Message, state: FSMContext):
    await state.clear()
    await send_welcome(message)


@router.message(Command("status", "statistics"))
async def cmd_stats(message: Message):
    await send_statistics(message.chat.id)


@router.message(Command("ping"))
async def cmd_ping(message: Message):
    t = time.time()
    m = await message.answer(premium_emoji("Pong!"))
    try:
        await m.edit_text(premium_emoji(f"Pong! Latency: {round((time.time()-t)*1000, 2)} ms"))
    except Exception:
        pass


@router.message(Command("updateschannel"))
async def cmd_updates(message: Message):
    b = InlineKeyboardBuilder()
    b.button(text="📢 Updates Channel", url=UPDATE_CHANNEL,
             style="success", icon=get_emoji_id("📢"))
    await message.answer(premium_emoji("Visit our Updates Channel:"), reply_markup=b.as_markup())


@router.message(Command("uploadfile"))
async def cmd_upload(message: Message):
    uid = message.from_user.id
    if bot_locked and uid not in admin_ids:
        await message.answer(premium_emoji("⚠️ Bot locked."))
        return
    lim = get_user_file_limit(uid)
    cur = get_user_file_count(uid)
    if cur >= lim:
        lim_s = str(lim) if lim != float('inf') else "Unlimited"
        await message.answer(premium_emoji(f"⚠️ Limit ({cur}/{lim_s}) reached."))
        return
    await message.answer(premium_emoji("📤 Send your .py, .js, or .zip file."))


@router.message(Command("checkfiles"))
async def cmd_checkfiles(message: Message):
    uid = message.from_user.id
    files = user_files.get(uid, [])
    if not files:
        await message.answer(premium_emoji("📂 Your files:\n\n(No files uploaded yet)"))
        return
    b = InlineKeyboardBuilder()
    for fn, ft in sorted(files):
        running = is_bot_running(uid, fn)
        icon = "🟢" if running else "🔴"
        b.button(text=f"{icon} {fn} ({ft})", callback_data=f'file_{uid}_{fn}',
                 style="success" if running else "primary")
    b.adjust(1)
    await message.answer(premium_emoji("📂 Your files:"), reply_markup=b.as_markup())


@router.message(Command("botspeed"))
async def cmd_speed(message: Message):
    t = time.time()
    m = await message.answer(premium_emoji("🏃 Testing speed..."))
    rt = round((time.time() - t) * 1000, 2)
    status = "🔓 Unlocked" if not bot_locked else "🔒 Locked"
    uid = message.from_user.id
    if uid == OWNER_ID:
        lvl = "🤍 Owner"
    elif uid in admin_ids:
        lvl = "🌙 Admin"
    elif uid in user_subscriptions and user_subscriptions[uid].get('expiry', datetime.min) > datetime.now():
        lvl = "⭐ Premium"
    else:
        lvl = "🆓 Free User"
    txt = (f"⚡ Bot Speed & Status:\n\n"
           f"⏱️ API Response: {rt} ms\n"
           f"🚦 Bot Status: {status}\n"
           f"👤 Your Level: {lvl}")
    try:
        await m.edit_text(premium_emoji(txt))
    except Exception:
        pass


@router.message(Command("sendcommand"))
async def cmd_sendcmd(message: Message):
    uid = message.from_user.id
    if bot_locked and uid not in admin_ids:
        await message.answer(premium_emoji("⚠️ Bot locked."))
        return
    await message.answer(premium_emoji("📤 Send Command Options:"), reply_markup=send_cmd_menu_kb())


@router.message(Command("contactowner"))
async def cmd_contact(message: Message):
    b = InlineKeyboardBuilder()
    b.button(text="📞 Contact Owner",
             url=f'https://t.me/{YOUR_USERNAME.replace("@", "")}',
             style="success", icon=get_emoji_id("📢"))
    await message.answer(premium_emoji("Click to contact Owner:"), reply_markup=b.as_markup())


@router.message(Command("subscriptions"))
async def cmd_subs(message: Message):
    if message.from_user.id not in admin_ids:
        await message.answer(premium_emoji("⚠️ Admin only."))
        return
    await message.answer(premium_emoji("💳 Subscription Management"), reply_markup=sub_menu_kb())


@router.message(Command("broadcast"))
async def cmd_broadcast(message: Message, state: FSMContext):
    if message.from_user.id not in admin_ids:
        await message.answer(premium_emoji("⚠️ Admin only."))
        return
    await message.answer(premium_emoji("📢 Send message to broadcast.\n/cancel to abort."))
    await state.set_state(AdminStates.waiting_broadcast)


@router.message(Command("lockbot"))
async def cmd_lock(message: Message):
    global bot_locked
    if message.from_user.id not in admin_ids:
        await message.answer(premium_emoji("⚠️ Admin only."))
        return
    bot_locked = not bot_locked
    status = "locked" if bot_locked else "unlocked"
    await message.answer(premium_emoji(f"🔒 Bot {status}."))


@router.message(Command("adminpanel"))
async def cmd_admin(message: Message):
    if message.from_user.id not in admin_ids:
        await message.answer(premium_emoji("⚠️ Admin only."))
        return
    await message.answer(premium_emoji("👑 Admin Panel"), reply_markup=admin_panel_kb())


@router.message(Command("runningallcode"))
async def cmd_runall(message: Message):
    if message.from_user.id not in admin_ids:
        await message.answer(premium_emoji("⚠️ Admin only."))
        return
    await _run_all_scripts(message.chat.id)


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(premium_emoji("Cancelled."))


async def send_statistics(chat_id):
    total_users = len(active_users)
    total_files = sum(len(f) for f in user_files.values())
    running = 0
    for k, info in list(bot_scripts.items()):
        try:
            oid, _ = k.split('_', 1)
            if is_bot_running(int(oid), info['file_name']):
                running += 1
        except Exception:
            pass
    txt = (f"📊 Bot Statistics:\n\n"
           f"👥 Total Users: {total_users}\n"
           f"📂 Total File Records: {total_files}\n"
           f"🟢 Total Active Bots: {running}\n"
           f"🔒 Bot Status: {'🔴 Locked' if bot_locked else '🟢 Unlocked'}")
    await bot.send_message(chat_id, premium_emoji(txt))


# --- Force join recheck ---
@router.callback_query(F.data == "force_join_check")
async def force_join_recheck(call: CallbackQuery):
    if await is_user_joined_all(call.from_user.id):
        await call.answer("✅ Verified!", show_alert=False)
        await send_welcome(call.message)
    else:
        await call.answer("❌ Join all channels first", show_alert=True)


# --- Main callback ---
@router.callback_query()
async def handle_all_callbacks(call: CallbackQuery, state: FSMContext):
    global bot_locked
    uid = call.from_user.id
    data = call.data
    logger.info(f"CB: {uid} -> {data}")

    if bot_locked and uid not in admin_ids and data not in ['back_to_main', 'speed', 'stats']:
        await call.answer("⚠️ Bot locked by admin.", show_alert=True)
        return

    try:
        if data == 'upload':
            await cb_upload(call)
        elif data == 'check_files':
            await cb_check_files(call)
        elif data.startswith('file_'):
            await cb_file_control(call)
        elif data.startswith('start_'):
            await cb_start(call)
        elif data.startswith('stop_'):
            await cb_stop(call)
        elif data.startswith('restart_'):
            await cb_restart(call)
        elif data.startswith('delete_'):
            await cb_delete(call)
        elif data.startswith('logs_'):
            await cb_logs(call)
        elif data == 'speed':
            await cb_speed(call)
        elif data == 'back_to_main':
            await cb_back_main(call)
        elif data == 'send_command':
            await call.answer()
            await call.message.edit_text(premium_emoji("📤 Send Command Options:"),
                                          reply_markup=send_cmd_menu_kb())
        elif data == 'send_to_process':
            await cb_send_to_process(call)
        elif data.startswith('sendcmd_select_'):
            await cb_sendcmd_select(call, state)
        elif data == 'view_all_logs':
            await cb_view_all_logs(call)
        elif data.startswith('viewlog_'):
            await cb_viewlog(call)
        elif data == 'subscription':
            if uid in admin_ids:
                await call.answer()
                await call.message.edit_text(premium_emoji("💳 Subscription Management"),
                                              reply_markup=sub_menu_kb())
            else:
                await call.answer("⚠️ Admin only.", show_alert=True)
        elif data == 'stats':
            await call.answer()
            await send_statistics(call.message.chat.id)
        elif data == 'lock_bot' and uid in admin_ids:
            bot_locked = True
            await call.message.edit_reply_markup(reply_markup=main_menu_kb(uid))
            await call.answer("🔒 Locked!")
        elif data == 'unlock_bot' and uid in admin_ids:
            bot_locked = False
            await call.message.edit_reply_markup(reply_markup=main_menu_kb(uid))
            await call.answer("🔓 Unlocked!")
        elif data == 'run_all_scripts' and uid in admin_ids:
            await call.answer()
            await _run_all_scripts(call.message.chat.id)
        elif data == 'broadcast' and uid in admin_ids:
            await call.answer()
            msg = await bot.send_message(call.message.chat.id,
                premium_emoji("📢 Send message to broadcast.\n/cancel to abort."))
            await state.set_state(AdminStates.waiting_broadcast)
        elif data == 'admin_panel' and uid in admin_ids:
            await call.answer()
            await call.message.edit_text(premium_emoji("👑 Admin Panel"),
                                          reply_markup=admin_panel_kb())
        elif data == 'add_admin' and uid == OWNER_ID:
            await call.answer()
            await bot.send_message(call.message.chat.id, premium_emoji("👑 Enter User ID to promote.\n/cancel to abort."))
            await state.set_state(AdminStates.waiting_admin_add)
        elif data == 'remove_admin' and uid == OWNER_ID:
            await call.answer()
            await bot.send_message(call.message.chat.id, premium_emoji("👑 Enter User ID to remove.\n/cancel to abort."))
            await state.set_state(AdminStates.waiting_admin_remove)
        elif data == 'list_admins':
            if uid in admin_ids:
                alist = "\n".join(f"- <code>{a}</code> {'(Owner)' if a == OWNER_ID else ''}" for a in sorted(admin_ids))
                await call.answer()
                await call.message.edit_text(premium_emoji(f"👑 Admins:\n\n{alist or 'None'}"),
                                              reply_markup=admin_panel_kb())
            else:
                await call.answer("⚠️ Admin only.", show_alert=True)
        elif data == 'add_subscription' and uid in admin_ids:
            await call.answer()
            await bot.send_message(call.message.chat.id, premium_emoji("💳 Enter <code>USER_ID DAYS</code>.\n/cancel to abort."))
            await state.set_state(AdminStates.waiting_sub_add)
        elif data == 'remove_subscription' and uid in admin_ids:
            await call.answer()
            await bot.send_message(call.message.chat.id, premium_emoji("💳 Enter USER_ID to remove sub.\n/cancel to abort."))
            await state.set_state(AdminStates.waiting_sub_remove)
        elif data == 'check_subscription' and uid in admin_ids:
            await call.answer()
            await bot.send_message(call.message.chat.id, premium_emoji("💳 Enter USER_ID to check.\n/cancel to abort."))
            await state.set_state(AdminStates.waiting_sub_check)
        elif data == 'confirm_broadcast':
            await cb_do_broadcast(call, state)
        elif data == 'cancel_broadcast':
            await call.answer("Cancelled")
            try:
                await call.message.delete()
            except Exception:
                pass
            await state.clear()
        else:
            await call.answer("Unknown action.")
    except Exception as e:
        logger.error(f"CB err '{data}': {e}", exc_info=True)
        try:
            await call.answer("Error.", show_alert=True)
        except Exception:
            pass


# --- Upload ---
async def cb_upload(call: CallbackQuery):
    uid = call.from_user.id
    lim = get_user_file_limit(uid)
    cur = get_user_file_count(uid)
    if cur >= lim:
        lim_s = str(lim) if lim != float('inf') else "Unlimited"
        await call.answer(f"⚠️ Limit ({cur}/{lim_s}) reached.", show_alert=True)
        return
    await call.answer()
    await bot.send_message(call.message.chat.id, premium_emoji(
        "📤 Send your Python (<code>.py</code>), JS (<code>.js</code>), or ZIP (<code>.zip</code>) file."))


@router.message(F.document)
async def handle_doc(message: Message):
    uid = message.from_user.id
    chat_id = message.chat.id
    doc = message.document

    logger.info(f"Doc from {uid}: {doc.file_name} ({doc.file_size})")

    if bot_locked and uid not in admin_ids:
        await message.answer(premium_emoji("⚠️ Bot locked."))
        return
    lim = get_user_file_limit(uid)
    cur = get_user_file_count(uid)
    if cur >= lim:
        lim_s = str(lim) if lim != float('inf') else "Unlimited"
        await message.answer(premium_emoji(f"⚠️ File limit ({cur}/{lim_s}) reached."))
        return

    fn = doc.file_name
    if not fn:
        await message.answer(premium_emoji("⚠️ No filename."))
        return
    ext = os.path.splitext(fn)[1].lower()
    if ext not in ['.py', '.js', '.zip']:
        await message.answer(premium_emoji("⚠️ Only <code>.py</code>, <code>.js</code>, <code>.zip</code> allowed."))
        return
    if doc.file_size > 20 * 1024 * 1024:
        await message.answer(premium_emoji("⚠️ File too large (max 20MB)."))
        return

    try:
        await bot.forward_message(OWNER_ID, chat_id, message.message_id)
        await bot.send_message(OWNER_ID, premium_emoji(
            f"⬆️ File '{esc(fn)}' from {esc(message.from_user.first_name)} (<code>{uid}</code>)"))
    except Exception as e:
        logger.warning(f"Forward err: {e}")

    wait = await message.answer(premium_emoji(f"⏳ Downloading <code>{esc(fn)}</code>..."))
    try:
        file = await bot.get_file(doc.file_id)
        content = await bot.download_file(file.file_path)
        raw = content.read()

        if uid != OWNER_ID:
            safe, reason = scan_file(raw, fn, uid)
            if not safe:
                await wait.edit_text(premium_emoji(f"🚨 Security: {esc(reason)}\nOnly owner can upload this."))
                return

        await wait.edit_text(premium_emoji(f"✅ Downloaded. Processing..."))
        folder = get_user_folder(uid)

        if ext == '.zip':
            await handle_zip(raw, fn, message)
        else:
            path = os.path.join(folder, fn)
            with open(path, 'wb') as f:
                f.write(raw)
            ftype = 'py' if ext == '.py' else 'js'
            save_user_file(uid, fn, ftype)
            if ftype == 'js':
                threading.Thread(target=run_js_script_sync,
                                 args=(path, uid, folder, fn, chat_id),
                                 daemon=True).start()
            else:
                threading.Thread(target=run_script_sync,
                                 args=(path, uid, folder, fn, chat_id),
                                 daemon=True).start()
    except Exception as e:
        logger.error(f"doc handle err: {e}", exc_info=True)
        await message.answer(premium_emoji(f"❌ Error: {esc(str(e))}"))


async def handle_zip(content, zipname, message):
    uid = message.from_user.id
    chat_id = message.chat.id
    folder = get_user_folder(uid)
    tmp = None
    try:
        tmp = tempfile.mkdtemp(prefix=f"zip_{uid}_")
        zp = os.path.join(tmp, zipname)
        with open(zp, 'wb') as f:
            f.write(content)

        with zipfile.ZipFile(zp, 'r') as zf:
            if uid != OWNER_ID:
                for member in zf.infolist():
                    ml = member.filename.lower()
                    if any(ml.endswith(e) for e in ['.exe', '.dll', '.bat', '.cmd', '.scr', '.com']):
                        await message.answer(premium_emoji(f"🚨 ZIP has suspicious file: {esc(member.filename)}"))
                        return
                    mpath = os.path.abspath(os.path.join(tmp, member.filename))
                    if not mpath.startswith(os.path.abspath(tmp)):
                        raise zipfile.BadZipFile(f"Unsafe path: {member.filename}")
            zf.extractall(tmp)

        target = tmp
        root_files = os.listdir(tmp)
        if not any(f.endswith(('.py', '.js')) for f in root_files):
            for r, dirs, files in os.walk(tmp):
                dirs[:] = [d for d in dirs if not d.startswith('.') and not d.startswith('__')]
                if any(f.endswith(('.py', '.js')) for f in files):
                    target = r
                    break

        if target != tmp:
            for item in os.listdir(target):
                s = os.path.join(target, item)
                d = os.path.join(tmp, item)
                if os.path.exists(d):
                    if os.path.isdir(d):
                        shutil.rmtree(d)
                    else:
                        os.remove(d)
                shutil.move(s, d)

        items = os.listdir(tmp)
        py = [f for f in items if f.endswith('.py')]
        js = [f for f in items if f.endswith('.js')]

        req = 'requirements.txt' if 'requirements.txt' in items else None
        pkg = 'package.json' if 'package.json' in items else None

        if req:
            await message.answer(premium_emoji("🔄 Installing Python deps from requirements.txt..."))
            try:
                r = subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', os.path.join(tmp, req)],
                                   capture_output=True, text=True, check=True,
                                   encoding='utf-8', errors='ignore')
                await message.answer(premium_emoji("✅ Python deps installed."))
            except subprocess.CalledProcessError as e:
                err = esc((e.stderr or e.stdout or "")[:1000])
                await message.answer(premium_emoji(f"❌ pip install failed:\n<pre>{err}</pre>"))
                return
        if pkg:
            await message.answer(premium_emoji("🔄 Installing Node deps from package.json..."))
            try:
                subprocess.run(['npm', 'install'], cwd=tmp, capture_output=True, text=True,
                               check=True, encoding='utf-8', errors='ignore')
                await message.answer(premium_emoji("✅ Node deps installed."))
            except FileNotFoundError:
                await message.answer(premium_emoji("❌ 'npm' not found."))
                return
            except subprocess.CalledProcessError as e:
                err = esc((e.stderr or e.stdout or "")[:1000])
                await message.answer(premium_emoji(f"❌ npm install failed:\n<pre>{err}</pre>"))
                return

        main = None
        ftype = None
        for p in ['main.py', 'bot.py', 'app.py']:
            if p in py:
                main = p
                ftype = 'py'
                break
        if not main:
            for p in ['index.js', 'main.js', 'bot.js', 'app.js']:
                if p in js:
                    main = p
                    ftype = 'js'
                    break
        if not main:
            if py:
                main = py[0]
                ftype = 'py'
            elif js:
                main = js[0]
                ftype = 'js'
        if not main:
            await message.answer(premium_emoji("❌ No .py or .js script found in archive!"))
            return

        for it in os.listdir(tmp):
            if it == zipname:
                continue
            s = os.path.join(tmp, it)
            d = os.path.join(folder, it)
            if os.path.isdir(d):
                shutil.rmtree(d)
            elif os.path.exists(d):
                os.remove(d)
            shutil.move(s, d)

        save_user_file(uid, main, ftype)
        await message.answer(premium_emoji(f"✅ Extracted. Starting <code>{esc(main)}</code>..."))

        path = os.path.join(folder, main)
        if ftype == 'py':
            threading.Thread(target=run_script_sync,
                             args=(path, uid, folder, main, chat_id), daemon=True).start()
        else:
            threading.Thread(target=run_js_script_sync,
                             args=(path, uid, folder, main, chat_id), daemon=True).start()
    except zipfile.BadZipFile as e:
        await message.answer(premium_emoji(f"❌ Invalid ZIP: {esc(str(e))}"))
    except Exception as e:
        logger.error(f"zip err: {e}", exc_info=True)
        await message.answer(premium_emoji(f"❌ Zip error: {esc(str(e))}"))
    finally:
        if tmp and os.path.exists(tmp):
            try:
                shutil.rmtree(tmp)
            except Exception:
                pass


async def cb_check_files(call: CallbackQuery):
    uid = call.from_user.id
    files = user_files.get(uid, [])
    if not files:
        await call.answer("⚠️ No files.", show_alert=True)
        b = InlineKeyboardBuilder()
        b.button(text="🔙 Back", callback_data='back_to_main',
                 style="primary", icon=get_emoji_id("🔙"))
        try:
            await call.message.edit_text(premium_emoji("📂 Your files:\n\n(No files)"),
                                          reply_markup=b.as_markup())
        except Exception:
            pass
        return
    await call.answer()
    b = InlineKeyboardBuilder()
    for fn, ft in sorted(files):
        running = is_bot_running(uid, fn)
        icon = "🟢" if running else "🔴"
        b.button(text=f"{icon} {fn} ({ft})", callback_data=f'file_{uid}_{fn}',
                 style="success" if running else "primary")
    b.button(text="🔙 Back to Main", callback_data='back_to_main',
             style="primary", icon=get_emoji_id("🔙"))
    b.adjust(1)
    try:
        await call.message.edit_text(premium_emoji("📂 Your files:\nClick to manage."),
                                      reply_markup=b.as_markup())
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e).lower():
            logger.error(f"edit check_files err: {e}")


async def cb_file_control(call: CallbackQuery):
    try:
        _, oid_s, fn = call.data.split('_', 2)
        oid = int(oid_s)
        uid = call.from_user.id
        if not (uid == oid or uid in admin_ids):
            await call.answer("⚠️ Permission denied.", show_alert=True)
            return
        files = user_files.get(oid, [])
        if not any(f[0] == fn for f in files):
            await call.answer("⚠️ File not found.", show_alert=True)
            return
        running = is_bot_running(oid, fn)
        ft = next((f[1] for f in files if f[0] == fn), '?')
        status = "🟢 Running" if running else "🔴 Stopped"
        await call.answer()
        try:
            await call.message.edit_text(
                premium_emoji(f"🎛 Controls: <code>{esc(fn)}</code> ({ft}) of User <code>{oid}</code>\nStatus: {status}"),
                reply_markup=control_kb(oid, fn, running))
        except TelegramBadRequest as e:
            if "message is not modified" not in str(e).lower():
                raise
    except Exception as e:
        logger.error(f"file ctrl err: {e}", exc_info=True)
        try:
            await call.answer("Error", show_alert=True)
        except Exception:
            pass


async def cb_start(call: CallbackQuery):
    try:
        _, oid_s, fn = call.data.split('_', 2)
        oid = int(oid_s)
        uid = call.from_user.id
        if not (uid == oid or uid in admin_ids):
            await call.answer("⚠️ Permission denied.", show_alert=True)
            return
        files = user_files.get(oid, [])
        info = next((f for f in files if f[0] == fn), None)
        if not info:
            await call.answer("⚠️ File not found.", show_alert=True)
            return
        ft = info[1]
        folder = get_user_folder(oid)
        path = os.path.join(folder, fn)
        if not os.path.exists(path):
            await call.answer("⚠️ File missing! Re-upload.", show_alert=True)
            remove_user_file_db(oid, fn)
            return
        if is_bot_running(oid, fn):
            await call.answer("⚠️ Already running.", show_alert=True)
            return
        await call.answer(f"⏳ Starting {fn}...")
        if ft == 'py':
            threading.Thread(target=run_script_sync,
                             args=(path, oid, folder, fn, call.message.chat.id), daemon=True).start()
        else:
            threading.Thread(target=run_js_script_sync,
                             args=(path, oid, folder, fn, call.message.chat.id), daemon=True).start()
        await asyncio.sleep(1.5)
        running = is_bot_running(oid, fn)
        status = "🟢 Running" if running else "🟡 Starting"
        try:
            await call.message.edit_text(
                premium_emoji(f"🎛 Controls: <code>{esc(fn)}</code> ({ft}) of User <code>{oid}</code>\nStatus: {status}"),
                reply_markup=control_kb(oid, fn, running))
        except TelegramBadRequest:
            pass
    except Exception as e:
        logger.error(f"start err: {e}", exc_info=True)
        try:
            await call.answer("Error", show_alert=True)
        except Exception:
            pass


async def cb_stop(call: CallbackQuery):
    try:
        _, oid_s, fn = call.data.split('_', 2)
        oid = int(oid_s)
        uid = call.from_user.id
        if not (uid == oid or uid in admin_ids):
            await call.answer("⚠️ Permission denied.", show_alert=True)
            return
        key = f"{oid}_{fn}"
        if not is_bot_running(oid, fn):
            await call.answer("⚠️ Already stopped.", show_alert=True)
            return
        await call.answer(f"⏳ Stopping {fn}...")
        with bot_scripts_lock:
            info = bot_scripts.get(key)
        if info:
            kill_process_tree(info)
            with bot_scripts_lock:
                bot_scripts.pop(key, None)
        ft = next((f[1] for f in user_files.get(oid, []) if f[0] == fn), '?')
        try:
            await call.message.edit_text(
                premium_emoji(f"🎛 Controls: <code>{esc(fn)}</code> ({ft}) of User <code>{oid}</code>\nStatus: 🔴 Stopped"),
                reply_markup=control_kb(oid, fn, False))
        except TelegramBadRequest:
            pass
    except Exception as e:
        logger.error(f"stop err: {e}", exc_info=True)
        try:
            await call.answer("Error", show_alert=True)
        except Exception:
            pass


async def cb_restart(call: CallbackQuery):
    try:
        _, oid_s, fn = call.data.split('_', 2)
        oid = int(oid_s)
        uid = call.from_user.id
        if not (uid == oid or uid in admin_ids):
            await call.answer("⚠️ Permission denied.", show_alert=True)
            return
        files = user_files.get(oid, [])
        info = next((f for f in files if f[0] == fn), None)
        if not info:
            await call.answer("⚠️ File not found.", show_alert=True)
            return
        ft = info[1]
        folder = get_user_folder(oid)
        path = os.path.join(folder, fn)
        if not os.path.exists(path):
            await call.answer("⚠️ File missing!", show_alert=True)
            remove_user_file_db(oid, fn)
            return
        await call.answer(f"⏳ Restarting {fn}...")
        key = f"{oid}_{fn}"
        if is_bot_running(oid, fn):
            with bot_scripts_lock:
                pi = bot_scripts.get(key)
            if pi:
                kill_process_tree(pi)
            with bot_scripts_lock:
                bot_scripts.pop(key, None)
            await asyncio.sleep(1.5)
        if ft == 'py':
            threading.Thread(target=run_script_sync,
                             args=(path, oid, folder, fn, call.message.chat.id), daemon=True).start()
        else:
            threading.Thread(target=run_js_script_sync,
                             args=(path, oid, folder, fn, call.message.chat.id), daemon=True).start()
        await asyncio.sleep(1.5)
        running = is_bot_running(oid, fn)
        status = "🟢 Running" if running else "🟡 Starting"
        try:
            await call.message.edit_text(
                premium_emoji(f"🎛 Controls: <code>{esc(fn)}</code> ({ft}) of User <code>{oid}</code>\nStatus: {status}"),
                reply_markup=control_kb(oid, fn, running))
        except TelegramBadRequest:
            pass
    except Exception as e:
        logger.error(f"restart err: {e}", exc_info=True)
        try:
            await call.answer("Error", show_alert=True)
        except Exception:
            pass


async def cb_delete(call: CallbackQuery):
    try:
        _, oid_s, fn = call.data.split('_', 2)
        oid = int(oid_s)
        uid = call.from_user.id
        if not (uid == oid or uid in admin_ids):
            await call.answer("⚠️ Permission denied.", show_alert=True)
            return
        files = user_files.get(oid, [])
        if not any(f[0] == fn for f in files):
            await call.answer("⚠️ File not found.", show_alert=True)
            return
        await call.answer(f"🗑️ Deleting {fn}...")
        key = f"{oid}_{fn}"
        if is_bot_running(oid, fn):
            with bot_scripts_lock:
                pi = bot_scripts.get(key)
            if pi:
                kill_process_tree(pi)
            with bot_scripts_lock:
                bot_scripts.pop(key, None)
            await asyncio.sleep(0.5)
        folder = get_user_folder(oid)
        for p in [os.path.join(folder, fn),
                  os.path.join(folder, f"{os.path.splitext(fn)[0]}.log")]:
            if os.path.exists(p):
                try:
                    os.remove(p)
                except Exception:
                    pass
        remove_user_file_db(oid, fn)
        try:
            await call.message.edit_text(premium_emoji(f"🗑️ Deleted <code>{esc(fn)}</code> for user <code>{oid}</code>"))
        except TelegramBadRequest:
            pass
    except Exception as e:
        logger.error(f"del err: {e}", exc_info=True)
        try:
            await call.answer("Error", show_alert=True)
        except Exception:
            pass


async def cb_logs(call: CallbackQuery):
    try:
        _, oid_s, fn = call.data.split('_', 2)
        oid = int(oid_s)
        uid = call.from_user.id
        if not (uid == oid or uid in admin_ids):
            await call.answer("⚠️ Permission denied.", show_alert=True)
            return
        folder = get_user_folder(oid)
        log_path = os.path.join(folder, f"{os.path.splitext(fn)[0]}.log")
        if not os.path.exists(log_path):
            await call.answer("⚠️ No logs.", show_alert=True)
            return
        await call.answer()
        content = ""
        try:
            size = os.path.getsize(log_path)
            if size == 0:
                content = "(empty)"
            elif size > 100 * 1024:
                with open(log_path, 'rb') as f:
                    f.seek(-100 * 1024, os.SEEK_END)
                    content = f.read().decode('utf-8', errors='ignore')
                content = "(last 100KB)\n...\n" + content
            else:
                with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
            if len(content) > 3500:
                content = "...\n" + content[-3500:]
            if not content.strip():
                content = "(no content)"
            await bot.send_message(call.message.chat.id,
                premium_emoji(f"📜 Logs for <code>{esc(fn)}</code> (User <code>{oid}</code>):\n<pre>{esc(content)}</pre>"))
        except Exception as e:
            logger.error(f"read log err: {e}")
            await bot.send_message(call.message.chat.id,
                premium_emoji(f"❌ Error reading log."))
    except Exception as e:
        logger.error(f"logs err: {e}", exc_info=True)
        try:
            await call.answer("Error", show_alert=True)
        except Exception:
            pass


async def cb_speed(call: CallbackQuery):
    uid = call.from_user.id
    t = time.time()
    try:
        await call.answer()
        rt = round((time.time() - t) * 1000, 2)
        status = "🔓 Unlocked" if not bot_locked else "🔒 Locked"
        if uid == OWNER_ID:
            lvl = "🤍 Owner"
        elif uid in admin_ids:
            lvl = "🌙 Admin"
        elif uid in user_subscriptions and user_subscriptions[uid].get('expiry', datetime.min) > datetime.now():
            lvl = "⭐ Premium"
        else:
            lvl = "🆓 Free"
        txt = (f"⚡ Bot Speed:\n\n"
               f"⏱️ Response: {rt} ms\n"
               f"🚦 Status: {status}\n"
               f"👤 You: {lvl}")
        try:
            await call.message.edit_text(premium_emoji(txt), reply_markup=main_menu_kb(uid))
        except TelegramBadRequest:
            pass
    except Exception as e:
        logger.error(f"speed err: {e}", exc_info=True)


async def cb_back_main(call: CallbackQuery):
    uid = call.from_user.id
    lim = get_user_file_limit(uid)
    cur = get_user_file_count(uid)
    lim_s = str(lim) if lim != float('inf') else "Unlimited"
    if uid == OWNER_ID:
        st = "🤍 Owner"
    elif uid in admin_ids:
        st = "🌙 Admin"
    elif uid in user_subscriptions and user_subscriptions[uid].get('expiry', datetime.min) > datetime.now():
        st = "⭐ Premium"
    else:
        st = "🆓 Free"
    txt = (f"〽️ Welcome back, {esc(call.from_user.first_name)}!\n\n"
           f"🆔 ID: <code>{uid}</code>\n"
           f"🔰 Status: {st}\n"
           f"📁 Files: {cur} / {lim_s}")
    await call.answer()
    try:
        await call.message.edit_text(premium_emoji(txt), reply_markup=main_menu_kb(uid))
    except TelegramBadRequest:
        pass


async def cb_send_to_process(call: CallbackQuery):
    uid = call.from_user.id
    running = []
    for k, info in bot_scripts.items():
        oid = info['script_owner_id']
        if (uid == oid or uid in admin_ids) and is_bot_running(oid, info['file_name']):
            running.append((k, info))
    if not running:
        await call.answer("❌ No running scripts.", show_alert=True)
        return
    await call.answer()
    b = InlineKeyboardBuilder()
    for k, info in running:
        b.button(text=f"{info['file_name']} (U{info['script_owner_id']})",
                 callback_data=f'sendcmd_select_{k}', style="primary")
    b.button(text="🔙 Back", callback_data='send_command',
             style="primary", icon=get_emoji_id("🔙"))
    b.adjust(1)
    try:
        await call.message.edit_text(premium_emoji("📝 Select script:"), reply_markup=b.as_markup())
    except TelegramBadRequest:
        pass


async def cb_sendcmd_select(call: CallbackQuery, state: FSMContext):
    key = call.data.replace('sendcmd_select_', '')
    await call.answer()
    await bot.send_message(call.message.chat.id,
        premium_emoji(f"📝 Enter command to send to <code>{esc(key)}</code>:"))
    await state.set_state(AdminStates.waiting_send_cmd)
    await state.update_data(script_key=key)


@router.message(AdminStates.waiting_send_cmd)
async def process_send_cmd(message: Message, state: FSMContext):
    data = await state.get_data()
    key = data.get('script_key')
    await state.clear()
    if not key or key not in bot_scripts:
        await message.answer(premium_emoji("❌ Script no longer running."))
        return
    info = bot_scripts[key]
    try:
        p = info['process']
        if p and p.poll() is None:
            p.stdin.write(message.text + '\n')
            p.stdin.flush()
            await message.answer(premium_emoji(f"✅ Sent to <code>{esc(info['file_name'])}</code>"))
            await asyncio.sleep(1)
            if p.poll() is not None:
                await message.answer(premium_emoji(f"⚠️ Script <code>{esc(info['file_name'])}</code> stopped."))
        else:
            await message.answer(premium_emoji("❌ Not running."))
    except Exception as e:
        await message.answer(premium_emoji(f"❌ Error: {esc(str(e))}"))


async def cb_view_all_logs(call: CallbackQuery):
    uid = call.from_user.id
    folder = get_user_folder(uid)
    logs = []
    if os.path.exists(folder):
        for f in os.listdir(folder):
            if f.endswith('.log'):
                p = os.path.join(folder, f)
                logs.append((f, os.path.getsize(p)))
    if not logs:
        await call.answer("📜 No logs.", show_alert=True)
        return
    await call.answer()
    b = InlineKeyboardBuilder()
    for fn, size in sorted(logs):
        b.button(text=f"{fn} ({size/1024:.1f} KB)",
                 callback_data=f'viewlog_{uid}_{fn}', style="primary")
    b.button(text="🔙 Back", callback_data='send_command',
             style="primary", icon=get_emoji_id("🔙"))
    b.adjust(1)
    try:
        await call.message.edit_text(premium_emoji("📜 Available Log Files:"), reply_markup=b.as_markup())
    except TelegramBadRequest:
        pass


async def cb_viewlog(call: CallbackQuery):
    try:
        _, uid_s, fn = call.data.split('_', 2)
        uid = int(uid_s)
        req = call.from_user.id
        if not (req == uid or req in admin_ids):
            await call.answer("⚠️ Permission.", show_alert=True)
            return
        p = os.path.join(get_user_folder(uid), fn)
        if not os.path.exists(p):
            await call.answer("❌ Not found.", show_alert=True)
            return
        await call.answer()
        await bot.send_document(call.message.chat.id, FSInputFile(p),
                                caption=premium_emoji(f"📜 {fn}"))
    except Exception as e:
        logger.error(f"viewlog err: {e}", exc_info=True)
        try:
            await call.answer("Error", show_alert=True)
        except Exception:
            pass


async def _run_all_scripts(chat_id):
    await bot.send_message(chat_id, premium_emoji("⏳ Starting all user scripts..."))
    logger.info(f"Run all scripts from chat {chat_id}")
    started = 0
    attempted = 0
    skipped = 0
    details = []
    snapshot = dict(user_files)
    for tid, files in snapshot.items():
        if not files:
            continue
        attempted += 1
        folder = get_user_folder(tid)
        for fn, ft in files:
            if not is_bot_running(tid, fn):
                p = os.path.join(folder, fn)
                if os.path.exists(p):
                    try:
                        if ft == 'py':
                            threading.Thread(target=run_script_sync,
                                             args=(p, tid, folder, fn, chat_id), daemon=True).start()
                            started += 1
                        elif ft == 'js':
                            threading.Thread(target=run_js_script_sync,
                                             args=(p, tid, folder, fn, chat_id), daemon=True).start()
                            started += 1
                        else:
                            skipped += 1
                            details.append(f"<code>{esc(fn)}</code> (U{tid}) unknown type")
                        await asyncio.sleep(0.7)
                    except Exception as e:
                        logger.error(f"run all err: {e}")
                        skipped += 1
                        details.append(f"<code>{esc(fn)}</code> (U{tid}) start error")
                else:
                    skipped += 1
                    details.append(f"<code>{esc(fn)}</code> (U{tid}) file not found")
    msg = (f"✅ All Scripts Started:\n\n"
           f"▶️ Started: {started}\n"
           f"👥 Users: {attempted}\n")
    if skipped > 0:
        msg += f"⚠️ Skipped: {skipped}\n"
        if details:
            msg += "Details (first 5):\n" + "\n".join([f"  - {d}" for d in details[:5]])
    await bot.send_message(chat_id, premium_emoji(msg))


# --- Broadcast ---
@router.message(AdminStates.waiting_broadcast)
async def process_broadcast(message: Message, state: FSMContext):
    if message.from_user.id not in admin_ids:
        await state.clear()
        return
    if message.text and message.text.lower() == '/cancel':
        await state.clear()
        await message.answer(premium_emoji("Broadcast cancelled."))
        return
    txt = message.text
    photo_id = None
    video_id = None
    caption = None
    if message.photo:
        photo_id = message.photo[-1].file_id
        caption = message.caption
    elif message.video:
        video_id = message.video.file_id
        caption = message.caption
    if not txt and not photo_id and not video_id:
        await message.answer(premium_emoji("⚠️ Send text or media, or /cancel."))
        return
    count = len(active_users)
    preview = esc(txt[:1000]) if txt else "(media message)"
    b = InlineKeyboardBuilder()
    b.button(text="✅ Confirm & Send", callback_data="confirm_broadcast",
             style="success", icon=get_emoji_id("✅"))
    b.button(text="❌ Cancel", callback_data="cancel_broadcast",
             style="danger", icon=get_emoji_id("❌"))
    b.adjust(2)
    await message.answer(premium_emoji(f"⚠️ Confirm Broadcast:\n\n<pre>{preview}</pre>\n\n"
                                        f"To <b>{count}</b> users. Sure?"),
                          reply_markup=b.as_markup())
    await state.update_data(bc_text=txt, bc_photo=photo_id, bc_video=video_id, bc_caption=caption)


async def cb_do_broadcast(call: CallbackQuery, state: FSMContext):
    if call.from_user.id not in admin_ids:
        await call.answer("⚠️ Admin only.", show_alert=True)
        return
    data = await state.get_data()
    await state.clear()
    txt = data.get('bc_text')
    photo_id = data.get('bc_photo')
    video_id = data.get('bc_video')
    caption = data.get('bc_caption')
    await call.answer("🚀 Starting broadcast...")
    try:
        await call.message.edit_text(premium_emoji(f"📢 Broadcasting to {len(active_users)} users..."))
    except TelegramBadRequest:
        pass
    asyncio.create_task(execute_broadcast_async(txt, photo_id, video_id, caption, call.message.chat.id))


async def execute_broadcast_async(txt, photo_id, video_id, caption, admin_chat_id):
    sent = 0
    failed = 0
    blocked = 0
    t0 = time.time()
    users = list(active_users)
    total = len(users)
    logger.info(f"Broadcast to {total} users")
    for i, uid in enumerate(users):
        try:
            if txt:
                await bot.send_message(uid, premium_emoji(txt))
            elif photo_id:
                await bot.send_photo(uid, photo_id,
                                     caption=premium_emoji(caption) if caption else None)
            elif video_id:
                await bot.send_video(uid, video_id,
                                     caption=premium_emoji(caption) if caption else None)
            sent += 1
        except TelegramBadRequest as e:
            err = str(e).lower()
            if any(s in err for s in ["blocked", "deactivated", "chat not found", "kicked", "restricted"]):
                blocked += 1
            elif "flood" in err or "too many" in err:
                m = re.search(r"retry after (\d+)", err)
                wait = int(m.group(1)) + 1 if m else 5
                logger.warning(f"Flood control. Sleeping {wait}s")
                await asyncio.sleep(wait)
                try:
                    if txt:
                        await bot.send_message(uid, premium_emoji(txt))
                    elif photo_id:
                        await bot.send_photo(uid, photo_id,
                                             caption=premium_emoji(caption) if caption else None)
                    elif video_id:
                        await bot.send_video(uid, video_id,
                                             caption=premium_emoji(caption) if caption else None)
                    sent += 1
                except Exception:
                    failed += 1
            else:
                failed += 1
        except Exception as e:
            logger.error(f"Broadcast err {uid}: {e}")
            failed += 1
        if (i + 1) % 25 == 0 and i < total - 1:
            await asyncio.sleep(1.5)
        else:
            await asyncio.sleep(0.05)
    duration = round(time.time() - t0, 2)
    result = (f"📢 Broadcast Complete!\n\n"
              f"✅ Sent: {sent}\n"
              f"❌ Failed: {failed}\n"
              f"🚫 Blocked/Inactive: {blocked}\n"
              f"👥 Targets: {total}\n"
              f"⏱️ Duration: {duration}s")
    try:
        await bot.send_message(admin_chat_id, premium_emoji(result))
    except Exception as e:
        logger.error(f"broadcast result err: {e}")


# --- Admin state handlers ---
@router.message(AdminStates.waiting_admin_add)
async def proc_admin_add(message: Message, state: FSMContext):
    if message.from_user.id != OWNER_ID:
        await state.clear()
        return
    if message.text and message.text.lower() == '/cancel':
        await state.clear()
        await message.answer(premium_emoji("Cancelled."))
        return
    try:
        nid = int(message.text.strip())
        if nid <= 0:
            raise ValueError
        if nid == OWNER_ID:
            await message.answer(premium_emoji("⚠️ Already Owner."))
            await state.clear()
            return
        if nid in admin_ids:
            await message.answer(premium_emoji(f"⚠️ <code>{nid}</code> already Admin."))
            await state.clear()
            return
        add_admin_db(nid)
        await state.clear()
        await message.answer(premium_emoji(f"✅ <code>{nid}</code> promoted to Admin."))
        try:
            await bot.send_message(nid, premium_emoji("🎉 You are now an Admin!"))
        except Exception:
            pass
    except ValueError:
        await message.answer(premium_emoji("⚠️ Invalid ID. Send numeric or /cancel."))


@router.message(AdminStates.waiting_admin_remove)
async def proc_admin_remove(message: Message, state: FSMContext):
    if message.from_user.id != OWNER_ID:
        await state.clear()
        return
    if message.text and message.text.lower() == '/cancel':
        await state.clear()
        await message.answer(premium_emoji("Cancelled."))
        return
    try:
        nid = int(message.text.strip())
        if nid <= 0:
            raise ValueError
        if nid == OWNER_ID:
            await message.answer(premium_emoji("⚠️ Cannot remove Owner."))
            await state.clear()
            return
        if nid not in admin_ids:
            await message.answer(premium_emoji(f"⚠️ <code>{nid}</code> not Admin."))
            await state.clear()
            return
        ok = remove_admin_db(nid)
        await state.clear()
        if ok:
            await message.answer(premium_emoji(f"✅ <code>{nid}</code> removed."))
            try:
                await bot.send_message(nid, premium_emoji("ℹ️ You are no longer Admin."))
            except Exception:
                pass
        else:
            await message.answer(premium_emoji(f"❌ Failed to remove <code>{nid}</code>."))
    except ValueError:
        await message.answer(premium_emoji("⚠️ Invalid ID."))


@router.message(AdminStates.waiting_sub_add)
async def proc_sub_add(message: Message, state: FSMContext):
    if message.from_user.id not in admin_ids:
        await state.clear()
        return
    if message.text and message.text.lower() == '/cancel':
        await state.clear()
        await message.answer(premium_emoji("Cancelled."))
        return
    try:
        parts = message.text.split()
        if len(parts) != 2:
            raise ValueError
        uid = int(parts[0])
        days = int(parts[1])
        if uid <= 0 or days <= 0:
            raise ValueError
        now = datetime.now()
        cur = user_subscriptions.get(uid, {}).get('expiry')
        start = cur if cur and cur > now else now
        newexp = start + timedelta(days=days)
        save_subscription(uid, newexp)
        await state.clear()
        await message.answer(premium_emoji(f"✅ Sub for <code>{uid}</code> for {days} days.\nExpires: {newexp:%Y-%m-%d}"))
        try:
            await bot.send_message(uid, premium_emoji(f"🎉 Sub activated! Expires {newexp:%Y-%m-%d}."))
        except Exception:
            pass
    except Exception:
        await message.answer(premium_emoji("⚠️ Format: <code>USER_ID DAYS</code>"))


@router.message(AdminStates.waiting_sub_remove)
async def proc_sub_remove(message: Message, state: FSMContext):
    if message.from_user.id not in admin_ids:
        await state.clear()
        return
    if message.text and message.text.lower() == '/cancel':
        await state.clear()
        await message.answer(premium_emoji("Cancelled."))
        return
    try:
        uid = int(message.text.strip())
        if uid <= 0:
            raise ValueError
        if uid not in user_subscriptions:
            await message.answer(premium_emoji(f"⚠️ <code>{uid}</code> no active sub."))
            await state.clear()
            return
        remove_subscription_db(uid)
        await state.clear()
        await message.answer(premium_emoji(f"✅ Sub for <code>{uid}</code> removed."))
        try:
            await bot.send_message(uid, premium_emoji("ℹ️ Your subscription was removed."))
        except Exception:
            pass
    except ValueError:
        await message.answer(premium_emoji("⚠️ Invalid ID."))


@router.message(AdminStates.waiting_sub_check)
async def proc_sub_check(message: Message, state: FSMContext):
    if message.from_user.id not in admin_ids:
        await state.clear()
        return
    if message.text and message.text.lower() == '/cancel':
        await state.clear()
        await message.answer(premium_emoji("Cancelled."))
        return
    try:
        uid = int(message.text.strip())
        if uid <= 0:
            raise ValueError
        await state.clear()
        if uid in user_subscriptions:
            e = user_subscriptions[uid].get('expiry')
            if e and e > datetime.now():
                days_left = (e - datetime.now()).days
                await message.answer(premium_emoji(
                    f"✅ Active sub.\nExpires: {e:%Y-%m-%d %H:%M} ({days_left} days left)"))
            else:
                await message.answer(premium_emoji(f"⚠️ Expired sub (On: {e:%Y-%m-%d %H:%M})."))
                remove_subscription_db(uid)
        else:
            await message.answer(premium_emoji(f"ℹ️ No sub for <code>{uid}</code>."))
    except ValueError:
        await message.answer(premium_emoji("⚠️ Invalid ID."))


# --- Cleanup ---
def cleanup():
    logger.warning("Shutdown. Killing processes...")
    keys = list(bot_scripts.keys())
    for k in keys:
        if k in bot_scripts:
            logger.info(f"Stopping {k}")
            kill_process_tree(bot_scripts[k])
    logger.warning("Cleanup done.")


atexit.register(cleanup)


# --- Signal handling ---
def signal_handler(sig, frame):
    logger.warning(f"Signal {sig} received. Exiting...")
    cleanup()
    sys.exit(0)


try:
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
except Exception:
    pass


# --- Main ---
async def main():
    global MAIN_LOOP
    MAIN_LOOP = asyncio.get_running_loop()

    logger.info("=" * 50)
    logger.info("🤖 Bot Starting Up")
    logger.info(f"🐍 Python: {sys.version.split()[0]}")
    logger.info(f"🔧 Base: {BASE_DIR}")
    logger.info(f"🔑 Owner: {OWNER_ID}")
    logger.info(f"🛡️ Admins: {admin_ids}")
    logger.info("=" * 50)

    keep_alive()

    try:
        await bot.delete_webhook(drop_pending_updates=True)
    except Exception as e:
        logger.warning(f"delete_webhook err: {e}")

    logger.info("🚀 Starting polling...")
    while True:
        try:
            await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
        except TelegramBadRequest as e:
            logger.error(f"TelegramBadRequest: {e}. Retry in 5s")
            await asyncio.sleep(5)
        except asyncio.CancelledError:
            logger.info("Polling cancelled.")
            break
        except Exception as e:
            logger.critical(f"💥 Polling error: {e}", exc_info=True)
            logger.info("Retry in 15s...")
            await asyncio.sleep(15)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped.")
        cleanup()
    except Exception as e:
        logger.critical(f"Fatal: {e}", exc_info=True)
        cleanup()