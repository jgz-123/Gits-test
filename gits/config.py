import os
import sys
import json
import argparse
import getpass
from conf import config as app_config
from gits.config_crypto import decrypt_config, encrypt_config, is_encrypted_config

if getattr(sys, 'frozen', False):
    # 打包模式：sys.executable 是可执行文件
    # base_dir 应该是可执行文件所在的目录
    base_dir = os.path.dirname(os.path.abspath(sys.executable))
else:
    # 脚本开发模式：当前文件是 gits/config.py
    # 根目录是 gits/config.py 的上级(gits)的上级(root)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MAIN_PATH = base_dir
CONFIG_PATH = os.path.join(base_dir, "conf", "config.json")
SENSITIVE_CONFIG_KEYS = {
    "lean_remote_ip",
    "lean_remote_port",
    "lean_remote_user",
    "lean_remote_pwd",
    "lean_remote_path",
}


def load_config():
    if not os.path.exists(CONFIG_PATH):
        # 容错：尝试在当前目录查找 (以防 config.json 没被放进 conf 文件夹)
        alt_path = os.path.join(base_dir, "config.json")
        if os.path.exists(alt_path):
            return _load_config_file(alt_path)
        # 如果找不到，抛出异常让 commands.py 捕获并生成
        raise FileNotFoundError(f"Configuration file not found at {CONFIG_PATH}")

    return _load_config_file(CONFIG_PATH)


def _load_config_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    if is_encrypted_config(config):
        return decrypt_config(config)
    return config


def _should_save_encrypted():
    if getattr(sys, 'frozen', False):
        return True
    if not os.path.exists(CONFIG_PATH):
        return False
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            return is_encrypted_config(json.load(f))
    except Exception:
        return False


def save_config(config):
    conf_dir = os.path.dirname(CONFIG_PATH)
    if not os.path.exists(conf_dir):
        os.makedirs(conf_dir, exist_ok=True)
    data = encrypt_config(config) if _should_save_encrypted() else config
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def execute_configs(args):
    try:
        config = load_config()
    except:
        return False

    lean_config = config["lean"]
    param_map = {
        "set_lean_remote_ip": "lean_remote_ip",
        "set_lean_remote_port": "lean_remote_port",
        "set_lean_remote_user": "lean_remote_user",
        "set_lean_remote_pwd": "lean_remote_pwd",
        "set_lean_remote_path": "lean_remote_path",
        "set_lean_local_path": "lean_local_path",
        "lean_remote_ip": "lean_remote_ip",
        "lean_remote_port": "lean_remote_port",
        "lean_remote_user": "lean_remote_user",
        "lean_remote_pwd": "lean_remote_pwd",
        "lean_remote_path": "lean_remote_path",
        "lean_local_path": "lean_local_path"
    }

    for param in ["set_lean_remote_ip", "set_lean_remote_port", "set_lean_remote_user", "set_lean_remote_pwd",
                  "set_lean_remote_path", "set_lean_local_path"]:
        value = getattr(args, param)
        if value is not None and value != '':
            key = param_map[param]
            if key == "lean_remote_port" and not 1 <= value <= 65535:
                print("Port must be between 1 and 65535.")
                return True
            if key in SENSITIVE_CONFIG_KEYS and not _confirm_sensitive_access():
                return True
            lean_config[key] = value
            save_config(config)
            print(f"set successful [{key} = {value}]")
            return True

    for flag in ["lean_remote_ip", "lean_remote_port", "lean_remote_user", "lean_remote_pwd",
                 "lean_remote_path", "lean_local_path"]:
        if getattr(args, flag):
            key = param_map[flag]
            if key in SENSITIVE_CONFIG_KEYS and not _confirm_sensitive_access():
                return True
            value = lean_config.get(key, 22) if key == "lean_remote_port" else lean_config[key]
            print(f"{key} = {value}")
            return True

    return False


def _confirm_sensitive_access():
    try:
        password = getpass.getpass("Password: ")
    except (EOFError, KeyboardInterrupt):
        print("\nPassword verification cancelled.")
        return False

    if password == getattr(app_config, "password", ""):
        return True

    print("Password verification failed.")
    return False


def show_config(conf=None):
    try:
        config = load_config()
    except:
        return None

    lean_config = config.get("lean", {})
    base_url = config.get("base_url")

    if conf:
        if conf == "base_url": return base_url
        if conf == "lean_remote_port": return lean_config.get(conf, 22)
        return lean_config.get(conf)

    print("Base URL:", base_url)
    for key, value in lean_config.items():
        print(f"{key}={value}")
    if "lean_remote_port" not in lean_config:
        print("lean_remote_port=22")


def get_lean_remote_port():
    port = show_config("lean_remote_port")
    try:
        port = int(port)
    except (TypeError, ValueError):
        raise ValueError("lean_remote_port must be an integer between 1 and 65535")
    if not 1 <= port <= 65535:
        raise ValueError("lean_remote_port must be an integer between 1 and 65535")
    return port
