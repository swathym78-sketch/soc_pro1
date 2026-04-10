import sqlite3
import hashlib
import os

# =======================================================
# CONFIGURATION
# =======================================================
DB_FILE = "soc_core.db"  # Renamed to force a fresh database and fix the schema error!
SECRET_CLEARANCE_CODE = "SOC-EXPERT-2026"  # The master code required to register

def hash_password(password):
    """Securely hashes a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    """Initializes the SQLite database with a simplified schema."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Create the simplified users table (Only Username and Password)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')
    
    # Create default admin account to prevent lockouts
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        default_user = "admin"
        default_pass = hash_password("admin123")
        
        cursor.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)", 
            (default_user, default_pass)
        )
        print("✅ Default Admin account created. (admin / admin123)")
        
    conn.commit()
    conn.close()

def verify_user(username, password):
    """Checks if the username and password match the database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    hashed_pw = hash_password(password)
    cursor.execute("SELECT username FROM users WHERE username = ? AND password_hash = ?", (username, hashed_pw))
    user = cursor.fetchone()
    
    conn.close()
    
    if user:
        return {"username": user[0]}
    return None

def register_user(username, password, clearance_code):
    """Validates the clearance code and provisions a new SOC account."""
    # 1. Gatekeeper: Check the Secret Clearance Code
    if clearance_code != SECRET_CLEARANCE_CODE:
        return False, "❌ CLASSIFIED: Invalid Clearance Code. Incident logged."
        
    # 2. Basic Input Validation
    if not username or not password:
        return False, "❌ Callsign and Passphrase are required."
        
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # 3. Check for existing username (Callsign)
    cursor.execute("SELECT username FROM users WHERE username = ?", (username,))
    if cursor.fetchone():
        conn.close()
        return False, f"❌ The callsign '{username}' is already in use."
        
    # 4. Insert the new user
    hashed_pw = hash_password(password)
    try:
        cursor.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, hashed_pw)
        )
        conn.commit()
        conn.close()
        return True, "✅ Clearance verified. Account provisioned successfully."
    except Exception as e:
        conn.close()
        return False, f"❌ Database failure during provisioning: {e}"

# Ensure the database is initialized
init_db()