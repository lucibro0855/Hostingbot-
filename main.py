# -*- coding: utf-8 -*-
import telebot
import subprocess
import os
import sys

os.environ["PYTHONIOENCODING"] = "utf-8"

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except:
    pass

import zipfile
import tempfile
import shutil
from telebot import types
import time
from datetime import datetime, timedelta
import psutil
import sqlite3
import json
import logging
import signal
import threading
import re
import atexit
import requests
import hashlib
import mimetypes
import struct

# --- Flask Keep Alive ---
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "bot is running...."

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()
    print("Flask Keep-Alive server started.")
# --- End Flask Keep Alive ---

# --- Configuration ---
TOKEN = "8824814752:AAFsQj8wKm7teJP2W28Fz1kWWDJRq_wWq2E"
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

bot = telebot.TeleBot(TOKEN)

# --- Data structures ---
bot_scripts = {}
user_subscriptions = {}
user_files = {}
active_users = set()
admin_ids = {ADMIN_ID, OWNER_ID}
bot_locked = False
file_db = {}
banned_users = set()
banned_usernames = set()

# --- Premium Emoji Configuration ---
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
    "🎛": "5258023599419171861", "🎯": "5122933683820430249", "📤": "5444908424015934570",
    "🚦": "5219901967916084166",
}

def premium_emoji(text):
    if not text:
        return text
    result = str(text)
    for emoji in sorted(PREMIUM_EMOJI_IDS.keys(), key=len, reverse=True):
        eid = PREMIUM_EMOJI_IDS[emoji]
        result = result.replace(emoji, f'<tg-emoji emoji-id="{eid}">{emoji}</tg-emoji>')
    return result

def _strip_tg_emoji(text):
    return re.sub(r'<tg-emoji[^>]*>(.*?)</tg-emoji>', r'\1', text, flags=re.DOTALL)

def send_premium(chat_id, text, **kwargs):
    try:
        return bot.send_message(chat_id, premium_emoji(text), parse_mode='HTML', **kwargs)
    except Exception as e:
        logger.error(f"send_premium failed: {e}")
        try:
            clean = _strip_tg_emoji(text)
            kwargs.pop('parse_mode', None)
            return bot.send_message(chat_id, clean, **kwargs)
        except Exception as e2:
            logger.error(f"send_premium fallback failed: {e2}")
            return None

def reply_premium(message, text, **kwargs):
    try:
        return bot.reply_to(message, premium_emoji(text), parse_mode='HTML', **kwargs)
    except Exception as e:
        logger.error(f"reply_premium failed: {e}")
        try:
            clean = _strip_tg_emoji(text)
            kwargs.pop('parse_mode', None)
            return bot.reply_to(message, clean, **kwargs)
        except Exception as e2:
            logger.error(f"reply_premium fallback failed: {e2}")
            return None

def edit_premium(chat_id, msg_id, text, **kwargs):
    try:
        return bot.edit_message_text(premium_emoji(text), chat_id, msg_id, parse_mode='HTML', **kwargs)
    except telebot.apihelper.ApiTelegramException as e:
        if "message is not modified" in str(e).lower():
            return None
        logger.error(f"edit_premium failed: {e}")
        try:
            clean = _strip_tg_emoji(text)
            kwargs.pop('parse_mode', None)
            return bot.edit_message_text(clean, chat_id, msg_id, **kwargs)
        except Exception as e2:
            logger.error(f"edit_premium fallback failed: {e2}")
            return None

# --- Malware Detection Config ---
MALWARE_SIGNATURES = [
    b'MZ', b'\x7fELF', b'\xfe\xed\xfa', b'\xce\xfa\xed\xfe', b'PK', b'Rar!',
]
ENCRYPTED_FILE_INDICATORS = [
    b'openssl', b'encrypted', b'cipher', b'DES', b'RSA', b'GPG', b'PGP',
]
SUSPICIOUS_KEYWORDS = [
    b'ransomware', b'trojan', b'virus', b'malware', b'backdoor', b'exploit',
    b'payload', b'botnet', b'keylogger', b'rootkit',
]

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Command Button Layouts (ReplyKeyboardMarkup) ---
COMMAND_BUTTONS_LAYOUT_USER_SPEC = [
    ["📢 Updates Channel"],
    ["📤 Upload File", "📂 Check Files"],
    ["⚡ Bot Speed", "📊 Statistics"],
    ["📤 Send Command", "📞 Contact Owner"]
]
ADMIN_COMMAND_BUTTONS_LAYOUT_USER_SPEC = [
    ["📢 Updates Channel"],
    ["📤 Upload File", "📂 Check Files"],
    ["⚡ Bot Speed", "📊 Statistics"],
    ["💳 Subscriptions", "📢 Broadcast"],
    ["🔒 Lock Bot", "🟢 Running All Code"],
    ["📤 Send Command", "👑 Admin Panel"],
    ["📞 Contact Owner"]
]

def send_force_join_msg(chat_id):
    markup = types.InlineKeyboardMarkup(row_width=1)
    for ch, name in FORCE_JOIN_CHANNELS.items():
        markup.add(types.InlineKeyboardButton(text=name, url=f"https://t.me/{ch.replace('@', '')}"))
    markup.add(types.InlineKeyboardButton("✅ Joined All", callback_data="force_join_check"))
    send_premium(chat_id, "𝐉𝐎𝐈𝐍 𝐀𝐋𝐋 𝐂𝐇𝐀𝐍𝐍𝐄𝐋 𝐓𝐎 𝐔𝐒𝐄 𝐌𝐄 🤍🌙:", reply_markup=markup)

def is_user_joined_all(user_id):
    try:
        for ch in FORCE_JOIN_CHANNELS.keys():
            member = bot.get_chat_member(ch, user_id)
            if member.status not in ['member', 'administrator', 'creator']:
                return False
        return True
    except Exception as e:
        logger.warning(f"Force join check error for {user_id}: {e}")
        return True  # ✅ FIX: error pe True return karo

# --- Database Setup ---
def init_db():
    logger.info(f"Initializing database at: {DATABASE_PATH}")
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
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error(f"❌ Database initialization error: {e}", exc_info=True)

def load_data():
    logger.info("Loading data from database...")
    try:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute('SELECT user_id, expiry FROM subscriptions')
        for user_id, expiry in c.fetchall():
            try:
                user_subscriptions[user_id] = {'expiry': datetime.fromisoformat(expiry)}
            except ValueError:
                pass
        c.execute('SELECT user_id, file_name, file_type FROM user_files')
        for user_id, file_name, file_type in c.fetchall():
            if user_id not in user_files:
                user_files[user_id] = []
            user_files[user_id].append((file_name, file_type))
        c.execute('SELECT user_id FROM active_users')
        active_users.update(user_id for (user_id,) in c.fetchall())
        c.execute('SELECT user_id FROM admins')
        admin_ids.update(user_id for (user_id,) in c.fetchall())
        conn.close()
        logger.info(f"Data loaded: {len(active_users)} users, {len(user_subscriptions)} subs, {len(admin_ids)} admins.")
    except Exception as e:
        logger.error(f"❌ Error loading data: {e}", exc_info=True)

init_db()
load_data()

# --- Malware Detection Functions ---
def get_file_type(file_content):
    signatures = {
        b'\x7fELF': 'application/x-executable',
        b'MZ': 'application/x-dosexec',
        b'\xfe\xed\xfa': 'application/x-mach-binary',
        b'\xce\xfa\xed\xfe': 'application/x-mach-binary',
        b'PK': 'application/zip',
        b'Rar!': 'application/x-rar',
    }
    for signature, mime_type in signatures.items():
        if file_content.startswith(signature):
            return mime_type
    return 'application/octet-stream'

def is_suspicious_file(file_content, file_name):
    file_lower = file_name.lower()
    suspicious_extensions = ['.exe', '.dll', '.bat', '.cmd', '.scr', '.com', '.pif', '.application', '.gadget',
                            '.msi', '.msp', '.com', '.scr', '.hta', '.cpl', '.msc', '.jar', '.bin', '.deb', '.rpm',
                            '.apk', '.app', '.dmg', '.iso', '.img']
    if any(file_lower.endswith(ext) for ext in suspicious_extensions):
        return True, f"Suspicious file extension: {file_name}"
    for signature in MALWARE_SIGNATURES:
        if file_content.startswith(signature):
            return True, f"Malware signature detected: {signature}"
    sample_size = min(len(file_content), 4096)
    file_sample = file_content[:sample_size]
    for indicator in ENCRYPTED_FILE_INDICATORS:
        if indicator in file_sample:
            return True, f"Encrypted file indicator: {indicator.decode('utf-8', errors='ignore')}"
    sample_text = file_sample.decode('utf-8', errors='ignore').lower()
    for keyword in SUSPICIOUS_KEYWORDS:
        if keyword.decode('utf-8').lower() in sample_text:
            return True, f"Suspicious keyword found: {keyword.decode('utf-8')}"
    try:
        file_type = get_file_type(file_sample)
        if file_type in ['application/x-dosexec', 'application/x-executable', 'application/x-mach-binary']:
            return True, f"Executable file type detected: {file_type}"
    except Exception as e:
        logger.warning(f"Could not determine file type: {e}")
    return False, "File appears safe"

def scan_file_for_malware(file_content, file_name, user_id):
    if user_id == OWNER_ID:
        return True, "Owner bypassed security check"
    is_suspicious, reason = is_suspicious_file(file_content, file_name)
    if is_suspicious:
        logger.warning(f"🚨 Malware detected in {file_name} from user {user_id}: {reason}")
        return False, f"Security violation: {reason}"
    return True, "File passed security check"

# --- Helper Functions ---
def get_user_folder(user_id):
    user_folder = os.path.join(UPLOAD_BOTS_DIR, str(user_id))
    os.makedirs(user_folder, exist_ok=True)
    return user_folder

def get_user_file_limit(user_id):
    if user_id == OWNER_ID: return OWNER_LIMIT
    if user_id in admin_ids: return ADMIN_LIMIT
    if user_id in user_subscriptions and user_subscriptions[user_id]['expiry'] > datetime.now():
        return SUBSCRIBED_USER_LIMIT
    return FREE_USER_LIMIT

def get_user_file_count(user_id):
    return len(user_files.get(user_id, []))

def is_bot_running(script_owner_id, file_name):
    script_key = f"{script_owner_id}_{file_name}"
    script_info = bot_scripts.get(script_key)
    if script_info and script_info.get('process'):
        try:
            proc = psutil.Process(script_info['process'].pid)
            is_running = proc.is_running() and proc.status() != psutil.STATUS_ZOMBIE
            if not is_running:
                if 'log_file' in script_info and hasattr(script_info['log_file'], 'close') and not script_info['log_file'].closed:
                    try:
                        script_info['log_file'].close()
                    except Exception:
                        pass
                if script_key in bot_scripts:
                    del bot_scripts[script_key]
            return is_running
        except psutil.NoSuchProcess:
            if 'log_file' in script_info and hasattr(script_info['log_file'], 'close') and not script_info['log_file'].closed:
                try:
                    script_info['log_file'].close()
                except Exception:
                    pass
            if script_key in bot_scripts:
                del bot_scripts[script_key]
            return False
        except Exception as e:
            logger.error(f"Error checking process status for {script_key}: {e}", exc_info=True)
            return False
    return False

def kill_process_tree(process_info):
    pid = None
    script_key = process_info.get('script_key', 'N/A')
    try:
        if 'log_file' in process_info and hasattr(process_info['log_file'], 'close') and not process_info['log_file'].closed:
            try:
                process_info['log_file'].close()
            except Exception as log_e:
                logger.error(f"Error closing log file during kill for {script_key}: {log_e}")
        process = process_info.get('process')
        if process and hasattr(process, 'pid'):
            pid = process.pid
            if pid:
                try:
                    parent = psutil.Process(pid)
                    children = parent.children(recursive=True)
                    for child in children:
                        try:
                            child.terminate()
                        except psutil.NoSuchProcess:
                            pass
                        except Exception as e:
                            try:
                                child.kill()
                            except Exception:
                                pass
                    gone, alive = psutil.wait_procs(children, timeout=1)
                    for p in alive:
                        try:
                            p.kill()
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
                    except Exception as e:
                        try:
                            parent.kill()
                        except Exception:
                            pass
                except psutil.NoSuchProcess:
                    pass
    except Exception as e:
        logger.error(f"❌ Unexpected error killing process tree for PID {pid or 'N/A'} ({script_key}): {e}", exc_info=True)

