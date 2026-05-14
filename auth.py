import json
import os
import bcrypt
from datetime import datetime

USERS_FILE = "users.json"

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

def register_user(username, password):
    users = load_users()
    if username in users:
        return False, "Username already exists"
    hashed = bcrypt.hashpw(
        password.encode(), bcrypt.gensalt()
    ).decode()
    users[username] = {
        "password":   hashed,
        "created":    datetime.now().strftime("%Y-%m-%d"),
        "last_login": None
    }
    save_users(users)
    return True, "User created successfully"

def login_user(username, password):
    users = load_users()
    if username not in users:
        return False, "User not found"
    stored = users[username]["password"].encode()
    if bcrypt.checkpw(password.encode(), stored):
        users[username]["last_login"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        save_users(users)
        return True, "Login successful"
    return False, "Incorrect password"

def user_exists():
    return len(load_users()) > 0