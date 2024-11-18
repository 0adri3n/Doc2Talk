import sqlite3
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.backends import default_backend
import base64
import uuid
import datetime
import json
from pyDes import triple_des

CONFIG_PATH = "data/data_location.json"
DB_FILE_PATH = ""
KEY_FILE_PATH = ""

def load_config():
    global DB_FILE_PATH, KEY_FILE_PATH
    with open(CONFIG_PATH, "r") as config_file:
        conf_json = json.load(config_file)
        KEY_FILE_PATH = conf_json["encryption_key_path"]
        DB_FILE_PATH = conf_json["db_path"]


# Load encryption key
def load_encryption_key():
    if not os.path.exists(KEY_FILE_PATH):
        raise FileNotFoundError("Encryption key not found. Generate it using the key generation script.")
    with open(KEY_FILE_PATH, "rb") as key_file:
        return key_file.read()

# Encrypt/decrypt data using Fernet
class EncryptedDB:
    def __init__(self, db_path, key):
        self.db_path = db_path
        self.key = key

    def encrypt(self, data):
        return triple_des(self.key).encrypt(data, padmode=2)

    def decrypt(self, data):
        return triple_des(self.key).decrypt(data, padmode=2)

# Token manager class
class TokenManager:
    def __init__(self, db_path, encryption_key):
        self.db_path = db_path
        self.encrypted_db = EncryptedDB(db_path, encryption_key)
        self.init_db()

    def init_db(self):
        # Initialize the SQLite database and create the table if not exists
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tokens (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    token TEXT NOT NULL UNIQUE,
                    name TEXT NOT NULL,
                    surname TEXT NOT NULL,
                    employee_id TEXT NOT NULL UNIQUE,
                    created_at TEXT NOT NULL
                )
            """)
            conn.commit()

    def generate_token(self, name, surname, employee_id):
        # Generate a unique token
        token = str(uuid.uuid4())
        encrypted_token = self.encrypted_db.encrypt(token)
        created_at = datetime.datetime.utcnow().isoformat()
        # Store token in the database
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT INTO tokens (token, name, surname, employee_id, created_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (encrypted_token, name, surname, employee_id, created_at))
                conn.commit()
                print(f"Token successfully created for {name} {surname} (ID: {employee_id})")
                return token
            except sqlite3.IntegrityError:
                raise ValueError(f"Employee ID {employee_id} already has a token.")

    def validate_token(self, token):
        encrypted_token = self.encrypted_db.encrypt(token)
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM tokens WHERE token = ?", (encrypted_token,))
            row = cursor.fetchone()
            if row:
                return {
                    "id": row[0],
                    "name": row[2],
                    "surname": row[3],
                    "employee_id": row[4],
                    "created_at": row[5]
                }
            return None

    def revoke_token(self, token):
        encrypted_token = self.encrypted_db.encrypt(token)
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM tokens WHERE token = ?", (encrypted_token,))
            if cursor.rowcount > 0:
                conn.commit()
                print("Token successfully revoked.")
            else:
                print("Token not found.")

    def list_tokens(self):
        # List all tokens (decrypted for display)
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name, surname, employee_id, created_at FROM tokens")
            rows = cursor.fetchall()
            return [{"name": r[0], "surname": r[1], "employee_id": r[2], "created_at": r[3]} for r in rows]

# Main functions
def main():
    load_config()
    key = load_encryption_key()
    manager = TokenManager(DB_FILE_PATH, key)

    print("\nToken Manager")
    print("1. Generate a new token")
    print("2. Validate a token")
    print("3. Revoke a token")
    print("4. List all tokens")
    print("5. Exit")

    while True:
        choice = input("\nSelect an option: ")
        if choice == "1":
            name = input("Enter user's name: ")
            surname = input("Enter user's surname: ")
            employee_id = input("Enter user's employee ID: ")
            try:
                token = manager.generate_token(name, surname, employee_id)
                print(f"Generated Token (Not encrypted. Please write it down.): {token}")
            except ValueError as e:
                print(e)
        elif choice == "2":
            token = input("Enter the token: ")
            result = manager.validate_token(token)
            if result:
                print(f"Token is valid for: {result['name']} {result['surname']} (ID: {result['employee_id']})")
            else:
                print("Invalid token.")
        elif choice == "3":
            token = input("Enter the token to revoke: ")
            manager.revoke_token(token)
        elif choice == "4":
            tokens = manager.list_tokens()
            if tokens:
                for t in tokens:
                    print(f"Name: {t['name']}, Surname: {t['surname']}, Employee ID: {t['employee_id']}, Created At: {t['created_at']}")
            else:
                print("No tokens found.")
        elif choice == "5":
            print("Exiting Token Manager.")
            break
        else:
            print("Invalid option. Please try again.")

if __name__ == "__main__":
    main()