# --- Auto Install ---
def attempt_install_pip(module_name, message):
    package_name = TELEGRAM_MODULES.get(module_name.lower(), module_name)
    if module_name.lower() == "pil":
        package_name = "pillow"
    if package_name is None:
        return False
    try:
        reply_premium(message, f"🐍 Module <code>{module_name}</code> not found. Installing <code>{package_name}</code>...")
        command = [sys.executable, '-m', 'pip', 'install', package_name]
        result = subprocess.run(command, capture_output=True, text=True, check=False,
                                encoding='utf-8', errors='replace',
                                env={**os.environ, "PYTHONIOENCODING": "utf-8"})
        if result.returncode == 0:
            reply_premium(message, f"✅ Package <code>{package_name}</code> installed.")
            return True
        else:
            error_msg = (f"❌ Failed to install <code>{package_name}</code>.\n"
                         f"<pre>{(result.stderr or result.stdout)[:3500]}</pre>")
            reply_premium(message, error_msg)
            return False
    except Exception as e:
        logger.error(f"Error installing {package_name}: {e}", exc_info=True)
        reply_premium(message, f"❌ Error installing <code>{package_name}</code>: {str(e)}")
        return False

def attempt_install_npm(module_name, user_folder, message):
    try:
        reply_premium(message, f"🟠 Node package <code>{module_name}</code> not found. Installing locally...")
        command = ['npm', 'install', module_name]
        result = subprocess.run(command, capture_output=True, text=True, check=False,
                                cwd=user_folder, encoding='utf-8', errors='replace')
        if result.returncode == 0:
            reply_premium(message, f"✅ Node package <code>{module_name}</code> installed.")
            return True
        else:
            error_msg = (f"❌ Failed to install Node package <code>{module_name}</code>.\n"
                         f"<pre>{(result.stderr or result.stdout)[:3500]}</pre>")
            reply_premium(message, error_msg)
            return False
    except FileNotFoundError:
        reply_premium(message, "❌ Error: 'npm' not found. Ensure Node.js/npm are installed.")
        return False
    except Exception as e:
        logger.error(f"Error installing Node package {module_name}: {e}", exc_info=True)
        reply_premium(message, f"❌ Error installing <code>{module_name}</code>: {str(e)}")
        return False

def run_script(script_path, script_owner_id, user_folder, file_name, message_obj_for_reply, attempt=1):
    max_attempts = 2
    if attempt > max_attempts:
        reply_premium(message_obj_for_reply, f"❌ Failed to run '{file_name}' after {max_attempts} attempts.")
        return
    script_key = f"{script_owner_id}_{file_name}"
    logger.info(f"Attempt {attempt} to run Python script: {script_path} (Key: {script_key})")
    try:
        if not os.path.exists(script_path):
            reply_premium(message_obj_for_reply, f"❌ Script '{file_name}' not found!")
            if script_owner_id in user_files:
                user_files[script_owner_id] = [f for f in user_files.get(script_owner_id, []) if f[0] != file_name]
            remove_user_file_db(script_owner_id, file_name)
            return

        if attempt == 1:
            check_command = [sys.executable, script_path]
            check_proc = None
            try:
                check_proc = subprocess.Popen(check_command, cwd=user_folder,
                                              stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                              text=True, encoding='utf-8', errors='replace',
                                              env={**os.environ, "PYTHONIOENCODING": "utf-8"})
                stdout, stderr = check_proc.communicate(timeout=5)
                return_code = check_proc.returncode
                if return_code != 0 and stderr:
                    match_py = re.search(r"ModuleNotFoundError: No module named '(.+?)'", stderr)
                    if match_py:
                        module_name = match_py.group(1).strip()
                        if attempt_install_pip(module_name, message_obj_for_reply):
                            reply_premium(message_obj_for_reply, f"🔄 Retrying '{file_name}'...")
                            time.sleep(2)
                            threading.Thread(target=run_script, args=(
                                script_path, script_owner_id, user_folder, file_name,
                                message_obj_for_reply, attempt + 1)).start()
                            return
                        else:
                            reply_premium(message_obj_for_reply, f"❌ Install failed for '{module_name}'")
                            return
                    else:
                        error_summary = stderr[:500]
                        reply_premium(message_obj_for_reply, f"❌ Error in script pre-check:\n<pre>{error_summary}</pre>")
                        return
            except subprocess.TimeoutExpired:
                if check_proc and check_proc.poll() is None:
                    check_proc.kill()
                    check_proc.communicate()
            except FileNotFoundError:
                reply_premium(message_obj_for_reply, "❌ Python interpreter not found.")
                return
            except Exception as e:
                reply_premium(message_obj_for_reply, f"❌ Pre-check error: {str(e)}")
                return
            finally:
                if check_proc and check_proc.poll() is None:
                    check_proc.kill()
                    check_proc.communicate()

        log_file_path = os.path.join(user_folder, f"{os.path.splitext(file_name)[0]}.log")
        log_file = None
        process = None
        try:
            log_file = open(log_file_path, 'w', encoding='utf-8', errors='replace')
        except Exception as e:
            reply_premium(message_obj_for_reply, f"❌ Failed to open log file: {str(e)}")
            return
        try:
            startupinfo = None
            creationflags = 0
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
            process = subprocess.Popen([sys.executable, script_path], cwd=user_folder,
                                       stdout=log_file, stderr=log_file, stdin=subprocess.PIPE,
                                       startupinfo=startupinfo, creationflags=creationflags,
                                       text=True, encoding='utf-8', errors='replace',
                                       env={**os.environ, "PYTHONIOENCODING": "utf-8"})
            bot_scripts[script_key] = {
                'process': process, 'log_file': log_file, 'file_name': file_name,
                'chat_id': message_obj_for_reply.chat.id, 'script_owner_id': script_owner_id,
                'start_time': datetime.now(), 'user_folder': user_folder,
                'type': 'py', 'script_key': script_key
            }
            reply_premium(message_obj_for_reply,
                          f"✅ Python script '{file_name}' started!\n🆔 PID: <code>{process.pid}</code>")
        except FileNotFoundError:
            reply_premium(message_obj_for_reply, "❌ Python interpreter not found.")
            if log_file and not log_file.closed:
                log_file.close()
            if script_key in bot_scripts:
                del bot_scripts[script_key]
        except Exception as e:
            if log_file and not log_file.closed:
                log_file.close()
            reply_premium(message_obj_for_reply, f"❌ Failed to start script: {str(e)}")
            if process and process.poll() is None:
                kill_process_tree({'process': process, 'log_file': log_file, 'script_key': script_key})
            if script_key in bot_scripts:
                del bot_scripts[script_key]
    except Exception as e:
        logger.error(f"Unexpected run_script error: {e}", exc_info=True)
        reply_premium(message_obj_for_reply, f"❌ Unexpected error: {str(e)}")
        if script_key in bot_scripts:
            kill_process_tree(bot_scripts[script_key])
            del bot_scripts[script_key]

def run_js_script(script_path, script_owner_id, user_folder, file_name, message_obj_for_reply, attempt=1):
    max_attempts = 2
    if attempt > max_attempts:
        reply_premium(message_obj_for_reply, f"❌ Failed to run '{file_name}' after {max_attempts} attempts.")
        return
    script_key = f"{script_owner_id}_{file_name}"
    logger.info(f"Attempt {attempt} to run JS script: {script_path} (Key: {script_key})")
    try:
        if not os.path.exists(script_path):
            reply_premium(message_obj_for_reply, f"❌ Script '{file_name}' not found!")
            if script_owner_id in user_files:
                user_files[script_owner_id] = [f for f in user_files.get(script_owner_id, []) if f[0] != file_name]
            remove_user_file_db(script_owner_id, file_name)
            return

        if attempt == 1:
            check_command = ['node', script_path]
            check_proc = None
            try:
                check_proc = subprocess.Popen(check_command, cwd=user_folder,
                                              stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                              text=True, encoding='utf-8', errors='replace',
                                              env={**os.environ, "PYTHONIOENCODING": "utf-8"})
                stdout, stderr = check_proc.communicate(timeout=5)
                return_code = check_proc.returncode
                if return_code != 0 and stderr:
                    match_js = re.search(r"Cannot find module '(.+?)'", stderr)
                    if match_js:
                        module_name = match_js.group(1).strip()
                        if not module_name.startswith('.') and not module_name.startswith('/'):
                            if attempt_install_npm(module_name, user_folder, message_obj_for_reply):
                                reply_premium(message_obj_for_reply, f"🔄 Retrying '{file_name}'...")
                                time.sleep(2)
                                threading.Thread(target=run_js_script, args=(
                                    script_path, script_owner_id, user_folder, file_name,
                                    message_obj_for_reply, attempt + 1)).start()
                                return
                            else:
                                reply_premium(message_obj_for_reply, f"❌ Failed to install '{module_name}'")
                                return
                    error_summary = stderr[:500]
                    reply_premium(message_obj_for_reply, f"❌ JS Script Error:\n<pre>{error_summary}</pre>")
                    return
            except subprocess.TimeoutExpired:
                if check_proc and check_proc.poll() is None:
                    check_proc.kill()
                    check_proc.communicate()
            except FileNotFoundError:
                reply_premium(message_obj_for_reply, "❌ Node.js not installed.")
                return
            except Exception as e:
                reply_premium(message_obj_for_reply, f"❌ JS pre-check error: {str(e)}")
                return
            finally:
                if check_proc and check_proc.poll() is None:
                    check_proc.kill()
                    check_proc.communicate()

        log_file_path = os.path.join(user_folder, f"{os.path.splitext(file_name)[0]}.log")
        log_file = None
        process = None
        try:
            log_file = open(log_file_path, 'w', encoding='utf-8', errors='replace')
        except Exception as e:
            reply_premium(message_obj_for_reply, f"❌ Failed to open log file: {str(e)}")
            return
        try:
            startupinfo = None
            creationflags = 0
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
            process = subprocess.Popen(['node', script_path], cwd=user_folder,
                                       stdout=log_file, stderr=log_file, stdin=subprocess.PIPE,
                                       startupinfo=startupinfo, creationflags=creationflags,
                                       text=True, encoding='utf-8', errors='replace',
                                       env={**os.environ, "PYTHONIOENCODING": "utf-8"})
            bot_scripts[script_key] = {
                'process': process, 'log_file': log_file, 'file_name': file_name,
                'chat_id': message_obj_for_reply.chat.id, 'script_owner_id': script_owner_id,
                'start_time': datetime.now(), 'user_folder': user_folder,
                'type': 'js', 'script_key': script_key
            }
            reply_premium(message_obj_for_reply,
                          f"✅ JS script '{file_name}' started!\n🆔 PID: <code>{process.pid}</code>")
        except FileNotFoundError:
            reply_premium(message_obj_for_reply, "❌ Node.js not installed.")
            if log_file and not log_file.closed:
                log_file.close()
            if script_key in bot_scripts:
                del bot_scripts[script_key]
        except Exception as e:
            if log_file and not log_file.closed:
                log_file.close()
            reply_premium(message_obj_for_reply, f"❌ Failed to start JS script: {str(e)}")
            if process and process.poll() is None:
                kill_process_tree({'process': process, 'log_file': log_file, 'script_key': script_key})
            if script_key in bot_scripts:
                del bot_scripts[script_key]
    except Exception as e:
        logger.error(f"Unexpected run_js_script error: {e}", exc_info=True)
        reply_premium(message_obj_for_reply, f"❌ Unexpected JS error: {str(e)}")
        if script_key in bot_scripts:
            kill_process_tree(bot_scripts[script_key])
            del bot_scripts[script_key]

