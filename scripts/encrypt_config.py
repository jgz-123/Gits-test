import importlib.util
import json
import os
import sys


ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CRYPTO_PATH = os.path.join(ROOT_DIR, "gits", "config_crypto.py")


def load_config_crypto():
    spec = importlib.util.spec_from_file_location("gits_config_crypto", CRYPTO_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    if len(sys.argv) != 3:
        print("Usage: python scripts/encrypt_config.py <source_config.json> <target_config.json>")
        return 1

    source_path = sys.argv[1]
    target_path = sys.argv[2]
    config_crypto = load_config_crypto()

    with open(source_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    if not config_crypto.is_encrypted_config(config):
        config = config_crypto.encrypt_config(config)

    target_dir = os.path.dirname(os.path.abspath(target_path))
    os.makedirs(target_dir, exist_ok=True)
    with open(target_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
