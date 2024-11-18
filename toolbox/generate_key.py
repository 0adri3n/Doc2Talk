import json
from pathlib import Path
import secrets

# Load configuration
CONFIG_PATH = "data/data_location.json"

def load_config():
    with open(CONFIG_PATH, "r") as config_file:
        return json.load(config_file)

def main():
    config = load_config()
    key_path = Path(config["encryption_key_path"])

    if key_path.exists():
        print(f"Key already exists at {key_path}.")
        return

    encryption_key = secrets.token_bytes(24)
    key_path.parent.mkdir(parents=True, exist_ok=True) 

    with open(key_path, "wb") as key_file:
        key_file.write(encryption_key)

    print(f"Encryption key generated and saved to {key_path}.")

if __name__ == "__main__":
    main()