# --- Map Telegram import names to actual PyPI package names ---
TELEGRAM_MODULES = {
    'telebot': 'pyTelegramBotAPI',
    'telegram': 'python-telegram-bot',
    'python_telegram_bot': 'python-telegram-bot',
    'aiogram': 'aiogram',
    'pyrogram': 'pyrogram',
    'telethon': 'telethon',
    'telethon.sync': 'telethon',
    'telepot': 'telepot',
    'tgcrypto': 'tgcrypto',
    'telegram_upload': 'telegram-upload',
    'telegram_send': 'telegram-send',
    'telegram_text': 'telegram-text',
    'mtproto': 'telegram-mtproto',
    'tl': 'telethon',
    'telegram_utils': 'telegram-utils',
    'telegram_logger': 'telegram-logger',
    'telegram_handlers': 'python-telegram-handlers',
    'telegram_redis': 'telegram-redis',
    'telegram_sqlalchemy': 'telegram-sqlalchemy',
    'telegram_payment': 'telegram-payment',
    'telegram_shop': 'telegram-shop-sdk',
    'telegram_debug': 'telegram-debug',
    'telegram_scraper': 'telegram-scraper',
    'telegram_analytics': 'telegram-analytics',
    'telegram_nlp': 'telegram-nlp-toolkit',
    'telegram_ai': 'telegram-ai',
    'telegram_api': 'telegram-api-client',
    'telegram_web': 'telegram-web-integration',
    'telegram_games': 'telegram-games',
    'telegram_quiz': 'telegram-quiz-bot',
    'telegram_ffmpeg': 'telegram-ffmpeg',
    'telegram_media': 'telegram-media-utils',
    'telegram_2fa': 'telegram-twofa',
    'telegram_crypto': 'telegram-crypto-bot',
    'telegram_i18n': 'telegram-i18n',
    'telegram_translate': 'telegram-translate',
    'bs4': 'beautifulsoup4',
    'requests': 'requests',
    'pillow': 'Pillow',
    'cv2': 'opencv-python',
    'yaml': 'PyYAML',
    'dotenv': 'python-dotenv',
    'dateutil': 'python-dateutil',
    'pandas': 'pandas',
    'numpy': 'numpy',
    'flask': 'Flask',
    'django': 'Django',
    'sqlalchemy': 'SQLAlchemy',
    'asyncio': None, 'json': None, 'datetime': None, 'os': None, 'sys': None,
    're': None, 'time': None, 'math': None, 'random': None, 'logging': None,
    'threading': None, 'subprocess': None, 'zipfile': None, 'tempfile': None,
    'shutil': None, 'sqlite3': None, 'psutil': 'psutil', 'atexit': None
}

# --- Database Operations ---
DB_LOCK = threading.Lock()

def save_user_file(user_id, file_name, file_type='py'):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            c.execute('INSERT OR REPLACE INTO user_files (user_id, file_name, file_type) VALUES (?, ?, ?)',
                      (user_id, file_name, file_type))
            conn.commit()
            if user_id not in user_files: user_files[user_id] = []
            user_files[user_id] = [(fn, ft) for fn, ft in user_files[user_id] if fn != file_name]
            user_files[user_id].append((file_name, file_type))
        except Exception as e:
            logger.error(f"❌ Error saving file for {user_id}, {file_name}: {e}")
        finally:
            conn.close()

def remove_user_file_db(user_id, file_name):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            c.execute('DELETE FROM user_files WHERE user_id = ? AND file_name = ?', (user_id, file_name))
            conn.commit()
            if user_id in user_files:
                user_files[user_id] = [f for f in user_files[user_id] if f[0] != file_name]
                if not user_files[user_id]: del user_files[user_id]
        except Exception as e:
            logger.error(f"❌ Error removing file for {user_id}, {file_name}: {e}")
        finally:
            conn.close()

def add_active_user(user_id):
    active_users.add(user_id)
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            c.execute('INSERT OR IGNORE INTO active_users (user_id) VALUES (?)', (user_id,))
            conn.commit()
        except Exception as e:
            logger.error(f"❌ Error adding active user {user_id}: {e}")
        finally:
            conn.close()

def save_subscription(user_id, expiry):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            expiry_str = expiry.isoformat()
            c.execute('INSERT OR REPLACE INTO subscriptions (user_id, expiry) VALUES (?, ?)', (user_id, expiry_str))
            conn.commit()
            user_subscriptions[user_id] = {'expiry': expiry}
        except Exception as e:
            logger.error(f"❌ Error saving subscription for {user_id}: {e}")
        finally:
            conn.close()

def remove_subscription_db(user_id):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            c.execute('DELETE FROM subscriptions WHERE user_id = ?', (user_id,))
            conn.commit()
            if user_id in user_subscriptions: del user_subscriptions[user_id]
        except Exception as e:
            logger.error(f"❌ Error removing subscription for {user_id}: {e}")
        finally:
            conn.close()

def add_admin_db(admin_id):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            c.execute('INSERT OR IGNORE INTO admins (user_id) VALUES (?)', (admin_id,))
            conn.commit()
            admin_ids.add(admin_id)
        except Exception as e:
            logger.error(f"❌ Error adding admin {admin_id}: {e}")
        finally:
            conn.close()

def remove_admin_db(admin_id):
    if admin_id == OWNER_ID:
        return False
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        removed = False
        try:
            c.execute('SELECT 1 FROM admins WHERE user_id = ?', (admin_id,))
            if c.fetchone():
                c.execute('DELETE FROM admins WHERE user_id = ?', (admin_id,))
                conn.commit()
                removed = c.rowcount > 0
                if removed: admin_ids.discard(admin_id)
            else:
                admin_ids.discard(admin_id)
            return removed
        except Exception as e:
            logger.error(f"❌ Error removing admin {admin_id}: {e}")
            return False
        finally:
            conn.close()

# --- Menu creation ---
def create_main_menu_inline(user_id):
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = [
        types.InlineKeyboardButton('📢 Updates Channel', url=UPDATE_CHANNEL),
        types.InlineKeyboardButton('📤 Upload File', callback_data='upload'),
        types.InlineKeyboardButton('📂 Check Files', callback_data='check_files'),
        types.InlineKeyboardButton('⚡ Bot Speed', callback_data='speed'),
        types.InlineKeyboardButton('📤 Send Command', callback_data='send_command'),
        types.InlineKeyboardButton('📞 Contact Owner', url=f'https://t.me/{YOUR_USERNAME.replace("@", "")}')
    ]
    if user_id in admin_ids:
        admin_buttons = [
            types.InlineKeyboardButton('💳 Subscriptions', callback_data='subscription'),
            types.InlineKeyboardButton('📊 Statistics', callback_data='stats'),
            types.InlineKeyboardButton('🔒 Lock Bot' if not bot_locked else '🔓 Unlock Bot',
                                     callback_data='lock_bot' if not bot_locked else 'unlock_bot'),
            types.InlineKeyboardButton('📢 Broadcast', callback_data='broadcast'),
            types.InlineKeyboardButton('👑 Admin Panel', callback_data='admin_panel'),
            types.InlineKeyboardButton('🟢 Run All User Scripts', callback_data='run_all_scripts')
        ]
        markup.add(buttons[0])
        markup.add(buttons[1], buttons[2])
        markup.add(buttons[3], admin_buttons[0])
        markup.add(admin_buttons[1], admin_buttons[3])
        markup.add(admin_buttons[2], admin_buttons[5])
        markup.add(buttons[4])
        markup.add(admin_buttons[4])
        markup.add(buttons[5])
    else:
        markup.add(buttons[0])
        markup.add(buttons[1], buttons[2])
        markup.add(buttons[3])
        markup.add(buttons[4])
        markup.add(types.InlineKeyboardButton('📊 Statistics', callback_data='stats'))
        markup.add(buttons[5])
    return markup

