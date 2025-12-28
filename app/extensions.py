#stops circular imports
from flask_mail import Mail
import os
from app.data.db import get_database
from app.auth.services import generate_password_hash

mail = Mail()
security_salt = None
serializer = None


def Register_Admins() -> None:

    """ Registers Admin Users """
    
    Admin1Username = os.getenv('ADMIN_1_USERNAME')
    Admin1Password = os.getenv('ADMIN_1_PASSWORD_HASHED')
    Admin1email = os.getenv('ADMIN_1_EMAIL')

    db = get_database()
    cur = db.cursor()

    cur.execute("SELECT * FROM Users WHERE username = ?", (Admin1Username,))
    if cur.fetchone():
        print("Admin already exists")
        return
        
    cur.execute("INSERT INTO Users (username, password, email, isAdmin) VALUES ( ?, ?, ?, ?)",(Admin1Username, Admin1Password, Admin1email, True))
    db.commit()

    print("successfully registered ADMIN1")

    return

#def Register_Test() -> None:
    """ Registers Test User """
    
    Admin1Username = os.getenv('TEST_USERNAME')
    Admin1Password = os.getenv('ADMIN_1_PASSWORD_HASHED')

    db = get_database()
    cur = db.cursor()

    cur.execute("SELECT * FROM Users WHERE username = ?", (Admin1Username,))
    if cur.fetchone():
        print("Admin already exists")
        return
        
    cur.execute("INSERT INTO Users (username, password, isAdmin) VALUES ( ?, ?, ?)",(Admin1Username, Admin1Password, True))
    db.commit()

    print("successfully registered ADMIN1")

    return