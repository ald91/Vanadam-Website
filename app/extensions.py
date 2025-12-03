#stops circular imports
from flask_mail import Mail

mail = Mail()
security_salt = None
serializer = None