def create_reply_keyboard_main_menu(user_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    layout_to_use = ADMIN_COMMAND_BUTTONS_LAYOUT_USER_SPEC if user_id in admin_ids else COMMAND_BUTTONS_LAYOUT_USER_SPEC
    for row_buttons_text in layout_to_use:
        markup.add(*[types.KeyboardButton(text) for text in row_buttons_text])
    return markup

def create_control_buttons(script_owner_id, file_name, is_running=True):
    markup = types.InlineKeyboardMarkup(row_width=2)
    if is_running:
        markup.row(
            types.InlineKeyboardButton("🔴 Stop", callback_data=f'stop_{script_owner_id}_{file_name}'),
            types.InlineKeyboardButton("🔄 Restart", callback_data=f'restart_{script_owner_id}_{file_name}')
        )
        markup.row(
            types.InlineKeyboardButton("🗑️ Delete", callback_data=f'delete_{script_owner_id}_{file_name}'),
            types.InlineKeyboardButton("📜 Logs", callback_data=f'logs_{script_owner_id}_{file_name}')
        )
    else:
        markup.row(
            types.InlineKeyboardButton("🟢 Start", callback_data=f'start_{script_owner_id}_{file_name}'),
            types.InlineKeyboardButton("🗑️ Delete", callback_data=f'delete_{script_owner_id}_{file_name}')
        )
        markup.row(
            types.InlineKeyboardButton("📜 View Logs", callback_data=f'logs_{script_owner_id}_{file_name}')
        )
    markup.add(types.InlineKeyboardButton("🔙 Back to Files", callback_data='check_files'))
    return markup

def create_admin_panel():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.row(
        types.InlineKeyboardButton('➕ Add Admin', callback_data='add_admin'),
        types.InlineKeyboardButton('➖ Remove Admin', callback_data='remove_admin')
    )
    markup.row(types.InlineKeyboardButton('📋 List Admins', callback_data='list_admins'))
    markup.row(types.InlineKeyboardButton('🔙 Back to Main', callback_data='back_to_main'))
    return markup

def create_subscription_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.row(
        types.InlineKeyboardButton('➕ Add Subscription', callback_data='add_subscription'),
        types.InlineKeyboardButton('➖ Remove Subscription', callback_data='remove_subscription')
    )
    markup.row(types.InlineKeyboardButton('🔍 Check Subscription', callback_data='check_subscription'))
    markup.row(types.InlineKeyboardButton('🔙 Back to Main', callback_data='back_to_main'))
    return markup

def create_send_command_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.row(
        types.InlineKeyboardButton('📝 Send to Process', callback_data='send_to_process'),
        types.InlineKeyboardButton('🔍 View All Logs', callback_data='view_all_logs')
    )
    markup.row(types.InlineKeyboardButton('🔙 Back to Main', callback_data='back_to_main'))
    return markup

# --- File Handling ---
def handle_zip_file(downloaded_file_content, file_name_zip, message):
    user_id = message.from_user.id
    user_folder = get_user_folder(user_id)
    temp_dir = None
    if user_id != OWNER_ID:
        is_safe, reason = scan_file_for_malware(downloaded_file_content, file_name_zip, user_id)
        if not is_safe:
            reply_premium(message, f"🚨 Security Alert: {reason}\nOnly owner can upload this type of file.")
            return
    try:
        temp_dir = tempfile.mkdtemp(prefix=f"user_{user_id}_zip_")
        zip_path = os.path.join(temp_dir, file_name_zip)
        with open(zip_path, 'wb') as new_file:
            new_file.write(downloaded_file_content)
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            if user_id != OWNER_ID:
                for member in zip_ref.infolist():
                    member_name_lower = member.filename.lower()
                    suspicious_extensions = ['.exe', '.dll', '.bat', '.cmd', '.scr', '.com']
                    if any(member_name_lower.endswith(ext) for ext in suspicious_extensions):
                        reply_premium(message, f"🚨 Security Alert: ZIP contains suspicious file: {member.filename}")
                        return
                    member_path = os.path.abspath(os.path.join(temp_dir, member.filename))
                    if not member_path.startswith(os.path.abspath(temp_dir)):
                        raise zipfile.BadZipFile(f"Zip has unsafe path: {member.filename}")
            zip_ref.extractall(temp_dir)

        target_dir = temp_dir
        root_files = os.listdir(target_dir)
        if not any(f.endswith(('.py', '.js')) for f in root_files):
            for root, dirs, files in os.walk(temp_dir):
                dirs[:] = [d for d in dirs if not d.startswith('.') and not d.startswith('__')]
                if any(f.endswith(('.py', '.js')) for f in files):
                    target_dir = root
                    break

        if target_dir != temp_dir:
            for item in os.listdir(target_dir):
                s = os.path.join(target_dir, item)
                d = os.path.join(temp_dir, item)
                if os.path.exists(d):
                    if os.path.isdir(d): shutil.rmtree(d)
                    else: os.remove(d)
                shutil.move(s, d)
            extracted_items = os.listdir(temp_dir)
        else:
            extracted_items = root_files

        py_files = [f for f in extracted_items if f.endswith('.py')]
        js_files = [f for f in extracted_items if f.endswith('.js')]
        req_file = 'requirements.txt' if 'requirements.txt' in extracted_items else None
        pkg_json = 'package.json' if 'package.json' in extracted_items else None

        if req_file:
            req_path = os.path.join(temp_dir, req_file)
            reply_premium(message, f"🔄 Installing Python deps from <code>{req_file}</code>...")
            try:
                command = [sys.executable, '-m', 'pip', 'install', '-r', req_path]
                result = subprocess.run(command, capture_output=True, text=True, check=True, encoding='utf-8', errors='ignore')
                reply_premium(message, f"✅ Python deps from <code>{req_file}</code> installed.")
            except subprocess.CalledProcessError as e:
                error_msg = f"❌ Failed to install Python deps.\n<pre>{(e.stderr or e.stdout)[:3500]}</pre>"
                reply_premium(message, error_msg)
                return
            except Exception as e:
                reply_premium(message, f"❌ Unexpected error installing Python deps: {str(e)}")
                return

        if pkg_json:
            reply_premium(message, f"🔄 Installing Node deps from <code>{pkg_json}</code>...")
            try:
                command = ['npm', 'install']
                result = subprocess.run(command, capture_output=True, text=True, check=True, cwd=temp_dir, encoding='utf-8', errors='ignore')
                reply_premium(message, f"✅ Node deps from <code>{pkg_json}</code> installed.")
            except FileNotFoundError:
                reply_premium(message, "❌ 'npm' not found. Cannot install Node deps.")
                return
            except subprocess.CalledProcessError as e:
                error_msg = f"❌ Failed to install Node deps.\n<pre>{(e.stderr or e.stdout)[:3500]}</pre>"
                reply_premium(message, error_msg)
                return
            except Exception as e:
                reply_premium(message, f"❌ Unexpected error installing Node deps: {str(e)}")
                return

        main_script_name = None
        file_type = None
        preferred_py = ['main.py', 'bot.py', 'app.py']
        preferred_js = ['index.js', 'main.js', 'bot.js', 'app.js']
        for p in preferred_py:
            if p in py_files:
                main_script_name = p
                file_type = 'py'
                break
        if not main_script_name:
            for p in preferred_js:
                if p in js_files:
                    main_script_name = p
                    file_type = 'js'
                    break
        if not main_script_name:
            if py_files:
                main_script_name = py_files[0]
                file_type = 'py'
            elif js_files:
                main_script_name = js_files[0]
                file_type = 'js'
        if not main_script_name:
            reply_premium(message, "❌ No <code>.py</code> or <code>.js</code> script found in archive!")
            return

        for item_name in os.listdir(temp_dir):
            if item_name == file_name_zip: continue
            src_path = os.path.join(temp_dir, item_name)
            dest_path = os.path.join(user_folder, item_name)
            if os.path.isdir(dest_path): shutil.rmtree(dest_path)
            elif os.path.exists(dest_path): os.remove(dest_path)
            shutil.move(src_path, dest_path)

        save_user_file(user_id, main_script_name, file_type)
        main_script_path = os.path.join(user_folder, main_script_name)
        reply_premium(message, f"✅ Files extracted. Starting main script: <code>{main_script_name}</code>...")

        if file_type == 'py':
            threading.Thread(target=run_script, args=(main_script_path, user_id, user_folder, main_script_name, message)).start()
        elif file_type == 'js':
            threading.Thread(target=run_js_script, args=(main_script_path, user_id, user_folder, main_script_name, message)).start()

    except zipfile.BadZipFile as e:
        reply_premium(message, f"❌ Invalid/corrupted ZIP. {str(e)}")
    except Exception as e:
        reply_premium(message, f"❌ Error processing zip: {str(e)}")
    finally:
        if temp_dir and os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
            except Exception:
                pass

def handle_js_file(file_path, script_owner_id, user_folder, file_name, message):
    try:
        save_user_file(script_owner_id, file_name, 'js')
        threading.Thread(target=run_js_script, args=(file_path, script_owner_id, user_folder, file_name, message)).start()
    except Exception as e:
        reply_premium(message, f"❌ Error processing JS file: {str(e)}")

def handle_py_file(file_path, script_owner_id, user_folder, file_name, message):
    try:
        save_user_file(script_owner_id, file_name, 'py')
        threading.Thread(target=run_script, args=(file_path, script_owner_id, user_folder, file_name, message)).start()
    except Exception as e:
        reply_premium(message, f"❌ Error processing Python file: {str(e)}")

# --- Send Command ---
def _logic_send_command(message):
    user_id = message.from_user.id
    if bot_locked and user_id not in admin_ids:
        reply_premium(message, "⚠️ Bot locked by admin.")
        return
    reply_premium(message, "📤 Send Command Options:", reply_markup=create_send_command_menu())

def send_to_process_init(message):
    user_id = message.from_user.id
    user_running_scripts = []
    for script_key, script_info in bot_scripts.items():
        script_owner_id = script_info['script_owner_id']
        if (user_id == script_owner_id or user_id in admin_ids) and is_bot_running(script_owner_id, script_info['file_name']):
            user_running_scripts.append((script_key, script_info))
    if not user_running_scripts:
        reply_premium(message, "❌ No running scripts found.")
        return
    markup = types.InlineKeyboardMarkup(row_width=1)
    for script_key, script_info in user_running_scripts:
        btn_text = f"{script_info['file_name']} (User: {script_info['script_owner_id']})"
        markup.add(types.InlineKeyboardButton(btn_text, callback_data=f'sendcmd_select_{script_key}'))
    markup.add(types.InlineKeyboardButton("🔙 Back", callback_data='send_command'))
    reply_premium(message, "📝 Select a running script to send command to:", reply_markup=markup)

def process_send_command(message, script_key):
    if script_key not in bot_scripts:
        reply_premium(message, "❌ Script no longer running.")
        return
    script_info = bot_scripts[script_key]
    command_text = message.text
    try:
        process = script_info['process']
        if process and process.poll() is None:
            process.stdin.write(command_text + '\n')
            process.stdin.flush()
            reply_premium(message, f"✅ Command sent to <code>{script_info['file_name']}</code>:\n<code>{command_text}</code>")
            time.sleep(1)
            if process.poll() is not None:
                reply_premium(message, f"⚠️ Script <code>{script_info['file_name']}</code> stopped after receiving command.")
        else:
            reply_premium(message, f"❌ Script <code>{script_info['file_name']}</code> is not running.")
    except Exception as e:
        reply_premium(message, f"❌ Error sending command: {str(e)}")

def view_all_logs(message):
    user_id = message.from_user.id
    user_logs = []
    user_folder = get_user_folder(user_id)
    if os.path.exists(user_folder):
        for file in os.listdir(user_folder):
            if file.endswith('.log'):
                log_path = os.path.join(user_folder, file)
                file_size = os.path.getsize(log_path)
                user_logs.append((file, file_size, log_path))
    if not user_logs:
        reply_premium(message, "📜 No log files found.")
        return
    markup = types.InlineKeyboardMarkup(row_width=1)
    for log_file, size, log_path in sorted(user_logs):
        size_kb = size / 1024
        btn_text = f"{log_file} ({size_kb:.1f} KB)"
        markup.add(types.InlineKeyboardButton(btn_text, callback_data=f'viewlog_{user_id}_{log_file}'))
    markup.add(types.InlineKeyboardButton("🔙 Back", callback_data='send_command'))
    reply_premium(message, "📜 Available Log Files:", reply_markup=markup)

def send_log_file(message, log_path, log_filename):
    try:
        file_size = os.path.getsize(log_path)
        if file_size > 50 * 1024 * 1024:
            reply_premium(message, f"❌ Log file too large ({file_size/1024/1024:.1f} MB). Maximum 50MB.")
            return
        with open(log_path, 'rb') as log_file:
            bot.send_document(message.chat.id, log_file, caption=f"📜 {log_filename}")
    except Exception as e:
        reply_premium(message, f"❌ Error sending log file: {str(e)}")

# --- Logic Functions ---
def _logic_send_welcome(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    user_name = message.from_user.first_name
    user_username = message.from_user.username
    logger.info(f"Welcome request from user_id: {user_id}, username: @{user_username}")

    if user_id not in admin_ids:
        if not is_user_joined_all(user_id):
            send_force_join_msg(chat_id)
            return

    if bot_locked and user_id not in admin_ids:
        send_premium(chat_id, "⚠️ Bot locked by admin. Try later.")
        return

    user_bio = "Could not fetch bio"
    photo_file_id = None
    try:
        user_bio = bot.get_chat(user_id).bio or "No bio"
    except Exception:
        pass
    try:
        user_profile_photos = bot.get_user_profile_photos(user_id, limit=1)
        if user_profile_photos.photos:
            photo_file_id = user_profile_photos.photos[0][-1].file_id
    except Exception:
        pass

    if user_id not in active_users:
        add_active_user(user_id)
        try:
            owner_notification = (f"🎉 New user!\n👤 Name: {user_name}\n✳️ User: @{user_username or 'N/A'}\n"
                                  f"🆔 ID: <code>{user_id}</code>\n📝 Bio: {user_bio}")
            send_premium(OWNER_ID, owner_notification)
            if photo_file_id:
                bot.send_photo(OWNER_ID, photo_file_id, caption=f"Pic of new user {user_id}")
        except Exception as e:
            logger.error(f"⚠️ Failed to notify owner about new user {user_id}: {e}")

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

    welcome_msg_text = (f"〽️ Welcome, {user_name}!\n\n"
                        f"🆔 Your User ID: <code>{user_id}</code>\n"
                        f"✳️ Username: <code>@{user_username or 'Not set'}</code>\n"
                        f"🔰 Your Status: {user_status}{expiry_info}\n"
                        f"📁 Files Uploaded: {current_files} / {limit_str}\n\n"
                        f"🤖 Host & run Python (<code>.py</code>) or JS (<code>.js</code>) scripts.\n"
                        f"   Upload single scripts or <code>.zip</code> archives.\n\n"
                        f"👇 Use buttons or type commands.")
    main_reply_markup = create_reply_keyboard_main_menu(user_id)
    try:
        if photo_file_id:
            bot.send_photo(chat_id, photo_file_id)
        send_premium(chat_id, welcome_msg_text, reply_markup=main_reply_markup)
    except Exception as e:
        logger.error(f"Error sending welcome to {user_id}: {e}", exc_info=True)
        try:
            send_premium(chat_id, welcome_msg_text, reply_markup=main_reply_markup)
        except Exception as fallback_e:
            logger.error(f"Fallback send_message failed for {user_id}: {fallback_e}")

def _logic_updates_channel(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('📢 Updates Channel', url=UPDATE_CHANNEL))
    reply_premium(message, "Visit our Updates Channel:", reply_markup=markup)

def _logic_upload_file(message):
    user_id = message.from_user.id
    if bot_locked and user_id not in admin_ids:
        reply_premium(message, "⚠️ Bot locked by admin, cannot accept files.")
        return
    file_limit = get_user_file_limit(user_id)
    current_files = get_user_file_count(user_id)
    if current_files >= file_limit:
        limit_str = str(file_limit) if file_limit != float('inf') else "Unlimited"
        reply_premium(message, f"⚠️ File limit ({current_files}/{limit_str}) reached. Delete files first.")
        return
    reply_premium(message, "📤 Send your Python (<code>.py</code>), JS (<code>.js</code>), or ZIP (<code>.zip</code>) file.")

def _logic_check_files(message):
    user_id = message.from_user.id
    user_files_list = user_files.get(user_id, [])
    if not user_files_list:
        reply_premium(message, "📂 Your files:\n\n(No files uploaded yet)")
        return
    markup = types.InlineKeyboardMarkup(row_width=1)
    for file_name, file_type in sorted(user_files_list):
        is_running = is_bot_running(user_id, file_name)
        status_icon = "🟢 Running" if is_running else "🔴 Stopped"
        btn_text = f"{file_name} ({file_type}) - {status_icon}"
        markup.add(types.InlineKeyboardButton(btn_text, callback_data=f'file_{user_id}_{file_name}'))
    reply_premium(message, "📂 Your files:\nClick to manage.", reply_markup=markup)

def _logic_bot_speed(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    start_time_ping = time.time()
    wait_msg = reply_premium(message, "🏃 Testing speed...")
    try:
        bot.send_chat_action(chat_id, 'typing')
        response_time = round((time.time() - start_time_ping) * 1000, 2)
        status = "🔓 Unlocked" if not bot_locked else "🔒 Locked"
        if user_id == OWNER_ID:
            user_level = "🤍 Owner"
        elif user_id in admin_ids:
            user_level = "🌙 Admin"
        elif user_id in user_subscriptions and user_subscriptions[user_id].get('expiry', datetime.min) > datetime.now():
            user_level = "⭐ Premium"
        else:
            user_level = "🆓 Free User"
        speed_msg = (f"⚡ Bot Speed & Status:\n\n"
                     f"⏱️ API Response Time: {response_time} ms\n"
                     f"🚦 Bot Status: {status}\n"
                     f"👤 Your Level: {user_level}")
        if wait_msg:
            edit_premium(chat_id, wait_msg.message_id, speed_msg)
    except Exception as e:
        logger.error(f"Error during speed test: {e}", exc_info=True)
        if wait_msg:
            edit_premium(chat_id, wait_msg.message_id, "❌ Error during speed test.")

def _logic_contact_owner(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('📞 Contact Owner', url=f'https://t.me/{YOUR_USERNAME.replace("@", "")}'))
    reply_premium(message, "Click to contact Owner:", reply_markup=markup)

def _logic_subscriptions_panel(message):
    if message.from_user.id not in admin_ids:
        reply_premium(message, "⚠️ Admin permissions required.")
        return
    reply_premium(message, "💳 Subscription Management\nUse inline buttons.", reply_markup=create_subscription_menu())

def _logic_statistics(message):
    user_id = message.from_user.id
    total_users = len(active_users)
    total_files_records = sum(len(files) for files in user_files.values())
    running_bots_count = 0
    user_running_bots = 0
    for script_key_iter, script_info_iter in list(bot_scripts.items()):
        s_owner_id, _ = script_key_iter.split('_', 1)
        if is_bot_running(int(s_owner_id), script_info_iter['file_name']):
            running_bots_count += 1
            if int(s_owner_id) == user_id:
                user_running_bots += 1
    stats_msg_base = (f"📊 Bot Statistics:\n\n"
                      f"👥 Total Users: {total_users}\n"
                      f"📂 Total File Records: {total_files_records}\n"
                      f"🟢 Total Active Bots: {running_bots_count}\n")
    if user_id in admin_ids:
        stats_msg_admin = (f"🔒 Bot Status: {'🔴 Locked' if bot_locked else '🟢 Unlocked'}\n"
                           f"🤖 Your Running Bots: {user_running_bots}")
        stats_msg = stats_msg_base + stats_msg_admin
    else:
        stats_msg = stats_msg_base + f"🤖 Your Running Bots: {user_running_bots}"
    reply_premium(message, stats_msg)

def _logic_broadcast_init(message):
    if message.from_user.id not in admin_ids:
        reply_premium(message, "⚠️ Admin permissions required.")
        return
    msg = reply_premium(message, "📢 Send message to broadcast to all active users.\n/cancel to abort.")
    bot.register_next_step_handler(msg, process_broadcast_message)

def _logic_toggle_lock_bot(message):
    if message.from_user.id not in admin_ids:
        reply_premium(message, "⚠️ Admin permissions required.")
        return
    global bot_locked
    bot_locked = not bot_locked
    status = "locked" if bot_locked else "unlocked"
    logger.warning(f"Bot {status} by Admin {message.from_user.id}")
    reply_premium(message, f"🔒 Bot has been {status}.")

def _logic_admin_panel(message):
    if message.from_user.id not in admin_ids:
        reply_premium(message, "⚠️ Admin permissions required.")
        return
    reply_premium(message, "👑 Admin Panel\nManage admins.", reply_markup=create_admin_panel())

def _logic_run_all_scripts(message_or_call):
    if isinstance(message_or_call, telebot.types.Message):
        admin_user_id = message_or_call.from_user.id
        admin_chat_id = message_or_call.chat.id
        reply_func = lambda text, **kwargs: reply_premium(message_or_call, text, **kwargs)
        admin_message_obj_for_script_runner = message_or_call
    elif isinstance(message_or_call, telebot.types.CallbackQuery):
        admin_user_id = message_or_call.from_user.id
        admin_chat_id = message_or_call.message.chat.id
        bot.answer_callback_query(message_or_call.id)
        reply_func = lambda text, **kwargs: send_premium(admin_chat_id, text, **kwargs)
        admin_message_obj_for_script_runner = message_or_call.message
    else:
        return

    if admin_user_id not in admin_ids:
        reply_func("⚠️ Admin permissions required.")
        return

    reply_func("⏳ Starting process to run all user scripts...")
    logger.info(f"Admin {admin_user_id} initiated 'run all scripts'.")

    started_count = 0
    attempted_users = 0
    skipped_files = 0
    error_files_details = []
    all_user_files_snapshot = dict(user_files)

    for target_user_id, files_for_user in all_user_files_snapshot.items():
        if not files_for_user:
            continue
        attempted_users += 1
        user_folder = get_user_folder(target_user_id)
        for file_name, file_type in files_for_user:
            if not is_bot_running(target_user_id, file_name):
                file_path = os.path.join(user_folder, file_name)
                if os.path.exists(file_path):
                    try:
                        if file_type == 'py':
                            threading.Thread(target=run_script, args=(
                                file_path, target_user_id, user_folder, file_name,
                                admin_message_obj_for_script_runner)).start()
                            started_count += 1
                        elif file_type == 'js':
                            threading.Thread(target=run_js_script, args=(
                                file_path, target_user_id, user_folder, file_name,
                                admin_message_obj_for_script_runner)).start()
                            started_count += 1
                        else:
                            skipped_files += 1
                            error_files_details.append(f"<code>{file_name}</code> (U{target_user_id}) - Unknown type")
                        time.sleep(0.7)
                    except Exception as e:
                        logger.error(f"Queue start err '{file_name}': {e}")
                        error_files_details.append(f"<code>{file_name}</code> (U{target_user_id}) - Start error")
                        skipped_files += 1
                else:
                    error_files_details.append(f"<code>{file_name}</code> (U{target_user_id}) - File not found")
                    skipped_files += 1

    summary_msg = (f"✅ All Users' Scripts - Processing Complete:\n\n"
                   f"▶️ Attempted to start: {started_count} scripts.\n"
                   f"👥 Users processed: {attempted_users}.\n")
    if skipped_files > 0:
        summary_msg += f"⚠️ Skipped/Error files: {skipped_files}\n"
        if error_files_details:
            summary_msg += "Details (first 5):\n" + "\n".join([f"  - {err}" for err in error_files_details[:5]])
            if len(error_files_details) > 5:
                summary_msg += "\n  ... and more (check logs)."
    reply_func(summary_msg)
    logger.info(f"Run all scripts finished. Admin: {admin_user_id}. Started: {started_count}. Skipped: {skipped_files}")

# --- Command Handlers ---
@bot.message_handler(commands=['start', 'help'])
def command_send_welcome(message):
    _logic_send_welcome(message)

@bot.message_handler(commands=['status'])
def command_show_status(message):
    _logic_statistics(message)

BUTTON_TEXT_TO_LOGIC = {
    "📢 Updates Channel": _logic_updates_channel,
    "📤 Upload File": _logic_upload_file,
    "📂 Check Files": _logic_check_files,
    "⚡ Bot Speed": _logic_bot_speed,
    "📤 Send Command": _logic_send_command,
    "📞 Contact Owner": _logic_contact_owner,
    "📊 Statistics": _logic_statistics,
    "💳 Subscriptions": _logic_subscriptions_panel,
    "📢 Broadcast": _logic_broadcast_init,
    "🔒 Lock Bot": _logic_toggle_lock_bot,
    "🟢 Running All Code": _logic_run_all_scripts,
    "👑 Admin Panel": _logic_admin_panel,
}

@bot.message_handler(func=lambda message: message.text in BUTTON_TEXT_TO_LOGIC)
def handle_button_text(message):
    logic_func = BUTTON_TEXT_TO_LOGIC.get(message.text)
    if logic_func:
        logic_func(message)

@bot.message_handler(commands=['updateschannel'])
def command_updates_channel(message):
    _logic_updates_channel(message)

@bot.message_handler(commands=['uploadfile'])
def command_upload_file(message):
    _logic_upload_file(message)

@bot.message_handler(commands=['checkfiles'])
def command_check_files(message):
    _logic_check_files(message)

@bot.message_handler(commands=['botspeed'])
def command_bot_speed(message):
    _logic_bot_speed(message)

@bot.message_handler(commands=['sendcommand'])
def command_send_command(message):
    _logic_send_command(message)

@bot.message_handler(commands=['contactowner'])
def command_contact_owner(message):
    _logic_contact_owner(message)

@bot.message_handler(commands=['subscriptions'])
def command_subscriptions(message):
    _logic_subscriptions_panel(message)

@bot.message_handler(commands=['statistics'])
def command_statistics(message):
    _logic_statistics(message)

@bot.message_handler(commands=['broadcast'])
def command_broadcast(message):
    _logic_broadcast_init(message)

@bot.message_handler(commands=['lockbot'])
def command_lock_bot(message):
    _logic_toggle_lock_bot(message)

@bot.message_handler(commands=['adminpanel'])
def command_admin_panel(message):
    _logic_admin_panel(message)

@bot.message_handler(commands=['runningallcode'])
def command_run_all_code(message):
    _logic_run_all_scripts(message)

@bot.message_handler(commands=['ping'])
def ping(message):
    start_ping_time = time.time()
    msg = reply_premium(message, "Pong!")
    latency = round((time.time() - start_ping_time) * 1000, 2)
    if msg:
        edit_premium(message.chat.id, msg.message_id, f"Pong! Latency: {latency} ms")

# --- Document Handler ---
@bot.message_handler(content_types=['document'])
def handle_file_upload_doc(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    doc = message.document
    logger.info(f"Doc from {user_id}: {doc.file_name} ({doc.mime_type}), Size: {doc.file_size}")

    if bot_locked and user_id not in admin_ids:
        reply_premium(message, "⚠️ Bot locked, cannot accept files.")
        return

    file_limit = get_user_file_limit(user_id)
    current_files = get_user_file_count(user_id)
    if current_files >= file_limit:
        limit_str = str(file_limit) if file_limit != float('inf') else "Unlimited"
        reply_premium(message, f"⚠️ File limit ({current_files}/{limit_str}) reached. Delete files via /checkfiles.")
        return

    file_name = doc.file_name
    if not file_name:
        reply_premium(message, "⚠️ No file name. Ensure file has a name.")
        return
    file_ext = os.path.splitext(file_name)[1].lower()
    if file_ext not in ['.py', '.js', '.zip']:
        reply_premium(message, "⚠️ Unsupported type! Only <code>.py</code>, <code>.js</code>, <code>.zip</code> allowed.")
        return
    max_file_size = 20 * 1024 * 1024
    if doc.file_size > max_file_size:
        reply_premium(message, f"⚠️ File too large (Max: {max_file_size // 1024 // 1024} MB).")
        return

    try:
        try:
            bot.forward_message(OWNER_ID, chat_id, message.message_id)
            send_premium(OWNER_ID, f"⬆️ File '{file_name}' from {message.from_user.first_name} (<code>{user_id}</code>)")
        except Exception as e:
            logger.error(f"Failed to forward uploaded file to OWNER_ID {OWNER_ID}: {e}")

        download_wait_msg = reply_premium(message, f"⏳ Downloading <code>{file_name}</code>...")
        file_info_tg_doc = bot.get_file(doc.file_id)
        downloaded_file_content = bot.download_file(file_info_tg_doc.file_path)

        if user_id != OWNER_ID:
            is_safe, reason = scan_file_for_malware(downloaded_file_content, file_name, user_id)
            if not is_safe:
                if download_wait_msg:
                    edit_premium(chat_id, download_wait_msg.message_id, f"🚨 Security Alert: {reason}")
                return

        if download_wait_msg:
            edit_premium(chat_id, download_wait_msg.message_id, f"✅ Downloaded <code>{file_name}</code>. Processing...")
        logger.info(f"Downloaded {file_name} for user {user_id}")
        user_folder = get_user_folder(user_id)

        if file_ext == '.zip':
            handle_zip_file(downloaded_file_content, file_name, message)
        else:
            file_path = os.path.join(user_folder, file_name)
            with open(file_path, 'wb') as f:
                f.write(downloaded_file_content)
            logger.info(f"Saved single file to {file_path}")
            if file_ext == '.js':
                handle_js_file(file_path, user_id, user_folder, file_name, message)
            elif file_ext == '.py':
                handle_py_file(file_path, user_id, user_folder, file_name, message)
    except telebot.apihelper.ApiTelegramException as e:
        logger.error(f"Telegram API Error handling file for {user_id}: {e}", exc_info=True)
        if "file is too big" in str(e).lower():
            reply_premium(message, "❌ Telegram API Error: File too large to download (~20MB limit).")
        else:
            reply_premium(message, f"❌ Telegram API Error: {str(e)}. Try later.")
    except Exception as e:
        logger.error(f"❌ General error handling file for {user_id}: {e}", exc_info=True)
        reply_premium(message, f"❌ Unexpected error: {str(e)}")

# --- Callback Query Handlers ---
@bot.callback_query_handler(func=lambda call: call.data == "force_join_check")
def force_join_recheck(call):
    user_id = call.from_user.id
    if is_user_joined_all(user_id):
        bot.answer_callback_query(call.id, "✅ All channels verified!")
        _logic_send_welcome(call.message)
    else:
        bot.answer_callback_query(call.id, "❌ Sab channels join karo pehle", show_alert=True)

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    user_id = call.from_user.id
    data = call.data
    logger.info(f"Callback: User={user_id}, Data='{data}'")

    if bot_locked and user_id not in admin_ids and data not in ['back_to_main', 'speed', 'stats']:
        bot.answer_callback_query(call.id, "⚠️ Bot locked by admin.", show_alert=True)
        return
    try:
        if data == 'upload':
            upload_callback(call)
        elif data == 'check_files':
            check_files_callback(call)
        elif data.startswith('file_'):
            file_control_callback(call)
        elif data.startswith('start_'):
            start_bot_callback(call)
        elif data.startswith('stop_'):
            stop_bot_callback(call)
        elif data.startswith('restart_'):
            restart_bot_callback(call)
        elif data.startswith('delete_'):
            delete_bot_callback(call)
        elif data.startswith('logs_'):
            logs_bot_callback(call)
        elif data == 'speed':
            speed_callback(call)
        elif data == 'back_to_main':
            back_to_main_callback(call)
        elif data.startswith('confirm_broadcast_'):
            handle_confirm_broadcast(call)
        elif data == 'cancel_broadcast':
            handle_cancel_broadcast(call)
        elif data == 'send_command':
            send_command_callback(call)
        elif data == 'send_to_process':
            send_to_process_callback(call)
        elif data.startswith('sendcmd_select_'):
            sendcmd_select_callback(call)
        elif data == 'view_all_logs':
            view_all_logs_callback(call)
        elif data.startswith('viewlog_'):
            viewlog_callback(call)
        elif data == 'subscription':
            admin_required_callback(call, subscription_management_callback)
        elif data == 'stats':
            stats_callback(call)
        elif data == 'lock_bot':
            admin_required_callback(call, lock_bot_callback)
        elif data == 'unlock_bot':
            admin_required_callback(call, unlock_bot_callback)
        elif data == 'run_all_scripts':
            admin_required_callback(call, run_all_scripts_callback)
        elif data == 'broadcast':
            admin_required_callback(call, broadcast_init_callback)
        elif data == 'admin_panel':
            admin_required_callback(call, admin_panel_callback)
        elif data == 'add_admin':
            owner_required_callback(call, add_admin_init_callback)
        elif data == 'remove_admin':
            owner_required_callback(call, remove_admin_init_callback)
        elif data == 'list_admins':
            admin_required_callback(call, list_admins_callback)
        elif data == 'add_subscription':
            admin_required_callback(call, add_subscription_init_callback)
        elif data == 'remove_subscription':
            admin_required_callback(call, remove_subscription_init_callback)
        elif data == 'check_subscription':
            admin_required_callback(call, check_subscription_init_callback)
        else:
            bot.answer_callback_query(call.id, "Unknown action.")
    except Exception as e:
        logger.error(f"Error handling callback '{data}' for {user_id}: {e}", exc_info=True)
        try:
            bot.answer_callback_query(call.id, "Error processing request.", show_alert=True)
        except Exception:
            pass

def admin_required_callback(call, func_to_run):
    if call.from_user.id not in admin_ids:
        bot.answer_callback_query(call.id, "⚠️ Admin permissions required.", show_alert=True)
        return
    func_to_run(call)

def owner_required_callback(call, func_to_run):
    if call.from_user.id != OWNER_ID:
        bot.answer_callback_query(call.id, "⚠️ Owner permissions required.", show_alert=True)
        return
    func_to_run(call)

def send_command_callback(call):
    bot.answer_callback_query(call.id)
    edit_premium(call.message.chat.id, call.message.message_id,
                 "📤 Send Command Options:", reply_markup=create_send_command_menu())

def send_to_process_callback(call):
    bot.answer_callback_query(call.id)
    msg = send_premium(call.message.chat.id, "📝 Send the command you want to execute:")
    if msg:
        bot.register_next_step_handler(msg, lambda m: send_to_process_init(m))

def sendcmd_select_callback(call):
    try:
        script_key = call.data.replace('sendcmd_select_', '')
        bot.answer_callback_query(call.id, f"Selected script: {script_key}")
        msg = send_premium(call.message.chat.id, f"📝 Enter command to send to <code>{script_key}</code>:")
        if msg:
            bot.register_next_step_handler(msg, lambda m: process_send_command(m, script_key))
    except Exception as e:
        bot.answer_callback_query(call.id, "Error selecting script.")

def view_all_logs_callback(call):
    bot.answer_callback_query(call.id)
    view_all_logs(call.message)

def viewlog_callback(call):
    try:
        _, user_id_str, log_filename = call.data.split('_', 2)
        user_id = int(user_id_str)
        requesting_user_id = call.from_user.id
        if not (requesting_user_id == user_id or requesting_user_id in admin_ids):
            bot.answer_callback_query(call.id, "⚠️ You can only view your own logs.", show_alert=True)
            return
        user_folder = get_user_folder(user_id)
        log_path = os.path.join(user_folder, log_filename)
        if not os.path.exists(log_path):
            bot.answer_callback_query(call.id, "❌ Log file not found.", show_alert=True)
            return
        bot.answer_callback_query(call.id, "📜 Sending log file...")
        send_log_file(call.message, log_path, log_filename)
    except Exception as e:
        bot.answer_callback_query(call.id, "Error viewing log.")

def upload_callback(call):
    user_id = call.from_user.id
    file_limit = get_user_file_limit(user_id)
    current_files = get_user_file_count(user_id)
    if current_files >= file_limit:
        limit_str = str(file_limit) if file_limit != float('inf') else "Unlimited"
        bot.answer_callback_query(call.id, f"⚠️ File limit ({current_files}/{limit_str}) reached.", show_alert=True)
        return
    bot.answer_callback_query(call.id)
    send_premium(call.message.chat.id, "📤 Send your Python (<code>.py</code>), JS (<code>.js</code>), or ZIP (<code>.zip</code>) file.")

def check_files_callback(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    user_files_list = user_files.get(user_id, [])
    if not user_files_list:
        bot.answer_callback_query(call.id, "⚠️ No files uploaded.", show_alert=True)
        try:
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🔙 Back to Main", callback_data='back_to_main'))
            edit_premium(chat_id, call.message.message_id, "📂 Your files:\n\n(No files uploaded)", reply_markup=markup)
        except Exception:
            pass
        return
    bot.answer_callback_query(call.id)
    markup = types.InlineKeyboardMarkup(row_width=1)
    for file_name, file_type in sorted(user_files_list):
        is_running = is_bot_running(user_id, file_name)
        status_icon = "🟢 Running" if is_running else "🔴 Stopped"
        btn_text = f"{file_name} ({file_type}) - {status_icon}"
        markup.add(types.InlineKeyboardButton(btn_text, callback_data=f'file_{user_id}_{file_name}'))
    markup.add(types.InlineKeyboardButton("🔙 Back to Main", callback_data='back_to_main'))
    try:
        edit_premium(chat_id, call.message.message_id, "📂 Your files:\nClick to manage.", reply_markup=markup)
    except Exception:
        pass

def file_control_callback(call):
    try:
        _, script_owner_id_str, file_name = call.data.split('_', 2)
        script_owner_id = int(script_owner_id_str)
        requesting_user_id = call.from_user.id
        if not (requesting_user_id == script_owner_id or requesting_user_id in admin_ids):
            bot.answer_callback_query(call.id, "⚠️ You can only manage your own files.", show_alert=True)
            check_files_callback(call)
            return
        user_files_list = user_files.get(script_owner_id, [])
        if not any(f[0] == file_name for f in user_files_list):
            bot.answer_callback_query(call.id, "⚠️ File not found.", show_alert=True)
            check_files_callback(call)
            return
        bot.answer_callback_query(call.id)
        is_running = is_bot_running(script_owner_id, file_name)
        status_text = '🟢 Running' if is_running else '🔴 Stopped'
        file_type = next((f[1] for f in user_files_list if f[0] == file_name), '?')
        try:
            edit_premium(
                call.message.chat.id, call.message.message_id,
                f"⚙️ Controls for: <code>{file_name}</code> ({file_type}) of User <code>{script_owner_id}</code>\nStatus: {status_text}",
                reply_markup=create_control_buttons(script_owner_id, file_name, is_running)
            )
        except Exception:
            pass
    except Exception as e:
        logger.error(f"Error in file_control_callback: {e}", exc_info=True)
        bot.answer_callback_query(call.id, "An error occurred.", show_alert=True)

def start_bot_callback(call):
    try:
        _, script_owner_id_str, file_name = call.data.split('_', 2)
        script_owner_id = int(script_owner_id_str)
        requesting_user_id = call.from_user.id
        chat_id_for_reply = call.message.chat.id
        if not (requesting_user_id == script_owner_id or requesting_user_id in admin_ids):
            bot.answer_callback_query(call.id, "⚠️ Permission denied.", show_alert=True)
            return
        user_files_list = user_files.get(script_owner_id, [])
        file_info = next((f for f in user_files_list if f[0] == file_name), None)
        if not file_info:
            bot.answer_callback_query(call.id, "⚠️ File not found.", show_alert=True)
            check_files_callback(call)
            return
        file_type = file_info[1]
        user_folder = get_user_folder(script_owner_id)
        file_path = os.path.join(user_folder, file_name)
        if not os.path.exists(file_path):
            bot.answer_callback_query(call.id, f"⚠️ File missing! Re-upload.", show_alert=True)
            remove_user_file_db(script_owner_id, file_name)
            check_files_callback(call)
            return
        if is_bot_running(script_owner_id, file_name):
            bot.answer_callback_query(call.id, f"⚠️ Already running.", show_alert=True)
            try:
                bot.edit_message_reply_markup(chat_id_for_reply, call.message.message_id,
                                              reply_markup=create_control_buttons(script_owner_id, file_name, True))
            except Exception:
                pass
            return
        bot.answer_callback_query(call.id, f"⏳ Starting {file_name}...")
        if file_type == 'py':
            threading.Thread(target=run_script, args=(file_path, script_owner_id, user_folder, file_name, call.message)).start()
        elif file_type == 'js':
            threading.Thread(target=run_js_script, args=(file_path, script_owner_id, user_folder, file_name, call.message)).start()
        else:
            send_premium(chat_id_for_reply, f"❌ Unknown type '{file_type}'.")
            return
        time.sleep(1.5)
        is_now_running = is_bot_running(script_owner_id, file_name)
        status_text = '🟢 Running' if is_now_running else '🟡 Starting (or failed)'
        try:
            edit_premium(
                chat_id_for_reply, call.message.message_id,
                f"⚙️ Controls for: <code>{file_name}</code> ({file_type}) of User <code>{script_owner_id}</code>\nStatus: {status_text}",
                reply_markup=create_control_buttons(script_owner_id, file_name, is_now_running)
            )
        except Exception:
            pass
    except Exception as e:
        logger.error(f"Error in start_bot_callback: {e}", exc_info=True)
        bot.answer_callback_query(call.id, "Error starting.", show_alert=True)

def stop_bot_callback(call):
    try:
        _, script_owner_id_str, file_name = call.data.split('_', 2)
        script_owner_id = int(script_owner_id_str)
        requesting_user_id = call.from_user.id
        chat_id_for_reply = call.message.chat.id
        if not (requesting_user_id == script_owner_id or requesting_user_id in admin_ids):
            bot.answer_callback_query(call.id, "⚠️ Permission denied.", show_alert=True)
            return
        user_files_list = user_files.get(script_owner_id, [])
        file_info = next((f for f in user_files_list if f[0] == file_name), None)
        if not file_info:
            bot.answer_callback_query(call.id, "⚠️ File not found.", show_alert=True)
            check_files_callback(call)
            return
        file_type = file_info[1]
        script_key = f"{script_owner_id}_{file_name}"
        if not is_bot_running(script_owner_id, file_name):
            bot.answer_callback_query(call.id, f"⚠️ Already stopped.", show_alert=True)
            try:
                edit_premium(chat_id_for_reply, call.message.message_id,
                             f"⚙️ Controls for: <code>{file_name}</code> ({file_type})\nStatus: 🔴 Stopped",
                             reply_markup=create_control_buttons(script_owner_id, file_name, False))
            except Exception:
                pass
            return
        bot.answer_callback_query(call.id, f"⏳ Stopping {file_name}...")
        process_info = bot_scripts.get(script_key)
        if process_info:
            kill_process_tree(process_info)
            if script_key in bot_scripts:
                del bot_scripts[script_key]
        try:
            edit_premium(chat_id_for_reply, call.message.message_id,
                         f"⚙️ Controls for: <code>{file_name}</code> ({file_type})\nStatus: 🔴 Stopped",
                         reply_markup=create_control_buttons(script_owner_id, file_name, False))
        except Exception:
            pass
    except Exception as e:
        bot.answer_callback_query(call.id, "Error stopping.", show_alert=True)

def restart_bot_callback(call):
    try:
        _, script_owner_id_str, file_name = call.data.split('_', 2)
        script_owner_id = int(script_owner_id_str)
        requesting_user_id = call.from_user.id
        chat_id_for_reply = call.message.chat.id
        if not (requesting_user_id == script_owner_id or requesting_user_id in admin_ids):
            bot.answer_callback_query(call.id, "⚠️ Permission denied.", show_alert=True)
            return
        user_files_list = user_files.get(script_owner_id, [])
        file_info = next((f for f in user_files_list if f[0] == file_name), None)
        if not file_info:
            bot.answer_callback_query(call.id, "⚠️ File not found.", show_alert=True)
            check_files_callback(call)
            return
        file_type = file_info[1]
        user_folder = get_user_folder(script_owner_id)
        file_path = os.path.join(user_folder, file_name)
        script_key = f"{script_owner_id}_{file_name}"
        if not os.path.exists(file_path):
            bot.answer_callback_query(call.id, f"⚠️ File missing!", show_alert=True)
            remove_user_file_db(script_owner_id, file_name)
            if script_key in bot_scripts:
                del bot_scripts[script_key]
            check_files_callback(call)
            return
        bot.answer_callback_query(call.id, f"⏳ Restarting {file_name}...")
        if is_bot_running(script_owner_id, file_name):
            process_info = bot_scripts.get(script_key)
            if process_info:
                kill_process_tree(process_info)
            if script_key in bot_scripts:
                del bot_scripts[script_key]
            time.sleep(1.5)
        if file_type == 'py':
            threading.Thread(target=run_script, args=(file_path, script_owner_id, user_folder, file_name, call.message)).start()
        elif file_type == 'js':
            threading.Thread(target=run_js_script, args=(file_path, script_owner_id, user_folder, file_name, call.message)).start()
        else:
            send_premium(chat_id_for_reply, f"❌ Unknown type '{file_type}'.")
            return
        time.sleep(1.5)
        is_now_running = is_bot_running(script_owner_id, file_name)
        status_text = '🟢 Running' if is_now_running else '🟡 Starting'
        try:
            edit_premium(chat_id_for_reply, call.message.message_id,
                         f"⚙️ Controls for: <code>{file_name}</code> ({file_type})\nStatus: {status_text}",
                         reply_markup=create_control_buttons(script_owner_id, file_name, is_now_running))
        except Exception:
            pass
    except Exception as e:
        bot.answer_callback_query(call.id, "Error restarting.", show_alert=True)

def delete_bot_callback(call):
    try:
        _, script_owner_id_str, file_name = call.data.split('_', 2)
        script_owner_id = int(script_owner_id_str)
        requesting_user_id = call.from_user.id
        chat_id_for_reply = call.message.chat.id
        if not (requesting_user_id == script_owner_id or requesting_user_id in admin_ids):
            bot.answer_callback_query(call.id, "⚠️ Permission denied.", show_alert=True)
            return
        user_files_list = user_files.get(script_owner_id, [])
        if not any(f[0] == file_name for f in user_files_list):
            bot.answer_callback_query(call.id, "⚠️ File not found.", show_alert=True)
            check_files_callback(call)
            return
        bot.answer_callback_query(call.id, f"🗑️ Deleting {file_name}...")
        script_key = f"{script_owner_id}_{file_name}"
        if is_bot_running(script_owner_id, file_name):
            process_info = bot_scripts.get(script_key)
            if process_info:
                kill_process_tree(process_info)
            if script_key in bot_scripts:
                del bot_scripts[script_key]
            time.sleep(0.5)
        user_folder = get_user_folder(script_owner_id)
        file_path = os.path.join(user_folder, file_name)
        log_path = os.path.join(user_folder, f"{os.path.splitext(file_name)[0]}.log")
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except OSError:
                pass
        if os.path.exists(log_path):
            try:
                os.remove(log_path)
            except OSError:
                pass
        remove_user_file_db(script_owner_id, file_name)
        try:
            edit_premium(chat_id_for_reply, call.message.message_id,
                         f"🗑️ Record <code>{file_name}</code> (User <code>{script_owner_id}</code>) deleted!",
                         reply_markup=None)
        except Exception:
            send_premium(chat_id_for_reply, f"🗑️ Record <code>{file_name}</code> deleted.")
    except Exception as e:
        bot.answer_callback_query(call.id, "Error deleting.", show_alert=True)

def logs_bot_callback(call):
    try:
        _, script_owner_id_str, file_name = call.data.split('_', 2)
        script_owner_id = int(script_owner_id_str)
        requesting_user_id = call.from_user.id
        chat_id_for_reply = call.message.chat.id
        if not (requesting_user_id == script_owner_id or requesting_user_id in admin_ids):
            bot.answer_callback_query(call.id, "⚠️ Permission denied.", show_alert=True)
            return
        user_files_list = user_files.get(script_owner_id, [])
        if not any(f[0] == file_name for f in user_files_list):
            bot.answer_callback_query(call.id, "⚠️ File not found.", show_alert=True)
            check_files_callback(call)
            return
        user_folder = get_user_folder(script_owner_id)
        log_path = os.path.join(user_folder, f"{os.path.splitext(file_name)[0]}.log")
        if not os.path.exists(log_path):
            bot.answer_callback_query(call.id, f"⚠️ No logs for '{file_name}'.", show_alert=True)
            return
        bot.answer_callback_query(call.id)
        try:
            log_content = ""
            file_size = os.path.getsize(log_path)
            max_log_kb = 100
            max_tg_msg = 3500
            if file_size == 0:
                log_content = "(Log empty)"
            elif file_size > max_log_kb * 1024:
                with open(log_path, 'rb') as f:
                    f.seek(-max_log_kb * 1024, os.SEEK_END)
                    log_bytes = f.read()
                log_content = log_bytes.decode('utf-8', errors='ignore')
                log_content = f"(Last {max_log_kb} KB)\n...\n" + log_content
            else:
                with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                    log_content = f.read()
            if len(log_content) > max_tg_msg:
                log_content = log_content[-max_tg_msg:]
            if not log_content.strip():
                log_content = "(No visible content)"
            send_premium(chat_id_for_reply,
                         f"📜 Logs for <code>{file_name}</code> (User <code>{script_owner_id}</code>):\n<pre>{log_content}</pre>")
        except Exception as e:
            logger.error(f"Error reading log: {e}")
            send_premium(chat_id_for_reply, f"❌ Error reading log for <code>{file_name}</code>.")
    except Exception as e:
        bot.answer_callback_query(call.id, "Error fetching logs.", show_alert=True)

def speed_callback(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    start_cb_ping_time = time.time()
    try:
        edit_premium(chat_id, call.message.message_id, "🏃 Testing speed...")
        bot.send_chat_action(chat_id, 'typing')
        response_time = round((time.time() - start_cb_ping_time) * 1000, 2)
        status = "🔓 Unlocked" if not bot_locked else "🔒 Locked"
        if user_id == OWNER_ID:
            user_level = "🤍 Owner"
        elif user_id in admin_ids:
            user_level = "🌙 Admin"
        elif user_id in user_subscriptions and user_subscriptions[user_id].get('expiry', datetime.min) > datetime.now():
            user_level = "⭐ Premium"
        else:
            user_level = "🆓 Free User"
        speed_msg = (f"⚡ Bot Speed & Status:\n\n"
                     f"⏱️ API Response Time: {response_time} ms\n"
                     f"🚦 Bot Status: {status}\n"
                     f"👤 Your Level: {user_level}")
        bot.answer_callback_query(call.id)
        edit_premium(chat_id, call.message.message_id, speed_msg, reply_markup=create_main_menu_inline(user_id))
    except Exception as e:
        logger.error(f"Error during speed test cb: {e}", exc_info=True)
        try:
            bot.answer_callback_query(call.id, "Error in speed test.", show_alert=True)
            edit_premium(chat_id, call.message.message_id, "〽️ Main Menu", reply_markup=create_main_menu_inline(user_id))
        except Exception:
            pass

def back_to_main_callback(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
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
    else:
        user_status = "🆓 Free User"
    main_menu_text = (f"〽️ Welcome back, {call.from_user.first_name}!\n\n"
                      f"🆔 ID: <code>{user_id}</code>\n"
                      f"🔰 Status: {user_status}{expiry_info}\n"
                      f"📁 Files: {current_files} / {limit_str}\n\n"
                      f"👇 Use buttons or type commands.")
    try:
        bot.answer_callback_query(call.id)
        edit_premium(chat_id, call.message.message_id, main_menu_text, reply_markup=create_main_menu_inline(user_id))
    except Exception:
        pass

# --- Admin Callback Implementations ---
def subscription_management_callback(call):
    bot.answer_callback_query(call.id)
    edit_premium(call.message.chat.id, call.message.message_id,
                 "💳 Subscription Management\nSelect action:",
                 reply_markup=create_subscription_menu())

def stats_callback(call):
    bot.answer_callback_query(call.id)
    _logic_statistics(call.message)
    try:
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
                                      reply_markup=create_main_menu_inline(call.from_user.id))
    except Exception:
        pass

def lock_bot_callback(call):
    global bot_locked
    bot_locked = True
    bot.answer_callback_query(call.id, "🔒 Bot locked.")
    try:
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
                                      reply_markup=create_main_menu_inline(call.from_user.id))
    except Exception:
        pass

def unlock_bot_callback(call):
    global bot_locked
    bot_locked = False
    bot.answer_callback_query(call.id, "🔓 Bot unlocked.")
    try:
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
                                      reply_markup=create_main_menu_inline(call.from_user.id))
    except Exception:
        pass

def run_all_scripts_callback(call):
    _logic_run_all_scripts(call)

def broadcast_init_callback(call):
    bot.answer_callback_query(call.id)
    msg = send_premium(call.message.chat.id, "📢 Send message to broadcast.\n/cancel to abort.")
    if msg:
        bot.register_next_step_handler(msg, process_broadcast_message)

def process_broadcast_message(message):
    user_id = message.from_user.id
    if user_id not in admin_ids:
        reply_premium(message, "⚠️ Not authorized.")
        return
    if message.text and message.text.lower() == '/cancel':
        reply_premium(message, "Broadcast cancelled.")
        return
    broadcast_content = message.text
    if not broadcast_content and not (message.photo or message.video or message.document or message.sticker or message.voice or message.audio):
        reply_premium(message, "⚠️ Cannot broadcast empty message.")
        msg = send_premium(message.chat.id, "📢 Send broadcast message or /cancel.")
        if msg:
            bot.register_next_step_handler(msg, process_broadcast_message)
        return
    target_count = len(active_users)
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton("✅ Confirm & Send", callback_data=f"confirm_broadcast_{message.message_id}"),
               types.InlineKeyboardButton("❌ Cancel", callback_data="cancel_broadcast"))
    preview_text = broadcast_content[:1000].strip() if broadcast_content else "(Media message)"
    reply_premium(message, f"⚠️ Confirm Broadcast:\n\n<pre>{preview_text}</pre>\n"
                           f"To <b>{target_count}</b> users. Sure?", reply_markup=markup)

def handle_confirm_broadcast(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    if user_id not in admin_ids:
        bot.answer_callback_query(call.id, "⚠️ Admin only.", show_alert=True)
        return
    try:
        original_message = call.message.reply_to_message
        if not original_message:
            raise ValueError("Could not retrieve original message.")
        broadcast_text = None
        broadcast_photo_id = None
        broadcast_video_id = None
        if original_message.text:
            broadcast_text = original_message.text
        elif original_message.photo:
            broadcast_photo_id = original_message.photo[-1].file_id
        elif original_message.video:
            broadcast_video_id = original_message.video.file_id
        else:
            raise ValueError("Message has no text or supported media.")
        bot.answer_callback_query(call.id, "🚀 Starting broadcast...")
        edit_premium(chat_id, call.message.message_id, f"📢 Broadcasting to {len(active_users)} users...", reply_markup=None)
        thread = threading.Thread(target=execute_broadcast, args=(
            broadcast_text, broadcast_photo_id, broadcast_video_id,
            original_message.caption if (broadcast_photo_id or broadcast_video_id) else None,
            chat_id))
        thread.start()
    except ValueError as ve:
        edit_premium(chat_id, call.message.message_id, f"❌ Error: {str(ve)}", reply_markup=None)
    except Exception as e:
        edit_premium(chat_id, call.message.message_id, "❌ Unexpected error.", reply_markup=None)

def handle_cancel_broadcast(call):
    bot.answer_callback_query(call.id, "Broadcast cancelled.")
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
        if call.message.reply_to_message:
            bot.delete_message(call.message.chat.id, call.message.reply_to_message.message_id)
    except Exception:
        pass

def execute_broadcast(broadcast_text, photo_id, video_id, caption, admin_chat_id):
    sent_count = 0
    failed_count = 0
    blocked_count = 0
    start_exec_time = time.time()
    users_to_broadcast = list(active_users)
    total_users = len(users_to_broadcast)
    batch_size = 25
    delay_batches = 1.5
    for i, user_id_bc in enumerate(users_to_broadcast):
        try:
            if broadcast_text:
                bot.send_message(user_id_bc, premium_emoji(broadcast_text), parse_mode='HTML')
            elif photo_id:
                bot.send_photo(user_id_bc, photo_id,
                               caption=premium_emoji(caption) if caption else None,
                               parse_mode='HTML' if caption else None)
            elif video_id:
                bot.send_video(user_id_bc, video_id,
                               caption=premium_emoji(caption) if caption else None,
                               parse_mode='HTML' if caption else None)
            sent_count += 1
        except telebot.apihelper.ApiTelegramException as e:
            err_desc = str(e).lower()
            if any(s in err_desc for s in ["bot was blocked", "user is deactivated", "chat not found", "kicked from", "restricted"]):
                blocked_count += 1
            elif "flood control" in err_desc or "too many requests" in err_desc:
                retry_after = 5
                match = re.search(r"retry after (\d+)", err_desc)
                if match:
                    retry_after = int(match.group(1)) + 1
                time.sleep(retry_after)
                try:
                    if broadcast_text:
                        bot.send_message(user_id_bc, premium_emoji(broadcast_text), parse_mode='HTML')
                    elif photo_id:
                        bot.send_photo(user_id_bc, photo_id, caption=premium_emoji(caption) if caption else None, parse_mode='HTML' if caption else None)
                    elif video_id:
                        bot.send_video(user_id_bc, video_id, caption=premium_emoji(caption) if caption else None, parse_mode='HTML' if caption else None)
                    sent_count += 1
                except Exception:
                    failed_count += 1
            else:
                failed_count += 1
        except Exception:
            failed_count += 1
        if (i + 1) % batch_size == 0 and i < total_users - 1:
            time.sleep(delay_batches)
        elif i % 5 == 0:
            time.sleep(0.2)
    duration = round(time.time() - start_exec_time, 2)
    result_msg = (f"📢 Broadcast Complete!\n\n"
                  f"✅ Sent: {sent_count}\n"
                  f"❌ Failed: {failed_count}\n"
                  f"🚫 Blocked/Inactive: {blocked_count}\n"
                  f"👥 Targets: {total_users}\n"
                  f"⏱️ Duration: {duration}s")
    try:
        send_premium(admin_chat_id, result_msg)
    except Exception:
        pass

def admin_panel_callback(call):
    bot.answer_callback_query(call.id)
    edit_premium(call.message.chat.id, call.message.message_id,
                 "👑 Admin Panel\nManage admins.",
                 reply_markup=create_admin_panel())

def add_admin_init_callback(call):
    bot.answer_callback_query(call.id)
    msg = send_premium(call.message.chat.id, "👑 Enter User ID to promote to Admin.\n/cancel to abort.")
    if msg:
        bot.register_next_step_handler(msg, process_add_admin_id)

def process_add_admin_id(message):
    owner_id_check = message.from_user.id
    if owner_id_check != OWNER_ID:
        reply_premium(message, "⚠️ Owner only.")
        return
    if message.text and message.text.lower() == '/cancel':
        reply_premium(message, "Admin promotion cancelled.")
        return
    try:
        new_admin_id = int(message.text.strip())
        if new_admin_id <= 0:
            raise ValueError("ID must be positive")
        if new_admin_id == OWNER_ID:
            reply_premium(message, "⚠️ Owner is already Owner.")
            return
        if new_admin_id in admin_ids:
            reply_premium(message, f"⚠️ User <code>{new_admin_id}</code> already Admin.")
            return
        add_admin_db(new_admin_id)
        reply_premium(message, f"✅ User <code>{new_admin_id}</code> promoted to Admin.")
        try:
            send_premium(new_admin_id, "🎉 Congrats! You are now an Admin.")
        except Exception:
            pass
    except ValueError:
        reply_premium(message, "⚠️ Invalid ID. Send numerical ID or /cancel.")
        msg = send_premium(message.chat.id, "👑 Enter User ID to promote or /cancel.")
        if msg:
            bot.register_next_step_handler(msg, process_add_admin_id)

def remove_admin_init_callback(call):
    bot.answer_callback_query(call.id)
    msg = send_premium(call.message.chat.id, "👑 Enter User ID of Admin to remove.\n/cancel to abort.")
    if msg:
        bot.register_next_step_handler(msg, process_remove_admin_id)

def process_remove_admin_id(message):
    owner_id_check = message.from_user.id
    if owner_id_check != OWNER_ID:
        reply_premium(message, "⚠️ Owner only.")
        return
    if message.text and message.text.lower() == '/cancel':
        reply_premium(message, "Admin removal cancelled.")
        return
    try:
        admin_id_remove = int(message.text.strip())
        if admin_id_remove <= 0:
            raise ValueError("ID must be positive")
        if admin_id_remove == OWNER_ID:
            reply_premium(message, "⚠️ Owner cannot remove self.")
            return
        if admin_id_remove not in admin_ids:
            reply_premium(message, f"⚠️ User <code>{admin_id_remove}</code> not Admin.")
            return
        if remove_admin_db(admin_id_remove):
            reply_premium(message, f"✅ Admin <code>{admin_id_remove}</code> removed.")
            try:
                send_premium(admin_id_remove, "ℹ️ You are no longer an Admin.")
            except Exception:
                pass
        else:
            reply_premium(message, f"❌ Failed to remove admin <code>{admin_id_remove}</code>.")
    except ValueError:
        reply_premium(message, "⚠️ Invalid ID.")
        msg = send_premium(message.chat.id, "👑 Enter Admin ID to remove or /cancel.")
        if msg:
            bot.register_next_step_handler(msg, process_remove_admin_id)

def list_admins_callback(call):
    bot.answer_callback_query(call.id)
    try:
        admin_list_str = "\n".join(f"- <code>{aid}</code> {'(Owner)' if aid == OWNER_ID else ''}" for aid in sorted(list(admin_ids)))
        if not admin_list_str:
            admin_list_str = "(No Owner/Admins configured!)"
        edit_premium(call.message.chat.id, call.message.message_id,
                     f"👑 Current Admins:\n\n{admin_list_str}",
                     reply_markup=create_admin_panel())
    except Exception:
        pass

def add_subscription_init_callback(call):
    bot.answer_callback_query(call.id)
    msg = send_premium(call.message.chat.id, "💳 Enter User ID & days (e.g., <code>12345678 30</code>).\n/cancel to abort.")
    if msg:
        bot.register_next_step_handler(msg, process_add_subscription_details)

def process_add_subscription_details(message):
    admin_id_check = message.from_user.id
    if admin_id_check not in admin_ids:
        reply_premium(message, "⚠️ Not authorized.")
        return
    if message.text and message.text.lower() == '/cancel':
        reply_premium(message, "Sub add cancelled.")
        return
    try:
        parts = message.text.split()
        if len(parts) != 2:
            raise ValueError("Incorrect format")
        sub_user_id = int(parts[0].strip())
        days = int(parts[1].strip())
        if sub_user_id <= 0 or days <= 0:
            raise ValueError("User ID/days must be positive")
        current_expiry = user_subscriptions.get(sub_user_id, {}).get('expiry')
        start_date_new_sub = datetime.now()
        if current_expiry and current_expiry > start_date_new_sub:
            start_date_new_sub = current_expiry
        new_expiry = start_date_new_sub + timedelta(days=days)
        save_subscription(sub_user_id, new_expiry)
        reply_premium(message, f"✅ Sub for <code>{sub_user_id}</code> by {days} days.\nNew expiry: {new_expiry:%Y-%m-%d}")
        try:
            send_premium(sub_user_id, f"🎉 Sub activated/extended by {days} days! Expires: {new_expiry:%Y-%m-%d}.")
        except Exception:
            pass
    except ValueError as e:
        reply_premium(message, f"⚠️ Invalid: {str(e)}. Format: <code>ID days</code> or /cancel.")
        msg = send_premium(message.chat.id, "💳 Enter User ID & days, or /cancel.")
        if msg:
            bot.register_next_step_handler(msg, process_add_subscription_details)

def remove_subscription_init_callback(call):
    bot.answer_callback_query(call.id)
    msg = send_premium(call.message.chat.id, "💳 Enter User ID to remove sub.\n/cancel to abort.")
    if msg:
        bot.register_next_step_handler(msg, process_remove_subscription_id)

def process_remove_subscription_id(message):
    admin_id_check = message.from_user.id
    if admin_id_check not in admin_ids:
        reply_premium(message, "⚠️ Not authorized.")
        return
    if message.text and message.text.lower() == '/cancel':
        reply_premium(message, "Sub removal cancelled.")
        return
    try:
        sub_user_id_remove = int(message.text.strip())
        if sub_user_id_remove <= 0:
            raise ValueError("ID must be positive")
        if sub_user_id_remove not in user_subscriptions:
            reply_premium(message, f"⚠️ User <code>{sub_user_id_remove}</code> no active sub.")
            return
        remove_subscription_db(sub_user_id_remove)
        reply_premium(message, f"✅ Sub for <code>{sub_user_id_remove}</code> removed.")
        try:
            send_premium(sub_user_id_remove, "ℹ️ Your subscription removed by admin.")
        except Exception:
            pass
    except ValueError:
        reply_premium(message, "⚠️ Invalid ID.")
        msg = send_premium(message.chat.id, "💳 Enter User ID to remove sub from, or /cancel.")
        if msg:
            bot.register_next_step_handler(msg, process_remove_subscription_id)

def check_subscription_init_callback(call):
    bot.answer_callback_query(call.id)
    msg = send_premium(call.message.chat.id, "💳 Enter User ID to check sub.\n/cancel to abort.")
    if msg:
        bot.register_next_step_handler(msg, process_check_subscription_id)

def process_check_subscription_id(message):
    admin_id_check = message.from_user.id
    if admin_id_check not in admin_ids:
        reply_premium(message, "⚠️ Not authorized.")
        return
    if message.text and message.text.lower() == '/cancel':
        reply_premium(message, "Sub check cancelled.")
        return
    try:
        sub_user_id_check = int(message.text.strip())
        if sub_user_id_check <= 0:
            raise ValueError("ID must be positive")
        if sub_user_id_check in user_subscriptions:
            expiry_dt = user_subscriptions[sub_user_id_check].get('expiry')
            if expiry_dt:
                if expiry_dt > datetime.now():
                    days_left = (expiry_dt - datetime.now()).days
                    reply_premium(message, f"✅ User <code>{sub_user_id_check}</code> active sub.\nExpires: {expiry_dt:%Y-%m-%d %H:%M:%S} ({days_left} days left).")
                else:
                    reply_premium(message, f"⚠️ User <code>{sub_user_id_check}</code> expired sub.")
                    remove_subscription_db(sub_user_id_check)
            else:
                reply_premium(message, f"⚠️ User <code>{sub_user_id_check}</code> in sub list but expiry missing.")
        else:
            reply_premium(message, f"ℹ️ User <code>{sub_user_id_check}</code> no active sub record.")
    except ValueError:
        reply_premium(message, "⚠️ Invalid ID.")
        msg = send_premium(message.chat.id, "💳 Enter User ID to check, or /cancel.")
        if msg:
            bot.register_next_step_handler(msg, process_check_subscription_id)

# --- Cleanup ---
def cleanup():
    logger.warning("Shutdown. Cleaning up processes...")
    script_keys_to_stop = list(bot_scripts.keys())
    if not script_keys_to_stop:
        return
    for key in script_keys_to_stop:
        if key in bot_scripts:
            kill_process_tree(bot_scripts[key])

atexit.register(cleanup)

# --- Main ---
if __name__ == '__main__':
    logger.info("=" * 40 + "\n🤖 Bot Starting Up...\n" + f"🐍 Python: {sys.version.split()[0]}\n" +
                f"🔧 Base Dir: {BASE_DIR}\n📁 Upload Dir: {UPLOAD_BOTS_DIR}\n" +
                f"📊 Data Dir: {IROTECH_DIR}\n🔑 Owner ID: {OWNER_ID}\n🛡️ Admins: {admin_ids}\n" + "=" * 40)
    keep_alive()
    logger.info("🚀 Starting polling...")
    while True:
        try:
            bot.infinity_polling(logger_level=logging.INFO, timeout=60, long_polling_timeout=30)
        except requests.exceptions.ReadTimeout:
            time.sleep(5)
        except requests.exceptions.ConnectionError:
            time.sleep(15)
        except Exception as e:
            logger.critical(f"💥 Unrecoverable polling error: {e}", exc_info=True)
            time.sleep(30)