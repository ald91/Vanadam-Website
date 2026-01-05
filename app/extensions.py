#stops circular imports
from flask_mail import Mail
import os
from app.data.db import get_database
from app.auth.services import generate_password_hash

mail = Mail()
security_salt = None
serializer = None


def register_admins() -> None:

    """Registers Admin Users using .env file"""
    
    Admin1Username = os.getenv('ADMIN_1_USERNAME')
    Admin1PasswordHashed = os.getenv('ADMIN_1_PASSWORD_HASHED')
    Admin1email = os.getenv('ADMIN_1_EMAIL')

    db = get_database()
    cur = db.cursor()

    cur.execute("SELECT * FROM Users WHERE username = ?", (Admin1Username,))
    if cur.fetchone():
        print("Admin account already initialized")
        return
        
    cur.execute("INSERT INTO Users (username, password, email, isAdmin) VALUES ( ?, ?, ?, ?)",(Admin1Username, Admin1PasswordHashed, Admin1email, True))
    db.commit()

    print("successfully registered ADMIN1")

    return

def register_test() -> None:
    """ Registers Test User """
    
    testUsername = os.getenv('TEST_USER_USERNAME')
    testPasswordHashed = os.getenv('TEST_USER_PASSWORD_HASHED')
    testEmail = os.getenv('TEST_USER_EMAIL')

    db = get_database()
    cur = db.cursor()

    cur.execute("SELECT * FROM Users WHERE username = ?", (testUsername,))
    if cur.fetchone():
        print("Test user already initialized")
        return
        
    cur.execute("INSERT INTO Users (username, password, email, isAdmin) VALUES ( ?, ?, ?, ?)",(testUsername, testPasswordHashed, testEmail , False))
    db.commit()

    print("successfully registered test user")

    return